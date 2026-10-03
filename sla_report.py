#!/usr/bin/env python3
"""
Vireo Audio - weekly first-response SLA breach report (prototype).

Usage:
    python sla_report.py --data ./data --out ./out [--week 2026-06-22] [--llm]

Inputs  (in --data): tickets.csv, agents.csv   (orders/customers/products not needed)
Outputs (in --out) : weekly_trend.csv, weekly_by_shift.csv, agent_report.csv,
                     weekly_report.md  (manager-friendly summary)
Rules come from support-policy.pdf v3.2 (targets s.3, shifts s.7, credit s.3).
"""
import argparse, math, os
import numpy as np
import pandas as pd

# ---- policy constants (support-policy.pdf) ---------------------------------
TARGET_MIN = {"chat": 15, "voice": 120, "social": 240, "email": 480}   # s.3
CREDIT_INR = 350                                                        # s.3
SHIFTS = {"Morning": (6, 14), "Day": (14, 22), "Night": (22, 6)}        # s.7, IST
IST = pd.Timedelta(hours=5, minutes=30)                                 # export is UTC
ROSTER_CHANGE = pd.Timestamp("2025-06-30")                              # Indore night shift ends 29 Jun

# ---- risk thresholds (tunable, documented in README) -----------------------
SHIFT_RED, SHIFT_AMBER = 0.25, 0.15       # trailing-4-week breach rate
AGENT_MIN_N, AGENT_RATIO, AGENT_P = 30, 1.5, 0.01   # trailing-13-week, in-hours only


def shift_of(hour):
    return "Morning" if 6 <= hour < 14 else "Day" if 14 <= hour < 22 else "Night"


def load(data):
    t = pd.read_csv(os.path.join(data, "tickets.csv"))
    a = pd.read_csv(os.path.join(data, "agents.csv"), parse_dates=["from_date", "to_date"])
    n_raw = len(t)
    # 1. de-duplicate migration re-imports: keep the helpdesk copy (sorts before legacy_fd)
    t = t.sort_values(["ticket_id", "source_system"]).drop_duplicates("ticket_id", keep="first")
    n_dupes = n_raw - len(t)
    for c in ["created_at", "first_response_at", "resolved_at"]:
        t[c] = pd.to_datetime(t[c])
    # 2. UTC -> IST (everything downstream is IST)
    t["created_ist"] = t.created_at + IST
    t["frt_min"] = (t.first_response_at - t.created_at).dt.total_seconds() / 60
    # 3. CSAT: legacy 0 = no response -> blank; never treat blank as zero
    t["csat"] = t.csat_score.where(t.csat_score > 0)
    # 4. SLA flag (policy s.3 / s.10)
    t["target_min"] = t.channel.map(TARGET_MIN)
    t["breach"] = t.frt_min > t.target_min
    t["credit_eligible"] = t.breach & t.status.isin(["resolved", "closed"])
    # 5. shift = shift in force when the ticket ARRIVED (not the resolver's shift)
    t["arrival_shift"] = t.created_ist.dt.hour.map(shift_of)
    t["week"] = t.created_ist.dt.to_period("W-SUN").dt.start_time
    # 6. resolver's roster row on creation date (one row per assignment)
    d = t.created_ist.dt.normalize()
    m = t[["ticket_id", "agent_id"]].assign(d=d.values).merge(a, on="agent_id", how="left")
    m = m[(m.from_date <= m.d) & (m.to_date.isna() | (m.to_date >= m.d))]
    m = m.drop_duplicates("ticket_id").set_index("ticket_id")
    t = t.join(m[["name", "team", "shift", "site", "tier"]].rename(
        columns={"name": "agent_name", "team": "agent_team", "shift": "agent_shift",
                 "site": "agent_site", "tier": "agent_tier"}), on="ticket_id")
    return t, a, {"raw_rows": n_raw, "duplicates_removed": n_dupes}


def poisson_sf(k, mu):
    """P(X >= k) for Poisson(mu)."""
    return 1 - sum(math.exp(-mu) * mu ** i / math.factorial(i) for i in range(k))


def staffed_hours_flag(t, a):
    """Is any rostered agent on the arrival shift for the ticket's channel pool on that date?"""
    d = t.created_ist.dt.normalize()
    on = {}
    for day in d.unique():
        r = a[(a.from_date <= day) & (a.to_date.isna() | (a.to_date >= day))]
        on[day] = set(r["shift"])
    return pd.Series([s in on[x] for s, x in zip(t.arrival_shift, d)], index=t.index)


