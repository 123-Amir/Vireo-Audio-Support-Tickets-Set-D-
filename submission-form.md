# Submission Form — Vireo Audio: Weekly SLA Breach Report (Set D)

> No `submission-form.md` template was included in the upload, so this uses a standard structure.
> If your programme has a fixed template, paste these answers into it. The "prompts / versions" section
> describes the analytical iterations actually performed in this session; edit it to match your own process.

## 1. Client and request
- **Client:** Vireo Audio Pvt. Ltd. — Neha Kulkarni, Support Operations Manager
- **Ask (email 9 Sep 2026):** weekly first-response SLA breach report by agent and shift; "nothing fancy".
- **Constraints heard in thread:** headcount frozen to Q4 (Arjun); don't demoralise the morning chat team (Priya); credits line has tripled (Arjun) vs "credits look flat, CSAT moved" (Priya).

## 2. Business problem (one sentence)
First-response breaches rose from ~9% to ~25% of tickets after 30 Jun 2025, and the cause is that tickets arriving 22:00–06:00 IST have had no rostered agent since the Indore night shift was dissolved — but the standard report blames the morning agents who inherit them.

## 3. Data used and quality handling
| Issue | Handling |
|---|---|
| 616 ticket_ids duplicated (helpdesk + legacy_fd), identical except CSAT | Kept helpdesk copy → 11,816 rows → 11,200 tickets |
| Export is UTC; policy shifts are IST | +5:30 before any shift/week logic (68% of tickets would change shift label otherwise) |
| Legacy CSAT 0 = no response | Treated as blank (excluded from averages) |
| `agent_id` = resolver, not first responder | Disclosed; agent view uses staffed-hours breaches only |
| Roster is one row per assignment | Joined on ticket creation date |
| 3 night agents (A3001, A3016, A3017) end 29 Jun 2025 with no successor row | Flagged to client: left, or missing rows? |
| `orders.csv` listed in README but not supplied | Not needed for SLA question; noted |
| `submission-form.md`, `email-thread.txt` | Thread read from prompt; form template not supplied |

## 4. Goal (measurable)
- **Current state (Q2 2026):** 563 / 2,230 tickets breached = 25.2%; 534 credit-eligible → Rs 1,86,900 credits; night-arrival tickets 80% breached (405 of 504) = 72% of credits.
- **Target state:** night-arrival breach rate ≤ 12% (pre-reshuffle night rate was 10.3%; in-hours is 8.9%); overall ≈ 9.8%.
- **Expected improvement:** −15.4 pts overall breach rate; ~345 fewer breaches per quarter.
- **Estimated quarterly impact:** ≈ Rs 1.15 lakh fewer credits (range Rs 1.0–1.3 L; ≈ Rs 4.6 L/yr) at zero incremental cost if covered by reallocating existing agents; plus night-arrival CSAT recovery (2.94 → ~3.4 on responders).

## 5. Solution
Local Python (pandas) script, CSV in → weekly Markdown/CSV out. No database. Optional Claude call rewrites the numeric summary into plain English (off by default). Files: `sla_tool/sla_report.py`, `sample_output/`.

## 6. Validation summary
Independent re-computation of headline numbers; quality gates in code (unique IDs, no negative response times, voice only 08–22 IST, every resolver on roster); date-aligned step change at the 30 Jun 2025 roster change; shift-level result invariant to dedupe; sensitivity to UTC-vs-IST shown. **Confidence:** high on pattern and cause; medium on rupee savings (depends on night coverage actually working and on night arrivals continuing at ~500/qtr).

## 7. Risks
Moving agents to night shifts could raise day breaches if day capacity is not truly slack (ticket counts per agent are low and cannot prove slack); night differential/allowance cost unknown; resolver ≠ first responder; people may read agent tables as blame.

## 8. Assumptions
Export is the full ticket population; policy v3.2 targets and shifts applied for the whole period; credit applies to breached tickets in resolved/closed status only; hour-of-day in IST = arrival time + 5:30.

## 9. Prompts / versions / discarded
- **Prompt:** the single structured brief (10 steps) from the user, with the instruction "do not assume anything not supported by the files".
- **v1 (discarded):** breach rate by resolving agent, as the helpdesk reports it → morning chat agents at 37–42%, looks like a people problem.
- **v2 (discarded):** shift by resolver roster shift / UTC clock → mislabels 68% of tickets, hides the pattern (Night "13.8%").
- **v3 (final):** IST conversion + de-dup + shift of arrival + date-aware roster join → night arrivals 79% breached post-June vs 10% before; in-hours flat ~9%.
- **Also discarded:** hiring recommendation (headcount frozen; one night seat ≈ Rs 1.2 L/qtr ≈ the credits saved); agent league table on raw rate.

## 10. AI usage and its limits
AI used for exploration, code drafting and wording. Every figure in the memo comes from the script, not from model recall. In the shipped tool, AI only rewrites numbers it is given; all calculations are deterministic pandas.
