#!/usr/bin/env python3
"""
Validator for problems/003

Checks that:
- Reservation R123 exists
- Services "Breakfast" and "Parking" are attached to reservation R123
"""
import json
import sys
from pathlib import Path

def load_json_array(path):
    if not path.exists():
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_result.py <data_directory>", file=sys.stderr)
        sys.exit(1)

    data_dir = Path(sys.argv[1])

    if not data_dir.exists():
        print(f"Error: Data directory '{data_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    reservations = load_json_array(data_dir / "reservations.json")
    services = load_json_array(data_dir / "services.json")

    results = []

    # Check reservation R123 exists
    r123 = next((r for r in reservations if r.get('id') == 'R123'), None)
    if r123 is None:
        results.append({
            "name": "reservation_R123_exists",
            "passed": False,
            "comment": "Reservation R123 not found"
        })
    else:
        results.append({
            "name": "reservation_R123_exists",
            "passed": True,
            "comment": ""
        })

    # Find services attached to R123
    services_r123 = [s for s in services if s.get('reservation_id') == 'R123']

    # Helper to find service by name (case-insensitive substring match)
    def has_service_named(target):
        target = target.lower()
        for s in services_r123:
            name = (s.get('name') or "").lower()
            category = (s.get('category') or "").lower()
            if target in name or target in category:
                return True
        return False

    breakfast_ok = has_service_named("breakfast")
    parking_ok = has_service_named("parking")

    if breakfast_ok:
        results.append({
            "name": "breakfast_added_to_R123",
            "passed": True,
            "comment": ""
        })
    else:
        results.append({
            "name": "breakfast_added_to_R123",
            "passed": False,
            "comment": f"Breakfast service not found for R123. Services found: {[s.get('name') for s in services_r123]}"
        })

    if parking_ok:
        results.append({
            "name": "parking_added_to_R123",
            "passed": True,
            "comment": ""
        })
    else:
        results.append({
            "name": "parking_added_to_R123",
            "passed": False,
            "comment": f"Parking service not found for R123. Services found: {[s.get('name') for s in services_r123]}"
        })

    # Write results.json
    try:
        with open(data_dir / "results.json", "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {data_dir / 'results.json'}")
    except Exception as e:
        print(f"Error writing results.json: {e}", file=sys.stderr)
        sys.exit(1)

    # Print summary and exit code
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    print(f"Tests passed: {passed_count}/{total_count}")
    if passed_count == total_count:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed:")
        for result in results:
            if not result['passed']:
                print(f"  - {result['name']}: {result['comment']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