def build(t, a, week):
    week = pd.Timestamp(week) if week else t.week[t.week < t.week.max()].max()  # last COMPLETE week
    t = t.copy()
    t["staffed"] = staffed_hours_flag(t, a)
    # inevitable = due time falls before the next staffed shift start (06:00 IST for night arrivals)
    due = t.created_ist + pd.to_timedelta(t.target_min, unit="m")
    h = t.created_ist.dt.hour
    nxt = np.where(h >= 22, t.created_ist.dt.normalize() + pd.Timedelta(days=1, hours=6),
                   np.where(h < 6, t.created_ist.dt.normalize() + pd.Timedelta(hours=6), t.created_ist))
    t["structural"] = (~t.staffed) & (due < pd.to_datetime(nxt))

    def agg(g):
        return pd.Series({"tickets": len(g), "breaches": int(g.breach.sum()),
                          "breach_rate": g.breach.mean(),
                          "structural_breaches": int((g.breach & g.structural).sum()),
                          "credit_inr": int(g.credit_eligible.sum()) * CREDIT_INR,
                          "csat": g.csat.mean(), "csat_n": int(g.csat.notna().sum())})

    trend = t.groupby("week").apply(agg, include_groups=False).reset_index()
    trend["rolling4_rate"] = (trend.breaches.rolling(4, min_periods=1).sum() /
                              trend.tickets.rolling(4, min_periods=1).sum())
    by_shift = t.groupby(["week", "arrival_shift"]).apply(agg, include_groups=False).reset_index()

    # trailing windows
    w4 = t[(t.week > week - pd.Timedelta(weeks=4)) & (t.week <= week)]
    s4 = w4.groupby("arrival_shift").apply(agg, include_groups=False)
    s4["status"] = np.where(s4.breach_rate >= SHIFT_RED, "RED",
                            np.where(s4.breach_rate >= SHIFT_AMBER, "AMBER", "GREEN"))

    # agent view: resolver per policy s.3, but split controllable (staffed hours) vs structural
    w13 = t[(t.week > week - pd.Timedelta(weeks=13)) & (t.week <= week)]
    ih = w13[w13.staffed]
    exp_rate = ih.groupby("channel").breach.mean()          # channel-mix adjustment
    rows = []
    for ag, g in w13.groupby("agent_id"):
        gi = g[g.staffed]
        exp = gi.channel.map(exp_rate).sum()
        act = int(gi.breach.sum())
        ratio = act / exp if exp else np.nan
        p = poisson_sf(act, exp) if exp else np.nan
        rows.append({"agent_id": ag, "name": g.agent_name.iloc[-1], "team": g.agent_team.iloc[-1],
                     "shift": g.agent_shift.iloc[-1], "tier": g.agent_tier.iloc[-1],
                     "tickets": len(g), "raw_breach_rate": g.breach.mean(),
                     "pct_tickets_arrived_unstaffed": (~g.staffed).mean(),
                     "in_hours_tickets": len(gi), "in_hours_breach_rate": gi.breach.mean() if len(gi) else np.nan,
                     "expected_breaches": round(exp, 1), "actual_breaches": act,
                     "ratio_vs_expected": round(ratio, 2), "p_value": round(p, 4) if exp else np.nan})
    ag = pd.DataFrame(rows)
    ag["flag"] = np.where((ag.in_hours_tickets >= AGENT_MIN_N) & (ag.ratio_vs_expected >= AGENT_RATIO)
                          & (ag.p_value < AGENT_P) & (ag.tier == 1), "WATCH",
                          np.where((ag.tier == 2) & (ag.ratio_vs_expected >= AGENT_RATIO), "TIER2-n/a", ""))
    ag = ag.sort_values("raw_breach_rate", ascending=False)
    return week, t, trend, by_shift, s4, ag


