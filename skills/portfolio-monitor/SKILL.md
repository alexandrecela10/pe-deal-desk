---
name: portfolio-monitor
description: Analyse a portfolio company's monthly or quarterly reporting pack — KPI variance vs budget and prior year, covenant headroom (leverage, interest cover), cash runway and an early-warning summary for the deal team or board. Use when the user shares a management accounts pack, KPI file, or asks about covenant headroom or portfolio performance.
---

# Portfolio Monitor

## Inputs
- KPI data as CSV with columns `metric, actual, budget, prior_year` (one period) — see `examples/kpis.csv` in this skill's folder. If the user gives a PDF or Excel pack, extract the figures into this format first and show them the extracted table to confirm.
- For covenants: net debt, LTM EBITDA, LTM interest, and the covenant levels from the facility agreement.
- Optional: `higher_is_better` column (true/false) for metrics where lower is good (e.g. churn, DSO, costs). If missing, the script guesses from the metric name and lists its guesses.

## Run
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/portfolio-monitor/scripts/kpi_monitor.py" kpis.csv \
  --net-debt 180 --ltm-ebitda 41 --ltm-interest 14 \
  --max-leverage 5.5 --min-interest-cover 2.5 --out monitor_output
```

Run the script yourself — the user should never have to open a terminal or type a command. If `CLAUDE_PLUGIN_ROOT` is not set (e.g. in Claude chat or Cowork), run it from this skill's own `scripts/` folder.
Outputs `monitor_output.md` with a RAG-rated variance table and covenant headroom, and `monitor_output.csv`.

## RAG thresholds (defaults, override with flags)
- Green: within 5% of budget or better.
- Amber: 5–10% adverse.
- Red: more than 10% adverse.
- Covenant headroom: Red below 10% EBITDA headroom, Amber 10–20%, Green above 20%.

EBITDA headroom = how far LTM EBITDA can fall before the leverage covenant is breached: `1 − (net debt / max leverage) / LTM EBITDA`.

## Presenting
1. **Headline** (3 lines): on track / watch / concern, and why.
2. **What moved**: the 3 biggest variances with the likely driver (ask the user or check commentary in the pack — do not invent a driver).
3. **Covenants**: current level, covenant, headroom, and the EBITDA fall that would cause a breach.
4. **Questions for management** for the next portfolio review.
If the user tracks several periods, append each run to a `history.csv` and show the trend for the red metrics.
