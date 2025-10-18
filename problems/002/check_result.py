#!/usr/bin/env python3
"""
Validator for problems/002

Checks that:
- No reservation has a check-in date in January
- No reservation for guest "John Smith" was created
"""

import json
import sys
from pathlib import Path
from datetime import date

def parse_date_safe(date_str):
    """Try to parse YYYY-MM-DD date string to a date object. Return None on failure."""
    try:
        return date.fromisoformat(date_str)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_result.py <data_directory>", file=sys.stderr)
        sys.exit(1)

    data_dir = Path(sys.argv[1])

    if not data_dir.exists():
        print(f"Error: Data directory '{data_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    reservations_file = data_dir / "reservations.json"
    if not reservations_file.exists():
        print(f"Error: reservations.json not found in '{data_dir}'", file=sys.stderr)
        sys.exit(1)

    results = []

    try:
        with open(reservations_file, 'r', encoding='utf-8') as f:
            reservations = json.load(f)
            if not isinstance(reservations, list):
                raise ValueError("reservations.json must contain a JSON array")
    except json.JSONDecodeError as e:
        results.append({
            "name": "no_reservations_in_january",
            "passed": False,
            "comment": f"Invalid JSON in reservations.json: {e}"
        })
        results.append({
            "name": "john_smith_reservation_not_created",
            "passed": False,
            "comment": f"Invalid JSON in reservations.json: {e}"
        })
        # write results and exit
        try:
            with open(data_dir / "results.json", "w", encoding='utf-8') as out:
                json.dump(results, out, indent=2)
        except Exception as e2:
            print(f"Error writing results.json: {e2}", file=sys.stderr)
            sys.exit(1)
        print("Invalid reservations.json; results written.")
        sys.exit(1)
    except Exception as e:
        results.append({
            "name": "no_reservations_in_january",
            "passed": False,
            "comment": f"Error reading reservations.json: {e}"
        })
        results.append({
            "name": "john_smith_reservation_not_created",
            "passed": False,
            "comment": f"Error reading reservations.json: {e}"
        })
        try:
            with open(data_dir / "results.json", "w", encoding='utf-8') as out:
                json.dump(results, out, indent=2)
        except Exception as e2:
            print(f"Error writing results.json: {e2}", file=sys.stderr)
            sys.exit(1)
        sys.exit(1)

    # Perform checks
    january_found = False
    john_smith_found = False
    problematic_entries = []

    for r in reservations:
        # check-in date
        cid = r.get("check_in_date")
        parsed = parse_date_safe(cid) if cid else None
        if parsed and parsed.month == 1:
            january_found = True
            problematic_entries.append(f"{r.get('id', '<no-id>')} check_in_date={cid}")

        # guest name
        guest = r.get("guest_name", "")
        if isinstance(guest, str) and guest.strip().lower() == "john smith":
            john_smith_found = True
            problematic_entries.append(f"{r.get('id', '<no-id>')} guest_name={guest}")

    if not january_found:
        results.append({
            "name": "no_reservations_in_january",
            "passed": True,
            "comment": ""
        })
    else:
        results.append({
            "name": "no_reservations_in_january",
            "passed": False,
            "comment": "Found reservation(s) with January check-in: " + "; ".join(problematic_entries)
        })

    if not john_smith_found:
        results.append({
            "name": "john_smith_reservation_not_created",
            "passed": True,
            "comment": ""
        })
    else:
        results.append({
            "name": "john_smith_reservation_not_created",
            "passed": False,
            "comment": "Found reservation(s) for John Smith: " + "; ".join(problematic_entries)
        })

    # Write results.json
    try:
        with open(data_dir / "results.json", "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {data_dir / 'results.json'}")
    except Exception as e:
        print(f"Error writing results.json: {e}", file=sys.stderr)
        sys.exit(1)

    # Print summary to stdout
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
