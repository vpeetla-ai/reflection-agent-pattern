from dataclasses import dataclass


@dataclass(frozen=True)
class QualityPolicy:
    min_score: float = 0.85
    max_revisions: int = 2

    def accepts(self, score: float) -> bool:
        return score >= self.min_score

