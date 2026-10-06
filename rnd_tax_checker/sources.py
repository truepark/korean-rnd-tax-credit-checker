from urllib.parse import urlencode

RND_LAB_SEARCH_BASE = "https://www.rnd.or.kr/user/infoservice/search5.do"
RND_LAB_BUSINESS_NUMBER_INPUT_ID = "s_custsuno1"
RND_LAB_BUSINESS_NUMBER_SELECTOR = f"#{RND_LAB_BUSINESS_NUMBER_INPUT_ID}"


def normalize_business_number(value: str) -> str:
    digits = "".join(ch for ch in (value or "") if ch.isdigit())
    if len(digits) != 10:
        raise ValueError("사업자등록번호는 숫자 10자리여야 합니다.")
    return digits


def build_rnd_lab_search_url(business_number: str) -> str:
    """보조용 GET URL. 가능하면 실제 브라우저에서 #s_custsuno1 입력 후 검색 실행을 우선한다."""
    digits = normalize_business_number(business_number)
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


def build_rnd_lab_browser_steps(business_number: str) -> dict:
    """브라우저 자동화 구현에 사용할 정확한 입력 대상을 반환한다."""
    digits = normalize_business_number(business_number)
    return {
        "url": RND_LAB_SEARCH_BASE,
        "business_number": digits,
        "input_id": RND_LAB_BUSINESS_NUMBER_INPUT_ID,
        "input_selector": RND_LAB_BUSINESS_NUMBER_SELECTOR,
        "action": "fill_business_number_then_click_search",
    }


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
        "business_number_input_id": RND_LAB_BUSINESS_NUMBER_INPUT_ID,
        "business_number_selector": RND_LAB_BUSINESS_NUMBER_SELECTOR,
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
