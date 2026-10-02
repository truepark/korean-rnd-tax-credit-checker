from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class Verdict(str, Enum):
    CONFIRMED = "CONFIRMED"
    POSSIBLE = "POSSIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class CriterionResult:
    criterion: str
    status: str
    detail: str
    source_url: Optional[str] = None
    checked_at: Optional[str] = None


@dataclass
class CompanyCheckResult:
    business_number: str
    company_name: Optional[str]
    verdict: Verdict
    matched_rule: Optional[str]
    reasons: List[str]
    criteria: List[CriterionResult]
    additional_evidence_required: List[str]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["verdict"] = self.verdict.value
        return data
