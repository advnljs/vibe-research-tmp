# Reviews

This directory stores tracked, de-identified release-hardening review outputs.

- Point metajudge outputs contain structured second-pass decisions over processed candidate points and no-point negative controls.
- Semantic duplicate outputs contain generic LLM fingerprints and pair-level duplicate/leakage decisions.
- Review narrative outputs contain Chinese dashboard explanations generated from aggregate statistics only; they do not include raw transcripts, raw community posts, or raw API responses.
- Raw API requests/responses and checkpoints remain under ignored `data/work/` and must not be committed.
