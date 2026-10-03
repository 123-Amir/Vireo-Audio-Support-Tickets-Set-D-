# Weekly SLA breach report (prototype)

Setup (once): `python -m venv .venv && source .venv/bin/activate && pip install pandas numpy` (add `anthropic` for `--llm`)

Run weekly:
1. Export tickets.csv and agents.csv from the helpdesk (API export is UTC; the script converts to IST).
2. Put them in `./data/`.
3. `python sla_report.py --data ./data --out ./out` → open `out/weekly_report.md`.
   Optional: `--week 2026-06-22` for a specific Monday; `--llm` (needs ANTHROPIC_API_KEY) adds a plain-English note.

Rules live at the top of the script (SLA targets, Rs 350 credit, shift hours, risk thresholds). Change them there.
The script stops with an error if a data-quality gate fails instead of publishing a wrong report.
