from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ScoreWeights:
    methodological_novelty: float
    frontier_alignment: float
    domain_utility: float
    execution_efficiency: float
    scholarly_impact: float

    @property
    def total(self) -> float:
        return (
            self.methodological_novelty
            + self.frontier_alignment
            + self.domain_utility
            + self.execution_efficiency
            + self.scholarly_impact
        )


def phase_one_score(methodological_novelty: float, frontier_alignment: float) -> float:
    return methodological_novelty * 0.6 + frontier_alignment * 0.4


def phase_two_score(domain_utility: float, execution_efficiency: float) -> float:
    return domain_utility * 0.7 + execution_efficiency * 0.3


def total_score(scores: dict, weights: ScoreWeights, utility_threshold: float) -> float:
    required = (
        "methodological_novelty",
        "frontier_alignment",
        "domain_utility",
        "execution_efficiency",
        "scholarly_impact",
    )
    if any(key not in scores for key in required):
        raise ValueError("all five score dimensions are required")
    if weights.total <= 0 or not isfinite(weights.total):
        raise ValueError("score weights must have a positive finite total")

    penalty = 0.7 if scores["domain_utility"] < utility_threshold else 1.0
    weighted = (
        scores["methodological_novelty"] * weights.methodological_novelty
        + scores["frontier_alignment"] * weights.frontier_alignment
        + scores["domain_utility"] * weights.domain_utility
        + scores["execution_efficiency"] * weights.execution_efficiency
        + scores["scholarly_impact"] * weights.scholarly_impact
    )
    return weighted * penalty
