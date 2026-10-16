#!/usr/bin/env python3
"""Daily signal monitor — deterministic digest of AIRDROP-RELEVANT public feed items.

Only items whose titles match the keyword filter are included, so the cron
change-detector wakes the analyst only when something airdrop-worthy changed,
not on general crypto news churn. Output is deterministic (no timestamps).
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import collect  # noqa: E402

KEYWORDS = re.compile(
    r"airdrop|air ?drop|snapshot|points|claim|tge|testnet|incentiv|quest|"
    r"waitlist|token (launch|generation)|genesis|reward campaign|season \d|"
    r"eligib|allocat",
    re.IGNORECASE,
)


def main() -> int:
    with open(os.path.join(collect.DATA, "sources.json")) as f:
        sources = json.load(f)
    lines = []
    for s in sources["rss"]:
        try:
            items = collect.parse_rss(collect.fetch(s["url"]))
            hits = [i["title"] for i in items if KEYWORDS.search(i["title"])]
            lines.append(f"{s['name']}: {len(hits)} relevant of {len(items)}")
            lines.extend(f"  - {h}" for h in hits[:12])
            # a feed-level error state is itself a change worth seeing
            if not items:
                lines.append(f"  - WARNING: {s['name']} returned 0 items")
        except Exception as e:  # noqa: BLE001
            lines.append(f"{s['name']}: ERROR {e!r}")
    blob = "\n".join(lines)
    print(blob)
    print(f"\nSHA256: {hashlib.sha256(blob.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
