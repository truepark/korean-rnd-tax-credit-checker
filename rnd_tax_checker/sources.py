from urllib.parse import urlencode

RND_LAB_SEARCH_BASE = "https://www.rnd.or.kr/user/infoservice/search5.do"
RND_LAB_BUSINESS_NUMBER_INPUT_ID = "s_custsuno1"
RND_LAB_BUSINESS_NUMBER_INPUT_NAME = "s_custsuno1"
RND_LAB_BUSINESS_NUMBER_INPUT_CLASS = "c__input"
RND_LAB_BUSINESS_NUMBER_MAXLENGTH = 10
RND_LAB_BUSINESS_NUMBER_SELECTOR = 'input#s_custsuno1[name="s_custsuno1"]'


def normalize_business_number(value: str) -> str:
    digits = "".join(ch for ch in (value or "") if ch.isdigit())
    if len(digits) != RND_LAB_BUSINESS_NUMBER_MAXLENGTH:
        raise ValueError("사업자등록번호는 하이픈 없는 숫자 10자리여야 합니다.")
    return digits


def build_rnd_lab_search_url(business_number: str) -> str:
    """보조용 GET URL. 공식 확인은 가능하면 실제 input에 입력 후 검색 실행을 우선한다."""
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
    """rnd.or.kr 실제 사업자번호 입력요소에 맞춘 브라우저 자동화 계약을 반환한다."""
    digits = normalize_business_number(business_number)
    return {
        "url": RND_LAB_SEARCH_BASE,
        "business_number": digits,
        "input": {
            "type": "text",
            "id": RND_LAB_BUSINESS_NUMBER_INPUT_ID,
            "name": RND_LAB_BUSINESS_NUMBER_INPUT_NAME,
            "class": RND_LAB_BUSINESS_NUMBER_INPUT_CLASS,
            "maxlength": RND_LAB_BUSINESS_NUMBER_MAXLENGTH,
            "placeholder": "000-00-00000",
            "selector": RND_LAB_BUSINESS_NUMBER_SELECTOR,
            "value_format": "10 digits without hyphens",
        },
        "steps": [
            "open_search_page",
            "locate_business_number_input",
            "clear_existing_value",
            "fill_10_digit_business_number",
            "dispatch_input_change_and_optional_blur",
            "verify_input_value_equals_business_number",
            "click_search_or_submit_form",
            "wait_for_result_table_or_count_change",
            "parse_results",
        ],
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
        "business_number_input_name": RND_LAB_BUSINESS_NUMBER_INPUT_NAME,
        "business_number_selector": RND_LAB_BUSINESS_NUMBER_SELECTOR,
        "business_number_maxlength": RND_LAB_BUSINESS_NUMBER_MAXLENGTH,
        "business_number_value_format": "digits_only",
    },
}

RND_LOOKUP_STATUS = {
    "confirmed": "공식 확인",
    "zero_results": "공식 검색 0건",
    "input_value_failed": "입력값 설정 실패",
    "execution_unavailable": "직접검색 실행 불가",
}

SOURCE_PRIORITY = [
    "정부/공공기관 공식 API 또는 공식 검색폼 직접조회",
    "정부/공공기관 공식 검색 결과",
    "공식 인증서 또는 등록증",
    "사업자등록증 및 계약서",
    "기타 공개자료",
]
