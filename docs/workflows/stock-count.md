# Stock Count Workflow

**Actors**: Warehouse Operator, Warehouse Manager, Accountant
**Inputs**: Stock count request, location(s) to count, expected stock quantities

## Flow

1. Manager initiates a stock count, selects location(s), and assigns operator(s).
2. System freezes the location (no transfers allowed during the count; optionally freeze the whole warehouse).
3. Operator scans the location and each item, entering the counted quantity.
4. Operator reviews and confirms the count is complete; system compares against expected quantity.
5. Operator submits the count; system highlights discrepancies and unfreezes the location.
6. Manager reviews and investigates discrepancies, then approves an adjustment if needed.
7. If approved, the system records the discrepancy through the appropriate ERPNext stock-affecting document/API, updating the Stock Ledger; the count is marked complete.

## Exceptions & Approval

| Exception | Handling | Requires Approval |
|---|---|---|
| Cannot freeze location (pending transfers) | Manager must resolve pending operations first | — |
| Discrepancy above threshold | Manager investigation | Yes |
| Item not found (missing) | Record as missing, exception document | Yes |
| Extra item found | Record as extra, exception document | Yes |

Stock count initiation itself also requires manager sign-off; an accountant may review adjustments with significant financial impact.

## ERPNext Integration

- **Created**: Stock Reconciliation or another appropriate stock-affecting document. See [ADR-0006](../decisions/ADR-0006-physical-stock-location-strategy.md) for the limits of dimension-aware Stock Reconciliation — it is not a general-purpose bin-count adjustment mechanism, so a reviewed count-to-adjustment workflow is required.
- **Referenced**: Item, Warehouse, WMS Location, Stock Ledger (for expected quantity).

## Remarks & Attachments

- Optional remarks for a normal count.
- **Required** for discrepancies above threshold, missing items, extra items, or unusual findings.
- Attachments: count sheets, photos of discrepancies, investigation notes.

## Audit Fields

Location counted, item code & description, expected quantity, counted quantity, discrepancy, operator, manager, timestamp, stock document reference (if adjusted), exceptions, approval, remarks.

## Future Considerations (Mobile & Offline)

Mobile scanning with batch counting mode. Offline: queue counts, sync expected-stock data, detect conflicts if a location was already counted, sync audit trail once online.
