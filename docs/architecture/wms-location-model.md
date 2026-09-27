# WMS Physical Location Model

## Purpose

`WMS Location` models the physical location hierarchy used by warehouse operations. It provides flexible Warehouse, Zone, Aisle, Rack, Shelf, and Bin levels without requiring every site to use every level.

## ERPNext Warehouse vs WMS Location

- **ERPNext Warehouse** is the official inventory and accounting warehouse.
- **WMS Location** is the physical storage location inside that warehouse.

WMS Location does not own authoritative stock balances, valuation, or the ERPNext Stock Ledger.

## Physical Location Hierarchy

```text
Warehouse
  → Zone
    → Aisle
      → Rack
        → Shelf
          → Bin
```

The tree is intentionally flexible. For example, `Warehouse → Bin` and `Warehouse → Zone → Bin` are both valid layouts.

## Non-Location Stock States

In addition to physical storage locations, WMS supports logical stock states that represent the operational status of inventory. These are implemented as special `WMS Location` records with `location_type = "State"`.

### Supported States

- **Receiving**: Items that have arrived at the warehouse but have not yet been put away into a physical bin.
- **Quarantine**: Items held for quality inspection or other hold reasons.
- **Transit**: Items moving between locations or warehouses.
- **Damaged**: Items that are damaged and require disposition.
- **Packing**: Items being prepared for shipment.
- **Staging**: Items gathered for outbound loading.

### State Location Design

State locations are structurally distinct from physical locations:

1. **Structure**: State locations are root-level records that link directly to an ERPNext Warehouse. They do not participate in the physical location tree (no parent_location).
2. **Uniqueness**: Each state name (e.g., "Receiving") is unique per warehouse. You cannot have two "Receiving" state locations for the same warehouse.
3. **Usage**: State locations are used when items cannot be assigned to a physical bin yet, or when the physical location is not the primary concern for the current operation.
4. **Example Workflow**: A receiving dock receives items and places them in the "Receiving" state location. During putaway, items are transferred from "Receiving" to their assigned physical bin location.

### Implementation Notes

- State locations use the same `WMS Location` DocType and Inventory Dimension field as physical locations.
- The `state_name` field specifies which state the location represents.
- State locations are validated to ensure they have no parent in the physical tree and that they link to a valid ERPNext Warehouse.
- When configured as an Inventory Dimension, both physical bins and state locations populate the same dimension field, allowing unified reporting across all location types.
