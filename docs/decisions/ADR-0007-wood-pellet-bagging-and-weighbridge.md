# ADR-0007: Wood Pellet Bagging, Big Bag Lifecycle, and Weighbridge Boundary

## Status
Accepted (Manual-first implementation; weighbridge hardware integration deferred)

## Context

The business produces and sells wood pellets. Physical flow: bulk pellet is bagged
into reusable "big bags", big bags are loaded into a container for shipment, and
shipments are weighed at a weighbridge before dispatch. Each big bag carries an
RFID tag and a QR code so it can be identified and tracked individually.

Three open questions needed a decision before implementation could start:

1. How is a **reusable, damageable, occasionally-sold** big bag represented in
   ERPNext without creating a competing tracking system?
2. How is a **weighbridge ticket** represented, given the company already has a
   separate weighbridge application that will be integrated later, but needs a
   manual-entry path now?
3. How does a shipment (a set of big bags loaded into one container) relate to
   the weighbridge ticket and to standard ERPNext outbound documents?

This ADR builds on ADR-0001 (ERPNext Stock as System of Record), ADR-0002 (WMS
Application Boundary), ADR-0003 (ERPNext Item and Variant Master), and ADR-0006
(Physical Stock Location Strategy via Inventory Dimension). It does not
reopen any of those decisions.

## Decision

### 1. Big Bag is a Serialized ERPNext Item, not a WMS-owned entity

- A big bag is modeled as its own ERPNext **Item** (e.g. `BIGBAG-1000L`), separate
  from the `Wood Pellet` item, with **Serial No** tracking enabled.
- The RFID tag value and the QR code value are both recorded against the Serial
  No (RFID as the primary scan method; QR as a fallback/manual lookup key).
- Because big bags are normally **reusable**, a bag's Serial No persists across
  many fill/empty cycles. Each cycle is a sequence of standard ERPNext
  stock-affecting documents (see Decision 3) referencing the same Serial No,
  not a new identity per cycle.
- A big bag's **physical location** at any point in time is read from the
  Inventory Dimension established in ADR-0006 (`WMS Location`), using the same
  serial-to-last-inward-dimension validation ERPNext already provides. This is
  also the mechanism for periodic RFID-based location audits: scanning a bag's
  RFID and confirming it against its last recorded WMS Location is a
  **verification/reporting** action, not a new stock movement, unless a
  discrepancy is found and corrected (which then follows the normal Adjustment
  workflow).
- **No separate WMS ledger, register, or lifecycle table is created for big
  bags.** This would duplicate what Serial No + Inventory Dimension already
  provide, which ADR-0001 and ADR-0006 both rule out.

### 2. Big Bag lifecycle states are handled as ERPNext-native events, not a custom state machine

| Event | Representation |
|---|---|
| Bag filled with pellet | Stock Entry (Manufacture): consume bulk pellet + empty bag, produce filled-bag output |
| Bag emptied back out | Stock Entry (Manufacture or Repack): reverse — bag becomes "empty" again, ready for reuse |
| Bag damaged | Exception/write-off, following the same pattern already used for damage in `putaway.md` / `picking.md`: required remarks, manager approval, Serial No retired (not deleted) |
| Bag sold together with its container/shipment | Sold as its own line item (its own Item code) on the Delivery Note / Sales Invoice, alongside the pellet — not treated as consumed packaging |

No new "Big Bag Status" DocType is introduced. Status is always inferable from
the bag's Serial No history in ERPNext (last stock movement, whether it has
been written off, whether it has been sold).

### 3. Weighbridge Ticket is a WMS document that references bags and one outbound ERPNext document — manual entry first

A new custom DocType, **`WMS Weighbridge Ticket`**, is introduced with this scope:

- Fields: ticket number, gross/tare/net weight, vehicle/container reference,
  timestamp in/out, operator, remarks.
- A **child table of big bag Serial Nos** (with their RFID/QR values) included
  in that specific shipment — functioning similarly to a Delivery Order's item
  table, but at the bag level rather than the pellet-quantity level.
- A **link field to the ERPNext outbound document** (Delivery Note / Stock
  Entry) that actually moves the stock. The ticket is a **reference and
  verification document**, not a stock-affecting one — it does not itself
  change any ERPNext Stock Ledger balance.
- **Data entry is manual for this phase.** The company's existing separate
  weighbridge application is not integrated yet. The DocType is deliberately
  structured so that weight fields can later be populated by an automated
  integration without changing the document's shape or its relationship to
  bags and the Delivery Note.
- Quantity/weight mismatch between the ticket and the linked ERPNext document
  follows the same **exception + manager approval** pattern already
  established in `receiving.md`, `putaway.md`, and `transfer.md`.

## Rationale

- Keeps ERPNext as the single source of stock truth (ADR-0001): big bags and
  their movements are ordinary Items, Serial Nos, and stock-affecting
  documents, not a parallel system.
- Reuses the Inventory Dimension mechanism already decided in ADR-0006 instead
  of inventing new location-tracking logic for bags specifically.
- Treats the weighbridge ticket the same way other WMS workflow documents
  treat exceptions and approvals, so the pattern is consistent across the app
  rather than one-off.
- Defers the real integration risk (hardware/serial-port/API to the existing
  weighbridge app) to a later phase, while making sure today's manual-entry
  design does not need to be reworked when that integration lands.

## Consequences

### Positive
- No competing tracking system for big bags; audit trail is entirely ERPNext's.
- Big bag reuse, damage, and occasional resale are all representable without
  special-casing the Item or Serial No model.
- Weighbridge integration can be added later without changing the ticket's
  document structure or its relationships to bags and Delivery Note.

### Negative
- Every bag fill/empty/transfer cycle must go through a proper ERPNext stock
  document; there is no shortcut "just scan the RFID and it's tracked" path —
  the RFID scan must resolve to a Serial No used inside a real stock
  transaction (or a verification report) for it to be reflected as an
  inventory event.
- RFID-based periodic location checks are a manual/scheduled verification
  process against Inventory Dimension data, not a live real-time feed, until a
  dedicated scanning workflow is built.
- Until the weighbridge application is integrated, ticket weight data is only
  as accurate as manual entry.

## Alternatives Considered

### Big Bag as a non-serialized, batch-tracked item
- **Rejected**: batches do not give per-bag identity, which is required
  because bags carry individual RFID/QR tags and can be individually damaged
  or sold.

### Big Bag as a WMS-owned "asset ledger" separate from ERPNext Serial No
- **Rejected**: would duplicate ERPNext's existing serial tracking and
  require a reconciliation layer, which ADR-0001/ADR-0006 already rule out for
  stock-related entities.

### Weighbridge Ticket as the stock-affecting document itself
- **Rejected**: would make WMS responsible for posting stock changes outside
  the standard ERPNext document flow, violating ADR-0001. The ticket remains a
  reference/verification document; the Delivery Note (or equivalent) remains
  the actual stock-affecting transaction.

## Related Decisions
- [ADR-0001: ERPNext Stock as System of Record](ADR-0001-erpnext-stock-as-system-of-record.md)
- [ADR-0003: ERPNext Item and Variant Master](ADR-0003-erpnext-item-and-variant-master.md)
- [ADR-0006: Physical Stock Location Strategy](ADR-0006-physical-stock-location-strategy.md)

## Open Items for Future ADRs
- Formal design of the RFID-based periodic verification/audit workflow.
- Weighbridge hardware/application integration approach (once resumed).
- Whether high-value or long-lived big bags warrant asset-style depreciation
  tracking in ERPNext (out of scope for this ADR).
