# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial Frappe v16 application scaffold
- Project documentation structure
- Architecture decision records
- Business and functional requirements
- Deployment documentation
- Workflow documentation templates
- ADR-0007: Wood pellet bagging and weighbridge boundary
- Phase 2.5 (Wood Pellet Bagging & Weighbridge) added to roadmap
- WMS Bag Fill Log with staged Scan Station (QR/RFID)
- WMS Location State (Kosong, Isi, Rusak, Hilang, Terjual)
- Dashboard and Number Cards, including 4 "Bag per Lokasi" cards
- Location Tree JS (ERPNext Warehouse and State Name fields in the New dialog)
- Patch `setup_inventory_dimension` (idempotent) creating the `WMS Location` Inventory Dimension
- Fixtures: role `WMS Warehouse Manager`, WMS Location State
- ADR-0008 (Proposed): Jumbo Bag location via ERPNext Warehouse, superseding ADR-0005 and ADR-0006
- WMS Bag Transfer (branch `feat/wms-bag-transfer`, not yet merged; automated tests not yet run)

### Changed
- WMS Location: `quick_entry` disabled, default view is List
- `hooks.py`: Custom Field fixture filter narrowed with `module=WMS`
- ADR-0006: hasil validasi runtime parsial (Frappe 16.35.0 / ERPNext 16.36.0)
- ADR-0007: addendum desain Bag Fill Log (Material Transfer, pellet keluar di weighbridge)
- Consolidated root-level status/roadmap/changelog/security docs into `docs/`
- Merged physical stock location architecture and its runtime validation report into ADR-0006
- PROJECT_STATUS and ROADMAP updated to match implemented components
- ADR-0008 (2026-09-30): added test result P1 (one Stock Entry row per bag preserves per-Serial No valuation, no GL from transfer), decision 10 (one row per bag; Stock Reconciliation must not be used for bags), and deferral of cost/GL design

### Known Issues
- Bag Transfer is not yet listed in the WMS workspace sidebar (`wms/wms/workspace_sidebar/wms/wms.json` still lists Location, Location State, Bag Fill Log).
- Dashboard "Bag per Lokasi" cards query a column that does not exist on the test site; a fix is prepared on a separate branch and not yet merged.
- Manual confirmation method has no UI path; it is reachable only through the server method `confirm_receipt`.

### Operations
- 2026-09-29: all test data removed from the working site (test companies, items, stock transactions, test users and roles, test locations PLTB and CMR). Clean-state backup taken (`20260929_072949`). `bench run-tests` must not be run on the working site.
- 2026-09-29: timezone check found System Settings at Asia/Kolkata while user time zones are Asia/Jakarta. Target is Asia/Jakarta; change pending.
- 2026-09-29: RFID handheld plan recorded (smartphone-connected reader, APK not yet built).
- 2026-09-30: Bag Transfer verification runs only on the disposable site `test.local`; production is untouched. Do not run `bench migrate` on production before the WMS Location removal patch is ready.
