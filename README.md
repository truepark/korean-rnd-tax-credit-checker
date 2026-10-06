# Korean R&D Tax Credit Checker

한국 조세특례제한법상 연구·인력개발비 세액공제의 외부 시험/연구기관 적격성 검토를 보조하는 프로젝트입니다.

## 핵심 사용법

사업자등록번호를 입력하면 다음 4개 축을 우선 확인합니다.

1. 전문연구사업자
2. KSIC(한국표준산업분류)상 기술시험·검사 및 분석업
3. KOLAS 공인시험기관 및 인정범위
4. 기업부설연구소/연구개발전담부서

그 후 조세특례제한법 시행령 별표 6의 외부 위탁기관 유형과 대조하여 다음 상태 중 하나로 표시합니다.

- CONFIRMED: 공식 근거와 별표6 해당유형이 직접 확인됨
- POSSIBLE: 적격 가능성이 높으나 업무내용/인정범위 등 추가 확인 필요
- REVIEW_REQUIRED: 핵심 증빙이 부족하거나 법적 연결관계 추가 검토 필요
- NOT_APPLICABLE: 확인된 정보상 해당 유형과 불일치

> 중요: KOLAS 인정, 기업부설연구소 보유, 특정 KSIC 코드 중 하나만으로 세액공제 적격성이 자동 확정되는 것은 아닙니다.

## rnd.or.kr 사업자번호 직접조회

공식 연구소/전담부서 검색 화면은 다음 주소를 사용합니다.

`https://www.rnd.or.kr/user/infoservice/search5.do`

현재 확인된 화면 구조는 다음과 같습니다.

- 사업자번호 입력: `input#s_custsuno1[name="s_custsuno1"]`
- 입력값: 하이픈 없는 숫자 10자리
- 검색 버튼 문구: `검색하기`
- 결과: `기업명 / 연구소·전담부서명 / 규모 / 연구분야 / 구분`

사이트가 검색 버튼 클릭 후 결과를 생성하므로 단순 URL 조합이 아니라 Playwright로 실제 브라우저를 조작합니다.

설치:

```bash
pip install -r requirements.txt
playwright install chromium
```

명령행 조회:

```bash
python scripts/rnd_lab_lookup.py 1198683629
```

브라우저 창을 보면서 테스트하려면:

```bash
python scripts/rnd_lab_lookup.py 1198683629 --show-browser
```

Python에서 직접 사용:

```python
from rnd_tax_checker import lookup_rnd_lab

result = lookup_rnd_lab("119-86-83629")
print(result.to_dict())
```

정상 조회 시 예시는 다음 구조입니다.

```json
{
  "status": "confirmed",
  "business_number": "1198683629",
  "input_value": "1198683629",
  "total_count": 1,
  "records": [
    {
      "company_name": "...",
      "lab_name": "...",
      "scale": "...",
      "research_field": "...",
      "lab_type": "연구소"
    }
  ],
  "source": "https://www.rnd.or.kr/user/infoservice/search5.do"
}
```

조회 결과가 없으면 `zero_results`, 입력값이 바뀌지 않으면 `input_value_failed`, 사이트 구조가 바뀌면 `input_not_found` 또는 `search_control_not_found` 상태로 반환합니다.

## ChatGPT 플러그인 방식

이 저장소에는 skills 기반 플러그인 정의를 포함합니다.

예시 입력:

```
1058211278 적격 여부 확인해줘
```

권장 출력:

| 항목 | 결과 | 확인 내용 |
|---|---|---|
| 사업자번호 | 105-82-11278 | 정상 형식 |
| 기관명 | 재단법인 키엘연구원 | 현재 명칭 확인 |
| 전문연구사업자 | 확인 필요 | 공식 등록현황 검색 |
| KSIC | 확인 필요 | 기술시험·검사 및 분석업 영위 여부 |
| KOLAS | 확인 | KT099 등 현재 인정상태/범위 확인 |
| 기업부설연구소 | 확인 필요 | rnd.or.kr 사업자번호 직접조회 |
| 별표6 | 가능성 있음 | 해당 기관 유형 및 실제 위탁업무 추가 검토 |

## Python 사용 예시

```python
from rnd_tax_checker.checker import check_company

result = check_company(
    business_number="1058211278",
    company_name="재단법인 키엘연구원",
    evidence={
        "kolas": {
            "status": "confirmed",
            "detail": "KOLAS 시험기관 인정 확인",
            "scope": ["해당 시험분야는 인정서에서 별도 확인 필요"]
        }
    }
)

print(result)
```

## 공식 확인 우선순위

1. 국가법령정보센터
2. 국가기술표준원 / KOLAS
3. 연구산업진흥 관련 공식 신고현황
4. rnd.or.kr 기업부설연구소/전담부서 신고관리시스템
5. 통계청 KSIC 및 사업자등록증
6. 기타 공공기관 자료
7. 민간 기업정보는 식별 보조용으로만 사용

## 현재 한계

`lookup_rnd_lab()` 자체는 Playwright가 설치된 실행환경에서 실제 브라우저를 사용합니다. ChatGPT의 skills-only 플러그인은 Python/Playwright를 직접 실행하는 도구가 아니므로, ChatGPT 안에서 이 함수를 자동 호출하려면 이 조회 함수를 MCP/API 도구로 별도 연결해야 합니다.

즉 저장소 코드는 실제 조회가 가능하지만, 플러그인에서 완전 자동 호출하려면 다음 단계가 필요합니다.

- Playwright가 설치된 서버 또는 로컬 MCP에서 `lookup_rnd_lab` 실행
- 입력: 사업자번호 10자리
- 출력: 등록여부, 기업명, 연구소/전담부서명, 규모, 연구분야, 구분
- ChatGPT 플러그인에서 해당 MCP/API 도구 호출

## 구조

- `rnd_tax_checker/` : 판정 엔진 및 rnd.or.kr 직접조회
- `scripts/rnd_lab_lookup.py` : 사업자번호 조회 CLI
- `skills/rnd-tax-credit-check/` : ChatGPT 플러그인 워크플로우
- `docs/` : 공식 데이터소스 및 판정 규칙
- `examples/` : 예시
- `tests/` : 테스트

## 면책

본 도구는 세무검토 보조도구입니다. 실제 세액공제 적용 여부는 적용 사업연도 법령, 계약상대방, 연구과제, 실제 수행업무, 재위탁 여부, 수행장소, 시험 범위, 증빙 등을 함께 검토해야 합니다.
