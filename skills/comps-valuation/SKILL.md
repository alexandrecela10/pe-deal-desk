---
name: comps-valuation
description: Build trading comps or precedent transaction tables (EV/Revenue, EV/EBITDA, EV/EBIT, P/E), compute summary statistics, flag outliers and derive an implied valuation range for a target. Use when the user asks for comps, multiples, "what's it worth", benchmarking a price, or a football field.
---

# Comps Valuation

## Inputs
A CSV with one row per comparable. Required columns: `company`, `ev`, plus at least one of `revenue`, `ebitda`, `ebit`. Optional: `net_income`, `market_cap`, `type` (trading / transaction), `date`, `notes`. All figures in the same currency and units. See `examples/comps.csv` in this skill's folder.

If the user only gives names, ask them for the data or a data export (Capital IQ, PitchBook, FactSet, Bloomberg). Do not invent multiples from memory; if a figure must come from a public source, cite the source and date next to it.

## Run
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/comps-valuation/scripts/comps.py" comps.csv \
  --target-ebitda 42 --target-revenue 210 --target-net-debt 95 --out comps_output
```

Run the script yourself — the user should never have to open a terminal or type a command. If `CLAUDE_PLUGIN_ROOT` is not set (e.g. in Claude chat or Cowork), run it from this skill's own `scripts/` folder.
Outputs `comps_output.md` (multiples table, stats, implied EV and equity ranges) and `comps_output.csv`.

## Method
- Multiples are only computed when the denominator is positive.
- Outliers (outside 1.5× IQR, or EV/EBITDA above 40x) are flagged and **excluded from the stats** but still shown, so the user sees what was dropped.
- Implied valuation uses the 25th percentile / median / 75th percentile of each multiple.
- Equity value = implied EV − target net debt (if provided).

## Presenting
- Lead with the implied EV range and the multiple it rests on, then the table.
- Say which comps are least comparable and why (size, growth, margin, geography). A median of poor comps is not a valuation.
- If both trading and transaction comps are present, show them separately — transaction multiples include a control premium.
- Offer a football-field chart (range bars per method) if the user wants a visual.
