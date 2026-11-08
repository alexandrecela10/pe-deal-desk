#!/usr/bin/env python3
"""Portfolio company KPI variance and covenant headroom.

Usage:
    python3 kpi_monitor.py kpis.csv [--net-debt X --ltm-ebitda X --ltm-interest X]
                           [--max-leverage X] [--min-interest-cover X]
                           [--amber 0.05] [--red 0.10] [--out monitor_output]

CSV columns: metric, actual, budget, prior_year (optional), higher_is_better (optional true/false).
Standard library only.
"""
import argparse
import csv

LOWER_IS_BETTER_HINTS = ("churn", "cost", "opex", "dso", "days", "debt", "capex", "attrition",
                         "turnover", "complaint", "returns", "cac", "payback", "arrears", "overdue")


def fnum(v):
    try:
        return float(str(v).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def rag(adverse_pct, amber, red):
    if adverse_pct is None:
        return "n/a"
    if adverse_pct > red:
        return "🔴 Red"
    if adverse_pct > amber:
        return "🟠 Amber"
    return "🟢 Green"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--net-debt", type=float)
    ap.add_argument("--ltm-ebitda", type=float)
    ap.add_argument("--ltm-interest", type=float)
    ap.add_argument("--max-leverage", type=float)
    ap.add_argument("--min-interest-cover", type=float)
    ap.add_argument("--amber", type=float, default=0.05)
    ap.add_argument("--red", type=float, default=0.10)
    ap.add_argument("--out", default="monitor_output")
    args = ap.parse_args()

    with open(args.csv, newline="") as f:
        rows = [{k.strip().lower(): v for k, v in r.items()} for r in csv.DictReader(f)]

    guessed, out = [], []
    for r in rows:
        name = r["metric"].strip()
        a, b, py = fnum(r.get("actual")), fnum(r.get("budget")), fnum(r.get("prior_year"))
        hib = (r.get("higher_is_better") or "").strip().lower()
        if hib in ("true", "false", "yes", "no", "1", "0"):
            higher = hib in ("true", "yes", "1")
        else:
            higher = not any(h in name.lower() for h in LOWER_IS_BETTER_HINTS)
            guessed.append(f"{name}: {'higher' if higher else 'lower'} is better")
        vs_bud = (a - b) / abs(b) if a is not None and b not in (None, 0) else None
        vs_py = (a - py) / abs(py) if a is not None and py not in (None, 0) else None
        adverse = None
        if vs_bud is not None:
            adverse = -vs_bud if higher else vs_bud
        out.append({"metric": name, "actual": a, "budget": b, "prior_year": py,
                    "vs_budget_pct": vs_bud, "vs_prior_year_pct": vs_py,
                    "higher_is_better": higher, "adverse_pct": adverse,
                    "rag": rag(adverse, args.amber, args.red)})

    def p(x):
        return "n/a" if x is None else f"{x * 100:+.1f}%"

    def n(x):
        return "n/a" if x is None else f"{x:,.1f}"

    order = {"🔴 Red": 0, "🟠 Amber": 1, "🟢 Green": 2, "n/a": 3}
    out.sort(key=lambda r: (order[r["rag"]], -(r["adverse_pct"] or 0)))
    reds = [r["metric"] for r in out if r["rag"] == "🔴 Red"]
    ambers = [r["metric"] for r in out if r["rag"] == "🟠 Amber"]

    md = ["# Portfolio monitoring summary", "",
          f"**{len(reds)} red, {len(ambers)} amber, "
          f"{sum(r['rag'] == '🟢 Green' for r in out)} green** "
          f"(amber > {args.amber:.0%} adverse to budget, red > {args.red:.0%})", ""]
    if reds:
        md.append("Red: " + ", ".join(reds))
        md.append("")
    md += ["## KPI variance", "", "| Metric | Actual | Budget | vs budget | Prior year | vs PY | RAG |",
           "|---|---|---|---|---|---|---|"]
    for r in out:
        md.append(f"| {r['metric']} | {n(r['actual'])} | {n(r['budget'])} | {p(r['vs_budget_pct'])} | "
                  f"{n(r['prior_year'])} | {p(r['vs_prior_year_pct'])} | {r['rag']} |")

    cov = []
    if args.net_debt is not None and args.ltm_ebitda:
        lev = args.net_debt / args.ltm_ebitda
        line = f"| Net leverage | {lev:.2f}x |"
        if args.max_leverage:
            breach_ebitda = args.net_debt / args.max_leverage
            headroom = 1 - breach_ebitda / args.ltm_ebitda
            status = "🔴 Red" if headroom < 0.10 else "🟠 Amber" if headroom < 0.20 else "🟢 Green"
            line += (f" ≤ {args.max_leverage:.2f}x | {headroom:.1%} EBITDA headroom "
                     f"(breach if LTM EBITDA < {breach_ebitda:,.1f}) | {status} |")
        else:
            line += " n/a | n/a | n/a |"
        cov.append(line)
    if args.ltm_interest and args.ltm_ebitda:
        ic = args.ltm_ebitda / args.ltm_interest
        line = f"| Interest cover | {ic:.2f}x |"
        if args.min_interest_cover:
            breach_ebitda = args.min_interest_cover * args.ltm_interest
            headroom = 1 - breach_ebitda / args.ltm_ebitda
            status = "🔴 Red" if headroom < 0.10 else "🟠 Amber" if headroom < 0.20 else "🟢 Green"
            line += (f" ≥ {args.min_interest_cover:.2f}x | {headroom:.1%} EBITDA headroom "
                     f"(breach if LTM EBITDA < {breach_ebitda:,.1f}) | {status} |")
        else:
            line += " n/a | n/a | n/a |"
        cov.append(line)
    if cov:
        md += ["", "## Covenants", "", "| Test | Current | Covenant | Headroom | RAG |", "|---|---|---|---|---|"] + cov
    if guessed:
        md += ["", "## Direction guesses (confirm)", ""] + [f"- {g}" for g in guessed]
    md.append("")

    with open(f"{args.out}.md", "w") as f:
        f.write("\n".join(md))
    with open(f"{args.out}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"{len(reds)} red / {len(ambers)} amber | wrote {args.out}.md and {args.out}.csv")


if __name__ == "__main__":
    main()
