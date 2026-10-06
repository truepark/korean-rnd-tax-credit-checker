from urllib.parse import urlencode

RND_LAB_SEARCH_BASE = "https://www.rnd.or.kr/user/infoservice/search5.do"


def build_rnd_lab_search_url(business_number: str) -> str:
    digits = "".join(ch for ch in (business_number or "") if ch.isdigit())
    if len(digits) != 10:
        raise ValueError("사업자등록번호는 숫자 10자리여야 합니다.")
    params = {
        "currentPage": "1",
        "excel_yn": "N",
        "recordCountPerPage": "20",
        "s_custsuno1": digits,
        "s_type": "CUSTNAME",
        "s_yngugubn": "3",
        "save_s_yngugubn": "3",
    }
    return f"{RND_LAB_SEARCH_BASE}?{urlencode(params)}"


OFFICIAL_SOURCES = {
    "law": {
        "name": "국가법령정보센터",
        "url": "https://www.law.go.kr/",
        "purpose": "조세특례제한법 시행령 제9조 및 별표6 확인",
    },
    "kolas": {
        "name": "KOLAS 한국인정기구",
        "url": "https://www.knab.go.kr/",
        "purpose": "공인시험기관 및 인정범위 확인",
    },
    "rnd_lab": {
        "name": "기업부설연구소/전담부서 신고관리시스템",
        "url": RND_LAB_SEARCH_BASE,
        "purpose": "기업부설연구소 및 연구개발전담부서 공식 검색",
        "search_key": "사업자번호 10자리 직접검색 우선, 0건일 때만 기업명 보조검색",
        "business_number_param": "s_custsuno1",
    },
}

RND_LOOKUP_STATUS = {
    "confirmed": "공식 확인",
    "zero_results": "공식 검색 0건",
    "execution_unavailable": "직접검색 실행 불가",
}

SOURCE_PRIORITY = [
    "정부/공공기관 공식 API 또는 공식 검색폼 직접조회",
    "정부/공공기관 공식 검색 결과",
    "공식 인증서 또는 등록증",
    "사업자등록증 및 계약서",
    "기타 공개자료",
]
