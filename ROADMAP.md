# Roadmap

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

**Status**: Not Started

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

**Status**: Not Started

See [ADR-0007](decisions/ADR-0007-wood-pellet-bagging-and-weighbridge.md) for
the accepted design (Big Bag as serialized ERPNext Item; Weighbridge Ticket as
a manual-entry reference document).

- [ ] Big Bag Item + Serial No setup (RFID + QR fields)
- [ ] Empty Bag → Filled Bag workflow (Stock Entry - Manufacture)
- [ ] Filled Bag → Empty Bag reverse workflow (reuse cycle)
- [ ] Big Bag damage / write-off exception flow
- [ ] Big Bag sold-with-shipment flow (own line item on Delivery Note/Sales Invoice)
- [ ] Filled Bag → Container loading workflow (Material Transfer / Delivery Note)
- [ ] WMS Weighbridge Ticket DocType (manual entry; bag/RFID child table; link to Delivery Note)
- [ ] Weight/quantity mismatch exception + approval flow
- [ ] Periodic RFID-based location verification report (WMS Location vs. last scan)
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
