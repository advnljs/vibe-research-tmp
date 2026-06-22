# Reddit Case Preparation Summary

- Source CSV rows: `8712`
- Unique posts after exact-hash deduplication: `7685`
- Duplicate rows removed: `1027`
- LLM screen candidates: `2541`
- Too short: `129`
- Too long: `66`
- High-risk lexical exclusion: `359`
- PII/link lexical exclusion: `318`
- No reality-boundary lexical probe hit: `4748`

The lexical probe is candidate generation only. It is not a diagnosis, delusion label, or evidence that a post is eligible.
Raw post text is stored only under ignored `data/work/reddit_cases/`; tracked manifests contain hashes and lineage only.
