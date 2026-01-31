"""
Root cause analyzer for safety incidents.
"""

import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class ContributingFactor:
    """A factor that contributed to the incident."""
    factor: str
    description: str
    severity: str  # low, medium, high, critical
    category: str  # safeguard_gap, policy_gap, design_flaw, edge_case


@dataclass
class RootCauseAnalysis:
    """Complete root cause analysis for an incident."""
    incident_id: str
    failure_type: str
    first_unsafe_turn: int
    contributing_factors: list[ContributingFactor]
    mitigation_candidates: list[str]
    confidence: float

    def to_dict(self) -> dict:
        return {
            'incident_id': self.incident_id,
            'failure_type': self.failure_type,
            'first_unsafe_turn': self.first_unsafe_turn,
            'contributing_factors': [
                {
                    'factor': f.factor,
                    'description': f.description,
                    'severity': f.severity,
                    'category': f.category
                }
                for f in self.contributing_factors
            ],
            'mitigation_candidates': self.mitigation_candidates,
            'confidence': self.confidence
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class RootCauseAnalyzer:
    """
    Analyzes incidents to identify root causes and mitigations.
    """

    # Known root causes and their analysis
    ROOT_CAUSE_DB = {
        'injection_in_tool_output': {
            'description': 'Malicious instructions embedded in tool output',
            'severity': 'critical',
            'category': 'safeguard_gap',
            'mitigations': ['Add tool output sanitization', 'Implement instruction boundary markers']
        },
        'no_output_sanitization': {
            'description': 'Tool outputs not sanitized before processing',
            'severity': 'high',
            'category': 'design_flaw',
            'mitigations': ['Add output content filter', 'Implement allowlist for tool outputs']
        },
        'instruction_boundary_confusion': {
            'description': 'Model confused user data with instructions',
            'severity': 'critical',
            'category': 'design_flaw',
            'mitigations': ['Use explicit instruction delimiters', 'Train on boundary detection']
        },
        'path_escalation_not_detected': {
            'description': 'Gradual path escalation not flagged',
            'severity': 'high',
            'category': 'safeguard_gap',
            'mitigations': ['Implement path sensitivity scoring', 'Add directory traversal detection']
        },
        'tool_chain_not_analyzed': {
            'description': 'Sequence of tool calls not analyzed for risk',
            'severity': 'medium',
            'category': 'safeguard_gap',
            'mitigations': ['Add tool chain analyzer', 'Track cumulative tool risk']
        },
        'gradual_context_normalization': {
            'description': 'Risky requests normalized through gradual escalation',
            'severity': 'high',
            'category': 'policy_gap',
            'mitigations': ['Lower drift threshold', 'Implement trajectory-level intent tracking']
        },
        'drift_threshold_not_triggered': {
            'description': 'Cumulative drift below detection threshold',
            'severity': 'medium',
            'category': 'safeguard_gap',
            'mitigations': ['Lower drift threshold', 'Add slope-based detection']
        },
        'educational_framing_exploitation': {
            'description': 'Educational context exploited to extract harmful info',
            'severity': 'high',
            'category': 'policy_gap',
            'mitigations': ['Add educational content limits', 'Detect theory-to-practice pivots']
        },
        'authority_claim_not_verified': {
            'description': 'False authority claims accepted without verification',
            'severity': 'high',
            'category': 'design_flaw',
            'mitigations': ['Require identity verification', 'Flag unverified authority claims']
        },
        'no_cross_session_tracking': {
            'description': 'Information gathering across sessions not detected',
            'severity': 'high',
            'category': 'safeguard_gap',
            'mitigations': ['Implement cross-session analysis', 'Track information fragments']
        }
    }

    def load_incident(self, path: str) -> dict:
        """Load incident from JSON file."""
        with open(path) as f:
            return json.load(f)

    def analyze(self, incident: dict, verbose: bool = True) -> RootCauseAnalysis:
        """
        Perform root cause analysis on an incident.

        Args:
            incident: Incident data
            verbose: Print analysis

        Returns:
            RootCauseAnalysis with findings
        """
        incident_id = incident['incident_id']
        failure_type = incident.get('failure_type', 'unknown')
        first_unsafe = incident.get('first_unsafe_turn', -1)
        raw_causes = incident.get('root_causes', [])

        # Analyze each root cause
        factors = []
        all_mitigations = set()

        for cause in raw_causes:
            if cause in self.ROOT_CAUSE_DB:
                info = self.ROOT_CAUSE_DB[cause]
                factors.append(ContributingFactor(
                    factor=cause,
                    description=info['description'],
                    severity=info['severity'],
                    category=info['category']
                ))
                all_mitigations.update(info['mitigations'])
            else:
                factors.append(ContributingFactor(
                    factor=cause,
                    description=f'Unknown factor: {cause}',
                    severity='medium',
                    category='unknown'
                ))

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        factors.sort(key=lambda f: severity_order.get(f.severity, 4))

        # Calculate confidence based on known causes
        known_count = sum(1 for c in raw_causes if c in self.ROOT_CAUSE_DB)
        confidence = known_count / len(raw_causes) if raw_causes else 0.5

        analysis = RootCauseAnalysis(
            incident_id=incident_id,
            failure_type=failure_type,
            first_unsafe_turn=first_unsafe,
            contributing_factors=factors,
            mitigation_candidates=list(all_mitigations),
            confidence=confidence
        )

        if verbose:
            print(analysis.to_json())

        return analysis


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze incident root cause')
    parser.add_argument('--incident', required=True, help='Path to incident JSON')

    args = parser.parse_args()

    analyzer = RootCauseAnalyzer()
    incident = analyzer.load_incident(args.incident)
    analyzer.analyze(incident)


if __name__ == '__main__':
    main()
