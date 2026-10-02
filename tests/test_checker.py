from rnd_tax_checker.checker import check_company


def test_ksic_and_kolas_possible():
    result = check_company(
        "105-82-11278",
        "테스트기관",
        {
            "ksic": {"code": "72919", "name": "기타 기술 시험, 검사 및 분석업"},
            "kolas": {"status": "confirmed", "scope": ["자동차 부품 시험"]},
        },
    )
    assert result["business_number"] == "1058211278"
    assert result["verdict"] == "POSSIBLE"


def test_invalid_business_number():
    try:
        check_company("123")
        assert False
    except ValueError:
        assert True
