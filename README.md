# PE Deal Desk — private equity skills for Claude Code

Six skills that cover a deal from first look to portfolio monitoring. Each skill tells Claude how a PE deal team actually works, and the numerical ones ship with small, readable Python scripts (standard library only) so the numbers are reproducible rather than made up in the chat.

| Skill | What it does | Ask Claude something like |
|---|---|---|
| `cim-screen` | One-page go/no-go note from a CIM or teaser: financial snapshot, add-back review, hockey-stick check, red flags, banker questions | "Screen this CIM against our criteria" |
| `lbo-model` | Paper LBO: sources & uses, debt schedule with cash sweep, IRR/MOIC, value creation bridge, sensitivity grids, max price for a target IRR | "Run an LBO at 10x with 5x leverage — what can we pay for a 20% IRR?" |
| `comps-valuation` | Trading and transaction comps, outlier handling, implied EV and equity ranges | "Build comps from this export and value the target" |
| `diligence-plan` | Thesis-driven DD plan, prioritised IRL, sector-specific requests, red-flag tracker | "We're in exclusivity, build the diligence plan and IRL" |
| `ic-memo` | IC memo that reuses the outputs above, with an honest bear case | "Draft the IC memo for final approval" |
| `portfolio-monitor` | KPI variance vs budget/PY with RAG, covenant headroom, management questions | "Review this month's pack — how much covenant headroom do we have?" |

The skills hand off to each other: the screen feeds the LBO and comps, and all of them feed the IC memo.

## Install

**As a plugin (recommended).** Push this folder to a GitHub repo, then in Claude Code:

```
/plugin marketplace add <github-user>/pe-deal-desk
/plugin install pe-deal-desk@pe-deal-desk
```

**Or copy the skills.** Copy each folder in `skills/` into `~/.claude/skills/` (all projects) or `.claude/skills/` in a project. Restart Claude Code.

Claude picks a skill automatically when the request matches; you can also name it ("use the lbo-model skill").

## Try it

```bash
python3 skills/lbo-model/scripts/lbo.py examples/lbo_inputs.json --target-irr 0.20 --out lbo_output
python3 skills/comps-valuation/scripts/comps.py examples/comps.csv --target-ebitda 42 --target-revenue 210 --target-net-debt 95
python3 skills/portfolio-monitor/scripts/kpi_monitor.py examples/kpis.csv --net-debt 180 --ltm-ebitda 41 --ltm-interest 14 --max-leverage 5.5 --min-interest-cover 2.5
```

## Make it yours

- Put your fund's investment criteria in a `criteria.md` in your deal folder; `cim-screen` will read it.
- Put your house IC template in the deal folder and tell Claude to use it; `ic-memo` follows a house template over its default.
- Edit the RAG thresholds, sector add-ons or memo structure directly in each `SKILL.md`.

## Confidentiality

Deal documents are confidential. Use these skills only with tools and accounts your firm has approved for that data, and check your NDA before uploading a CIM anywhere.

## Model simplifications

The LBO script is a paper LBO: interest on opening balances, no revolver, no PIK, no dividend recaps, no management rollover. It is built to be checked by hand, not to replace the deal model. The `lbo-model` skill tells Claude to extend it explicitly when a deal needs more.
