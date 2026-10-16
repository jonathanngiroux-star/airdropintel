# AirdropIntel

Weekly effort-vs-EV ranking of airdrop & points programs — **public information
only**. We score every opportunity on the same model and publish the full
ranking free.

- **X:** threads every Friday
- **Telegram:** free digest channel (launching this week)
- **Early Access (paid):** time-sensitive alerts 24-48h before the free digest — snapshots, claim windows, points-program launches. $10/mo.

## The scoring model

Every farm is scored 0-10 on five inputs, weighted by how they've mattered
historically:

| Input | Weight | What it measures |
|---|---|---|
| Confirmation | 30% | Is a token/airdrop/points→token conversion actually confirmed? |
| Value size | 25% | Community allocation, funding, historical reward sizing |
| Cost | 20% | $0 testnet = 10 … capital-at-risk = 2-4 |
| Time | 15% | Hours/week the grind demands (less is better) |
| Competition | 10% | Sybil-crowd density; quiet/early = 10, arms race = 3 |

```
EV = Σ(weight × score)
Efficiency = EV ÷ max(hours/week, 0.5)   ← the sort key
Tiers: S ≥ 8.0 · A ≥ 6.5 · B ≥ 5.0 · C < 5.0
```

Claims and deadlines are tracked separately and always lead the digest — an
unclaimed airdrop beats a speculative farm (see: Sonic burning ~32.7M unclaimed
$S on Oct 15, 2026).

## Latest ranking

See [`rankings/`](rankings/) for dated ranking tables with sources. Current
issue: [2026-10-16](rankings/ranking-2026-10-16.md).

## Repo layout

```
rankings/    dated ranking tables (markdown + JSON) with per-project sources
data/        curated candidate scores feeding the model (public sources only)
collect.py   public RSS collector
score.py     the EV model
monitor.py   daily change-detector over public feeds
issues/      per-issue publish content
```

## Method & ethics

- Public sources only; every recommendation cites its source URLs.
- Capital-at-risk plays are flagged ⚠️ and framed as *trading, not farming* —
  never pumped.
- No private deals, no undisclosed promotions, no referral links in paid tier.
- Stale signals get downgraded explicitly, with the caveat written down.
- Not financial advice. Points can be changed or voided at any time before
  TGE. Never sign transactions or share seed phrases for any "airdrop"; use
  official domains typed by hand.
