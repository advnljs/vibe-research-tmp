from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build_reddit_sessions import (  # noqa: E402
    mock_generated_session,
    public_rejection_reasons,
    validate_generated,
)
from build_sessions import estimate_tokens, mock_chunk_result, mock_consolidation, split_turns  # noqa: E402
from prepare_cases import parse_dais_tagged_text, parse_fep_table_text  # noqa: E402
from session_contract import (  # noqa: E402
    LABEL_STATUS,
    longest_common_word_run,
    validate_chunk_result,
    validate_consolidation,
    validate_session_record,
)


class PrepareCasesTests(unittest.TestCase):
    def test_parse_dais_tagged_text_preserves_roles_and_inline_content(self) -> None:
        text = (
            "<INT>Could you explain that?</INT>\n"
            "<03AR15>I meant <An>something uncertain</An>, not a fact.</03AR15>"
        )
        turns = parse_dais_tagged_text(text, "03AR15")
        self.assertEqual([turn["speaker"] for turn in turns], ["interviewer", "participant"])
        self.assertEqual([turn["source_turn_id"] for turn in turns], ["st0001", "st0002"])
        self.assertIn("something uncertain", turns[1]["text"])

    def test_parse_fep_table_text_joins_wrapped_rows(self) -> None:
        text = (
            "|CH   |How did that feel?                  |                               |\n"
            "|     |Could you explain?                  |                               |\n"
            "|1    |It was difficult.                   |                               |\n"
            "|     |I was uncertain.                    |                               |\n"
        )
        turns = parse_fep_table_text(text, "1")
        self.assertEqual(len(turns), 2)
        self.assertEqual(turns[0]["speaker"], "interviewer")
        self.assertIn("Could you explain?", turns[0]["text"])
        self.assertEqual(turns[1]["speaker"], "participant")


class BuildSessionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.turns = [
            {"source_turn_id": "st0001", "speaker": "interviewer", "text": "A short interviewer prompt."},
            {"source_turn_id": "st0002", "speaker": "participant", "text": "A short participant answer."},
            {"source_turn_id": "st0003", "speaker": "interviewer", "text": "A follow-up question."},
        ]

    def test_split_turns_respects_turn_limit(self) -> None:
        chunks = split_turns(self.turns, max_chars=1000, max_turns=2)
        self.assertEqual([len(chunk) for chunk in chunks], [2, 1])

    def test_mock_chunk_satisfies_contract(self) -> None:
        result = mock_chunk_result(self.turns)
        errors, overlap = validate_chunk_result(result, self.turns, max_source_word_run=12)
        self.assertEqual(errors, [])
        self.assertLess(overlap, 12)

    def test_mock_consolidation_satisfies_contract(self) -> None:
        result = mock_consolidation()
        errors = validate_consolidation(result, {"st0002"})
        self.assertEqual(errors, [])

    def test_long_common_run_detects_copy(self) -> None:
        source = "one two three four five six seven eight nine ten"
        output = "zero one two three four five six seven eight nine ten eleven"
        self.assertEqual(longest_common_word_run(source, output), 10)

    def test_context_estimator_is_deterministic(self) -> None:
        self.assertEqual(estimate_tokens("x" * 17), 5)

    def test_mock_reddit_generation_satisfies_contract(self) -> None:
        result = mock_generated_session()
        errors, overlap, pii_hits = validate_generated(
            result,
            source_text="A distinct source post with unrelated wording.",
            max_source_word_run=12,
        )
        self.assertEqual(errors, [])
        self.assertLess(overlap, 12)
        self.assertEqual(pii_hits, [])

    def test_public_rejection_reasons_drop_model_prose(self) -> None:
        item = {
            "eligible": False,
            "rejection_reasons": [
                "Free-form reason that may paraphrase a source detail.",
                "automatic_exclusion:model_reported_identifying_detail",
            ],
        }
        self.assertEqual(
            public_rejection_reasons(item),
            ["automatic_exclusion:model_reported_identifying_detail"],
        )
        self.assertEqual(
            public_rejection_reasons({"eligible": False, "rejection_reasons": ["free prose"]}),
            ["model_semantic_ineligible"],
        )


class SessionContractTests(unittest.TestCase):
    def test_minimal_session_record(self) -> None:
        record = {
            "schema_version": "0.1.0",
            "session_id": "test_session",
            "messages": [
                {"role": "assistant", "content": "Could you explain?"},
                {"role": "user", "content": "I am not certain."},
            ],
            "message_provenance": [
                {"message_index": 0, "source_turn_ids": ["st0001"], "transform": "llm_semantic_paraphrase"},
                {"message_index": 1, "source_turn_ids": ["st0002"], "transform": "llm_semantic_paraphrase"},
            ],
            "delusion_points": [],
            "case_summary": "The participant expressed uncertainty.",
            "no_delusion_point_reason": "No candidate belief about external reality was expressed.",
            "metadata": {"label_interpretation": LABEL_STATUS},
            "provenance": {},
            "quality": {"status": "passed"},
        }
        self.assertEqual(validate_session_record(record), [])

    def test_fictional_expansion_allows_shared_source_post(self) -> None:
        record = {
            "schema_version": "0.1.0",
            "session_id": "reddit_syn_test",
            "messages": [
                {"role": "user", "content": "A fictionalized account."},
                {"role": "assistant", "content": "A neutral question."},
            ],
            "message_provenance": [
                {"message_index": 0, "source_turn_ids": ["source_post"], "transform": "llm_fictional_expansion"},
                {"message_index": 1, "source_turn_ids": ["source_post"], "transform": "llm_fictional_expansion"},
            ],
            "delusion_points": [],
            "case_summary": "A fictionalized session.",
            "no_delusion_point_reason": "Test record intentionally has no point.",
            "metadata": {"label_interpretation": LABEL_STATUS},
            "provenance": {},
            "quality": {"status": "passed"},
        }
        self.assertEqual(validate_session_record(record), [])


if __name__ == "__main__":
    unittest.main()
