# Weekly first-response SLA report - week of 22 Jun 2026 (IST)

## Headline
- **49 of 207 tickets breached (23.7%) (+0.1% vs prior week).** Credits triggered: Rs 15,750.
- **73% of this week's breaches were on tickets that arrived when no agent was rostered** (46 tickets, 78% breached). In staffed hours the breach rate was 8.1%.

## Shifts (shift the ticket ARRIVED in, IST; trailing 4 weeks)

| Shift | Tickets | Breach rate | Structural* | Status |
|---|---|---|---|---|
| Morning | 258 | 8.9% | 0 | GREEN |
| Day | 305 | 8.9% | 0 | GREEN |
| Night | 164 | 78.0% | 86 | RED |

*Structural = target time passed before the next rostered shift could start; no agent action could have prevented it.

## Agents (trailing 13 weeks)

Raw breach rate is shown for completeness but is **not** used to flag people: agents who start the morning inherit overnight arrivals. WATCH uses breaches on tickets that arrived in staffed hours, adjusted for channel mix.

| Agent | Team/shift | Raw rate | % arrived unstaffed | In-hours vs expected | Flag |
|---|---|---|---|---|---|
| Sameer Joshi (A3005) | Chat Frontline / Morning | 59% | 55% | 1.52x |  |
| Neha Chatterjee (A3010) | Chat Frontline / Morning | 56% | 46% | 2.15x |  |
| Steven Kaur (A3008) | Chat Frontline / Morning | 51% | 49% | 1.02x |  |
| Neha Gaikwad (A3007) | Chat Frontline / Morning | 50% | 41% | 1.80x |  |
| Karan Roy (A3011) | Chat Frontline / Morning | 50% | 52% | 0.00x |  |
| Ritika Chatterjee (A3013) | Chat Frontline / Morning | 50% | 48% | 0.40x |  |
| Amit Kulkarni (A3033) | Billing / Morning | 45% | 40% | 1.15x |  |
| Riya Gaikwad (A3039) | Escalations & Warranty / Morning | 43% | 40% | 2.20x | TIER2-n/a |
| Ramesh Patel (A3009) | Chat Frontline / Morning | 40% | 36% | 0.73x |  |
| Krishna Kaur (A3028) | Logistics / Morning | 40% | 42% | 0.74x |  |

**Agents on WATCH (staffed-hours performance clearly above peers): none.**

## Trend (last 8 complete weeks)

| Week | Tickets | Breach rate | 4-wk rolling |
|---|---|---|---|
| 04 May | 158 | 22.2% | 25.5% |
| 11 May | 172 | 27.3% | 25.9% |
| 18 May | 178 | 25.3% | 25.0% |
| 25 May | 157 | 26.1% | 25.3% |
| 01 Jun | 162 | 22.2% | 25.3% |
| 08 Jun | 163 | 28.8% | 25.6% |
| 15 Jun | 195 | 23.6% | 25.1% |
| 22 Jun | 207 | 23.7% | 24.5% |

## Data notes
- 616 duplicate (migration re-import) rows removed; timestamps converted UTC->IST; legacy CSAT 0 treated as no response.
- `agent_id` is the **resolving** agent (policy s.3), not necessarily who sent the first reply.
- Quality gates passed (unique ids, no negative response times, every resolver on roster, voice only 08-22 IST).