# deepseek_v4_pro_interview_sessions_64k

- Generated at: `2026-06-22T10:29:56+00:00`
- Provider/model: `openai` / `deepseek-v4-pro`
- Context window: `65536` tokens
- Reserved max output: `8192` tokens
- Thinking mode: `disabled`
- Completed sessions: `29`
- Failed sessions: `0`
- Messages: `4090`
- Candidate delusion points: `40`
- Sessions with no extracted point: `15`
- Source datasets: `{'dais_c': 15, 'first_episode_psychosis_friendship': 14}`
- Source groups: `{'clinical_schizophrenia': 15, 'first_episode_psychosis': 14}`
- Label status: `llm_extracted_candidate_not_diagnosis`
- Raw source/API response included in processed data: `false`

## Session QC

| session_id | messages | delusion_points | chunks | max source-word run | QC |
|---|---:|---:|---:|---:|---|
| dais_c_cl_001 | 128 | 1 | 6 | 25 | passed |
| dais_c_cl_002 | 209 | 1 | 13 | 26 | passed |
| dais_c_cl_003 | 178 | 0 | 8 | 31 | passed |
| dais_c_cl_004 | 184 | 1 | 8 | 31 | passed |
| dais_c_cl_005 | 135 | 0 | 6 | 24 | passed |
| dais_c_cl_006 | 117 | 0 | 5 | 22 | passed |
| dais_c_cl_007 | 60 | 0 | 3 | 16 | passed |
| dais_c_cl_008 | 204 | 0 | 9 | 22 | passed |
| dais_c_cl_009 | 215 | 1 | 9 | 31 | passed |
| dais_c_cl_010 | 154 | 0 | 7 | 29 | passed |
| dais_c_cl_011 | 477 | 13 | 20 | 31 | passed |
| dais_c_cl_012 | 183 | 0 | 8 | 28 | passed |
| dais_c_cl_013 | 174 | 0 | 7 | 26 | passed |
| dais_c_cl_014 | 126 | 0 | 6 | 22 | passed |
| dais_c_cl_015 | 74 | 6 | 4 | 27 | passed |
| fep_friendship_001 | 131 | 0 | 6 | 28 | passed |
| fep_friendship_002 | 109 | 0 | 5 | 30 | passed |
| fep_friendship_003 | 169 | 0 | 7 | 26 | passed |
| fep_friendship_004 | 92 | 1 | 4 | 31 | passed |
| fep_friendship_005 | 84 | 1 | 4 | 31 | passed |
| fep_friendship_006 | 75 | 0 | 3 | 31 | passed |
| fep_friendship_007 | 94 | 0 | 4 | 30 | passed |
| fep_friendship_008 | 20 | 5 | 5 | 30 | passed |
| fep_friendship_009 | 97 | 1 | 4 | 31 | passed |
| fep_friendship_010 | 166 | 1 | 7 | 30 | passed |
| fep_friendship_011 | 69 | 0 | 4 | 31 | passed |
| fep_friendship_012 | 109 | 2 | 5 | 30 | passed |
| fep_friendship_013 | 130 | 4 | 6 | 31 | passed |
| fep_friendship_014 | 127 | 2 | 6 | 28 | passed |

## Interpretation boundary

`delusion_points` are LLM-extracted candidate text signals. They are not clinical diagnoses, participant-level ground truth, or evidence that every psychosis-related interview contains delusions.
