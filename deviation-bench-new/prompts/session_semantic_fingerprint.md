# Session Semantic Fingerprint Prompt

You are creating compact semantic fingerprints for de-identified processed sessions so they can be checked for duplicate or leakage risk.

Use only the provided processed session material. Do not infer diagnosis from source group or community membership. Do not quote long passages. Do not reconstruct names, locations, institutions, or rare event chains. Keep the fingerprint generic enough for governance review while preserving the core semantic pattern.

## Task

For each session, produce a short structured fingerprint:

- the broad reality-boundary pattern, if any;
- the generic belief objects or concerns;
- the evidence/uncertainty shape;
- distinctive but non-identifying elements;
- duplicate-screening terms that can help identify near-duplicates.

If a session has no candidate point, still summarize the main non-delusional interaction pattern.

## Input

The user will provide JSON:

```json
{
  "task": "session_semantic_fingerprint",
  "sessions": [
    {
      "session_id": "...",
      "source_family": "...",
      "split": "...",
      "case_summary": "...",
      "candidate_points": [{"category": "...", "summary": "..."}],
      "compact_messages": [{"message_index": 0, "role": "user", "content": "..."}]
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
      "session_id": "...",
      "semantic_signature": "One concise generic sentence.",
      "core_reality_boundary_pattern": "none_or_generic_pattern",
      "belief_objects": ["generic object"],
      "evidence_shape": "direct claim | inference from ambiguous events | uncertainty only | no reality-boundary claim",
      "uncertainty_profile": "confident | questioned | mixed | absent",
      "distinctive_nonidentifying_elements": ["generic element"],
      "duplicate_screening_terms": ["short generic term"],
      "source_specificity_risk": "low | medium | high",
      "rare_event_chain_risk": false,
      "rationale": "Brief reason using message indices or candidate point summaries, not long quotes."
    }
  ]
}
```

Keep every field concise. Avoid exact names, dates, addresses, organizations, URLs, handles, or other identifying details.
