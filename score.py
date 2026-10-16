#!/usr/bin/env python3
"""AirdropIntel scoring model — effort vs expected value for airdrop/points farming.

Reads the newest data/candidates-*.json and writes:
  rankings/ranking-YYYY-MM-DD.json
  rankings/ranking-YYYY-MM-DD.md

EV model (0-10 scale, weighted):
  confirmation 30%  - is a token/airdrop/points->token conversion actually confirmed?
  value_size    25%  - community allocation, funding, historical reward sizing
  cost          20%  - $0 testnet=10, gas-only=6, capital-at-risk=2-4
  time          15%  - hours/week the grind demands (less is better)
  competition   10%  - sybil-crowd density; quiet/early=10, arms race=3

efficiency = EV / max(hours_per_week, 0.5)  -> "farm efficiency", the core sort key.
Tiers: S >= 8.0, A >= 6.5, B >= 5.0, C < 5.0.

All inputs are analyst-curated from public sources; every candidate must carry source URLs.
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
RANKS = os.path.join(ROOT, "rankings")

WEIGHTS = {
    "confirmation": 0.30,
    "value_size": 0.25,
    "cost": 0.20,
    "time": 0.15,
    "competition": 0.10,
}


def ev(c: dict) -> float:
    s = 0.0
    for k, w in WEIGHTS.items():
        s += w * float(c.get(k, 5))
    return round(s, 2)


def tier(ev_score: float) -> str:
    if ev_score >= 8.0:
        return "S"
    if ev_score >= 6.5:
        return "A"
    if ev_score >= 5.0:
        return "B"
    return "C"


def main() -> int:
    os.makedirs(RANKS, exist_ok=True)
    files = sorted(glob.glob(os.path.join(DATA, "candidates-*.json")))
    if not files:
        print("No data/candidates-*.json found — curate one first.")
        return 1
    path = files[-1]
    with open(path) as f:
        candidates = json.load(f)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    farms, claims = [], []
    for c in candidates:
        e = ev(c)
        hours = float(c.get("hours_per_week", 1.0))
        row = dict(c)
        row["ev"] = e
        row["tier"] = tier(e)
        row["efficiency"] = round(e / max(hours, 0.5), 2)
        if c.get("type") == "claim":
            claims.append(row)
        else:
            farms.append(row)

    farms.sort(key=lambda r: (-r["efficiency"], -r["ev"]))
    claims.sort(key=lambda r: r.get("deadline", "9999"))

    out_json = os.path.join(RANKS, f"ranking-{today}.json")
    out_md = os.path.join(RANKS, f"ranking-{today}.md")
    with open(out_json, "w") as f:
        json.dump({"date": today, "farms": farms, "claims": claims}, f, indent=1)

    lines = [
        f"# AirdropIntel ranking — {today}",
        "",
        "## Farm ranking (effort vs expected value)",
        "",
        "| # | Tier | Project | EV | h/wk | Efficiency | Cost | Status |",
        "|---|------|---------|----|------|------------|------|--------|",
    ]
    for i, r in enumerate(farms, 1):
        lines.append(
            f"| {i} | {r['tier']} | {r['name']} ({r.get('ticker','—')}) | {r['ev']} | "
            f"{r.get('hours_per_week','—')} | {r['efficiency']} | {r.get('cost_label','—')} | {r.get('status','—')} |"
        )
    lines += ["", "## Claim/deadline radar (act now, ranked by deadline)", "",
              "| Deadline | Project | Action | Official route |", "|---|---|---|---|"]
    for r in claims:
        lines.append(f"| {r.get('deadline','?')} | {r['name']} ({r.get('ticker','—')}) | {r.get('action','claim')} | {r.get('official_route','—')} |")
    with open(out_md, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Scored {len(farms)} farms + {len(claims)} claim deadlines from {os.path.basename(path)}")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}\n")
    for i, r in enumerate(farms, 1):
        flag = " [CAPITAL-AT-RISK]" if r.get("capital") else ""
        print(f"  {i}. [{r['tier']}] {r['name']}: EV {r['ev']} @ {r.get('hours_per_week','?')}h/wk -> eff {r['efficiency']}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
