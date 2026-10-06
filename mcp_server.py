from mcp.server.fastmcp import FastMCP

from rnd_tax_checker.rnd_or_kr import lookup_rnd_lab

mcp = FastMCP("korean-rnd-tax-credit-checker")


@mcp.tool()
def search_rnd_lab(business_number: str, show_browser: bool = False) -> dict:
    """사업자번호로 rnd.or.kr 기업부설연구소/연구개발전담부서 등록 여부를 공식 검색한다.

    business_number: 10자리 숫자 또는 하이픈 포함 사업자등록번호
    show_browser: True이면 Chromium 브라우저 창을 표시한다.
    """
    result = lookup_rnd_lab(business_number, headless=not show_browser)
    return result.to_dict()


if __name__ == "__main__":
    mcp.run(transport="stdio")
