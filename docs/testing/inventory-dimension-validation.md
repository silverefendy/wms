# ERPNext Inventory Dimension Runtime Validation

## Status

**Blocked — runtime environment unavailable**

This report defines the requested proof-of-concept against the target disposable environment. It records what was actually executed. No production site was used and no runtime result is inferred from source inspection.

## Target environment

| Component | Required version | Observed |
|---|---:|---|
| Frappe | 16.34.0 | Not observable; Bench/site unavailable |
| ERPNext | 16.35.0 | Not observable; Bench/site unavailable |
| WMS | 0.0.1 | Repository source present; not installed into a runtime site |
| Site | disposable `wms.test` | Not discoverable |

Environment checks performed from the repository workspace:

- `bench` was not available on PATH.
- No Bench checkout/site was discoverable under the available workspace directories.
- Docker was installed, but no usable running container/site was available.
- WSL was inaccessible in the managed environment.

## Test data plan

The following data was **not created** because the runtime was unavailable:

- Company: `WMS Dimension Test Company`
- ERPNext Warehouse: `WMS Test Warehouse`
- WMS Location tree: `Zone A/BIN-001`, `Zone A/BIN-002`, `Zone B/BIN-003`
- Items: `TEST-ITEM-001`, `TEST-SERIAL-001`, `TEST-BATCH-001`
- Serial numbers: `SERIAL-001` through `SERIAL-003`
- Batch: `BATCH-001`
- Inventory Dimension: Reference Document `WMS Location`

No temporary configuration or transaction data was left behind.

## Results

| Test | Result | Notes |
|---|---|---|
| Configure dimension | NOT RUN | Requires disposable ERPNext site. Source inspection indicates `WMS Location` is eligible because it is a non-child DocType and is not one of ERPNext’s rejected built-in dimensions. |
| Verify applicable documents | NOT RUN | Must inspect generated fields on the target site. v16 source generates fields for applicable inventory documents and transfer variants for relevant child tables. |
| Material Receipt | NOT RUN | No runtime site available. |
| Same-warehouse transfer | NOT RUN | No runtime site available. |
| Second transfer | NOT RUN | No runtime site available. |
| Negative stock | NOT RUN | No runtime site available. v16 source contains dimension-level validation when enabled. |
| Serialized Item | NOT RUN | No runtime site available. v16 source contains serial/dimension mismatch validation. |
| Batch Item | NOT RUN | No runtime site available. Batch + dimension reconciliation remains a known validation risk. |
| Purchase Receipt | NOT RUN | No runtime site available. |
| Sales stock flow | NOT RUN | No runtime site available; POS and sales paths require exact-site testing. |
| Purchase Invoice with stock update | NOT RUN | No runtime site available. |
| Stock Reconciliation — opening stock | NOT RUN | Source/documentation indicates dimension use is intended for opening entries. |
| Stock Reconciliation — quantity modification | NOT RUN | Source/documentation indicates this is rejected for dimension rows. |
| Stock Reconciliation — valuation modification | NOT RUN | Source/documentation indicates this is rejected for dimension rows. |
| Stock Reconciliation — serialized item | NOT RUN | Requires exact-site test. |
| Stock Reconciliation — batch item | NOT RUN | Requires exact-site test; batch/dimension behavior is a known risk. |
| Stock Balance filter | NOT RUN | No runtime site available. |
| Stock Ledger filter | NOT RUN | No runtime site available. |
| Warehouse total vs dimension sum | NOT RUN | No runtime site available. |
| Warehouse/location consistency | NOT RUN | Must determine whether ERPNext rejects a location linked to another WMS Warehouse. A future WMS validation layer is expected if ERPNext does not. |
| Inactive location | NOT RUN | Must determine Link-field behavior and whether inactive locations remain selectable. |
| Location with existing ledger history | NOT RUN | Must determine deletion/rename behavior on the target site. |
| Location with child locations | NOT RUN | Must determine tree/lifecycle behavior on the target site. |
| Stock Ledger/Balance smoke performance | NOT RUN | No runtime site available. |

## Source-level evidence, not runtime evidence

The v16 source inspection completed during the architecture phase confirms:

- `Inventory Dimension` rejects `Warehouse`, `Item`, `Batch`, and `Serial No`, but accepts other non-child reference DocTypes.
- `WMS Location` therefore meets the reference-document shape.
- Generated fields include `Stock Ledger Entry` and `Stock Closing Balance`.
- Transfer fields are generated for Stock Entry Detail, Delivery Note Item, Sales Invoice Item, Purchase Receipt Item, and Purchase Invoice Item.
- Stock Ledger Entry can validate negative stock by item, warehouse, and configured dimension.
- Stock Ledger Entry validates serialized outward stock against the serial’s last inward dimension.
- Stock Reconciliation explicitly limits inventory-dimension use to opening entries and rejects general quantity/valuation modification.

These findings support the architecture but do not substitute for the requested transaction-level proof.

## Verdict

**B — VALID WITH LIMITATIONS, provisionally from source inspection; runtime verdict pending.**

The architecture remains the recommended smallest design, but it must not be marked fully runtime-validated until the exact Frappe `16.34.0` / ERPNext `16.35.0` disposable site is available and the table above is executed.

## Required next validation run

Run the test plan on an isolated site only, record document names and Stock Ledger/Stock Balance extracts, then clean all temporary records and Inventory Dimension custom fields. The final verdict should be updated only from those observed results.

