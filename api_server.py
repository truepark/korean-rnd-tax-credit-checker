from __future__ import annotations

import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from rnd_tax_checker.rnd_or_kr import lookup_rnd_lab

app = FastAPI(
    title="Korean R&D Tax Credit Checker API",
    version="0.3.1",
    description="사업자등록번호로 rnd.or.kr 기업부설연구소/연구개발전담부서 등록 여부를 조회합니다.",
)


class RndLabRequest(BaseModel):
    business_number: str = Field(..., description="10자리 또는 하이픈 포함 사업자등록번호")


def _authorize(x_api_key: str | None) -> None:
    expected = os.getenv("API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "korean-rnd-tax-credit-checker"}


@app.get("/search-rnd-lab/{business_number}")
def search_rnd_lab_get(
    business_number: str,
    x_api_key: str | None = Header(default=None),
) -> dict:
    _authorize(x_api_key)
    return lookup_rnd_lab(business_number, headless=True).to_dict()


@app.post("/search-rnd-lab")
def search_rnd_lab_post(
    payload: RndLabRequest,
    x_api_key: str | None = Header(default=None),
) -> dict:
    _authorize(x_api_key)
    return lookup_rnd_lab(payload.business_number, headless=True).to_dict()
