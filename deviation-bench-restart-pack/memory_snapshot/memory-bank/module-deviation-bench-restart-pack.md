# Module: deviation-bench-restart-pack

Last updated: 2026-07-07

## Module Responsibility

`deviation-bench-restart-pack/` is a local handoff package for restarting Deviation Bench from the original `deviation-bench/` motivation in another agent/workspace.

It is not a new benchmark implementation. It collects the old research rationale, navigation, data-source notes, prompts, scripts, experiments, paper notes, memory snapshot, local key file, and local downloaded-data copy into one directory.

## Entry Files

- `README.md`: package purpose, reading order, security/data boundaries.
- `01_initial_motivation_and_goals.md`: synthesized original research motivation and goals.
- `02_collected_materials_navigation.md`: curated navigation across documents/data/prompts/scripts.
- `PACKAGE_MANIFEST.md`: package contents, tracked vs local-only material, migration instructions.

## Key Directories

- `research_docs/00_core_motivation/`: copied original UIRD/context-retest reliability documents.
- `research_docs/01_data_generation/`: data-source and Bloom-like generation plans.
- `research_docs/02_evaluation_and_paper/`: LLM-only evaluation, related work, benchmark gap, historical annotation draft.
- `research_docs/03_later_agent_memory_optional/`: later agent-memory route, explicitly optional.
- `data_sources/`: data license/access manifest, notes, pattern bank, restricted-source application list, and ignored local downloaded-data copy.
- `prompts/`: copied old scenario, judge, metajudge, rewrite and memory prompts.
- `src/`: copied old pilot, dashboard, consensus, rewrite and memory scripts.
- `experiments/`: copied S0/mock/memory experiment notes.
- `memory_snapshot/`: copied AGENTS, research navigation, and memory-bank snapshot at handoff time.

## Local-Only Contents

- `ds_key.txt`: copied for migration at the user's explicit request; must not be read, printed, committed, pushed, or logged.
- `data_sources/downloaded/`: copied duplicate raw/third-party downloaded material for local directory migration; excluded from git to avoid duplicating sensitive/large data in the restart pack.

Both are ignored by `deviation-bench-restart-pack/.gitignore`.

## Common Modification Points

- Update `01_initial_motivation_and_goals.md` if the user changes the restart framing.
- Update `02_collected_materials_navigation.md` if files are added/removed from the pack.
- Update `PACKAGE_MANIFEST.md` after significant packaging changes or count/size changes.
- Do not modify `ds_key.txt` unless the user explicitly rotates/replaces the key.

## Verification

Current packaging verification:

- 74 tracked/candidate package files excluding `data_sources/downloaded/` and `ds_key.txt`.
- 2,568 local copied downloaded-data files.
- Package size about 204MB; downloaded-data copy about 203MB.
- `git check-ignore` confirms `ds_key.txt` and copied downloaded data are ignored.
- Pilot scenario validation from inside the pack loads 20 scenarios and returns `validation=ok`.
- `python3 -m py_compile deviation-bench-restart-pack/src/*.py` passes; generated `__pycache__` is removed after verification.
