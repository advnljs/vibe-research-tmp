# Semantic Duplicate Pair Review Prompt

You are reviewing pairs of de-identified session fingerprints for duplicate or train-test leakage risk.

Use only the supplied fingerprints and compact summaries. Do not infer diagnosis from source group or community membership. Do not quote long passages. Treat similar clinical category alone as insufficient for near-duplicate status.

## Decision Standard

Mark a pair as:

- `duplicate`: substantially the same fictional or interview-derived session pattern, with matching belief object, evidence shape, interaction arc, and distinctive non-identifying elements.
- `near_duplicate`: clearly overlapping enough that the pair should not be split across train/dev/validation/heldout without review.
- `not_duplicate`: shared broad category only, or generic similarity without matching scenario semantics.
- `unclear`: insufficient information to decide.

Leakage risk should be `medium` or `high` only when the two sessions share enough semantic structure that one could reveal the other as evaluation evidence.

## Input

```json
{
  "task": "semantic_duplicate_pair_review",
  "pairs": [
    {
      "pair_id": "...",
      "lexical_fingerprint_score": 0.0,
      "left": {"session_id": "...", "split": "...", "semantic_signature": "..."},
      "right": {"session_id": "...", "split": "...", "semantic_signature": "..."}
    }
  ]
}
```

## Output

Return one JSON object only:

```json
{
  "results": [
    {
      "pair_id": "...",
      "decision": "duplicate | near_duplicate | not_duplicate | unclear",
      "leakage_risk": "none | low | medium | high",
      "cross_split_risk": false,
      "recommended_action": "keep | same_split | exclude_one | manual_review",
      "shared_semantic_elements": ["generic shared element"],
      "distinguishing_elements": ["generic difference"],
      "rationale": "Brief reason without long quotes."
    }
  ]
}
```
