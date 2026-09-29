# Project Status

Updated: 2026-09-29 10:30 WIB

## Current Phase

**Foundation complete; Phase 1 (Master Data) and Phase 2.5 (Wood Pellet Bagging) partially implemented**

## Completed

- Business requirements collected
- Architecture direction decided (ADR-0001 to ADR-0007)
- ERPNext system-of-record decision confirmed
- Frappe v16 application scaffold created and installed on the working site
- Project documentation structure created
- Foundation validation passed (see [testing/foundation-validation.md](testing/foundation-validation.md))

## Implemented (code written and merged to `main`)

| Component | Notes |
|---|---|
| WMS Location (Tree DocType) | Physical location hierarchy, no stock fields (ADR-0005). List View is the default view; New from list opens the full form |
| WMS Location State | 5 states: Kosong, Isi, Rusak, Hilang, Terjual (bilingual) |
| Inventory Dimension `WMS Location` | Created by an idempotent patch (`setup_inventory_dimension`), per ADR-0006 |
| Big Bag as ERPNext Item + Serial No | RFID and QR fields on Serial No (ADR-0007) |
| WMS Bag Fill Log | Staged scanning through a Scan Station inside the form (QR/RFID per stage); posts native ERPNext Stock Entries |
| WMS Weighbridge Ticket + bag child table | Manual entry, reference document only, does not affect stock (ADR-0007) |
| Dashboard and Number Cards | Fill Log / Weighbridge status cards and 4 "Bag per Lokasi" cards |
| Fixtures | Role `WMS Warehouse Manager`, Location State; Custom Field fixture filtered by `module=WMS` |

Manually confirmed working on the working site (per session records): Number Cards, Location Tree dialog (Warehouse type), migrate, and the Inventory Dimension patch.

Not verified: Scan Station on a real phone or RFID reader, and New Tree View dialog for Zone/Aisle/Rack/Shelf/Bin.

## Data Cleanup (2026-09-29)

All test data was removed from the working site `erp.ciptamebel.co.id`: test companies, test items, stock transactions (Stock Entry, Stock Ledger Entry, GL Entry, Bin, Serial No, Serial and Batch Bundle), Repost Item Valuation queue, test users and roles. Some phases used raw SQL and forced `docstatus=2` on test-only documents.

Remaining after cleanup: company `Cipta Mebelindo Lestari` (220 accounts, 3 warehouses), WMS Location and WMS Location State records, the Inventory Dimension, Custom Fields.

Clean-state backup: `20260929_072949` (site timezone Asia/Kolkata).

Lessons recorded:
- `bench run-tests` on the working site recreates fixture data. Use a separate test site.
- ERPNext refuses to delete a warehouse that ever had a Stock Ledger Entry, even a cancelled one.

## Not Implemented Yet

### Designed (documented, no code)
- Receiving, Putaway, Transfer, Picking, Packing, Stock Count, Adjustment workflows
- POS / Kiosk workflow
- Offline synchronization architecture (Phase 7)

### Planned (not yet designed)
- Mobile UI (there is no dedicated scan page; scanning lives in the Bag Fill Log form)
- RFID hardware integration
- Filled Bag to Container loading, damage/write-off flow, weight-mismatch approval flow
- RFID-based location verification report
- Advanced manufacturing integration

### Status Legend

- **Designed**: Conceptual design documented, not implemented
- **Planned**: Intended for future phase, not yet designed
- **Implemented**: Code written, not necessarily tested in a Bench
- **Tested**: Code tested, not production-ready
- **Production Ready**: Deployed and operational

## Open Items

1. Site timezone reads as Asia/Kolkata in code and System Settings; clarify the intended setting.
2. ADR-0006 runtime validation is still partial; see the ADR for the per-row status.
3. Set up a separate test site before further automated testing.
4. Verify Scan Station on the real device (phone or RFID reader) before production use.

## Next Steps

1. Continue Phase 2.5: Filled Bag to Container loading and the damage/write-off flow.
2. Then Phase 1 remainder and Phase 2/3 workflows (Receiving first).
