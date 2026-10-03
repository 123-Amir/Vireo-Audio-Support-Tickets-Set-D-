# Vireo Audio – Weekly SLA Breach Reporting Tool

## Overview

This tool generates a weekly First Response SLA breach report for Vireo Audio's support operations team.

The report identifies:

* Weekly SLA breach percentage
* Breach trends over time
* Shift-wise performance (Morning, Day, Night)
* Agents with elevated breach rates
* Estimated SLA credit impact
* Structural breaches caused by roster gaps

The goal is to help Support Operations Managers quickly identify where SLA failures are occurring and take corrective action.

---

## Business Objective

Current breach rate: **23.7%**

Analysis shows that most breaches occur during unstaffed periods, especially overnight.

By identifying recurring breach patterns and shift-level staffing issues, the business can reduce SLA breaches and associated customer compensation costs.

Example from the latest report:

* 49 SLA breaches in one week
* Estimated SLA credits: ₹15,750

Reducing breaches from 23.7% to 15% would significantly reduce recurring support costs and improve customer experience.

---

## Project Structure

```text
data/
├── tickets.csv
├── agents.csv
├── customers.csv
├── orders.csv
└── products.csv

out/
├── weekly_report.md
├── weekly_by_shift.csv
├── weekly_trend.csv
└── agent_report.csv

sla_report.py
README.md
submission-form.md
```

---

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate environment:

### Windows

```bash
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install pandas numpy
```

---

## Running the Tool

Place the exported CSV files inside the `data` folder.

Run:

```bash
python sla_report.py --data ./data --out ./out
```

The tool generates:

```text
out/weekly_report.md
out/weekly_by_shift.csv
out/weekly_trend.csv
out/agent_report.csv
```

---

## Optional Arguments

Generate report for a specific week:

```bash
python sla_report.py --data ./data --out ./out --week 2026-06-22
```

Generate an LLM-assisted summary:

```bash
python sla_report.py --data ./data --out ./out --llm
```

Requires:

```bash
ANTHROPIC_API_KEY=<your_key>
```

---

## Validation & Data Quality Checks

Before generating the report, the tool validates:

* Duplicate ticket records
* Missing ticket IDs
* Negative response times
* Missing roster assignments
* Timestamp conversion consistency

The report generation stops if critical validation checks fail.

---

## Key Assumptions

* All exported timestamps are in UTC.
* The tool converts all timestamps to IST.
* SLA credit per breach = ₹350.
* Shift definitions and thresholds are configurable at the top of `sla_report.py`.
* Resolver agent is used for agent-level analysis.

---

## Output

The generated report includes:

1. Weekly SLA breach summary
2. Shift-wise breach analysis
3. Agent performance review
4. Historical trend analysis
5. Data quality notes

---

## Author

Amir Hussain
B.Tech Computer Science & Engineering
BIT Mesra (2026)
