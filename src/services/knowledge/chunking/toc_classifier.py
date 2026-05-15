# ---- Standard Library ----
import re

# ---- TOC Classifier ----
from langchain_core.documents import Document


class TOCClassifier:
    # ---- Initialize Patterns and Constants ----
    def __init__(
        self,
        threshold: float = 0.4,
        toc_keywords: list[str] | None = None,
    ):
        self.threshold = threshold

        self.toc_keywords = toc_keywords or [
            r"\btable of contents\b",
            r"\bcontents\b",
            r"\bbrief contents\b",
            r"\bdetailed contents\b",
            r"\blist of chapters\b",
            r"\bwhat's inside\b",
            r"\btable of exhibits\b",
            r"\bindex of titles\b",
            r"\boutline\b",
        ]

        self.keywords_pattern = re.compile(
            r"(" + "|".join(self.toc_keywords) + r")",
            re.IGNORECASE,
        )
        self.dots_pattern = re.compile(r"\.{3,}")
        self.page_num_pattern = re.compile(r"\d{1,3}\s*$", re.MULTILINE)

        self.keyword_score_weight = 0.5
        self.dots_density_weight = 0.3
        self.page_num_density_weight = 0.2

    # ---- Keyword Detection ----
    def has_toc_keywords(self, text: str) -> bool:
        if not text:
            return False
        return bool(self.keywords_pattern.search(text))

    # ---- Dots Density Calculation ----
    def get_dots_density(self, text: str) -> float:
        if not text:
            return 0.0

        lines = [l for l in text.split("\n") if l.strip()]
        if not lines:
            return 0.0

        dot_lines = sum(1 for l in lines if self.dots_pattern.search(l))
        return dot_lines / len(lines)

    # ---- Page Number Density Calculation ----
    def get_page_num_density(self, text: str) -> float:
        if not text:
            return 0.0

        lines = [l for l in text.split("\n") if l.strip()]
        if not lines:
            return 0.0

        page_lines = sum(1 for l in lines if self.page_num_pattern.search(l))
        return page_lines / len(lines)

    # ---- Score Computation ----
    def compute_toc_score(self, text: str) -> float:
        if not text:
            return 0.0

        score = 0.0

        if self.has_toc_keywords(text):
            score += self.keyword_score_weight

        score += self.get_dots_density(text) * self.dots_density_weight
        score += self.get_page_num_density(text) * self.page_num_density_weight

        return min(score, 1.0)

    # ---- TOC Classification ----
    def is_toc(self, text: str) -> tuple[bool, float]:
        score = self.compute_toc_score(text)
        return score >= self.threshold, score

    # ---- Metadata Enrichment ----
    def enrich_metadata(self, doc: Document) -> dict:
        text = doc.page_content
        toc_flag, toc_score = self.is_toc(text)

        new_metadata = doc.metadata.copy()
        new_metadata.update(
            {
                "is_toc": toc_flag,
                "toc_score": round(toc_score, 2),
                "toc_threshold_used": self.threshold,
            }
        )

        return new_metadata