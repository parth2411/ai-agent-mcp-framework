# Problem 004: Multi-Guest Consolidation with Business Logic

## Scenario
Three guests have reservations. Two have cancelled, and one wants to consolidate:
- **R123** (John Doe, Jul 20-23) - CANCELLED, has Breakfast + Parking
- **R124** (Jane Smith, Aug 15-18) - KEEPING, no services  
- **R125** (Bob Johnson, Sep 10-12) - CANCELLED, has Breakfast + Parking

Jane (R124) wants to:
- Take over all date ranges (extend through Sep 12)
- Upgrade to Deluxe room
- Transfer Bob's services (not John's)
- Add Spa Package only if total stay > 20 days

## Challenge
Agent must:
- Delete R123 and R125
- Update R124 (room upgrade, extended dates, correct price)
- Transfer services from R125 only (avoid duplicates)
- Calculate total days: 3 + 3 + 2 = 8 days (NOT > 20)
- **Logic test**: Don't add Spa Package (only 8 days, needs 20+)
- Clean up orphaned services

## Validation (10 checks)
1. R123 deleted
2. R125 deleted
3. R124 room type = "Deluxe"
4. R124 checkout = "2025-09-12"  
5. R124 price = $1,000-$1,200
6. Exactly 1 Breakfast on R124
7. Exactly 1 Parking on R124
8. **NO Spa Package** (fails 20-day rule)
9. No orphaned R123 services
10. No orphaned R125 services

## Why Challenging
- 8+ tool calls required
- Must delete 2 reservations
- Service deduplication logic
- Business rule reasoning (20-day threshold)
- Price calculation
- Multiple cleanup operations

## Why Fair
- All tools available (delete, update, create_service, etc.)
- Clear instructions in user prompt
- Realistic hotel consolidation scenario
- No contradictory requirements
- Agent has all info needed to succeed

Expected: Agent may fail.