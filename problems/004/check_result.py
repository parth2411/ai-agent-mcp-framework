#!/usr/bin/env python3
"""
NIGHTMARE MODE Validator - Multi-Guest Consolidation with Logic Tests

This validator checks:
1-2. R123 and R125 deleted
3-5. R124 updated correctly (room, dates, price)
6-7. Exactly ONE Breakfast and ONE Parking (no duplicates)
8. NO Spa Package (fails 20-day business rule)
9-10. All orphaned services cleaned up
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

    # Check 1-2: Deletions
    r123 = next((r for r in reservations if r.get('id') == 'R123'), None)
    r125 = next((r for r in reservations if r.get('id') == 'R125'), None)
    
    results.append({
        "name": "R123_deleted",
        "passed": r123 is None,
        "comment": "" if r123 is None else "R123 should be deleted"
    })
    results.append({
        "name": "R125_deleted",
        "passed": r125 is None,
        "comment": "" if r125 is None else "R125 should be deleted"
    })

    # Check 3: R124 exists
    r124 = next((r for r in reservations if r.get('id') == 'R124'), None)
    if r124 is None:
        results.append({"name": "R124_exists", "passed": False, "comment": "R124 not found"})
        # Skip remaining checks
        for name in ["R124_room_deluxe", "R124_checkout_correct", "R124_price_valid",
                     "exactly_one_breakfast", "exactly_one_parking", "no_spa_package",
                     "no_R123_services", "no_R125_services"]:
            results.append({"name": name, "passed": False, "comment": "R124 not found"})
    else:
        results.append({"name": "R124_exists", "passed": True, "comment": ""})
        
        # Check 4: Room type
        room = (r124.get('room_type') or "").strip().lower()
        results.append({
            "name": "R124_room_deluxe",
            "passed": room == "deluxe",
            "comment": "" if room == "deluxe" else f"Expected 'Deluxe', got '{r124.get('room_type')}'"
        })
        
        # Check 5: Checkout date
        checkout = r124.get('check_out_date')
        results.append({
            "name": "R124_checkout_correct",
            "passed": checkout == "2025-09-12",
            "comment": "" if checkout == "2025-09-12" else f"Expected '2025-09-12', got '{checkout}'"
        })
        
        # Check 6: Price (should be ~$1,100 for 11 days * $100)
        try:
            price = float(r124.get('total_price', 0))
            valid = 1000 <= price <= 1200
        except:
            price = 0
            valid = False
        results.append({
            "name": "R124_price_valid",
            "passed": valid,
            "comment": "" if valid else f"Expected $1,000-$1,200 (11 days * $100), got ${price}"
        })
        
        # Get R124 services
        r124_services = [s for s in services if s.get('reservation_id') == 'R124']
        
        # Check 7: Exactly ONE Breakfast
        breakfast_count = sum(1 for s in r124_services 
                            if 'breakfast' in (s.get('name') or '').lower() or
                               'breakfast' in (s.get('category') or '').lower())
        results.append({
            "name": "exactly_one_breakfast",
            "passed": breakfast_count == 1,
            "comment": "" if breakfast_count == 1 else f"Expected 1 Breakfast, found {breakfast_count}"
        })
        
        # Check 8: Exactly ONE Parking
        parking_count = sum(1 for s in r124_services 
                          if 'parking' in (s.get('name') or '').lower() or
                             'parking' in (s.get('category') or '').lower())
        results.append({
            "name": "exactly_one_parking",
            "passed": parking_count == 1,
            "comment": "" if parking_count == 1 else f"Expected 1 Parking, found {parking_count}"
        })
        
        # Check 9: NO Spa Package (logic test - only 11 days, needs 20+)
        spa_count = sum(1 for s in r124_services 
                       if 'spa' in (s.get('name') or '').lower() or
                          'spa' in (s.get('category') or '').lower())
        results.append({
            "name": "no_spa_package",
            "passed": spa_count == 0,
            "comment": "" if spa_count == 0 else f"Spa should NOT be added (only 11 days, needs 20+). Found {spa_count}"
        })
        
        # Check 10-11: Cleanup
        r123_services = [s for s in services if s.get('reservation_id') == 'R123']
        r125_services = [s for s in services if s.get('reservation_id') == 'R125']
        
        results.append({
            "name": "no_R123_services",
            "passed": len(r123_services) == 0,
            "comment": "" if not r123_services else f"Found orphaned R123 services: {[s.get('name') for s in r123_services]}"
        })
        results.append({
            "name": "no_R125_services",
            "passed": len(r125_services) == 0,
            "comment": "" if not r125_services else f"Found orphaned R125 services: {[s.get('name') for s in r125_services]}"
        })

    # Write results
    try:
        with open(data_dir / "results.json", "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {data_dir / 'results.json'}")
    except Exception as e:
        print(f"Error writing results.json: {e}", file=sys.stderr)
        sys.exit(1)

    # Summary
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ NIGHTMARE MODE COMPLETE - Agent mastered complex business logic!")
        sys.exit(0)
    else:
        print("\n✗ Failed checks:")
        for r in results:
            if not r['passed']:
                print(f"  - {r['name']}: {r['comment']}")
        print(f"\nThis test requires reasoning about business rules and avoiding logical errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()