#!/usr/bin/env python3
"""AirdropIntel collector — fetch public RSS signals into data/raw-YYYY-MM-DD.json.

Stdlib only. Reads data/sources.json, fetches each RSS feed, parses items,
prints a summary. The analyst layer (agent or cron job) then curates the
strongest signals into data/candidates-YYYY-MM-DD.json for scoring.
"""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")


def fetch(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (AirdropIntel research bot; public feeds)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_rss(xml_bytes: bytes) -> list:
    out = []
    root = ET.fromstring(xml_bytes)
    for item in root.iter("item"):
        def get(tag):
            return (item.findtext(tag) or "").strip()
        summary = get("description")
        import re
        summary = re.sub(r"<[^>]+>", " ", summary)[:300]
        out.append(
            {
                "title": get("title"),
                "link": get("link"),
                "date": get("pubDate"),
                "summary": summary,
            }
        )
    return out


def main() -> int:
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "sources.json")) as f:
        sources = json.load(f)

    signals, errors = [], []
    for s in sources.get("rss", []):
        try:
            items = parse_rss(fetch(s["url"]))
            for it in items[:20]:
                it["source"] = s["name"]
            signals.extend(items)
            print(f"OK   {s['name']}: {len(items)} items")
        except Exception as e:  # noqa: BLE001
            errors.append({"source": s["name"], "error": repr(e)})
            print(f"ERR  {s['name']}: {e}")

    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "signals": signals,
        "errors": errors,
    }
    out = os.path.join(DATA, f"raw-{datetime.now(timezone.utc):%Y-%m-%d}.json")
    with open(out, "w") as f:
        json.dump(payload, f, indent=1)
    print(f"\nWrote {out}: {len(signals)} signals, {len(errors)} feed errors")
    return 0 if signals else 1


if __name__ == "__main__":
    sys.exit(main())
