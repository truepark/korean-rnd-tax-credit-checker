#!/usr/bin/env python
import argparse
import json

from rnd_tax_checker.rnd_or_kr import lookup_rnd_lab


def main() -> int:
    parser = argparse.ArgumentParser(description="rnd.or.kr 기업부설연구소/전담부서 사업자번호 조회")
    parser.add_argument("business_number", help="사업자등록번호 10자리 또는 하이픈 포함 형식")
    parser.add_argument("--show-browser", action="store_true", help="브라우저 창을 표시해서 실행")
    args = parser.parse_args()

    result = lookup_rnd_lab(args.business_number, headless=not args.show_browser)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.status in {"confirmed", "zero_results"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
