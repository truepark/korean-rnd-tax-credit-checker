from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from rnd_tax_checker.rnd_or_kr import lookup_rnd_lab

PORT = int(os.getenv("PORT", "10000"))

mcp = FastMCP(
    "korean-rnd-tax-credit-checker",
    host="0.0.0.0",
    port=PORT,
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def search_rnd_lab(business_number: str) -> dict:
    """사업자번호로 rnd.or.kr 기업부설연구소/연구개발전담부서 등록 여부를 공식 조회한다.

    사용자가 하이픈을 포함해 입력해도 내부에서 숫자 10자리로 정규화한다.
    POST 직접조회가 우선이며, 필요 시 브라우저 자동화 fallback을 사용한다.
    """
    return lookup_rnd_lab(business_number, headless=True).to_dict()


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    return JSONResponse({"ok": True, "service": "korean-rnd-tax-credit-checker-mcp"})


@mcp.custom_route("/search-rnd-lab/{business_number}", methods=["GET"])
async def search_rnd_lab_http(request: Request) -> JSONResponse:
    business_number = request.path_params["business_number"]
    result = lookup_rnd_lab(business_number, headless=True).to_dict()
    return JSONResponse(result)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
