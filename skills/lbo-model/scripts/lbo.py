#!/usr/bin/env python3
"""Simple, transparent LBO engine.

Usage:
    python3 lbo.py inputs.json [--out lbo_output] [--grid-step 1.0] [--target-irr 0.20]

Conventions:
- Interest on opening debt balance (no circularity).
- FCF = net income + D&A - capex - increase in NWC.
- Mandatory amortisation first, then cash sweep (share of excess cash above
  min_cash) repays tranches flagged "sweep": true, in order.
- No interim distributions: IRR = MOIC ** (1 / years) - 1.
- Exit equity = exit EV - (debt - cash).
Standard library only.
"""
import argparse
import copy
import csv
import json
import sys

DEFAULTS = {
    "company": "Target",
    "currency": "m",
    "exit_year": 5,
    "revenue_growth": 0.05,
    "ebitda_margin": None,          # default: entry margin held flat
    "da_pct_revenue": 0.03,
    "capex_pct_revenue": 0.03,
    "nwc_pct_revenue": 0.10,
    "tax_rate": 0.25,
    "transaction_fees_pct": 0.02,   # % of entry EV
    "financing_fees_pct": 0.02,     # % of total debt
    "min_cash": 0.0,
    "cash_sweep_pct": 1.0,
    "interest_on_cash": 0.0,
    "exit_multiple": None,          # default: equal to entry multiple
    "debt": [
        {"name": "Senior term loan", "multiple": 4.0, "rate": 0.08, "amort_pct": 0.01, "sweep": True}
    ],
}

REQUIRED = ["entry_ebitda", "entry_revenue", "entry_multiple"]


def as_series(value, n, name):
    if isinstance(value, (int, float)):
        return [float(value)] * n
    if isinstance(value, list):
        if len(value) < n:
            # extend with the last value
            value = value + [value[-1]] * (n - len(value))
        return [float(v) for v in value[:n]]
    raise ValueError(f"{name} must be a number or a list")


def load_inputs(path):
    with open(path) as f:
        raw = json.load(f)
    missing = [k for k in REQUIRED if k not in raw]
    if missing:
        sys.exit(f"Missing required inputs: {', '.join(missing)}")
    cfg = copy.deepcopy(DEFAULTS)
    cfg.update(raw)
    defaulted = sorted(k for k in DEFAULTS if k not in raw)
    return cfg, defaulted


def run(cfg):
    n = int(cfg["exit_year"])
    e0 = float(cfg["entry_ebitda"])
    r0 = float(cfg["entry_revenue"])
    m_in = float(cfg["entry_multiple"])
    m_out = float(cfg["exit_multiple"] if cfg["exit_multiple"] is not None else m_in)
    growth = as_series(cfg["revenue_growth"], n, "revenue_growth")
    margin = as_series(cfg["ebitda_margin"] if cfg["ebitda_margin"] is not None else e0 / r0, n, "ebitda_margin")

    ev_in = e0 * m_in
    tranches = []
    for t in cfg["debt"]:
        amount = float(t.get("amount", float(t.get("multiple", 0)) * e0))
        tranches.append({
            "name": t["name"],
            "original": amount,
            "balance": amount,
            "rate": float(t.get("rate", 0)),
            "amort_pct": float(t.get("amort_pct", 0)),
            "sweep": bool(t.get("sweep", False)),
        })
    debt_in = sum(t["original"] for t in tranches)
    tx_fees = ev_in * float(cfg["transaction_fees_pct"])
    fin_fees = debt_in * float(cfg["financing_fees_pct"])
    min_cash = float(cfg["min_cash"])
    uses = {"Enterprise value": ev_in, "Transaction fees": tx_fees,
            "Financing fees": fin_fees, "Cash to balance sheet": min_cash}
    total_uses = sum(uses.values())
    equity_in = total_uses - debt_in
    sources = {t["name"]: t["original"] for t in tranches}
    sources["Sponsor equity"] = equity_in

    years = []
    warnings = []
    cash = min_cash
    rev_prev = r0
    for y in range(1, n + 1):
        rev = rev_prev * (1 + growth[y - 1])
        ebitda = rev * margin[y - 1]
        da = rev * float(cfg["da_pct_revenue"])
        ebit = ebitda - da
        interest = sum(t["balance"] * t["rate"] for t in tranches)
        interest_income = cash * float(cfg["interest_on_cash"])
        ebt = ebit - interest + interest_income
        tax = max(0.0, ebt * float(cfg["tax_rate"]))
        ni = ebt - tax
        capex = rev * float(cfg["capex_pct_revenue"])
        d_nwc = (rev - rev_prev) * float(cfg["nwc_pct_revenue"])
        fcf = ni + da - capex - d_nwc

        mandatory = 0.0
        for t in tranches:
            pay = min(t["original"] * t["amort_pct"], t["balance"])
            t["balance"] -= pay
            mandatory += pay
        available = cash + fcf - mandatory - min_cash
        sweep_total = 0.0
        if available > 0:
            to_sweep = available * float(cfg["cash_sweep_pct"])
            for t in tranches:
                if not t["sweep"] or to_sweep <= 0:
                    continue
                pay = min(to_sweep, t["balance"])
                t["balance"] -= pay
                to_sweep -= pay
                sweep_total += pay
        cash = cash + fcf - mandatory - sweep_total
        if cash < 0:
            warnings.append(f"Year {y}: cash shortfall of {-cash:.1f} (revolver not modelled)")
        debt = sum(t["balance"] for t in tranches)
        years.append({
            "year": y, "revenue": rev, "growth": growth[y - 1], "ebitda": ebitda,
            "margin": margin[y - 1], "da": da, "ebit": ebit, "interest": interest,
            "tax": tax, "net_income": ni, "capex": capex, "change_nwc": d_nwc,
            "fcf": fcf, "mandatory_amort": mandatory, "sweep": sweep_total,
            "cash": cash, "total_debt": debt, "net_debt": debt - cash,
            "leverage": (debt - cash) / ebitda if ebitda else float("nan"),
            "interest_cover": ebitda / interest if interest else float("inf"),
            **{f"debt_{t['name']}": t["balance"] for t in tranches},
        })
        rev_prev = rev

    last = years[-1]
    ev_out = last["ebitda"] * m_out
    nd_out = last["net_debt"]
    equity_out = ev_out - nd_out
    moic = equity_out / equity_in if equity_in > 0 else float("nan")
    irr = moic ** (1 / n) - 1 if moic and moic > 0 else float("nan")

    nd_in = debt_in - min_cash
    bridge = {
        "EBITDA growth": (last["ebitda"] - e0) * m_in,
        "Multiple expansion": (m_out - m_in) * last["ebitda"],
        "Deleveraging": nd_in - nd_out,
        "Fees": -(tx_fees + fin_fees),
    }
    bridge_total = sum(bridge.values())
    gain = equity_out - equity_in
    assert abs(bridge_total - gain) < 1e-6, (bridge_total, gain)

    return {
        "company": cfg["company"], "currency": cfg["currency"],
        "entry": {"ebitda": e0, "revenue": r0, "multiple": m_in, "ev": ev_in,
                  "total_debt": debt_in, "leverage": debt_in / e0, "equity": equity_in,
                  "equity_pct": equity_in / total_uses},
        "sources": sources, "uses": uses,
        "exit": {"year": n, "ebitda": last["ebitda"], "multiple": m_out, "ev": ev_out,
                 "net_debt": nd_out, "equity": equity_out},
        "returns": {"moic": moic, "irr": irr, "equity_gain": gain},
        "bridge": bridge, "years": years, "warnings": warnings,
    }


