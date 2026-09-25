# ADR-0006: Physical Stock Location Strategy

## Status

Accepted, with runtime validation pending

## Context

WMS needs to answer where stock is physically stored (for example `ABC / BIN-001`) while ERPNext remains authoritative for stock quantity, valuation, accounting, and stock-affecting transactions. The existing `WMS Location` Tree DocType models physical topology only — it has no stock quantity, valuation, reservation, or ledger fields, and this ADR does not add any.

ERPNext v16 provides **Inventory Dimensions**: a configurable extra stock-ledger dimension keyed on a non-child reference DocType, beyond the built-in Warehouse/Item/Batch/Serial dimensions.

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

### v16 Inventory Dimension findings (source inspection)

| Capability | v16 finding |
|---|---|
| Reference document | Any non-child DocType is eligible, except the built-in `Batch`, `Serial No`, `Warehouse`, and `Item` dimensions. `WMS Location` is eligible. |
| Generated fields | The dimension's Link field is added to applicable inventory documents and to `Stock Ledger Entry` and `Stock Closing Balance`. |
| Transfer fields | Source/target variants generated for Stock Entry Detail, Delivery Note Item, Sales Invoice Item, Purchase Receipt Item, Purchase Invoice Item. |
| Negative stock | When enabled, an outward Stock Ledger Entry checks `Item + Warehouse + dimension value`. |
| Serial validation | v16 checks that a serial's outward dimension matches its last inward dimension. |
| UOM | Quantities remain ERPNext stock quantities; the dimension adds no second UOM system. |
| Reconciliation | Dimension-aware Stock Reconciliation is intended for **opening entries only**; v16 rejects using it to modify current quantity/valuation in the general path. |
| Dimension lifecycle | Once ledger rows exist, identity/reference fields cannot be freely changed. |

