# deepseek_v4_pro_control_sessions_64k

- Generated at: `2026-06-22T10:29:56+00:00`
- Provider/model: `openai` / `deepseek-v4-pro`
- Context window: `65536` tokens
- Reserved max output: `8192` tokens
- Thinking mode: `disabled`
- Completed sessions: `13`
- Failed sessions: `0`
- Messages: `1206`
- Candidate delusion points: `0`
- Sessions with no extracted point: `13`
- Source datasets: `{'dais_c': 13}`
- Source groups: `{'control': 13}`
- Label status: `llm_extracted_candidate_not_diagnosis`
- Raw source/API response included in processed data: `false`

## Session QC

| session_id | messages | delusion_points | chunks | max source-word run | QC |
|---|---:|---:|---:|---:|---|
| dais_c_co_001 | 63 | 0 | 3 | 30 | passed |
| dais_c_co_002 | 104 | 0 | 5 | 26 | passed |
| dais_c_co_003 | 90 | 0 | 4 | 21 | passed |
| dais_c_co_004 | 59 | 0 | 3 | 31 | passed |
| dais_c_co_005 | 122 | 0 | 5 | 26 | passed |
| dais_c_co_006 | 58 | 0 | 3 | 27 | passed |
| dais_c_co_007 | 216 | 0 | 9 | 30 | passed |
| dais_c_co_008 | 66 | 0 | 3 | 31 | passed |
| dais_c_co_009 | 74 | 0 | 3 | 20 | passed |
| dais_c_co_010 | 36 | 0 | 5 | 15 | passed |
| dais_c_co_011 | 113 | 0 | 5 | 29 | passed |
| dais_c_co_012 | 88 | 0 | 4 | 27 | passed |
| dais_c_co_013 | 117 | 0 | 5 | 31 | passed |

## Interpretation boundary

`delusion_points` are LLM-extracted candidate text signals. They are not clinical diagnoses, participant-level ground truth, or evidence that every psychosis-related interview contains delusions.