def scaled_leverage(cfg, total_multiple):
    c = copy.deepcopy(cfg)
    base = sum(float(t.get("multiple", 0)) for t in c["debt"])
    if base <= 0:
        return c
    for t in c["debt"]:
        t["multiple"] = float(t.get("multiple", 0)) * total_multiple / base
        t.pop("amount", None)
    return c


def solve_entry_multiple(cfg, target_irr):
    lo, hi = 1.0, 40.0

    def f(m):
        c = copy.deepcopy(cfg)
        c["entry_multiple"] = m
        if c.get("exit_multiple") is None:
            c["exit_multiple"] = cfg["entry_multiple"]
        irr = run(c)["returns"]["irr"]
        return irr if irr == irr else -1.0  # nan -> very bad

    # Below a certain entry multiple, debt exceeds the price and equity is negative
    # (IRR undefined). Start the search at the lowest multiple with a valid IRR.
    while lo < hi and f(lo) == -1.0:
        lo += 0.25
    if lo >= hi or f(lo) < target_irr:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(mid) >= target_irr:
            lo = mid
        else:
            hi = mid
    return lo


def pct(x):
    return "n/m" if x != x else f"{x * 100:.1f}%"


def mult(x):
    return "n/m" if x != x else f"{x:.2f}x"


def num(x):
    return f"{x:,.1f}"


def grid(cfg, row_key, row_vals, col_key, col_vals, metric):
    rows = []
    for rv in row_vals:
        row = []
        for cv in col_vals:
            c = copy.deepcopy(cfg)
            if c.get("exit_multiple") is None:
                c["exit_multiple"] = cfg["entry_multiple"]
            for key, val in ((row_key, rv), (col_key, cv)):
                if key == "leverage":
                    c = scaled_leverage(c, val)
                else:
                    c[key] = val
            row.append(run(c)["returns"][metric])
        rows.append(row)
    return rows


