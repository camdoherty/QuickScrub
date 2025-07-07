from typing import List, Dict
from ..models.data_models import ScrubTask, ScrubResult
from ..recognizers.base import Finding

class ScrubberEngine:
    """The core logic engine for scrubbing PII from text."""

    def scrub(self, task: ScrubTask, findings: List[Finding]) -> ScrubResult:
        """The main public method to perform a full scrub operation."""
        final_findings = self._resolve_conflicts(findings, task.allow_list)
        scrubbed_text, legend = self._scrub_text(task.text, final_findings)
        return ScrubResult(scrubbed_text=scrubbed_text, legend=legend)

    def _resolve_conflicts(self, findings: List[Finding], allow_list: List[str]) -> List[Finding]:
        """Resolves overlaps and filters findings based on the allow list."""
        allow_set = {item.lower() for item in allow_list}
        allowed_findings = [f for f in findings if f.value.lower() not in allow_set]

        # Sort by start index (asc) and end index (desc) to prioritize longer matches
        sorted_findings = sorted(allowed_findings, key=lambda f: (f.start, -f.end))

        resolved: List[Finding] = []
        if not sorted_findings:
            return resolved

        last_accepted_finding = sorted_findings[0]
        resolved.append(last_accepted_finding)

        for current_finding in sorted_findings[1:]:
            if current_finding.start < last_accepted_finding.end:
                continue  # Overlap detected, discard current finding

            resolved.append(current_finding)
            last_accepted_finding = current_finding

        return resolved

    def _scrub_text(self, text: str, findings: List[Finding]) -> (str, List[Dict[str, str]]):
        """Replaces PII in text with placeholders and generates a legend."""
        scrubbed_text = text
        legend: List[Dict[str, str]] = []
        placeholder_counts: Dict[str, int] = {}

        for finding in reversed(findings):
            pii_type = finding.type
            count = placeholder_counts.get(pii_type, 0) + 1
            placeholder_counts[pii_type] = count
            placeholder = f"[{pii_type}_{count}]"

            end_index = finding.start + len(finding.value)
            scrubbed_text = scrubbed_text[:finding.start] + placeholder + scrubbed_text[end_index:]

            legend.insert(0, {"original": finding.value, "mock": placeholder, "type": pii_type})

        return scrubbed_text, legend
