import re
from datetime import datetime, timezone, timedelta

from .models import CompanyCheckResult, CriterionResult
from .rules import evaluate

KST = timezone(timedelta(hours=9))


def normalize_business_number(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) != 10:
        raise ValueError("사업자등록번호는 숫자 10자리여야 합니다.")
    return digits


def check_company(
    business_number: str,
    company_name: str | None = None,
    evidence: dict | None = None,
) -> dict:
    business_number = normalize_business_number(business_number)
    evidence = evidence or {}
    checked_at = datetime.now(KST).isoformat(timespec="seconds")

    criteria = []

    pro = evidence.get("professional_research_business", {})
    criteria.append(CriterionResult(
        criterion="전문연구사업자",
        status=pro.get("status", "not_checked"),
        detail=pro.get("detail", "공식 조회 필요"),
        source_url=pro.get("source_url"),
        checked_at=pro.get("checked_at", checked_at),
    ))

    ksic = evidence.get("ksic", {})
    criteria.append(CriterionResult(
        criterion="KSIC",
        status="confirmed" if ksic.get("code") else "not_checked",
        detail=f"{ksic.get('code', '')} {ksic.get('name', '')}".strip() or "공식 업종 확인 필요",
        source_url=ksic.get("source_url"),
        checked_at=ksic.get("checked_at", checked_at),
    ))

    kolas = evidence.get("kolas", {})
    scope = kolas.get("scope") or []
    criteria.append(CriterionResult(
        criterion="KOLAS",
        status=kolas.get("status", "not_checked"),
        detail=("인정범위: " + ", ".join(scope)) if scope else kolas.get("detail", "공인시험기관 및 인정범위 확인 필요"),
        source_url=kolas.get("source_url"),
        checked_at=kolas.get("checked_at", checked_at),
    ))

    lab = evidence.get("corporate_research_institute", {})
    criteria.append(CriterionResult(
        criterion="기업부설연구소",
        status=lab.get("status", "not_checked"),
        detail=lab.get("detail", "공식 확인 필요"),
        source_url=lab.get("source_url"),
        checked_at=lab.get("checked_at", checked_at),
    ))

    verdict, matched_rule, reasons, additional = evaluate(evidence)

    return CompanyCheckResult(
        business_number=business_number,
        company_name=company_name,
        verdict=verdict,
        matched_rule=matched_rule,
        reasons=reasons,
        criteria=criteria,
        additional_evidence_required=additional,
    ).to_dict()
