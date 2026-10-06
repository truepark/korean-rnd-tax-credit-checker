# Korean R&D Tax Credit Checker

한국 조세특례제한법상 연구·인력개발비 세액공제의 외부 시험/연구기관 적격성 검토를 보조하는 프로젝트입니다.

## 핵심 사용법

사업자등록번호를 입력하면 다음 4개 축을 우선 확인합니다.

1. 전문연구사업자
2. KSIC(한국표준산업분류)상 기술시험·검사 및 분석업
3. KOLAS 공인시험기관 및 인정범위
4. 기업부설연구소/연구개발전담부서

그 후 조세특례제한법 시행령 별표 6의 외부 위탁기관 유형과 대조합니다.

> 중요: KOLAS 인정, 기업부설연구소 보유, 특정 KSIC 코드 중 하나만으로 세액공제 적격성이 자동 확정되는 것은 아닙니다.

## rnd.or.kr 사업자번호 직접조회

공식 연구소/전담부서 검색 화면:

`https://www.rnd.or.kr/user/infoservice/search5.do`

현재 확인된 화면 구조:

- 사업자번호 입력: `input#s_custsuno1[name="s_custsuno1"]`
- 입력값: 하이픈 없는 숫자 10자리
- 검색 버튼 문구: `검색하기`
- 검색결과 표: `기업명 / 연구소·전담부서명 / 규모 / 연구분야 / 구분`

공식 페이지는 단순 URL 조회가 아니라 실제 폼 검색이 필요하므로 Playwright로 브라우저를 조작합니다.

로컬 설치:

```bash
pip install -r requirements.txt
playwright install chromium
```

명령행 조회:

```bash
python scripts/rnd_lab_lookup.py 1198683629
```

## 웹 ChatGPT용 Hosted API

데스크톱 앱 없이 웹 ChatGPT에서도 사용할 수 있도록 `api_server.py`를 제공합니다.

실행:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 10000
```

엔드포인트:

```text
GET  /health
GET  /search-rnd-lab/{business_number}
POST /search-rnd-lab
GET  /docs
GET  /openapi.json
```

POST 예:

```json
{
  "business_number": "3538800727"
}
```

`API_KEY` 환경변수를 설정하면 `X-API-Key` 헤더가 일치해야 조회할 수 있습니다. `API_KEY`가 없으면 인증 없이 동작합니다.

### Render 배포

저장소 루트의 `Dockerfile`과 `render.yaml`을 사용합니다. Render에서 이 GitHub 저장소를 Blueprint/Web Service로 연결하면 Playwright Chromium이 포함된 Docker 서비스가 생성됩니다.

`render.yaml`은 `/health`를 헬스체크로 사용하고 `API_KEY`를 자동 생성하도록 설정되어 있습니다.

배포 완료 후 예시는 다음과 같습니다.

```text
https://<your-render-service>/health
https://<your-render-service>/docs
https://<your-render-service>/search-rnd-lab/3538800727
```

API 키가 활성화된 경우 요청 헤더에 `X-API-Key`가 필요합니다.

## 로컬 MCP로 연결

`mcp_server.py`에는 `search_rnd_lab` STDIO MCP 도구가 포함되어 있습니다.

```bash
python mcp_server.py
```

ChatGPT Desktop/Codex에서 로컬 MCP로 연결하면 `search_rnd_lab`을 직접 호출할 수 있습니다.

## 웹 ChatGPT 연결 흐름

웹에서는 로컬 STDIO MCP 대신 Hosted API 또는 향후 Remote MCP를 사용합니다.

```text
웹 ChatGPT
  -> korean-rnd-tax-credit-checker
  -> Hosted search-rnd-lab API
  -> Playwright/Chromium
  -> rnd.or.kr
  -> 사업자번호 입력 및 검색
  -> 연구소/전담부서 결과 반환
```

현재 `FastAPI`가 자동으로 OpenAPI 스키마를 제공하므로 배포 후 `/openapi.json`을 이용해 웹용 도구/플러그인 연결을 구성할 수 있습니다.

## 공식 확인 우선순위

1. 국가법령정보센터
2. 국가기술표준원 / KOLAS
3. 연구산업진흥 관련 공식 신고현황
4. rnd.or.kr 기업부설연구소/전담부서 신고관리시스템
5. 통계청 KSIC 및 사업자등록증
6. 기타 공공기관 자료
7. 민간 기업정보는 식별 보조용으로만 사용

## 구조

- `rnd_tax_checker/` : 판정 엔진 및 rnd.or.kr 직접조회
- `scripts/rnd_lab_lookup.py` : 사업자번호 조회 CLI
- `mcp_server.py` : 로컬 `search_rnd_lab` STDIO MCP
- `api_server.py` : 웹용 FastAPI 서버
- `Dockerfile` : Playwright 포함 배포 이미지
- `render.yaml` : Render 배포 Blueprint
- `skills/rnd-tax-credit-check/` : ChatGPT 플러그인 워크플로우
- `docs/` : 공식 데이터소스 및 판정 규칙
- `tests/` : 테스트

## 면책

본 도구는 세무검토 보조도구입니다. 실제 세액공제 적용 여부는 적용 사업연도 법령, 계약상대방, 연구과제, 실제 수행업무, 재위탁 여부, 수행장소, 시험 범위, 증빙 등을 함께 검토해야 합니다.
