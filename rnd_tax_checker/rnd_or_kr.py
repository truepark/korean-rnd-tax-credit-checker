from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any

RND_SEARCH_URL = "https://www.rnd.or.kr/user/infoservice/search5.do"
BUSINESS_NUMBER_SELECTOR = 'input#s_custsuno1[name="s_custsuno1"]'


@dataclass
class RndLabRecord:
    company_name: str = ""
    lab_name: str = ""
    scale: str = ""
    research_field: str = ""
    lab_type: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class RndLabLookupResult:
    status: str
    business_number: str
    input_value: str = ""
    total_count: int | None = None
    records: list[RndLabRecord] | None = None
    error: str | None = None
    lookup_method: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "business_number": self.business_number,
            "input_value": self.input_value,
            "total_count": self.total_count,
            "records": [r.to_dict() for r in (self.records or [])],
            "error": self.error,
            "lookup_method": self.lookup_method,
            "source": RND_SEARCH_URL,
        }


def normalize_business_number(value: str) -> str:
    """하이픈/공백 등 숫자가 아닌 문자를 제거하고 10자리 사업자번호로 정규화한다."""
    digits = "".join(ch for ch in (value or "") if ch.isdigit())
    if len(digits) != 10:
        raise ValueError("사업자등록번호는 하이픈 포함 여부와 관계없이 숫자 10자리여야 합니다.")
    return digits


def _parse_total_count_text(text: str) -> int | None:
    patterns = [
        r"총\s*([0-9,]+)\s*개",
        r"총\s*([0-9,]+)\s*건",
        r"전체\s*([0-9,]+)\s*건",
    ]
    for pattern in patterns:
        match = re.search(pattern, text or "")
        if match:
            return int(match.group(1).replace(",", ""))
    return None


def _parse_html_records(html: str) -> tuple[int | None, list[RndLabRecord]]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    total_count = _parse_total_count_text(soup.get_text(" ", strip=True))
    records: list[RndLabRecord] = []

    for table in soup.find_all("table"):
        headers = [th.get_text(" ", strip=True) for th in table.find_all("th")]
        header_text = " | ".join(headers)
        if not ("기업명" in header_text and "연구소" in header_text and "구분" in header_text):
            continue

        for row in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in row.find_all("td")]
            if len(cells) < 6:
                continue
            # 예상 열: 번호, 기업명, 연구소/전담부서명, 규모, 연구분야, 구분, ...
            records.append(
                RndLabRecord(
                    company_name=cells[1],
                    lab_name=cells[2],
                    scale=cells[3],
                    research_field=cells[4],
                    lab_type=cells[5],
                )
            )
        if records:
            break

    if total_count is None and records:
        total_count = len(records)
    return total_count, records


