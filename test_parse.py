#!/usr/bin/env python3
"""Test curl parsing with multiline JSON."""

from backend.utils import parse_curl

# Your exact curl command
curl = """curl --location 'https://sooqtest.com/api/taxonomy-api/v10?Action_screen_name=search&abBucket=7&campaign=direct_app_open&source=opensooq&medium=none' \\
--header 'User-Agent: OpenSooq/439/v2.1/7 (Android-10/Google,Android SDK built for x86)' \\
--header 'Accept: application/json' \\
--header 'Content-Type: application/json' \\
--header 'country: jo' \\
--data '{
  "page": 1,
  "per_page": 20,
  "sort_code": "latest",
  "selected_cell_type": "all",
  "member_ids": [],
  "search_type": "dlp-X9AYOu1-275756992",
  "filters": {
    "status": "active",
    "date_from": null,
    "date_to": null
  },
  "include": {
    "pagination": true,
    "total_count": true
  }
}'"""

print("=" * 80)
print("Testing cURL parsing...")
print("=" * 80)

try:
    parsed = parse_curl(curl)

    print(f"\nURL: {parsed['url']}")
    print(f"Method: {parsed['method']}")
    print(f"Headers count: {len(parsed['headers'])}")
    print(f"\nData present: {bool(parsed['data'])}")

    if parsed['data']:
        print(f"Data length: {len(parsed['data'])} chars")
        print(f"\nData content (first 200 chars):")
        print(parsed['data'][:200])
    else:
        print("\n⚠️  ERROR: No data was parsed!")

    print("\n" + "=" * 80)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
