from typing import List, Dict, Any, Tuple


class PHQ9Scorer:
    QUESTION_COUNT = 9
    MIN_SCORE_PER_ITEM = 0
    MAX_SCORE_PER_ITEM = 3

    SEVERITY_TIERS = [
        (0, 4, "Minimal"),
        (5, 9, "Mild"),
        (10, 14, "Moderate"),
        (15, 19, "Moderately Severe"),
        (20, 27, "Severe")
    ]

    @classmethod
    def validate_and_score(cls, scores: List[int]) -> Dict[str, Any]:
        if not isinstance(scores, list) or len(scores) != cls.QUESTION_COUNT:
            raise ValueError(f"PHQ-9 requires exactly {cls.QUESTION_COUNT} items, received {len(scores) if isinstance(scores, list) else 'non-list'}")
        
        for idx, val in enumerate(scores):
            if not isinstance(val, int) or val < cls.MIN_SCORE_PER_ITEM or val > cls.MAX_SCORE_PER_ITEM:
                raise ValueError(f"PHQ-9 item {idx + 1} score '{val}' is invalid (must be integer between {cls.MIN_SCORE_PER_ITEM} and {cls.MAX_SCORE_PER_ITEM})")

        total = sum(scores)
        item_9 = scores[8]  # 0-indexed 9th question: self-harm/suicide ideation
        
        severity = "Severe"
        for low, high, label in cls.SEVERITY_TIERS:
            if low <= total <= high:
                severity = label
                break

        return {
            "total_score": total,
            "item_9_score": item_9,
            "is_item_9_positive": item_9 > 0,
            "severity": severity,
            "scores": scores
        }


class GAD7Scorer:
    QUESTION_COUNT = 7
    MIN_SCORE_PER_ITEM = 0
    MAX_SCORE_PER_ITEM = 3

    SEVERITY_TIERS = [
        (0, 4, "Minimal"),
        (5, 9, "Mild"),
        (10, 14, "Moderate"),
        (15, 21, "Severe")
    ]

    @classmethod
    def validate_and_score(cls, scores: List[int]) -> Dict[str, Any]:
        if not isinstance(scores, list) or len(scores) != cls.QUESTION_COUNT:
            raise ValueError(f"GAD-7 requires exactly {cls.QUESTION_COUNT} items, received {len(scores) if isinstance(scores, list) else 'non-list'}")

        for idx, val in enumerate(scores):
            if not isinstance(val, int) or val < cls.MIN_SCORE_PER_ITEM or val > cls.MAX_SCORE_PER_ITEM:
                raise ValueError(f"GAD-7 item {idx + 1} score '{val}' is invalid (must be integer between {cls.MIN_SCORE_PER_ITEM} and {cls.MAX_SCORE_PER_ITEM})")

        total = sum(scores)
        severity = "Severe"
        for low, high, label in cls.SEVERITY_TIERS:
            if low <= total <= high:
                severity = label
                break

        return {
            "total_score": total,
            "severity": severity,
            "scores": scores
        }


class AUDITCScorer:
    QUESTION_COUNT = 3
    MIN_SCORE_PER_ITEM = 0
    MAX_SCORE_PER_ITEM = 4

    @classmethod
    def validate_and_score(cls, scores: List[int]) -> Dict[str, Any]:
        if not isinstance(scores, list) or len(scores) != cls.QUESTION_COUNT:
            raise ValueError(f"AUDIT-C requires exactly {cls.QUESTION_COUNT} items, received {len(scores) if isinstance(scores, list) else 'non-list'}")

        for idx, val in enumerate(scores):
            if not isinstance(val, int) or val < cls.MIN_SCORE_PER_ITEM or val > cls.MAX_SCORE_PER_ITEM:
                raise ValueError(f"AUDIT-C item {idx + 1} score '{val}' is invalid (must be integer between {cls.MIN_SCORE_PER_ITEM} and {cls.MAX_SCORE_PER_ITEM})")

        total = sum(scores)
        risk_level = "Hazardous" if total >= 4 else "Low"
        return {
            "total_score": total,
            "risk_level": risk_level,
            "scores": scores
        }