def summary(week, t, trend, s4, ag, meta, w_quality):
    wk = trend[trend.week == week].iloc[0]
    prev = trend[trend.week == week - pd.Timedelta(weeks=1)]
    d = "" if prev.empty else f" ({wk.breach_rate - prev.breach_rate.iloc[0]:+.1%} vs prior week)"
    tw = t[t.week == week]
    unstaffed = tw[~tw.staffed]
    L = [f"# Weekly first-response SLA report - week of {week:%d %b %Y} (IST)", ""]
    L += ["## Headline",
          f"- **{int(wk.breaches)} of {int(wk.tickets)} tickets breached ({wk.breach_rate:.1%}){d}.** "
          f"Credits triggered: Rs {int(wk.credit_inr):,}.",
          f"- **{(unstaffed.breach.sum() / max(tw.breach.sum(), 1)):.0%} of this week's breaches were on tickets "
          f"that arrived when no agent was rostered** ({len(unstaffed)} tickets, "
          f"{unstaffed.breach.mean() if len(unstaffed) else 0:.0%} breached). "
          f"In staffed hours the breach rate was {tw[tw.staffed].breach.mean():.1%}.", ""]
    L += ["## Shifts (shift the ticket ARRIVED in, IST; trailing 4 weeks)", "",
          "| Shift | Tickets | Breach rate | Structural* | Status |", "|---|---|---|---|---|"]
    for sh in ["Morning", "Day", "Night"]:
        if sh in s4.index:
            r = s4.loc[sh]
            L.append(f"| {sh} | {int(r.tickets)} | {r.breach_rate:.1%} | {int(r.structural_breaches)} | {r.status} |")
    L += ["", "*Structural = target time passed before the next rostered shift could start; no agent action could have prevented it.", ""]
    L += ["## Agents (trailing 13 weeks)", "",
          "Raw breach rate is shown for completeness but is **not** used to flag people: agents who start the "
          "morning inherit overnight arrivals. WATCH uses breaches on tickets that arrived in staffed hours, "
          "adjusted for channel mix.", "",
          "| Agent | Team/shift | Raw rate | % arrived unstaffed | In-hours vs expected | Flag |", "|---|---|---|---|---|---|"]
    for _, r in ag.head(10).iterrows():
        L.append(f"| {r['name']} ({r.agent_id}) | {r.team} / {r['shift']} | {r.raw_breach_rate:.0%} | "
                 f"{r.pct_tickets_arrived_unstaffed:.0%} | {r.ratio_vs_expected:.2f}x | {r.flag} |")
    watch = ag[ag.flag == "WATCH"]
    L += ["", f"**Agents on WATCH (staffed-hours performance clearly above peers): "
              f"{', '.join(watch['name']) if len(watch) else 'none'}.**", ""]
    L += ["## Trend (last 8 complete weeks)", "", "| Week | Tickets | Breach rate | 4-wk rolling |", "|---|---|---|---|"]
    for _, r in trend[trend.week <= week].tail(8).iterrows():
        L.append(f"| {r.week:%d %b} | {int(r.tickets)} | {r.breach_rate:.1%} | {r.rolling4_rate:.1%} |")
    L += ["", "## Data notes",
          f"- {meta['duplicates_removed']} duplicate (migration re-import) rows removed; timestamps converted UTC->IST; "
          "legacy CSAT 0 treated as no response.",
          "- `agent_id` is the **resolving** agent (policy s.3), not necessarily who sent the first reply.",
          f"- {w_quality}"]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="./data"); ap.add_argument("--out", default="./out")
    ap.add_argument("--week", default=None, help="Monday of week to report (default: last complete week)")
    ap.add_argument("--llm", action="store_true", help="optional: have Claude rewrite the summary in plain English")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    t, a, meta = load(args.data)
    week, t, trend, by_shift, s4, ag = build(t, a, args.week)
    # data-quality gates (fail loudly rather than publish wrong numbers)
    assert t.ticket_id.is_unique, "duplicate ticket ids after de-dup"
    assert (t.frt_min >= 0).all(), "negative first-response time"
    assert t.agent_team.notna().all(), "ticket resolved by agent with no roster row on that date"
    voice_hours = t[t.channel == "voice"].created_ist.dt.hour
    assert voice_hours.between(8, 21).all(), "voice tickets outside 08-22 IST: timezone conversion is wrong"
    wq = "Quality gates passed (unique ids, no negative response times, every resolver on roster, voice only 08-22 IST)."

    trend.to_csv(os.path.join(args.out, "weekly_trend.csv"), index=False)
    by_shift.to_csv(os.path.join(args.out, "weekly_by_shift.csv"), index=False)
    ag.to_csv(os.path.join(args.out, "agent_report.csv"), index=False)
    md = summary(week, t, trend, s4, ag, meta, wq)

    if args.llm and os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic  # pip install anthropic ; the LLM only rewrites numbers it is given
        msg = anthropic.Anthropic().messages.create(
            model="claude-sonnet-4-6", max_tokens=600,
            messages=[{"role": "user", "content":
                       "Rewrite this SLA report as a 5-sentence plain-English note for a support operations "
                       "manager. Use ONLY numbers present in the text. Do not blame individuals for breaches on "
                       "tickets that arrived when no agent was rostered.\n\n" + md}])
        md = "## Manager note (AI-drafted from the numbers below)\n" + msg.content[0].text + "\n\n" + md
    open(os.path.join(args.out, "weekly_report.md"), "w").write(md)
    print(md)


if __name__ == "__main__":
    main()