Primary evidence: [ERPNext Inventory Dimension docs](https://docs.frappe.io/erpnext/inventory_dimension), [v16 inventory_dimension.py](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/doctype/inventory_dimension/inventory_dimension.py), [v16 Stock Ledger Entry](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/doctype/stock_ledger_entry/stock_ledger_entry.py), [v16 Stock Balance](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/report/stock_balance/stock_balance.py), [v16 Stock Reconciliation](https://github.com/frappe/erpnext/blob/version-16/erpnext/stock/doctype/stock_reconciliation/stock_reconciliation.py).

### Document coverage

| Flow | Dimension use |
|---|---|
| Stock Entry | Source/target location fields support receipt, issue, transfer, manufacture. Same-warehouse transfer changes location without changing warehouse. |
| Purchase Receipt | Inward location on the receipt item; rejected-item location is a separate field. |
| Delivery Note | Outward/source location captured. |
| Sales Invoice / Purchase Invoice (stock update) | Inventory fields on the item row support the dimension. |
| Stock Reconciliation | Opening entries only — not a general count/adjustment mechanism. |
| POS stock flow | Discovered as an inventory document only when rows carry serial/batch fields; must be explicitly tested before relying on a location picker. |
| Manufacturing | Stock Entry Detail source/target locations apply to consumption and output. |
| Putaway | A value can be set on receipt or fetched from a same-warehouse transfer after receipt. |

### Serial, batch, partial quantity, UOM

- **Serial**: `Serial ABC123 → BIN-001`, then a same-warehouse transfer to `BIN-002` — the outward SLE must use `BIN-001` (validated by v16 against the serial's last inward dimension) and the inward side of the transfer uses `BIN-002`.
- **Batch**: quantity naturally splits by dimension (e.g. `BATCH-001/BIN-001 = 100`, `BATCH-001/BIN-002 = 25`), but batch + dimension **Stock Reconciliation** is a known risk area needing exact-patch regression testing before productization.
- **Partial quantities**: independent per-location ledger rows are supported; the unfiltered Warehouse total remains correct.
- **UOM**: ERPNext stock UOM stays authoritative. A scanned box must be converted to stock UOM via Item/UOM conversion before posting; WMS must not maintain a second quantity basis.

## Decision

Use **`WMS Location` as an ERPNext Inventory Dimension**.

1. `WMS Location` becomes the Inventory Dimension reference document (e.g. field `wms_location`).
2. WMS does **not** create a physical-placement ledger, stock balance, location quantity, or reservation engine.
3. ERPNext sub-warehouses are **not** used for ordinary physical bins.
4. Every physical movement is a native ERPNext stock document. A same-warehouse bin move is a same-warehouse Material Transfer with source and target `WMS Location`.
5. Future WMS workflow/audit documents (receiving, putaway, picking, counting, offline sync) must orchestrate or reference these native documents rather than own a competing quantity.

The core invariant, at any posting timestamp:

```text
ERPNext stock for (Item, Warehouse, time)
=
sum of valid WMS Location dimension balances
+ explicit non-location stock states
```

Explicit non-location states (e.g. Receiving, Quarantine, Transit, Damaged, Packing, Staging) may later be represented as controlled `WMS Location` values when they are genuine stock-holding states within the same dimension. This ADR does not define that state taxonomy. The reconciliation check is a **report/query** comparing dimension-wise Stock Ledger/Balance totals to the unfiltered Warehouse total — it is not a second ledger.

## Alternatives Considered

### Option B — WMS Physical Placement Ledger
Would give WMS maximum control over putaway, picking, offline, and audit semantics, but creates a second quantity state: every receipt, issue, transfer, serial, batch, UOM conversion, cancellation, backdated posting, and ERPNext-originated transaction would need reconciliation. **Rejected** — not justified while Inventory Dimension can carry the location key.

### Option C — ERPNext Sub-Warehouses
Native and reportable, but turns every physical bin into an ERPNext warehouse/accounting dimension; same-warehouse bin moves become warehouse transfers, and large/changing layouts impose warehouse semantics. **Rejected** for ordinary bins — appropriate only where a node is intentionally an independent accounting warehouse, which is not the WMS requirement.

### Hybrid quantity architecture
A placement ledger alongside Inventory Dimension would create two operational quantity authorities without a requirement that justifies the cost. **Rejected**.

### Comparison summary

| Criterion | A — Inventory Dimension | B — Placement ledger | C — Sub-warehouses |
|---|---|---|---|
| Stock accuracy | Strong if every move carries location | Two-state reconciliation risk | Strong, but operationally coarse |
| Transfers | Same-warehouse Material Transfer | Flexible, but must reconcile | Becomes a warehouse transfer |
| Complexity | Lowest for stock truth | Highest | Wrong boundary for this requirement |
| Upgrade safety | Standard feature, version-specific gaps | Highest maintenance cost | Couples layout to warehouse semantics |

## Consequences

### Positive
- No competing WMS stock ledger.
- Stock Ledger Entry / Stock Balance natively carry and report the location dimension.
- Multiple bins share one ERPNext Warehouse; same-warehouse transfers need no accounting warehouse change.
- ERPNext stock UOM, valuation, serial, batch, cancellation, and audit remain authoritative.

### Negative
- A location move must always be posted through a supported ERPNext stock transaction.
- WMS cannot treat an offline local move as final stock before ERPNext accepts it.
- Stock Reconciliation is not a general-purpose bin-count engine.
- POS and batch reconciliation need exact-patch integration coverage before rollout.
- Customers must control or validate ERPNext transactions that bypass WMS location policy.

## Risks and Controls

- **Mandatory coverage**: require the dimension only where the process can always supply a location; use explicit non-location states rather than an ungoverned blank/unknown.
- **External transactions**: stock documents created outside WMS may omit the location — add validation/reporting before enabling the dimension in production.
- **Stock Reconciliation**: do not treat it as a bin-count engine; design a reviewed count workflow that posts a supported adjustment instead.
- **Batch reconciliation**: run v16 batch + dimension regression tests on the exact installed patch before rollout.
- **POS**: explicitly test POS Invoice stock update and location selection; define a controlled POS source location if the dimension cannot be carried reliably.
- **Offline**: moves must be idempotent native transactions, not treated as final stock until ERPNext accepts them; conflicts resolve against ERPNext's posted ledger.
- **Scale**: monitor dimension cardinality and SLE/report performance for the customer's transaction volume.
- **Location integrity**: validate that a `WMS Location` belongs to the same ERPNext Warehouse as the stock row, on both sides of a transfer.

## Runtime Validation Status

**Blocked — runtime environment unavailable at ADR acceptance time.** No production or existing user site was used; no runtime result is inferred from source inspection alone.

Target environment: Frappe `16.34.0`, ERPNext `16.35.0`, disposable site `wms.test`. At the time this ADR was written, `bench` was not on PATH, no Bench/site was discoverable in the workspace, Docker had no usable running container, and WSL was inaccessible — so the transaction-level test plan below was **not run**, only reasoned from v16 source inspection.

| Test area | Result | Basis |
|---|---|---|
| Dimension configuration (`WMS Location` as reference doc) | NOT RUN | Source inspection: eligible, non-rejected DocType |
| Generated fields on inventory documents / SLE / Stock Closing Balance | NOT RUN | Source inspection: fields generated as documented above |
| Material Receipt / same-warehouse transfer / second transfer | NOT RUN | Requires disposable site |
| Negative stock check (Item + Warehouse + dimension) | NOT RUN | Source inspection: validation exists when enabled |
| Serialized item outward/inward dimension match | NOT RUN | Source inspection: v16 validates this |
| Batch item partial quantities + reconciliation | NOT RUN | Known risk area; requires exact-patch regression test |
| Purchase Receipt / Sales stock flow / Purchase Invoice with stock update | NOT RUN | Requires disposable site |
| Stock Reconciliation (opening vs. quantity/valuation modification) | NOT RUN | Source/docs indicate opening-only support |
| Stock Balance / Stock Ledger dimension filter | NOT RUN | Requires disposable site |
| Warehouse total vs. dimension-sum invariant | NOT RUN | Requires disposable site |
| Warehouse/location integrity, inactive location, location with ledger history or children | NOT RUN | Requires disposable site |
| Ledger/report smoke performance | NOT RUN | Requires disposable site |

**Verdict at time of writing: valid with limitations, provisionally from source inspection only — not yet runtime-validated.** This ADR's decision stands as the smallest correct design, but must not be treated as fully proven until the exact Frappe/ERPNext patch combination is tested end to end.

**Required next validation run**: on an isolated `wms.test`-style site only, execute the table above, record document names and Stock Ledger/Stock Balance extracts, then remove all temporary records and Inventory Dimension custom fields. Update this section's verdict only from those observed results — do not mark any row PASS from source reasoning alone.

## Future Implications

The next implementation phase should build the Inventory Dimension configuration and the validation run above **before** building operational workflows. Workflows for receiving, putaway, picking, counting, and offline synchronization should then orchestrate native ERPNext documents and maintain their own workflow/audit state without ever owning official stock quantity.

## Related Decisions

- [ADR-0001: ERPNext Stock as System of Record](ADR-0001-erpnext-stock-as-system-of-record.md)
- [ADR-0005: WMS Physical Location Model](ADR-0005-wms-physical-location-model.md)
- [ADR-0007: Wood Pellet Bagging and Weighbridge Boundary](ADR-0007-wood-pellet-bagging-and-weighbridge.md)
