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
        "url": "https://www.rnd.or.kr/user/infoservice/search5.do",
        "purpose": "기업부설연구소 및 연구개발전담부서 공식 검색",
        "search_key": "사업자번호 우선, 미조회 시 기업명 보조검색",
    },
}

SOURCE_PRIORITY = [
    "정부/공공기관 공식 API",
    "정부/공공기관 공식 검색 결과",
    "공식 인증서 또는 등록증",
    "사업자등록증 및 계약서",
    "기타 공개자료",
]
