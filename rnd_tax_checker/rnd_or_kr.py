from __future__ import annotations

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "business_number": self.business_number,
            "input_value": self.input_value,
            "total_count": self.total_count,
            "records": [r.to_dict() for r in (self.records or [])],
            "error": self.error,
            "source": RND_SEARCH_URL,
        }


def normalize_business_number(value: str) -> str:
    digits = "".join(ch for ch in (value or "") if ch.isdigit())
    if len(digits) != 10:
        raise ValueError("사업자등록번호는 숫자 10자리여야 합니다.")
    return digits


def _parse_total_count(page) -> int | None:
    import re

    body = page.locator("body").inner_text()
    match = re.search(r"총\s*([0-9,]+)\s*개", body)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def _find_result_table(page):
    tables = page.locator("table")
    for i in range(tables.count()):
        table = tables.nth(i)
        try:
            text = table.inner_text(timeout=1500)
        except Exception:
            continue
        if "기업명" in text and "연구소/전담부서명" in text and "구분" in text:
            return table
    return None


def _parse_records(page) -> list[RndLabRecord]:
    table = _find_result_table(page)
    if table is None:
        return []

    rows = table.locator("tbody tr")
    records: list[RndLabRecord] = []
    for i in range(rows.count()):
        cells = rows.nth(i).locator("td")
        values = [cells.nth(j).inner_text().strip() for j in range(cells.count())]
        # 예상 열: 번호, 기업명, 연구소/전담부서명, 규모, 연구분야, 구분, 홍보제품
        if len(values) < 6:
            continue
        records.append(
            RndLabRecord(
                company_name=values[1],
                lab_name=values[2],
                scale=values[3],
                research_field=values[4],
                lab_type=values[5],
            )
        )
    return records


def lookup_rnd_lab(business_number: str, *, headless: bool = True, timeout_ms: int = 20000) -> RndLabLookupResult:
    """rnd.or.kr 공식 검색 화면을 실제 브라우저로 조작해 사업자번호별 연구소/전담부서를 조회한다.

    Playwright가 필요하다::

        pip install playwright
        playwright install chromium

    사이트의 검색 방식이 GET/POST/자바스크립트 중 무엇인지에 의존하지 않고,
    실제 입력창에 사업자번호를 넣은 뒤 '검색하기' 버튼을 클릭한다.
    """
    digits = normalize_business_number(business_number)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        return RndLabLookupResult(
            status="browser_dependency_missing",
            business_number=digits,
            error="playwright가 설치되어 있지 않습니다. pip install playwright 후 playwright install chromium을 실행하세요.",
        )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page(locale="ko-KR")
            page.goto(RND_SEARCH_URL, wait_until="domcontentloaded", timeout=timeout_ms)

            inputs = page.locator(BUSINESS_NUMBER_SELECTOR)
            if inputs.count() == 0:
                browser.close()
                return RndLabLookupResult(
                    status="input_not_found",
                    business_number=digits,
                    error=f"사업자번호 입력요소를 찾지 못했습니다: {BUSINESS_NUMBER_SELECTOR}",
                )

            input_box = None
            for i in range(inputs.count()):
                candidate = inputs.nth(i)
                if candidate.is_visible():
                    input_box = candidate
                    break
            if input_box is None:
                input_box = inputs.first

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
                )

            # 버튼 문구는 현재 공식 페이지에서 '검색하기'로 확인된다.
            buttons = page.get_by_role("button", name="검색하기")
            clicked = False
            for i in range(buttons.count()):
                button = buttons.nth(i)
                if button.is_visible():
                    button.click()
                    clicked = True
                    break

            if not clicked:
                # 역할 인식 실패 시 텍스트 기반 fallback
                fallback = page.locator('button:has-text("검색하기"), input[type="submit"][value*="검색"]')
                for i in range(fallback.count()):
                    button = fallback.nth(i)
                    if button.is_visible():
                        button.click()
                        clicked = True
                        break

            if not clicked:
                # input이 속한 form을 마지막 수단으로 submit
                form = input_box.locator("xpath=ancestor::form[1]")
                if form.count() > 0:
                    form.evaluate("form => form.submit()")
                    clicked = True

            if not clicked:
                browser.close()
                return RndLabLookupResult(
                    status="search_control_not_found",
                    business_number=digits,
                    input_value=actual_value,
                    error="검색 버튼 또는 검색 form을 찾지 못했습니다.",
                )

            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except Exception:
                page.wait_for_timeout(1200)

            total_count = _parse_total_count(page)
            records = _parse_records(page)
            browser.close()

            if total_count == 0 or (total_count is None and not records):
                return RndLabLookupResult(
                    status="zero_results",
                    business_number=digits,
                    input_value=actual_value,
                    total_count=0 if total_count == 0 else total_count,
                    records=[],
                )

            return RndLabLookupResult(
                status="confirmed",
                business_number=digits,
                input_value=actual_value,
                total_count=total_count if total_count is not None else len(records),
                records=records,
            )
    except Exception as exc:
        return RndLabLookupResult(
            status="execution_error",
            business_number=digits,
            error=f"{type(exc).__name__}: {exc}",
        )
