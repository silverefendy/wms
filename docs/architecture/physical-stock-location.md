# Physical Stock Location Architecture

## Problem statement

WMS needs to answer where stock is physically stored, for example `ABC / BIN-001`, while ERPNext remains authoritative for official stock quantity, valuation, accounting, and stock-affecting transactions. The design must support multiple physical locations inside one ERPNext Warehouse without creating a competing stock ledger.

This investigation is deliberately limited to architecture. It does not create a WMS stock balance, stock ledger, placement, reservation, quantity, or valuation DocType.

## Current WMS Location model

The existing `WMS Location` is a Frappe Tree DocType. A root location links to one ERPNext Warehouse and children describe the physical layout:

```text
ERPNext Warehouse
        │
        ▼
WMS Location
 ├── Zone
 │    └── Aisle
 │         └── Rack
 │              └── Shelf
 │                   └── Bin
```

The tree owns physical topology only. It currently has no stock quantity, valuation, reservation, or ledger fields.

## ERPNext v16 Inventory Dimension capability

ERPNext documents Inventory Dimensions as a v14+ feature for tracking inventory with parameters beyond the built-in warehouse, batch, and serial dimensions. A dimension is configured with a non-child Reference Document and a dimension name. ERPNext creates Link fields on applicable inventory documents and exposes the dimension in Stock Ledger and Stock Balance reports.

The v16 implementation (`version-16`, matching the installed v16 line) has these relevant properties:

| Capability | v16 finding |
|---|---|
| Reference document | Any non-child DocType is eligible, except the built-in `Batch`, `Serial No`, `Warehouse`, and `Item` dimensions. `WMS Location` is therefore eligible. |
| Generated fields | The configured Link field is added to applicable inventory documents and to `Stock Ledger Entry` and `Stock Closing Balance`. |
| Applicable documents | “All” is discovered from DocFields containing Batch or Serial fields, plus Putaway Rule; specific documents and conditions are also supported. |
| Transfer fields | Source/target variants are generated for Stock Entry Detail, Delivery Note Item, Sales Invoice Item, Purchase Receipt Item, and Purchase Invoice Item. |
| Parent fetch | A value may be fetched from a parent field, useful when every row in a receipt shares a putaway destination. |
| Ledger/reporting | Stock Ledger selects the dimension field; Stock Balance can show dimension-wise stock and filter by it. |
| Negative stock | When enabled on the dimension, an outward Stock Ledger Entry checks `Item + Warehouse + configured dimension value` before allowing negative stock. |
| Serial validation | v16 checks that each serial’s last inward dimension matches the dimension selected on an outward transaction. |
| UOM | Quantities remain ERPNext stock quantities. Reports expose Stock UOM and quantity; the dimension does not create a second UOM system. |
| Reconciliation | Inventory-dimension Stock Reconciliation is intended for opening entries. v16 rejects using a dimension to modify current quantity or valuation in the general reconciliation path. |
| Dimension lifecycle | Once ledger rows exist, the dimension’s identity/reference fields cannot be freely changed. |

The implementation intentionally ignores `Serial and Batch Bundle`, `Serial and Batch Entry`, and some non-stock child tables when creating custom dimension fields. This does not prevent Stock Ledger Entry from carrying the dimension, but it means serial/batch bundle handling must be validated through the surrounding stock transaction and ledger behavior.

Primary evidence:

