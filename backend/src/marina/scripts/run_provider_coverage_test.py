"""CLI Runner for Football Data Provider Coverage Testing Suite.

Executes the 5-match Chennaiyin FC 2026–27 coverage test across API-Football,
Sportmonks, FBref, and Manual CSV, validating against ground truth.
"""

import asyncio
import json
import os
import sys

# Ensure backend/src is in python path
sys.path.insert(0, os.path.abspath("backend/src"))

from marina.ingestion.providers.coverage_tester import ProviderCoverageTester


async def main():
    tester = ProviderCoverageTester()
    report = await tester.execute_full_coverage_suite()

    print("=" * 80)
    print("MARINA INTELLIGENCE — STAGE 1: PROVIDER COVERAGE TEST REPORT")
    print("=" * 80)
    print(f"Tested Fixtures ({report['fixture_count']}): {', '.join(report['tested_fixtures'])}")
    print(f"Providers Tested ({len(report['providers_evaluated'])}): {', '.join(report['providers_evaluated'])}")
    print("-" * 80)

    for prov_code, res in report["provider_results"].items():
        print(f"\n[PROVIDER] {res['provider_name']} ({prov_code})")
        print(f"  Effective Coverage Rate (Supported Tier): {res['effective_coverage_pct']}%")
        print(f"  Validations: {res['passed_validations']} Passed | {res['warned_validations']} Warned | {res['failed_validations']} Failed")
        print(f"  Unsupported Advanced Metrics (Spatial/xG): {res['unsupported_metrics']} (Safely set to NULL)")

        # Print Match-by-match breakdown
        for m in res["matches"]:
            s = m.get_summary()
            print(f"    - Match #{m.match_number} ({m.date}: {m.home_team} vs {m.away_team}): {s['passed']}/{s['total_metrics']} passed ({s['coverage_pct']}%)")

    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED SUCCESSFULLY.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
