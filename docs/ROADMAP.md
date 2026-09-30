# Roadmap

Updated: 2026-09-30 12:50 WIB

## Phase 0 — Foundation

**Status**: Complete

- [x] Frappe v16 target selection
- [x] ERPNext v16 target selection
- [x] WMS app scaffold
- [x] Git repository initialization
- [x] Documentation structure
- [ ] Development environment setup
- [ ] Staging environment setup
- [ ] Production architecture design
- [ ] Backup strategy definition

## Phase 1 — Master Data Integration

**Status**: In Progress

> Update 2026-09-29: WMS Location Tree, WMS Location State and the Inventory Dimension `WMS Location` are implemented. Location-type coverage in the New dialog is confirmed only for Warehouse; Zone to Bin are not yet verified, so the items below stay unchecked.

> Update 2026-09-30: ADR-0008 (Proposed) replaces the WMS Location / Inventory Dimension approach for Jumbo Bag with ERPNext Warehouse per stage. WMS Location, WMS Location State and the Inventory Dimension are to be removed only after ADR-0008 is accepted (see its removal order). Zone to Bin items below will be handled in ERPNext if needed.

- [ ] Item integration with ERPNext
- [ ] Item Variant integration
- [ ] UOM configuration
- [ ] Barcode support
- [ ] Serial number support
- [ ] Batch/lot support
- [ ] Warehouse configuration
- [ ] Zone configuration
- [ ] Aisle configuration
- [ ] Rack configuration
- [ ] Shelf configuration
- [ ] Bin configuration

## Phase 2 — Core Warehouse

**Status**: Not Started

- [ ] Receive workflow
- [ ] Putaway workflow
- [ ] Transfer workflow
- [ ] Issue workflow
- [ ] Return workflow
- [ ] Stock Count workflow
- [ ] Adjustment workflow

## Phase 2.5 — Wood Pellet Bagging & Weighbridge

**Status**: In Progress

See [ADR-0007](decisions/ADR-0007-wood-pellet-bagging-and-weighbridge.md) for
the accepted design (Big Bag as serialized ERPNext Item; Weighbridge Ticket as
a manual-entry reference document) and
[ADR-0008](decisions/ADR-0008-jumbo-bag-location-via-erpnext-warehouse.md)
(Proposed) for the Warehouse-per-stage model and WMS Bag Transfer.

> Update 2026-09-28: alur isi bag kini Material Transfer antar State (lihat addendum ADR-0007), bukan Manufacture. Item bertanda Manufacture di bawah perlu dibaca sesuai addendum.

> Update 2026-09-29: WMS Bag Fill Log (Scan Station) dan WMS Location State sudah diimplementasikan dan di-merge ke `main`. Verifikasi di perangkat nyata (HP / RFID reader) belum dilakukan.

> Update 2026-09-30: WMS Bag Transfer (satu dokumen banyak bag, konfirmasi terima lewat scan) dan dashboard "Bag per Lokasi" berbasis `Serial No.warehouse` sudah di-merge ke `main`. Transfer terbukti di test.local (uji P1: satu baris Stock Entry per bag, nilai per Serial No terjaga, tanpa GL dari transfer). Uji browser dan tes otomatis belum dijalankan. Bag Fill Log direncanakan dipensiunkan setelah ADR-0008 diterima. Desain beban/GL ditunda.

- [x] Big Bag Item + Serial No setup (RFID + QR fields)
- [x] Empty Bag → Filled Bag workflow (implemented as WMS Bag Fill Log with staged scanning; see ADR-0007 addendum; to be retired per ADR-0008)
- [ ] Filled Bag → Empty Bag reverse workflow (reuse cycle)
- [ ] Big Bag damage / write-off exception flow
- [ ] Big Bag sold-with-shipment flow (own line item on Delivery Note/Sales Invoice)
- [ ] Filled Bag → Container loading workflow (Material Transfer / Delivery Note)
- [x] WMS Weighbridge Ticket DocType (manual entry; bag/RFID child table; link to Delivery Note)
- [ ] Weight/quantity mismatch exception + approval flow
- [ ] Periodic RFID-based location verification report (Serial No Warehouse vs. last scan)
- [x] Dashboard Number Cards (Bag per Lokasi from Serial No Warehouse, Fill Log and Weighbridge status)
- [x] WMS Bag Transfer DocType (implemented, merged to `main`; browser UI test and automated tests pending)
- [ ] Verify WMS Bag Transfer in browser (U1-U5, U9, U10) and run its automated tests on `test.local`
- [ ] Manual confirmation path for WMS Warehouse Manager (currently server method only, no UI)
- [ ] Add WMS Bag Transfer to workspace sidebar
- [ ] Accept ADR-0008, then remove WMS Location, WMS Location State, Inventory Dimension and Bag Fill Log (each destructive step needs explicit confirmation)
- [ ] (Deferred) Bag cost / GL design: cost account, per-cycle value split
- [ ] (Future, deferred) Integration with existing weighbridge application/hardware

## Phase 3 — Purchasing Integration

**Status**: Not Started

- [ ] Supplier integration
- [ ] Purchase Order integration
- [ ] Purchase Receipt integration
- [ ] Receiving workflow
- [ ] Quality Check workflow
- [ ] Putaway after receiving

## Phase 4 — Sales Integration

**Status**: Not Started

- [ ] Customer integration
- [ ] Sales Order integration
- [ ] Picking workflow
- [ ] Packing workflow
- [ ] Delivery integration
- [ ] Sales Invoice integration
- [ ] Return workflow

## Phase 5 — POS / Kiosk

**Status**: Not Started

- [ ] ERPNext POS integration
- [ ] Custom POS UI
- [ ] Barcode POS
- [ ] Touchscreen interface
- [ ] Receipt printing
- [ ] Discount approval workflow
- [ ] Returns processing

## Phase 6 — Mobile

**Status**: Not Started

> Update 2026-09-29: the Scan Station is planned to be used with an RFID handheld reader connected to a smartphone. The APK is not built yet. Reader model and output mode (keyboard/HID versus vendor SDK) are still unknown. With HID mode, the browser-based Scan Station may work without an APK; with SDK-only readers, an intermediary app and a new ADR are needed.

- [ ] Android/tablet support
- [ ] Mobile scanning
- [ ] Mobile receiving
- [ ] Mobile transfer
- [ ] Mobile stock count
- [ ] Mobile picking
- [ ] Mobile packing
- [ ] Mobile RFID scanning (big bag verification)

## Phase 7 — Offline

**Status**: Not Started

- [ ] Local transaction queue
- [ ] Synchronization engine
- [ ] Duplicate detection
- [ ] Conflict detection
- [ ] Conflict resolution
- [ ] Sync audit trail

## Phase 8 — Advanced

**Status**: Not Started

- [ ] RFID hardware integration
- [ ] Advanced putaway algorithms
- [ ] Stock reservation system
- [ ] Reorder automation
- [ ] Expiry / FEFO management
- [ ] Warehouse analytics
- [ ] Advanced manufacturing integration
- [ ] External APIs
- [ ] Marketplace/e-commerce integrations