- [ERPNext Inventory Dimension documentation](https://docs.frappe.io/erpnext/inventory_dimension)
- [v16 inventory_dimension.py](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/doctype/inventory_dimension/inventory_dimension.py)
- [v16 Stock Ledger Entry validation](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/doctype/stock_ledger_entry/stock_ledger_entry.py)
- [v16 Stock Balance report](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/report/stock_balance/stock_balance.py)
- [v16 Stock Reconciliation validation](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/doctype/stock_reconciliation/stock_reconciliation.py)

## Can WMS Location be the dimension?

Yes, subject to the operational rules below. Configure one Inventory Dimension whose Reference Document is `WMS Location`, for example `wms_location`. Values `BIN-001`, `BIN-002`, and `BIN-003` can all belong to the same ERPNext Warehouse. The stock key becomes conceptually:

```text
Item + ERPNext Warehouse + WMS Location [+ Serial/Batch]
```

ERPNext still reports the official warehouse total when the location filter is not applied. The location-wise rows are a breakdown of the same ERPNext Stock Ledger, not another stock system.

The dimension is not a free-standing “move” engine. A physical movement must be represented by a native ERPNext stock transaction that has an outward/source location and an inward/target location. A same-warehouse Material Transfer is the natural representation for `BIN-001 → BIN-002`; it changes the dimension while leaving the accounting warehouse unchanged.

## Document and transaction coverage

The following is the architecture reading of the v16 source. Exact field visibility should still be covered by integration tests when implementation begins.

| Flow | Dimension use |
|---|---|
| Stock Entry | Source and target location fields support receipt, issue, material transfer, manufacture, and related Stock Entry flows. Same-warehouse transfer changes physical location without changing warehouse. |
| Purchase Receipt | Inward location is captured on the receipt item. Rejected-item location has a separate generated field. Internal-supplier transfers have source/target semantics. |
| Delivery Note | Outward/source location is captured; internal-customer flows can also receive a target field. |
| Sales Invoice with stock update | Uses Sales Invoice Item inventory fields for stock-out, with internal-customer target support where applicable. |
| Purchase Invoice with stock update | Uses Purchase Invoice Item fields for stock-in, including rejected/source handling and internal-supplier transfer semantics. |
| Stock Reconciliation | Dimension is available for opening entries, but is not a safe general-purpose physical count adjustment mechanism. Counts need a future WMS workflow that produces the appropriate ERPNext adjustment/transaction after review. |
| POS stock flow | POS Invoice is discovered as an inventory document when its rows contain serial/batch fields. The POS path must be explicitly tested before relying on a location picker; a POS sale cannot silently consume a location that was not carried into the stock transaction. |
| Manufacturing | Material consumption and finished/semi-finished movement use Stock Entry Detail, so source/target locations can participate. Work-in-progress locations should be represented as controlled WMS locations when the workflow is implemented. |
| Putaway | Inventory Dimension supports a value on the stock receipt and can fetch a parent value. A future WMS putaway workflow may choose the bin before submitting the Purchase Receipt or use a same-warehouse transfer after receipt. |

## Serial numbers, batches, partial quantities, and UOM

### Serial numbers

The desired invariant is representable:

```text
Serial ABC123 → BIN-001
same-warehouse transfer → BIN-002
```

The inward SLE carries `BIN-001`; the outward SLE for the serial must use `BIN-001`, and the inward side of the transfer uses `BIN-002`. v16 validates the selected outward dimension against the serial’s last inward dimension. This is stronger than a plain custom field, but it is still transaction-driven: every physical move must produce a valid ERPNext stock movement.

### Batches

Batch quantity is naturally split by dimension in the ledger/reporting path:

```text
ABC / BATCH-001 / BIN-001 = 100 pcs
ABC / BATCH-001 / BIN-002 = 25 pcs
```

The batch remains ERPNext’s batch identity and the location remains the extra ledger dimension. The major caution is Stock Reconciliation: v16 source and current issue reports show batch reconciliation paths that are not consistently dimension-aware in all cases. Batch/location counts therefore require a controlled future workflow and regression tests before productization.

### Partial quantities

Inventory Dimension supports independent ledger quantities for one item in several locations. `40 + 35 + 25 = 100` is representable, and the unfiltered ERPNext Warehouse balance remains 100.

### UOM

The ERPNext stock UOM must be authoritative for the location dimension. If the physical operation scans one box containing 12 pieces, the transaction should convert the box to 12 pieces using the Item/UOM conversion defined in ERPNext before posting. WMS may display operational UOMs, but it must not maintain a second quantity basis or allow a box quantity to bypass ERPNext conversion rules.

## Core invariant

The selected design uses this invariant at a defined posting timestamp:

```text
ERPNext stock for (Item, Warehouse, time)
=
sum of valid WMS Location dimension balances
+ explicit non-location stock states
```

For the first implementation, explicit states should be represented as controlled WMS Location values (for example Receiving, Quarantine, Transit, Damaged, Packing, or Staging) only when they are genuine stock-holding states and are included in the same ERPNext dimension. The state taxonomy is not implemented by this task.

The reconciliation check is not a second ledger. It is a report/query that compares the dimension-wise ERPNext Stock Ledger/Stock Balance total to the unfiltered ERPNext Warehouse total. Any exception must identify missing dimension, invalid location/warehouse pairing, or an external ERPNext transaction that bypassed the WMS location policy.

## Options

### Option A — ERPNext Inventory Dimension

```text
ERPNext Warehouse + WMS Location as Inventory Dimension
        ↓
ERPNext stock documents and Stock Ledger
```

This is the smallest design that gives a location key inside ERPNext’s existing stock engine. It preserves valuation and accounting ownership, supports same-warehouse movement, and provides native location-wise ledger/report filtering.

Main limitations are the need to use native documents for every move, the incomplete/general-purpose nature of dimension-aware Stock Reconciliation, and the need for explicit POS and batch regression coverage.

### Option B — WMS Physical Placement Ledger

```text
ERPNext Warehouse + WMS Location + WMS physical placement ledger
```

This gives WMS maximum control over putaway, picking, offline operations, location-only moves, and custom audit semantics. It also creates a second quantity state. Every receipt, issue, transfer, serial, batch, UOM conversion, cancellation, backdated posting, and ERPNext-originated transaction must reconcile. A WMS ledger would be a competing inventory truth unless it is strictly an operational projection with an explicit reconciliation boundary. That complexity is not justified while ERPNext Inventory Dimension can carry the location key.

### Option C — ERPNext sub-warehouses

```text
ERPNext Warehouse
 └── Zone → Rack → Shelf → Bin
```

This is native and reportable, but it turns every physical bin into an ERPNext warehouse/accounting stock dimension. Same-warehouse physical transfers become warehouse transfers, warehouse trees become operational master data, and large or frequently changing layouts impose ERPNext warehouse semantics. It also makes non-location states and multi-site productization less flexible. It is appropriate only where bins are intentionally independent accounting/stock warehouses, which is not the WMS requirement.

## Comparison matrix

| Criterion | A — Inventory Dimension | B — WMS placement ledger | C — Sub-warehouses |
|---|---|---|---|
| ERPNext integration | Native stock movement and ledger | Requires projection/reconciliation | Native, but changes warehouse semantics |
| Stock accuracy | Strong if every stock move carries location | Two-state reconciliation risk | Strong in ERPNext, operationally coarse |
| Serial | v16 validates serial dimension on outward stock | Flexible but WMS must reproduce serial rules | Native serial by warehouse |
| Batch | Dimension split works; reconciliation caveat | Flexible, but duplicate batch/location truth | Native batch by warehouse |
| UOM | ERPNext stock UOM remains authoritative | WMS must duplicate conversion correctly | ERPNext stock UOM |
| Transfers | Same-warehouse Material Transfer with source/target | Excellent location-only UX, but must reconcile | Warehouse transfer changes ERPNext warehouse |
| Receiving | Location on Purchase Receipt or follow-up transfer | Excellent | Native warehouse receipt |
| Putaway | Workflow around native receipt/transfer | Direct and flexible | Requires warehouse changes |
| Picking | WMS selects source dimension, then Delivery Note | Direct and flexible | Selects warehouse/bin warehouse |
| Stock count | Needs controlled adjustment workflow; not general dimension reconciliation | Natural operational count, then ERPNext adjustment still required | Native per warehouse, but bin = warehouse |
| POS | Needs explicit v16 POS validation | Flexible, but POS must reconcile | Native if POS uses bin warehouses |
| Manufacturing | Stock Entry source/target dimensions | Flexible, with integration work | Native, but more warehouses |
| Offline | Queue native idempotent ERPNext transactions; conflict on posting | Easier local moves, harder final reconciliation | Queue native warehouse transactions |
| Audit | ERPNext stock audit plus voucher and dimension | Two audits and reconciliation trail | ERPNext audit |
| Performance | One SLE table with indexed dimension fields; dimension cardinality must be monitored | Additional high-volume ledger and reconciliation queries | More ERPNext warehouse rows and ledger keys |
| Reporting | Native dimension-wise Stock Ledger/Stock Balance | Custom WMS reporting plus ERPNext comparison | Native warehouse reporting |
| Upgrade safety | Uses standard feature, with version-specific gaps | Custom engine has highest maintenance cost | Standard feature but couples layout to warehouse semantics |
| Complexity | Lowest for stock truth; medium workflow integration | Highest | Medium, but wrong boundary for this requirement |
| Productization | Good if customers accept ERPNext transaction discipline | Flexible but costly to standardize | Poorer fit for varied physical layouts |

## Recommendation

Select **Option A: use `WMS Location` as an ERPNext Inventory Dimension**.

1. WMS Location should become the Inventory Dimension reference document, with a stable field such as `wms_location`.
2. WMS should not create a physical-placement ledger, stock balance, stock ledger, location quantity, or reservation engine.
3. ERPNext sub-warehouses should not be used for ordinary physical bins.
4. WMS workflows should select locations and create/submit the appropriate native ERPNext stock document. A same-warehouse bin move is a same-warehouse Material Transfer with source and target locations.
5. WMS may later add workflow/audit documents for receiving, putaway, picking, counting, and offline synchronization, but these must orchestrate or reference ERPNext stock documents rather than own a competing quantity.

This is a constrained recommendation, not a claim that Inventory Dimension replaces all WMS workflow state. Operational workflow state can be added later without duplicating official stock quantity.

## Risks and controls

- **Mandatory coverage:** Configure the dimension as mandatory only where the business process can always supply a physical location. Use explicit non-location states for legitimate temporary stock states; do not create blank/unknown as an ungoverned escape hatch.
- **External ERPNext transactions:** Stock documents created outside WMS may omit the location. Add validation/reporting policy before enabling the dimension for production.
- **Stock Reconciliation:** Do not treat the standard reconciliation form as a bin-count engine. Design a future reviewed count workflow that posts a supported ERPNext adjustment and proves the invariant.
- **Batch reconciliation:** Run v16 batch + dimension regression tests on the exact installed ERPNext patch before rollout; do not assume the current source issue history is resolved by version label alone.
- **POS:** Test POS Invoice stock update and location selection explicitly. If the POS path cannot carry the dimension reliably, define a controlled POS source location or integration boundary before enabling POS location consumption.
- **Offline:** Offline moves must be idempotent native transactions or a WMS command that is not treated as final stock until ERPNext accepts it. Conflicts must be resolved against ERPNext’s posted ledger.
- **Scale:** Index/query the dimension field through ERPNext-supported mechanisms and measure SLE/report performance with the customer’s location cardinality and transaction volume.
- **Location integrity:** Validate that a WMS Location belongs to the same ERPNext Warehouse used by the stock row, including both source and target sides of transfers.

## Validation evidence

| Test | Expected | Actual | Result |
|---|---|---|---|
| Inspect v16 Inventory Dimension reference rules | WMS Location is eligible; Warehouse/Item/Batch/Serial are rejected | Source confirms any non-child DocType, with explicit rejection of Warehouse, Item, Batch, and Serial No | PASS (source inspection) |
| Inspect generated fields | Inventory documents plus Stock Ledger Entry and Stock Closing Balance receive fields | v16 source creates fields and transfer variants | PASS (source inspection) |
| Inspect ledger/report behavior | Dimension appears in SLE and Stock Balance filters/columns | v16 source and docs confirm dimension-wise ledger/balance support | PASS (source inspection) |
| Inspect negative stock | Outward quantity is checked by item, warehouse, and dimension | v16 SLE validation performs this when enabled | PASS (source inspection) |
| Inspect serial behavior | Outward serial must match its last inward dimension | v16 SLE validation checks this | PASS (source inspection) |
| Disposable `wms.test` prototype | Create temporary dimension, transact, inspect SLE/report, then clean up | Not run: no disposable Bench/site/runtime was available in the provided workspace; Docker was present but no running container/site was discoverable | NOT RUN |

The prototype row is intentionally not presented as a product test. Before implementation, run it on the exact Frappe `16.34.0` / ERPNext `16.35.0` site and record document-level results for non-serial, serial, batch, receipt, transfer, delivery, purchase invoice, stock reconciliation, POS, and manufacturing flows.

## Future implications

The next implementation phase should build the Inventory Dimension configuration and integration tests first, not a stock-placement engine. Tests should prove:

- multiple WMS Locations under one ERPNext Warehouse;
- same-warehouse transfer source/target behavior;
- serial movement and rejection of the wrong source location;
- batch/location partial quantities;
- stock UOM conversion;
- receipt, delivery, purchase invoice, POS, and manufacturing paths;
- location-aware count/adjustment policy;
- warehouse/location integrity and cancellation behavior; and
- the reconciliation invariant.

