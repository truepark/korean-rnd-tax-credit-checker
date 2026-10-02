from pprint import pprint
from rnd_tax_checker.checker import check_company

# 공개자료에서 KOLAS 인정이 확인되었다고 가정한 예시
result = check_company(
    business_number="105-82-11278",
    company_name="재단법인 키엘연구원",
    evidence={
        "kolas": {
            "status": "confirmed",
            "detail": "KOLAS 공인시험기관 확인",
            "scope": ["구체 인정범위는 인정서 확인 필요"]
        },
        "professional_research_business": {
            "status": "not_checked",
            "detail": "공식 신고현황 추가 조회 필요"
        },
        "corporate_research_institute": {
            "status": "not_checked",
            "detail": "공식 신고관리 정보 추가 확인 필요"
        }
    }
)

pprint(result)