def _lookup_via_post(business_number: str, timeout_ms: int = 20000) -> RndLabLookupResult:
    """개발자도구에서 확인된 search5.do POST 폼을 직접 재현한다."""
    digits = normalize_business_number(business_number)
    try:
        import requests
    except ImportError:
        return RndLabLookupResult(
            status="http_dependency_missing",
            business_number=digits,
            input_value=digits,
            error="requests가 설치되어 있지 않습니다.",
            lookup_method="POST",
        )

    payload = {
        "currentPage": "1",
        "s_yngugubn": "3",
        "y_code": "",
        "yngucode": "",
        "current_url": "",
        "save_s_key": "",
        "save_s_type": "",
        "save_s_yngugubn": "3",
        "save_s_custsuno1": digits,
        "save_s_custsuno2": "",
        "save_s_custsuno3": "",
        "s_custgwmo": "",
        "s_yngu_si": "",
        "save_s_yngu_gun": "",
        "s_custksic": "",
        "s_custksic2": "",
        "s_y_code": "",
        "s_codename": "",
        "save_s_ynguino": "",
        "excel_yn": "N",
        "s_type": "CUSTNAME",
        "s_key": "",
        "s_custsuno1": digits,
        "s_custsuno2": "",
        "s_custsuno3": "",
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": RND_SEARCH_URL,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        timeout = timeout_ms / 1000
        with requests.Session() as session:
            # 먼저 검색페이지를 열어 세션/쿠키를 확보한다.
            session.get(RND_SEARCH_URL, headers=headers, timeout=timeout)
            response = session.post(
                RND_SEARCH_URL,
                data=payload,
                headers=headers,
                timeout=timeout,
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding or response.encoding
            total_count, records = _parse_html_records(response.text)

        if total_count == 0 or (total_count is None and not records):
            return RndLabLookupResult(
                status="zero_results",
                business_number=digits,
                input_value=digits,
                total_count=0 if total_count == 0 else total_count,
                records=[],
                lookup_method="POST",
            )

        return RndLabLookupResult(
            status="confirmed",
            business_number=digits,
            input_value=digits,
            total_count=total_count if total_count is not None else len(records),
            records=records,
            lookup_method="POST",
        )
    except Exception as exc:
        return RndLabLookupResult(
            status="http_execution_error",
            business_number=digits,
            input_value=digits,
            error=f"{type(exc).__name__}: {exc}",
            lookup_method="POST",
        )


def _parse_total_count_page(page) -> int | None:
    return _parse_total_count_text(page.locator("body").inner_text())


def _find_result_table(page):
    tables = page.locator("table")
    for i in range(tables.count()):
        table = tables.nth(i)
        try:
            text = table.inner_text(timeout=1500)
        except Exception:
            continue
        if "기업명" in text and "연구소" in text and "구분" in text:
            return table
    return None


def _parse_records_page(page) -> list[RndLabRecord]:
    table = _find_result_table(page)
    if table is None:
        return []
    rows = table.locator("tbody tr")
    records: list[RndLabRecord] = []
    for i in range(rows.count()):
        cells = rows.nth(i).locator("td")
        values = [cells.nth(j).inner_text().strip() for j in range(cells.count())]
        if len(values) < 6:
            continue
        records.append(RndLabRecord(values[1], values[2], values[3], values[4], values[5]))
    return records


def _lookup_via_playwright(business_number: str, *, headless: bool = True, timeout_ms: int = 20000) -> RndLabLookupResult:
    digits = normalize_business_number(business_number)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return RndLabLookupResult(
            status="browser_dependency_missing",
            business_number=digits,
            input_value=digits,
            error="playwright가 설치되어 있지 않습니다.",
            lookup_method="Playwright",
        )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page(locale="ko-KR")
            page.goto(RND_SEARCH_URL, wait_until="domcontentloaded", timeout=timeout_ms)
            input_box = page.locator(BUSINESS_NUMBER_SELECTOR).first
            if input_box.count() == 0:
                browser.close()
                return RndLabLookupResult(
                    status="input_not_found",
                    business_number=digits,
                    input_value=digits,
                    error=f"사업자번호 입력요소를 찾지 못했습니다: {BUSINESS_NUMBER_SELECTOR}",
                    lookup_method="Playwright",
                )

            input_box.fill("")
            input_box.fill(digits)
            input_box.dispatch_event("input")
            input_box.dispatch_event("change")
            input_box.blur()
            actual_value = input_box.input_value()
            if actual_value != digits:
                browser.close()
                return RndLabLookupResult(
                    status="input_value_failed",
                    business_number=digits,
                    input_value=actual_value,
                    error="사업자번호 입력 후 실제 value가 요청번호와 일치하지 않습니다.",
                    lookup_method="Playwright",
                )

            buttons = page.get_by_role("button", name="검색하기")
            if buttons.count() > 0:
                buttons.first.click()
            else:
                fallback = page.locator('button:has-text("검색하기"), input[type="submit"][value*="검색"]')
                if fallback.count() > 0:
                    fallback.first.click()
                else:
                    form = input_box.locator("xpath=ancestor::form[1]")
                    if form.count() == 0:
                        browser.close()
                        return RndLabLookupResult(
                            status="search_control_not_found",
                            business_number=digits,
                            input_value=digits,
                            error="검색 버튼 또는 검색 form을 찾지 못했습니다.",
                            lookup_method="Playwright",
                        )
                    form.evaluate("form => form.submit()")

            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except Exception:
                page.wait_for_timeout(1200)

            total_count = _parse_total_count_page(page)
            records = _parse_records_page(page)
            browser.close()

            if total_count == 0 or (total_count is None and not records):
                return RndLabLookupResult("zero_results", digits, digits, 0 if total_count == 0 else total_count, [], lookup_method="Playwright")
            return RndLabLookupResult("confirmed", digits, digits, total_count or len(records), records, lookup_method="Playwright")
    except Exception as exc:
        return RndLabLookupResult(
            status="execution_error",
            business_number=digits,
            input_value=digits,
            error=f"{type(exc).__name__}: {exc}",
            lookup_method="Playwright",
        )


def lookup_rnd_lab(business_number: str, *, headless: bool = True, timeout_ms: int = 20000) -> RndLabLookupResult:
    """사업자번호로 rnd.or.kr 연구소/전담부서 등록 여부를 조회한다.

    1) 입력값에서 하이픈/공백을 제거해 숫자 10자리로 정규화
    2) 개발자도구에서 확인된 search5.do POST 검색을 우선 실행
    3) POST 방식 자체가 실행 오류인 경우에만 Playwright로 fallback
    """
    post_result = _lookup_via_post(business_number, timeout_ms=timeout_ms)
    if post_result.status not in {"http_dependency_missing", "http_execution_error"}:
        return post_result
    return _lookup_via_playwright(business_number, headless=headless, timeout_ms=timeout_ms)
