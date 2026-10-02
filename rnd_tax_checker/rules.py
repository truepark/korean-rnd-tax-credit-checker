from .models import Verdict


def evaluate(evidence: dict):
    reasons = []
    matched_rule = None

    pro = evidence.get("professional_research_business", {})
    ksic = evidence.get("ksic", {})
    kolas = evidence.get("kolas", {})
    lab = evidence.get("corporate_research_institute", {})

    if pro.get("status") == "confirmed":
        matched_rule = "전문연구사업자 관련 기관 해당 가능성"
        reasons.append("전문연구사업자 관련 공식 등록이 확인됨")
        return Verdict.POSSIBLE, matched_rule, reasons, [
            "적용 사업연도 별표6 문언과 등록 업종의 일치 여부 확인",
            "실제 위탁업무가 연구개발에 해당하는지 확인",
        ]

    if ksic.get("code") in {"72911", "72919"}:
        matched_rule = "기술시험·검사 및 분석업 관련 기관 해당 가능성"
        reasons.append(f"KSIC {ksic.get('code')} 업종이 확인됨")

        if kolas.get("status") == "confirmed":
            reasons.append("KOLAS 공인시험기관 여부가 확인됨")
            return Verdict.POSSIBLE, matched_rule, reasons, [
                "해당 시험이 KOLAS 인정범위에 포함되는지 확인",
                "사업자등록증상 실제 영위 업종 확인",
                "위탁시험이 연구개발 과제와 직접 관련되는지 확인",
            ]

        return Verdict.REVIEW_REQUIRED, matched_rule, reasons, [
            "KOLAS 인정 여부 및 인정범위 확인",
            "사업자등록증상 실제 업종 확인",
            "시험성적서/계약서상 수행 주체 확인",
        ]

    if lab.get("status") == "confirmed":
        reasons.append("기업부설연구소 또는 연구개발전담부서 관련 정보가 확인됨")
        return Verdict.REVIEW_REQUIRED, None, reasons, [
            "기업부설연구소 보유만으로 외부 위탁기관 적격이 확정되는지 별도 검토",
            "실제 계약 상대방과 연구소 운영 주체의 동일성 확인",
        ]

    return Verdict.REVIEW_REQUIRED, None, ["핵심 공식정보가 충분히 확인되지 않음"], [
        "전문연구사업자 등록 여부",
        "KSIC 및 실제 사업자등록 업종",
        "KOLAS 공인시험기관 및 인정범위",
        "기업부설연구소/연구개발전담부서 관련 정보",
    ]
