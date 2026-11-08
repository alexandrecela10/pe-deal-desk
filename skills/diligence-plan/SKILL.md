---
name: diligence-plan
description: Build a tailored due diligence plan — workstreams, information request list (IRL), key questions tied to the investment thesis, advisor scopes and a red-flag tracker. Use when the user moves a deal into diligence, asks for a DD checklist, IRL, data request list, or diligence questions.
---

# Diligence Plan

Diligence should test the thesis, not tick boxes. Every request should map to a thesis point or a risk.

## Inputs
- The thesis (from the screening note or IC memo if present in the working directory — look for `screening_note.md` or `ic_memo.md`).
- Sector, deal type (platform / add-on / carve-out / minority), timeline to signing.
- Any VDR index already available (if provided, map requests against it and mark what is already covered).

## Process
1. **List the 3–6 thesis pillars and the top 5 risks.** Confirm with the user if they were not given.
2. **For each pillar and risk, write the key question** that would prove or kill it, the evidence needed, and who answers it (management, VDR, commercial advisor, FDD, legal, tax, tech, ESG, insurance, management referencing).
3. **Build the IRL** grouped by workstream. Number each request (e.g. FIN-01), set a priority (P1 = needed for the decision, P2 = needed for SPA/financing, P3 = confirmatory), and link it to the question it answers.
4. **Sector add-ons:** add the requests specific to the sector. Examples:
   - Software/SaaS: ARR bridge, cohort retention, NRR/GRR, CAC payback, code ownership & open-source licences, hosting costs, security incidents.
   - Healthcare: reimbursement mix, regulatory inspections, clinician dependence.
   - Industrials: capacity utilisation, capex backlog, raw material pass-through clauses, environmental liabilities.
   - Consumer: channel mix, like-for-like sales, returns, inventory ageing.
   - Financial services: regulatory capital, licences, complaints data, conduct risk.
   - Carve-outs: TSA scope, stranded costs, standalone cost build.
5. **Quality of earnings focus list:** the EBITDA add-backs and working capital items the FDD provider must test.

## Outputs
- `diligence_plan.md` — pillars, key questions, workstream owners, timeline (week-by-week to signing).
- `irl.csv` — columns: `id, workstream, request, priority, linked_question, owner, status, date_requested, date_received, notes`. Status starts as `Open`.
- `red_flags.csv` — columns: `id, finding, severity (High/Med/Low), workstream, impact_on_valuation, mitigation, status`.

## Rules
- Keep P1 requests under ~40. A 400-line IRL on day one slows the process and annoys the seller.
- Every key question must have a "what answer kills the deal" line.
- When the user later shares VDR documents, update `irl.csv` statuses and add findings to `red_flags.csv` rather than starting again.