def md_grid(title, row_label, row_vals, col_label, col_vals, values, fmt):
    out = [f"### {title}", "", f"| {row_label} \\ {col_label} | " + " | ".join(f"{v:.1f}x" for v in col_vals) + " |",
           "|---|" + "---|" * len(col_vals)]
    for rv, row in zip(row_vals, values):
        out.append(f"| {rv:.1f}x | " + " | ".join(fmt(v) for v in row) + " |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs")
    ap.add_argument("--out", default="lbo_output")
    ap.add_argument("--grid-step", type=float, default=1.0)
    ap.add_argument("--target-irr", type=float)
    args = ap.parse_args()

    cfg, defaulted = load_inputs(args.inputs)
    res = run(cfg)
    cur = res["currency"]
    m_in = res["entry"]["multiple"]
    m_out = res["exit"]["multiple"]
    lev = res["entry"]["leverage"]
    s = args.grid_step
    entry_vals = [m_in + s * k for k in range(-2, 3)]
    exit_vals = [m_out + s * k for k in range(-2, 3)]
    lev_vals = [max(0.0, lev + 0.5 * k) for k in range(-2, 3)]

    irr_grid = grid(cfg, "entry_multiple", entry_vals, "exit_multiple", exit_vals, "irr")
    moic_grid = grid(cfg, "entry_multiple", entry_vals, "exit_multiple", exit_vals, "moic")
    lev_grid = grid(cfg, "leverage", lev_vals, "exit_multiple", exit_vals, "irr")
    res["sensitivities"] = {"entry_vals": entry_vals, "exit_vals": exit_vals, "leverage_vals": lev_vals,
                            "irr_entry_exit": irr_grid, "moic_entry_exit": moic_grid, "irr_leverage_exit": lev_grid}

    if args.target_irr is not None:
        res["max_entry_multiple"] = solve_entry_multiple(cfg, args.target_irr)

    md = [f"# {res['company']} — LBO summary ({cur})", ""]
    md += ["## Returns", "",
           f"- **IRR:** {pct(res['returns']['irr'])}   **MOIC:** {mult(res['returns']['moic'])}   "
           f"**Hold:** {res['exit']['year']} years",
           f"- Entry: {mult(m_in)} × {num(res['entry']['ebitda'])} EBITDA = EV {num(res['entry']['ev'])}; "
           f"leverage {mult(lev)}; equity {num(res['entry']['equity'])} ({pct(res['entry']['equity_pct'])} of uses)",
           f"- Exit: {mult(m_out)} × {num(res['exit']['ebitda'])} EBITDA = EV {num(res['exit']['ev'])}; "
           f"net debt {num(res['exit']['net_debt'])}; equity {num(res['exit']['equity'])}"]
    if args.target_irr is not None:
        mm = res["max_entry_multiple"]
        md.append(f"- **Max entry multiple for {pct(args.target_irr)} IRR:** "
                  + (f"{mult(mm)} (EV {num(mm * res['entry']['ebitda'])})" if mm else "not achievable above 1.0x"))
    md += ["", "## Sources & uses", "", "| Sources | | Uses | |", "|---|---|---|---|"]
    src, use = list(res["sources"].items()), list(res["uses"].items())
    for i in range(max(len(src), len(use))):
        a = src[i] if i < len(src) else ("", None)
        b = use[i] if i < len(use) else ("", None)
        md.append(f"| {a[0]} | {num(a[1]) if a[1] is not None else ''} | {b[0]} | {num(b[1]) if b[1] is not None else ''} |")
    md.append(f"| **Total** | **{num(sum(res['sources'].values()))}** | **Total** | **{num(sum(res['uses'].values()))}** |")
    md += ["", "## Value creation bridge", "", "| Driver | Value | % of gain |", "|---|---|---|"]
    gain = res["returns"]["equity_gain"]
    for k, v in res["bridge"].items():
        md.append(f"| {k} | {num(v)} | {pct(v / gain) if gain else 'n/m'} |")
    md.append(f"| **Equity gain** | **{num(gain)}** | 100% |")
    md += ["", "## Projections", "", "| Year | Revenue | EBITDA | Margin | FCF | Net debt | Net leverage | Interest cover |",
           "|---|---|---|---|---|---|---|---|"]
    for y in res["years"]:
        md.append(f"| {y['year']} | {num(y['revenue'])} | {num(y['ebitda'])} | {pct(y['margin'])} | {num(y['fcf'])} | "
                  f"{num(y['net_debt'])} | {mult(y['leverage'])} | {mult(y['interest_cover'])} |")
    md += ["", "## Sensitivities", ""]
    md.append(md_grid("IRR — entry vs exit multiple", "Entry", entry_vals, "Exit", exit_vals, irr_grid, pct))
    md.append(md_grid("MOIC — entry vs exit multiple", "Entry", entry_vals, "Exit", exit_vals, moic_grid, mult))
    md.append(md_grid("IRR — total leverage vs exit multiple", "Leverage", lev_vals, "Exit", exit_vals, lev_grid, pct))
    if res["warnings"]:
        md += ["## Warnings", ""] + [f"- {w}" for w in res["warnings"]] + [""]
    md += ["## Assumptions taken from defaults (confirm these)", "",
           ", ".join(defaulted) if defaulted else "None — all inputs supplied.", ""]

    with open(f"{args.out}.md", "w") as f:
        f.write("\n".join(md))
    with open(f"{args.out}.json", "w") as f:
        json.dump(res, f, indent=2, default=float)
    with open(f"{args.out}_years.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res["years"][0].keys()))
        w.writeheader()
        w.writerows(res["years"])
    print(f"IRR {pct(res['returns']['irr'])} | MOIC {mult(res['returns']['moic'])} | wrote {args.out}.md/.json/_years.csv")


if __name__ == "__main__":
    main()
