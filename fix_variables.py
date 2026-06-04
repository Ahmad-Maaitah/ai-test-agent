#!/usr/bin/env python3
"""
Fix variables that don't have API IDs assigned.
This tool will help you assign API IDs to existing variables.
"""

import json
import sys

def main():
    # Load data
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    variables = data.get('variables', [])
    apis = data.get('apis', [])

    print("=" * 60)
    print("VARIABLE FIX TOOL")
    print("=" * 60)
    print()

    # Show current state
    print(f"Total APIs: {len(apis)}")
    print(f"Total Variables: {len(variables)}")
    print()

    if len(apis) == 0:
        print("⚠️  NO SAVED APIs FOUND!")
        print()
        print("You need to SAVE your APIs first:")
        print("1. Open Create API page")
        print("2. Enter API name and curl")
        print("3. Add variables")
        print("4. Click 'Save API' button")
        print()
        print("After saving APIs, run this script again to assign API IDs to variables.")
        return

    # Show APIs
    print("Available APIs:")
    for i, api in enumerate(apis, 1):
        print(f"  {i}. {api.get('name')} (ID: {api.get('id')})")
    print()

    # Show variables without API ID
    vars_without_id = [v for v in variables if not v.get('source', {}).get('apiId')]

    if len(vars_without_id) == 0:
        print("✅ All variables have API IDs assigned!")
        return

    print(f"Variables WITHOUT API ID: {len(vars_without_id)}")
    print()

    # Ask user to assign API IDs
    for var in vars_without_id:
        print(f"Variable: {var.get('name')}")
        print(f"  Current value: {var.get('value')}")
        print(f"  Field path: {var.get('source', {}).get('fieldPath', 'N/A')}")
        print()
        print("Which API does this variable belong to?")
        for i, api in enumerate(apis, 1):
            print(f"  {i}. {api.get('name')}")
        print(f"  0. Skip this variable")
        print()

        choice = input("Enter number: ").strip()

        if choice == '0':
            print("Skipped.")
            print()
            continue

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(apis):
                api = apis[idx]
                # Assign API ID
                if 'source' not in var:
                    var['source'] = {}
                var['source']['apiId'] = api.get('id')
                var['source']['apiName'] = api.get('name')
                print(f"✅ Assigned to API: {api.get('name')}")
            else:
                print("Invalid choice. Skipped.")
        except ValueError:
            print("Invalid input. Skipped.")

        print()

    # Save data
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print("✅ DONE! Variables updated.")
    print("=" * 60)

if __name__ == '__main__':
    main()
