from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreWeights:
    methodological_novelty: float
    frontier_alignment: float
    domain_utility: float
    execution_efficiency: float
    scholarly_impact: float


def phase_one_score(methodological_novelty: float, frontier_alignment: float) -> float:
    return methodological_novelty * 0.6 + frontier_alignment * 0.4


def phase_two_score(domain_utility: float, execution_efficiency: float) -> float:
    return domain_utility * 0.7 + execution_efficiency * 0.3


def total_score(scores: dict, weights: ScoreWeights, utility_threshold: float) -> float:
    penalty = 0.7 if scores["domain_utility"] < utility_threshold else 1.0
    weighted = (
        scores["methodological_novelty"] * weights.methodological_novelty
        + scores["frontier_alignment"] * weights.frontier_alignment
        + scores["domain_utility"] * weights.domain_utility
        + scores["execution_efficiency"] * weights.execution_efficiency
        + scores["scholarly_impact"] * weights.scholarly_impact
    )
    return weighted * penalty
