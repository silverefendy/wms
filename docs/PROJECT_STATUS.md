# Project Status

Updated: 2026-09-29 09:30 WIB

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

All test data was removed from the working site `erp.ciptamebel.co.id`: test companies, test items, stock transactions (Stock Entry, Stock Ledger Entry, GL Entry, Bin, Serial No, Serial and Batch Bundle), Repost Item Valuation queue, test users and roles, and the test locations PLTB and CMR. Some phases used raw SQL and forced `docstatus=2` on test-only documents.

Remaining after cleanup: company `Cipta Mebelindo Lestari` (220 accounts, 3 warehouses: `All Warehouses - CML`, `Stores - CML`, `Wood Pellet - CML`), 5 WMS Location records of type State (WP-KOSONG, WP-ISI, WP-RUSAK, WP-HILANG, WP-TERJUAL), 5 WMS Location State records, the Inventory Dimension, Custom Fields. Users: Administrator, Guest, `support@ciptamebel.co.id`.

Clean-state backup: `20260929_072949` (file names use the site timezone, currently Asia/Kolkata). It was taken before PLTB and CMR were deleted.

Lessons recorded:
- `bench run-tests` on the working site recreates fixture data. Use a separate test site.
- ERPNext refuses to delete a warehouse that ever had a Stock Ledger Entry, even a cancelled one.
- A parent Company can only be deleted after its child companies are gone.
- `Repost Item Valuation` documents block deletion of an Item and cannot be cancelled while cancelled-document processing is pending.

## Timezone

Checked 2026-09-29 09:22 WIB:

| Setting | Value |
|---|---|
| System Settings time zone | Asia/Kolkata |
| User time zone (Administrator, Guest, support@) | Asia/Jakarta |
| Server / MariaDB clock | UTC (`SYSTEM`) |

Decision: the site should use **Asia/Jakarta**. The System Settings value has not been changed yet, so stored `creation` timestamps are still in Asia/Kolkata (1 h 30 min ahead of WIB). Change it in System Settings, then run `bench restart`.

## Not Implemented Yet

### Designed (documented, no code)
- Receiving, Putaway, Transfer, Picking, Packing, Stock Count, Adjustment workflows
- POS / Kiosk workflow
- Offline synchronization architecture (Phase 7)

### Planned (not yet designed)
- Mobile UI and Android app (APK). There is no dedicated scan page; scanning lives in the Bag Fill Log form
- RFID hardware integration (see plan below)
- Filled Bag to Container loading, damage/write-off flow, weight-mismatch approval flow
- RFID-based location verification report
- Advanced manufacturing integration

### RFID handheld plan (2026-09-29)

The Scan Station will later be used with an RFID handheld reader connected to a smartphone. The APK does not exist yet. Reader model and output mode are not yet known. If the reader has a keyboard (HID) mode, the Scan Station can be used in the phone browser without an APK, provided the typed tag value matches the RFID field on Serial No. If the reader only works through a vendor SDK, an intermediary app is needed and this becomes Phase 6 work with its own ADR.

### Status Legend

- **Designed**: Conceptual design documented, not implemented
- **Planned**: Intended for future phase, not yet designed
- **Implemented**: Code written, not necessarily tested in a Bench
- **Tested**: Code tested, not production-ready
- **Production Ready**: Deployed and operational

## Open Items

1. Change the System Settings time zone to Asia/Jakarta and restart the bench.
2. Identify the RFID handheld model and whether it has a keyboard (HID) mode.
3. Verify Scan Station on the real device (phone plus RFID reader) before production use.
4. ADR-0006 runtime validation is still partial; see the ADR for the per-row status.
5. Set up a separate test site before further automated testing (deferred by decision).
6. Confirm the New Tree View dialog for Zone, Aisle, Rack, Shelf and Bin.

## Next Steps

1. Continue Phase 2.5: Filled Bag to Container loading and the damage/write-off flow.
2. Then Phase 1 remainder and Phase 2/3 workflows (Receiving first).
