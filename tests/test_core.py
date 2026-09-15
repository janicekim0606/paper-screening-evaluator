import json
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from errors import ExternalServiceError, InputValidationError, InvalidResponseError
from scoring import ScoreWeights, phase_one_score, phase_two_score, total_score
from tools.data import load_data, sanitize_report_filename, save_report
from tools.llm import extract_json_from_text
from tools import openalex


class CoreTests(unittest.TestCase):
    def test_load_valid_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ideas.json"
            path.write_text(json.dumps([{"Title": "A", "Experiment": "B"}]), encoding="utf-8")
            self.assertEqual(load_data(path)[0]["Title"], "A")

    def test_reject_invalid_input_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ideas.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(InputValidationError):
                load_data(path)

    def test_reject_missing_required_field(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ideas.json"
            path.write_text(json.dumps([{"Title": "A"}]), encoding="utf-8")
            with self.assertRaises(InputValidationError):
                load_data(path)

    def test_extract_json_plain_and_markdown(self):
        self.assertEqual(extract_json_from_text('{"score": 8}')["score"], 8)
        self.assertEqual(extract_json_from_text("```json\n{\"score\": 9}\n```")["score"], 9)

    def test_extract_json_rejects_empty_response(self):
        with self.assertRaises(InvalidResponseError):
            extract_json_from_text(None)

    @patch("tools.llm.get_client")
    def test_llm_empty_api_response_is_invalid(self, get_client):
        get_client.return_value.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
        )
        from tools.llm import call_llm

        with self.assertRaises(InvalidResponseError):
            call_llm("test")

    @patch("tools.openalex.Works")
    def test_openalex_no_results_has_explicit_status(self, works):
        works.return_value.search.return_value.filter.return_value.get.return_value = []
        result = openalex.search_papers("test", limit=2)
        self.assertEqual(result.status, "no_results")
        self.assertEqual(result.papers, [])

    @patch("tools.openalex.Works")
    def test_openalex_failure_is_external_error(self, works):
        works.return_value.search.side_effect = RuntimeError("network down")
        with self.assertRaises(ExternalServiceError):
            openalex.search_papers("test", limit=2)

    def test_scores_are_deterministic(self):
        self.assertAlmostEqual(phase_one_score(8, 6), 7.2)
        self.assertAlmostEqual(phase_two_score(8, 6), 7.4)
        weights = ScoreWeights(1.5, 1.5, 2, 1, 1)
        scores = {
            "methodological_novelty": 8,
            "frontier_alignment": 7,
            "domain_utility": 8,
            "execution_efficiency": 6,
            "scholarly_impact": 7,
        }
        self.assertAlmostEqual(total_score(scores, weights, 7.5), 51.5)

    def test_report_writer_creates_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "reports"
            save_report("A title", "# report", output)
            self.assertTrue((output / f"{sanitize_report_filename('A title')}.md").exists())

    def test_report_filename_hash_prevents_collisions(self):
        first = sanitize_report_filename("A/B")
        second = sanitize_report_filename("AB")
        symbols = sanitize_report_filename("!!!")
        self.assertNotEqual(first, second)
        self.assertTrue(symbols.startswith("untitled_"))
        self.assertEqual(first, sanitize_report_filename("A/B"))

    def test_cli_threshold_overrides(self):
        import main

        with patch.object(sys, "argv", [
            "main.py",
            "--frontier-threshold", "8.25",
            "--impact-threshold", "7.75",
        ]):
            args = main.parse_args()
        self.assertEqual(args.frontier_threshold, 8.25)
        self.assertEqual(args.impact_threshold, 7.75)

    @patch("main.save_report")
    def test_rejected_reports_respect_runtime_switch(self, save_report):
        import main
        import config

        original = config.SAVE_REJECTED
        try:
            config.SAVE_REJECTED = False
            main.save_rejected_report("rejected", "content")
            save_report.assert_not_called()
        finally:
            config.SAVE_REJECTED = original

    def test_mocked_pipeline_handles_resume_encoding_and_thresholds(self):
        import config
        import main

        items = [
            {"Title": "Rejected Idea", "Experiment": "experiment"},
            {"Title": "Low Efficiency Idea", "Experiment": "experiment"},
            {"Title": "Accepted Idea", "Experiment": "experiment"},
        ]
        original_config = {
            name: getattr(config, name)
            for name in (
                "MAX_ITEMS_TO_PROCESS",
                "TARGET_ACCEPTED_COUNT",
                "SAVE_REJECTED",
                "THRESHOLD_NOVELTY",
                "THRESHOLD_FRONTIER",
                "THRESHOLD_UTILITY",
                "THRESHOLD_EFFICIENCY",
                "THRESHOLD_IMPACT",
            )
        }
        original_stdout, original_stderr = sys.stdout, sys.stderr
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                input_path = root / "ideas.json"
                input_path.write_text(json.dumps(items), encoding="utf-8")
                output_path = root / "output"
                output_path.mkdir()
                (output_path / "PHASE1_STAGING.json").write_text(
                    json.dumps({
                        "input": {"path": "old.json", "sha256": "old"},
                        "candidates": [{"item": {"Title": "Old"}}],
                    }),
                    encoding="utf-8",
                )

                class Args:
                    input = input_path
                    output = output_path
                    max_items = 3
                    top_n = 1
                    novelty_threshold = None
                    frontier_threshold = None
                    utility_threshold = None
                    efficiency_threshold = 7.0
                    impact_threshold = 6.5
                    no_resume = False
                    no_save_rejected = False

                sys.stdout = io.StringIO()
                sys.stderr = io.StringIO()
                with patch.object(main, "parse_args", return_value=Args()), \
                        patch.object(main, "check_novelty", side_effect=[
                            {"novelty_score": 1, "novelty_reason": "low", "similar_papers": []},
                            {"novelty_score": 8, "novelty_reason": "ok", "similar_papers": []},
                            {"novelty_score": 8, "novelty_reason": "ok", "similar_papers": []},
                        ]), \
                        patch.object(main, "review_idea", side_effect=[
                            {
                                "methodological_novelty": 8,
                                "frontier_alignment": 8,
                                "domain_utility": 8,
                                "execution_efficiency": 6,
                                "critique": "low efficiency",
                            },
                            {
                                "methodological_novelty": 8,
                                "frontier_alignment": 8,
                                "domain_utility": 8,
                                "execution_efficiency": 8,
                                "critique": "ok",
                            },
                        ]), \
                        patch.object(main, "predict_impact", side_effect=[
                            {"总体潜力评分": 8},
                            {"总体潜力评分": 8},
                        ]), \
                        patch.object(main, "generate_blueprint", return_value="# accepted"):
                    main.main()

                stdout = sys.stdout.getvalue()
                self.assertIn("Staging file does not match current input", stdout)
                self.assertIn("选定 [Rank 1]", stdout)
                rejected_name = sanitize_report_filename("REJECTED_PHASE1_NOVELTY_Rejected Idea")
                self.assertTrue((output_path / "rejected" / f"{rejected_name}.md").exists())
                self.assertTrue((output_path / "errors" / "001_quality.md").exists() or
                                (output_path / "errors" / "002_quality.md").exists())
                accepted_name = sanitize_report_filename("ACCEPTED_RANK1_Accepted Idea")
                self.assertTrue((output_path / "reports" / f"{accepted_name}.md").exists())
        finally:
            sys.stdout, sys.stderr = original_stdout, original_stderr
            for name, value in original_config.items():
                setattr(config, name, value)


if __name__ == "__main__":
    unittest.main()
