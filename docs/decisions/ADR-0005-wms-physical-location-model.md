# ADR-0005: WMS Physical Location Model

## Status

Accepted

## Decision

Use one hierarchical `WMS Location` Tree DocType for physical warehouse locations. Do not create separate Zone, Aisle, Rack, Shelf, or Bin DocTypes.

The hierarchy uses Frappe's standard Tree and Nested Set mechanisms. Location types remain flexible so a warehouse may use `Warehouse → Bin`, `Warehouse → Zone → Bin`, or a deeper layout.

## ERPNext Boundary

An ERPNext Warehouse remains the official stock and accounting dimension. A root WMS Location of type `Warehouse` links to exactly one ERPNext Warehouse; child locations inherit that warehouse context.

Physical locations are not represented as separate ERPNext stock warehouses by default because:

- ERPNext Warehouse owns the official inventory and accounting identity.
- Physical storage locations are an operational WMS concern.
- Additional ERPNext warehouses would create unnecessary stock and accounting dimensions.
- WMS needs flexible physical layouts without changing ERPNext stock semantics.

ERPNext itself supports detailed warehouse trees. WMS deliberately keeps the official ERPNext Warehouse identity separate from its physical location model to preserve a clean inventory and accounting boundary.

## Consequences

- WMS can describe physical layouts without creating a competing stock ledger.
- Future workflows can reference one stable physical-location DocType.
- Location records contain no stock quantity, valuation, reservation, or ledger fields.
