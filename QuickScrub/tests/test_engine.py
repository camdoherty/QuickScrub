import unittest
from ..core.engine import ScrubberEngine
from ..recognizers.base import Finding
from ..models.data_models import ScrubTask

class TestScrubberEngine(unittest.TestCase):
    def setUp(self): self.engine = ScrubberEngine()
    def test_resolve_no_overlap(self):
        findings = [Finding(0,3,"f","T1","R1"), Finding(4,7,"b","T2","R2")]; r = self.engine._resolve_conflicts(findings, []); self.assertEqual(len(r), 2)
    def test_resolve_with_allow_list(self):
        findings = [Finding(0,3,"foo","T1","R1"), Finding(4,7,"bar","T2","R2")]; r = self.engine._resolve_conflicts(findings, ["bar"]); self.assertEqual(len(r), 1); self.assertEqual(r[0].value, "foo")
    def test_resolve_complete_overlap(self):
        findings = [Finding(5,21,"long","T_L","R_L"), Finding(9,17,"short","T_S","R_S")]; r = self.engine._resolve_conflicts(findings, []); self.assertEqual(len(r), 1); self.assertEqual(r[0].type, "T_L")
    def test_full_scrub_process(self):
        text = "IP 1.1.1.1 and email test@dev.com."; findings = [Finding(3,10,"1.1.1.1","IP","IP"), Finding(21,35,"test@dev.com","EMAIL","Email")]
        task = ScrubTask(text=text, types=["IP", "EMAIL"]); result = self.engine.scrub(task, findings)
        self.assertEqual(result.scrubbed_text, "IP [IP_1] and email [EMAIL_1]."); self.assertEqual(len(result.legend), 2)
