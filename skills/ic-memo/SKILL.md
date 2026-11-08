---
name: ic-memo
description: Draft an investment committee (IC) memo for a private equity deal — recommendation, thesis, business overview, financials, valuation & returns, risks & mitigants, diligence findings, value creation plan and asks. Use when the user asks for an IC memo, IC paper, investment recommendation, or approval paper.
---

# IC Memo

An IC memo is an argument, not a data dump. Lead with the ask and the answer.

## Gather first
Look in the working directory for outputs from the other skills and reuse them rather than recomputing:
- `screening_note.md`, `screen_financials.csv` (cim-screen)
- `lbo_output.md` / `.json` (lbo-model)
- `comps_output.md` (comps-valuation)
- `diligence_plan.md`, `red_flags.csv` (diligence-plan)

Ask for: the stage (first-round / final / approval), the specific ask (bid range, budget for advisors, final approval), the fund's house template if they have one. If a house template exists, follow it exactly instead of the structure below.

## Default structure: `ic_memo.md`
1. **Recommendation & ask** (half a page): what we want approval for, price/range, equity cheque, expected IRR/MOIC base and downside, key conditions.
2. **Investment thesis**: 3–5 pillars, each with the evidence and the diligence that confirmed it.
3. **Business overview**: what it does, how it makes money, market position — short.
4. **Financial summary**: historical and projected table, quality of earnings adjustments, cash conversion.
5. **Valuation & returns**: entry multiple vs comps, sources & uses, base / upside / downside cases with the assumptions that differ, sensitivity table, value creation bridge.
6. **Key risks & mitigants**: table — risk, likelihood, impact, mitigant, residual risk. Include the risks the deal team is least comfortable with, not just the easy ones.
7. **Diligence status**: completed, open items, red flags and how each is resolved or priced in.
8. **Value creation plan**: first 100 days and the 3–4 levers in the base case, with owners and how they show up in EBITDA.
9. **Exit**: likely buyers and routes, exit multiple assumption and why it is credible.
10. **Appendix**: detailed tables.

## Writing rules
- Write for a sceptical partner: state the bear case honestly in its own section.
- Each number must match its source file. If two sources disagree, flag it rather than picking one silently.
- Downside case must be a real downside (e.g. no growth, margin compression, exit at entry multiple −2x), not base case minus 5%.
- Keep the body to ~6 pages; push detail to the appendix.
- Offer to turn it into a Word document or slides if the IC uses those.
