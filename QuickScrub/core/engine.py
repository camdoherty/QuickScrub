from typing import List, Dict
from ..models.data_models import ScrubTask, ScrubResult
from ..recognizers.base import Finding


class ScrubberEngine:
    def scrub(self, task: ScrubTask, findings: List[Finding]) -> ScrubResult:
        final_findings = self._resolve_conflicts(findings, task.allow_list)
        scrubbed_text, legend = self._scrub_text(task.text, final_findings)
        return ScrubResult(scrubbed_text=scrubbed_text, legend=legend)

    def _resolve_conflicts(self, findings: List[Finding], allow_list: List[str]) -> List[Finding]:
        """
        Resolves overlapping findings and filters out values from the allow list.
        The strategy is to sort by start index and then by length (longest first).
        This ensures that if a smaller finding is completely contained within a
        larger one (e.g., an email inside a sensitive URL), the larger finding is kept.
        """
        allow_set = {item.lower() for item in allow_list}
        allowed_findings = [f for f in findings if f.value.lower() not in allow_set]

        # Sort by start index, then by the negative of the end index (longest match first)
        sorted_findings = sorted(allowed_findings, key=lambda f: (f.start, -f.end))

        resolved: List[Finding] = []
        if not sorted_findings:
            return resolved

        # Use a variable to track the end of the last accepted finding.
        last_end = -1
        for finding in sorted_findings:
            # If the current finding starts after the last one ended, it's safe to add.
            if finding.start >= last_end:
                resolved.append(finding)
                last_end = finding.end
            # If it starts before the last one ended, it's an overlap. Because we sorted
            # by longest-first, we can be sure this finding is either fully contained
            # or a shorter, less-preferred overlap, so we discard it.

        return resolved

    def _scrub_text(self, text: str, findings: List[Finding]) -> (str, List[Dict[str, str]]):
        scrubbed_text = text
        placeholder_counts: Dict[str, int] = {}
        value_to_placeholder_map: Dict[str, str] = {}
        legend_map: Dict[str, Dict[str, str]] = {}

        for finding in sorted(findings, key=lambda f: f.start):
            if finding.value in value_to_placeholder_map:
                continue
            pii_type = finding.type
            count = placeholder_counts.get(pii_type, 0) + 1
            placeholder_counts[pii_type] = count
            placeholder = f"[{pii_type}_{count}]"
            value_to_placeholder_map[finding.value] = placeholder
            legend_map[placeholder] = {"original": finding.value, "mock": placeholder, "type": pii_type}

        # This replacement logic now operates on a clean, non-overlapping list of findings.
        for finding in reversed(findings):
            placeholder = value_to_placeholder_map[finding.value]
            scrubbed_text = scrubbed_text[:finding.start] + placeholder + scrubbed_text[finding.end:]

        legend = sorted(legend_map.values(), key=lambda item: int(item['mock'].split('_')[-1][:-1]))
        return scrubbed_text, legend
