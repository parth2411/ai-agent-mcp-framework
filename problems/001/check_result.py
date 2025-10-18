#!/usr/bin/env python3
"""
Script to check reservation data and generate test results.
Takes a data directory as positional argument and validates reservations.json.
"""

import json
import sys
import os
from pathlib import Path


def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python check_result.py <data_directory>", file=sys.stderr)
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    
    # Check if data directory exists
    if not data_dir.exists():
        print(f"Error: Data directory '{data_dir}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Path to reservations.json
    reservations_file = data_dir / "reservations.json"
    
    # Check if reservations.json exists - exit if not found
    if not reservations_file.exists():
        print(f"Error: reservations.json not found in '{data_dir}'", file=sys.stderr)
        sys.exit(1)
    
    results = []
    
    try:
        # Read and parse reservations.json
        with open(reservations_file, 'r') as f:
            reservations = json.load(f)
        
        # Find reservation RES001
        res001 = None
        for reservation in reservations:
            if reservation.get('id') == 'RES001':
                res001 = reservation
                break
        
        # Check if RES001 exists
        if res001 is None:
            results.append({
                "name": "reservation_RES001_exists",
                "passed": False,
                "comment": "Reservation RES001 not found"
            })
            results.append({
                "name": "guest_name_correct",
                "passed": False,
                "comment": "Cannot check guest name - reservation RES001 not found"
            })
        else:
            results.append({
                "name": "reservation_RES001_exists",
                "passed": True,
                "comment": ""
            })
            
            # Check guest name
            guest_name = res001.get('guest_name')
            if guest_name == 'John Smith':
                results.append({
                    "name": "guest_name_correct",
                    "passed": True,
                    "comment": ""
                })
            else:
                results.append({
                    "name": "guest_name_correct",
                    "passed": False,
                    "comment": f"Expected 'John Smith', got '{guest_name}'"
                })
    
    except json.JSONDecodeError as e:
        results.append({
            "name": "reservation_RES001_exists",
            "passed": False,
            "comment": f"Invalid JSON format: {e}"
        })
        results.append({
            "name": "guest_name_correct",
            "passed": False,
            "comment": "Cannot check guest name - invalid JSON"
        })
    except Exception as e:
        results.append({
            "name": "reservation_RES001_exists",
            "passed": False,
            "comment": f"Error reading file: {e}"
        })
        results.append({
            "name": "guest_name_correct",
            "passed": False,
            "comment": "Cannot check guest name - error reading file"
        })
    
    # Write results.json
    results_file = data_dir / "results.json"
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {results_file}")
        
        # Print summary
        passed_count = sum(1 for r in results if r['passed'])
        total_count = len(results)
        print(f"Tests passed: {passed_count}/{total_count}")
        
        if passed_count == total_count:
            print("All tests passed!")
        else:
            print("Some tests failed:")
            for result in results:
                if not result['passed']:
                    print(f"  - {result['name']}: {result['comment']}")
    
    except Exception as e:
        print(f"Error writing results.json: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 