import unittest
from ..core.engine import ScrubberEngine
from ..recognizers.base import Finding
from ..models.data_models import ScrubTask

class TestScrubberEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ScrubberEngine()

    def test_resolve_no_overlap(self):
        findings = [Finding(0, 3, "foo", "T1", "R1"), Finding(4, 7, "bar", "T2", "R2")]
        resolved = self.engine._resolve_conflicts(findings, [])
        self.assertEqual(len(resolved), 2)

    def test_resolve_with_allow_list(self):
        findings = [Finding(0, 3, "foo", "T1", "R1"), Finding(4, 7, "bar", "T2", "R2")]
        resolved = self.engine._resolve_conflicts(findings, ["bar"])
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].value, "foo")

    def test_resolve_complete_overlap(self):
        findings = [Finding(5, 21, "long_string", "T_LONG", "R_L"), Finding(9, 17, "short", "T_SHORT", "R_S")]
        resolved = self.engine._resolve_conflicts(findings, [])
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].type, "T_LONG")

    def test_resolve_partial_overlap(self):
        findings = [Finding(0, 10, "long_boi", "T_LONG", "R_L"), Finding(5, 15, "other_boi", "T_OTHER", "R_O")]
        resolved = self.engine._resolve_conflicts(findings, [])
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].type, "T_LONG")

    def test_full_scrub_process(self):
        text = "IP 1.1.1.1 and email test@dev.com. Ignore 8.8.8.8."
        findings = [
            Finding(3, 10, "1.1.1.1", "IP_ADDRESS", "IP"),
            Finding(21, 35, "test@dev.com", "EMAIL", "Email"),
            Finding(45, 52, "8.8.8.8", "IP_ADDRESS", "IP"),
        ]
        task = ScrubTask(text=text, types=["IP_ADDRESS", "EMAIL"], allow_list=["8.8.8.8"])
        result = self.engine.scrub(task, findings)

        expected_text = "IP [IP_ADDRESS_1] and email [EMAIL_1]. Ignore 8.8.8.8."
        self.assertEqual(result.scrubbed_text, expected_text)
        self.assertEqual(len(result.legend), 2)
        self.assertEqual(result.legend[0]['original'], "1.1.1.1")
        self.assertEqual(result.legend[1]['original'], "test@dev.com")
