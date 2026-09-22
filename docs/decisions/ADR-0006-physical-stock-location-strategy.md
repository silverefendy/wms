# ADR-0006: Physical Stock Location Strategy

## Status

Accepted with runtime validation pending

## Context

WMS needs to locate physical stock inside an ERPNext Warehouse while ERPNext remains authoritative for stock quantity, valuation, accounting, and stock-affecting transactions. The existing WMS Location Tree models physical topology but intentionally contains no quantities or ledger fields.

ERPNext v16 provides Inventory Dimensions. The v16 implementation accepts a non-child reference DocType other than the built-in Warehouse, Item, Batch, and Serial No dimensions; adds dimension fields to applicable stock documents and Stock Ledger Entry/Stock Closing Balance; supports dimension-wise Stock Ledger/Stock Balance reporting; validates negative stock per dimension when enabled; and validates serial availability against the last inward dimension. It has important limits around general Stock Reconciliation and must be tested on the exact installed patch.

The exact runtime proof-of-concept against Frappe `16.34.0` / ERPNext `16.35.0` could not be executed in this workspace because no disposable Bench/site was available. The source-level decision is accepted, but runtime acceptance remains an explicit gate before production configuration.

## Decision

Use `WMS Location` as an ERPNext Inventory Dimension.

The dimension value represents the physical location of the stock row. ERPNext Warehouse remains the official stock/accounting warehouse. WMS will not create a physical-placement ledger or any competing stock quantity model.

All physical stock movements must eventually be represented by an appropriate native ERPNext stock transaction. A bin-to-bin move inside one warehouse is a same-warehouse Material Transfer with a source WMS Location and target WMS Location. Receipts, deliveries, purchase/sales stock-update flows, POS, and manufacturing must carry a location according to their supported v16 document fields.

The first implementation must use ERPNext stock UOM as the authoritative quantity basis. WMS may display alternate operational UOMs only after applying ERPNext’s conversion rules.

## Alternatives

### Option B — WMS Physical Placement Ledger

Rejected for official stock truth. It would duplicate quantity and movement state, require reconciliation for every ERPNext transaction and cancellation, and make serial, batch, UOM, valuation, and offline conflict handling substantially more complex. Future WMS workflow/audit records may exist, but they must not replace ERPNext Stock Ledger.

### Option C — ERPNext Sub-Warehouses

Rejected for ordinary bins. It would turn physical topology into ERPNext warehouse/accounting identity and make same-warehouse bin movements warehouse movements. It is suitable only when each physical node is intentionally an independent ERPNext stock warehouse.

### Hybrid quantity architecture

Rejected. A hybrid physical quantity ledger plus ERPNext Inventory Dimension would create two operational quantity authorities without a requirement that justifies the cost. The selected design uses one ERPNext stock truth and future WMS workflow state around it.

## Rationale

The selected option is the smallest architecture that satisfies the core requirement:

```text
ERPNext Warehouse stock
=
sum of valid WMS Location dimension balances
+ explicit non-location stock states
```

It preserves native stock movement, valuation, accounting, serial/batch controls, and standard reporting while allowing many physical locations under one ERPNext Warehouse. It also keeps the existing WMS boundary intact: WMS owns topology and operational workflows; ERPNext owns official stock.

## Consequences

### Positive

- No competing WMS stock ledger is introduced.
- Stock Ledger Entry and Stock Balance can carry and report the physical location dimension.
- Multiple bins can share one ERPNext Warehouse.
- Same-warehouse bin transfers do not require an accounting warehouse change.
- ERPNext stock UOM, valuation, serial, batch, cancellation, and document audit remain authoritative.

### Negative

- A location move must be posted through a supported ERPNext stock transaction.
- WMS cannot treat an offline local move as final official stock before ERPNext accepts it.
- Stock Reconciliation is not a general-purpose location-count engine.
- POS and batch reconciliation need exact-patch integration coverage.
- Customers must control or validate ERPNext stock transactions that bypass WMS location policy.

## Future impact

The next phase should configure the Inventory Dimension and build integration tests before building operational workflows. Later receiving, putaway, picking, counting, and offline features should orchestrate native ERPNext documents and maintain workflow/audit state without owning official stock quantity.

Explicit temporary stock states such as Receiving, Quarantine, Transit, Damaged, Packing, and Staging may be represented as controlled WMS Location values when they hold stock and participate in the invariant. This ADR does not create those states.

Future count design must compare the physical count with the dimension-wise ERPNext balance, obtain review/approval, and post a supported ERPNext adjustment. It must not update a WMS quantity table.

## Runtime validation status

See [Inventory Dimension runtime validation](../testing/inventory-dimension-validation.md). All transaction-level tests are currently `NOT RUN` because the disposable environment was unavailable; no runtime evidence is being represented as a pass.

## Evidence

- [ERPNext Inventory Dimension documentation](https://docs.frappe.io/erpnext/inventory_dimension)
- [ERPNext v16 Inventory Dimension source](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/doctype/inventory_dimension/inventory_dimension.py)
- [ERPNext v16 Stock Ledger Entry source](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/doctype/stock_ledger_entry/stock_ledger_entry.py)
- [ERPNext v16 Stock Balance source](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/report/stock_balance/stock_balance.py)
- [ERPNext v16 Stock Reconciliation source](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/doctype/stock_reconciliation/stock_reconciliation.py)
