#!/usr/bin/env python3
"""Comparable companies / precedent transactions analysis.

Usage:
    python3 comps.py comps.csv [--target-revenue X] [--target-ebitda X] [--target-ebit X]
                     [--target-net-income X] [--target-net-debt X] [--out comps_output]

CSV columns: company, ev, revenue, ebitda, ebit (optional), net_income + market_cap (optional),
type (optional: trading / transaction). Standard library only.
"""
import argparse
import csv
import statistics

MULTIPLES = [
    ("EV/Revenue", "ev", "revenue", "target_revenue", 15.0),
    ("EV/EBITDA", "ev", "ebitda", "target_ebitda", 40.0),
    ("EV/EBIT", "ev", "ebit", "target_ebit", 60.0),
    ("P/E", "market_cap", "net_income", "target_net_income", 80.0),
]


def fnum(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = (len(sorted_vals) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def analyse(rows, group_label):
    results = {}
    for name, num_col, den_col, _, cap in MULTIPLES:
        vals = []
        for r in rows:
            n, d = fnum(r.get(num_col)), fnum(r.get(den_col))
            if n is None or d is None or d <= 0:
                r[name] = None
                continue
            r[name] = n / d
            vals.append((r["company"], n / d))
        if not vals:
            continue
        xs = sorted(v for _, v in vals)
        q1, q3 = quantile(xs, 0.25), quantile(xs, 0.75)
        iqr = q3 - q1
        lo_f, hi_f = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        kept, dropped = [], []
        for c, v in vals:
            if (len(vals) >= 4 and (v < lo_f or v > hi_f)) or v > cap:
                dropped.append((c, v))
            else:
                kept.append(v)
        kept.sort()
        if not kept:
            continue
        results[name] = {
            "n": len(kept), "min": kept[0], "p25": quantile(kept, 0.25),
            "median": statistics.median(kept), "mean": statistics.mean(kept),
            "p75": quantile(kept, 0.75), "max": kept[-1], "excluded": dropped,
        }
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    for _, _, _, tkey, _ in MULTIPLES:
        ap.add_argument("--" + tkey.replace("_", "-"), type=float, dest=tkey)
    ap.add_argument("--target-net-debt", type=float, dest="target_net_debt")
    ap.add_argument("--out", default="comps_output")
    args = ap.parse_args()

    with open(args.csv, newline="") as f:
        rows = [{k.strip().lower(): v for k, v in r.items()} for r in csv.DictReader(f)]
    groups = {}
    for r in rows:
        groups.setdefault((r.get("type") or "comps").strip().lower(), []).append(r)

    md = ["# Comparables analysis", ""]
    out_rows = []
    for g, grows in groups.items():
        stats = analyse(grows, g)
        md += [f"## {g.title()} ({len(grows)} companies)", "",
               "| Company | EV | " + " | ".join(m[0] for m in MULTIPLES if m[0] in stats) + " |",
               "|---|---|" + "---|" * len([m for m in MULTIPLES if m[0] in stats])]
        for r in grows:
            cells = []
            for m in MULTIPLES:
                if m[0] not in stats:
                    continue
                v = r.get(m[0])
                flag = " ⚠" if any(c == r["company"] for c, _ in stats[m[0]]["excluded"]) else ""
                cells.append("n/m" if v is None else f"{v:.1f}x{flag}")
            ev = fnum(r.get("ev"))
            md.append(f"| {r['company']} | {ev:,.0f} | " + " | ".join(cells) + " |" if ev is not None
                      else f"| {r['company']} | n/a | " + " | ".join(cells) + " |")
            out_rows.append({"group": g, "company": r["company"],
                             **{m[0]: r.get(m[0]) for m in MULTIPLES}})
        if any(s["excluded"] for s in stats.values()):
            md += ["", "⚠ = outlier, excluded from statistics."]
        md += ["", "| Multiple | n | Min | 25th | Median | Mean | 75th | Max |",
               "|---|---|---|---|---|---|---|---|"]
        for name, s in stats.items():
            md.append(f"| {name} | {s['n']} | {s['min']:.1f}x | {s['p25']:.1f}x | {s['median']:.1f}x | "
                      f"{s['mean']:.1f}x | {s['p75']:.1f}x | {s['max']:.1f}x |")
        implied = []
        for name, _, _, tkey, _ in MULTIPLES:
            metric = getattr(args, tkey)
            if metric is None or name not in stats:
                continue
            s = stats[name]
            lo, mid, hi = (s["p25"] * metric, s["median"] * metric, s["p75"] * metric)
            label = "Equity value" if name == "P/E" else "EV"
            row = f"| {name} | {metric:,.1f} | {label} | {lo:,.0f} | {mid:,.0f} | {hi:,.0f} |"
            if name != "P/E" and args.target_net_debt is not None:
                nd = args.target_net_debt
                row += f" {lo - nd:,.0f} – {hi - nd:,.0f} (mid {mid - nd:,.0f}) |"
            else:
                row += " |"
            implied.append(row)
        if implied:
            md += ["", "### Implied valuation (25th / median / 75th percentile)", "",
                   "| Multiple | Target metric | Basis | Low | Mid | High | Implied equity (EV − net debt) |",
                   "|---|---|---|---|---|---|---|"] + implied
        md.append("")

    with open(f"{args.out}.md", "w") as f:
        f.write("\n".join(md))
    with open(f"{args.out}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["group", "company"] + [m[0] for m in MULTIPLES])
        w.writeheader()
        w.writerows(out_rows)
    print(f"Wrote {args.out}.md and {args.out}.csv")


if __name__ == "__main__":
    main()
