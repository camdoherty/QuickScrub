from typing import List, Dict
from ..models.data_models import ScrubTask, ScrubResult
from ..recognizers.base import Finding

class ScrubberEngine:
    def scrub(self, task: ScrubTask, findings: List[Finding]) -> ScrubResult:
        final_findings = self._resolve_conflicts(findings, task.allow_list)
        scrubbed_text, legend = self._scrub_text(task.text, final_findings)
        return ScrubResult(scrubbed_text=scrubbed_text, legend=legend)

    def _resolve_conflicts(self, findings: List[Finding], allow_list: List[str]) -> List[Finding]:
        allow_set = {item.lower() for item in allow_list}
        allowed_findings = [f for f in findings if f.value.lower() not in allow_set]
        sorted_findings = sorted(allowed_findings, key=lambda f: (f.start, -f.end))

        resolved: List[Finding] = []
        if not sorted_findings: return resolved

        last_accepted_finding = sorted_findings[0]
        resolved.append(last_accepted_finding)

        for current_finding in sorted_findings[1:]:
            if current_finding.start < last_accepted_finding.end: continue
            resolved.append(current_finding)
            last_accepted_finding = current_finding

        return resolved

    def _scrub_text(self, text: str, findings: List[Finding]) -> (str, List[Dict[str, str]]):
        """
        Replaces PII in text with consistent placeholders and generates a unique legend.
        """
        scrubbed_text = text
        
        # --- MODIFIED LOGIC START ---

        # Keeps track of the next available index for a given PII type (e.g., IP_ADDRESS -> 1)
        placeholder_counts: Dict[str, int] = {}
        # Maps a unique value to its generated placeholder (e.g., "192.168.1.1" -> "[IP_ADDRESS_1]")
        value_to_placeholder_map: Dict[str, str] = {}
        # Stores the unique legend items in the order they are first seen.
        legend_map: Dict[str, Dict[str, str]] = {}

        # First pass: Generate placeholders and legend for unique values
        # We iterate through the findings in their original order to make the legend sequential.
        for finding in sorted(findings, key=lambda f: f.start):
            # If we've already created a placeholder for this value, skip it.
            if finding.value in value_to_placeholder_map:
                continue

            pii_type = finding.type
            
            # Get the next available count for this type and increment it
            count = placeholder_counts.get(pii_type, 0) + 1
            placeholder_counts[pii_type] = count
            
            placeholder = f"[{pii_type}_{count}]"
            
            # Store the mappings
            value_to_placeholder_map[finding.value] = placeholder
            legend_map[placeholder] = {
                "original": finding.value,
                "mock": placeholder,
                "type": pii_type
            }

        # Second pass: Replace text using the consistent placeholders
        # We iterate backwards to preserve character indices during replacement.
        for finding in reversed(findings):
            placeholder = value_to_placeholder_map[finding.value]
            scrubbed_text = scrubbed_text[:finding.start] + placeholder + scrubbed_text[finding.end:]

        # Create the final legend from our map, sorted by the placeholder number
        legend = sorted(legend_map.values(), key=lambda item: int(item['mock'].split('_')[-1][:-1]))

        # --- MODIFIED LOGIC END ---

        return scrubbed_text, legend