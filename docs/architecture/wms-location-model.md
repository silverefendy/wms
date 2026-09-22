# WMS Physical Location Model

## Purpose

`WMS Location` models the physical location hierarchy used by warehouse operations. It provides flexible Warehouse, Zone, Aisle, Rack, Shelf, and Bin levels without requiring every site to use every level.

## ERPNext Warehouse vs WMS Location

- **ERPNext Warehouse** is the official inventory and accounting warehouse.
- **WMS Location** is the physical storage location inside that warehouse.

WMS Location does not own authoritative stock balances, valuation, or the ERPNext Stock Ledger.

## Hierarchy

```text
Warehouse
  → Zone
    → Aisle
      → Rack
        → Shelf
          → Bin
```

The tree is intentionally flexible. For example, `Warehouse → Bin` and `Warehouse → Zone → Bin` are both valid layouts.
