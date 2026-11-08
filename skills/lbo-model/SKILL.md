---
name: lbo-model
description: Build a quick LBO / paper LBO and returns analysis (sources & uses, debt schedule with cash sweep, IRR, MOIC, value creation bridge, sensitivity tables). Use when the user asks for an LBO, returns analysis, "what IRR do we get", "how much can we pay", leverage scenarios, or a paper LBO.
---

# LBO Model

A transparent, scriptable LBO. The engine is `scripts/lbo.py` (standard library only). It is deliberately simple so every number can be checked by hand.

## Workflow
1. **Gather assumptions** into a JSON file (copy `examples/lbo_inputs.json` from this skill's folder as a template). Ask for anything material that is missing — entry EBITDA, entry multiple, leverage and exit year are mandatory. For other fields, use the template defaults and list them explicitly as assumptions in the output.
2. **Run the base case:**
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/lbo-model/scripts/lbo.py" inputs.json --out lbo_output
   ```
   (If `CLAUDE_PLUGIN_ROOT` is not set — e.g. in Claude chat or Cowork — run the script from this skill's own `scripts/` folder. Run it yourself — the user should never have to type a command.)
   This writes `lbo_output.md` (readable summary), `lbo_output.json` (all numbers) and `lbo_output_years.csv` (annual projections).
3. **Sensitivities** are included automatically: IRR and MOIC across entry × exit multiple, and IRR across exit multiple × leverage. Pass `--grid-step 0.5` to change the multiple step.
4. **Max price question** ("what can we pay for a 20% IRR?"): run with `--target-irr 0.20`; the script solves for the entry multiple.
5. **Present** the summary: sources & uses, returns, value creation bridge, key sensitivities, and the 3 assumptions the answer is most sensitive to.

## Model conventions (state these when presenting)
- Interest is charged on the opening debt balance of each year (avoids circularity).
- Free cash flow = net income + D&A − capex − increase in net working capital.
- Mandatory amortisation is paid first; a share of the remaining cash (`cash_sweep_pct`) repays the senior tranche. Junior tranches are bullet unless `amort_pct` is set.
- No dividend recaps or interim distributions, so IRR = MOIC^(1/years) − 1.
- Exit equity = exit EV − net debt (debt − cash).
- Value creation bridge splits the equity gain into EBITDA growth (at entry multiple), multiple expansion (on exit EBITDA), deleveraging, and fees leakage. The parts sum exactly to the gain.

## Going further
- If the user wants an Excel model, build it with formulas (not hard-coded values) mirroring these conventions, and check it ties to the script output to the nearest 0.1.
- Management rollover, earn-outs, PIK, or dividend recaps are not in the script: model them explicitly in Python and explain the change.
- Never present the base case without the sensitivity table: a single IRR is a false-precision answer.
