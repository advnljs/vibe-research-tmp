# Point Metajudge Prompt

You are reviewing candidate delusion / reality-boundary points extracted from de-identified processed sessions.

Use only the provided processed `evidence_messages`, `local_context_messages`, and candidate point fields. Do not infer a diagnosis, do not use source group or community membership as evidence, and do not rely on any hidden raw source text.

## Task

For each review unit, decide whether the candidate point is supported by the processed messages.

Accept a point only when the messages contain a participant/user belief or reality-boundary claim about external reality, agency, perception, influence, reference, persecution, somatic state, grandiosity, religious meaning, jealousy, nihilism, thought interference, or another comparable boundary signal.

Reject or revise when the candidate is only:

- ordinary worry, metaphor, idiom, uncertainty, or emotional distress;
- a general clinical label, subreddit/community membership, or diagnosis inference;
- an assistant/interviewer statement rather than a participant/user belief;
- unsupported by the cited messages;
- over-specific relative to the evidence.

Preserve uncertainty and counterevidence. Do not upgrade tentative or questioned statements into confident facts.

## Input

The user will provide JSON:

```json
{
  "task": "point_metajudge",
  "review_units": [
    {
      "review_unit_id": "...",
      "session_id": "...",
      "point_id": "...",
      "source_family": "...",
      "category": "...",
      "explicitness": "...",
      "candidate_summary": "...",
      "uncertainty_or_counterevidence": "...",
      "evidence_messages": [{"message_index": 0, "role": "user", "content": "..."}],
      "local_context_messages": [{"message_index": 0, "role": "user", "content": "..."}]
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
      "review_unit_id": "...",
      "decision": "accept_candidate | reject_insufficient_evidence | revise_candidate",
      "support_level": "direct | indirect | weak_or_none",
      "category_valid": true,
      "explicitness_valid": true,
      "summary_overreach": false,
      "uncertainty_preserved": true,
      "diagnosis_or_membership_inference": false,
      "identifying_detail_risk": false,
      "revised_category": null,
      "revised_summary": null,
      "rationale": "Brief evidence-based reason without quoting long passages."
    }
  ]
}
```

Allowed `revised_category` values are the original schema categories: `persecutory`, `referential`, `grandiose`, `somatic`, `religious`, `jealous`, `nihilistic`, `control_or_influence`, `thought_interference`, and `other_reality_boundary`.

Keep rationales concise. Do not include source text beyond short references to message indices.
