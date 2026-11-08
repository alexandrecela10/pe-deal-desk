---
name: cim-screen
description: Screen a CIM, teaser, management presentation or info memo into a one-page go/no-go screening note with key metrics, thesis, red flags and first-round questions. Use when the user shares a CIM/teaser PDF or asks "should we look at this deal", "screen this", "first look".
---

# CIM Screen

Turn a sell-side document into a one-page screening note a deal team can decide on in five minutes.

## Inputs
- The CIM / teaser / management presentation (PDF, DOCX or pasted text). Read the whole document, including the appendix: the financial tables and footnotes are usually at the back.
- Optional: the fund's investment criteria (cheque size, sectors, geography, EBITDA range, control vs minority). If a `criteria.md` exists in the working directory, read it. If none is given, ask once; if the user does not answer, screen against generic mid-market buyout criteria and say so.

## Process
1. **Extract the numbers first.** Build a small table of historical and projected revenue, gross margin, EBITDA (reported and adjusted), capex and cash conversion for every year shown. Write it to `screen_financials.csv`. Note the source page for each figure.
2. **Reconcile adjustments.** List every EBITDA add-back with its amount and % of adjusted EBITDA. Flag add-backs above 10% of EBITDA in total, any "run-rate" or "pro forma" synergies, and one-offs that recur across years.
3. **Check the hockey stick.** Compare projected growth and margin against the historical CAGR. Flag any year where projected growth is more than 1.5x the historical CAGR or margin expands by more than 300bps without a stated driver.
4. **Concentration & quality.** Customer concentration (top 1 / top 10), supplier concentration, recurring vs one-off revenue, contract length, churn/NRR if SaaS, working capital seasonality.
5. **Score against criteria.** Pass / Borderline / Fail on each criterion.
6. **Write the note** using the template below.

## Output: `screening_note.md`

```
# [Company] — Screening note
**Recommendation:** Pursue / Pass / Pursue with conditions   **Confidence:** High / Med / Low
**Process:** [banker, round, timing, indicative bid date if stated]

## Snapshot
| | FY-2 | FY-1 | FY0 / LTM | FY+1 (mgmt) |
| Revenue | | | | |
| Growth % | | | | |
| Adj. EBITDA | | | | |
| Margin % | | | | |
| Cash conversion % | | | | |

## What the business does (3 lines max)
## Why it could be interesting (thesis, 3 bullets)
## Red flags (ranked, each with the CIM page reference)
## Criteria fit (table: criterion | requirement | company | pass/fail)
## Indicative valuation range (ask-implied multiple vs sector range; say "not enough data" rather than invent)
## First-round questions for the banker (max 8, the ones that would change the decision)
```

## Rules
- Every number must trace to a page in the document. If a figure is derived, show the calculation.
- Never fill a gap with an assumption presented as fact. Write "not disclosed".
- Keep the note to one page. Detail goes in `screen_financials.csv`.
- For a valuation check, hand off to the `comps-valuation` skill; for a quick returns check, hand off to `lbo-model`.
