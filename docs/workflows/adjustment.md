# Adjustment Workflow

**Actors**: Warehouse Operator, Warehouse Manager, Accountant
**Inputs**: Adjustment request, item(s), reason, adjustment quantity

## Flow

1. Operator/manager selects item(s), enters the adjustment quantity (+/-) and location.
2. Operator selects a reason from a predefined list and provides a detailed explanation (remarks always required).
3. Operator attaches supporting documentation (required for significant adjustments).
4. Operator submits for approval; system routes to the manager.
5. Manager reviews, verifies documentation, investigates if needed, and approves or rejects.
6. If approved, the system records it through the appropriate ERPNext stock-affecting document/API, updating the Stock Ledger and accounting entries; the adjustment is marked complete.

## Exceptions & Approval

| Exception | Handling | Requires Approval |
|---|---|---|
| Insufficient justification | Rejected; operator must add documentation | — |
| Above threshold | Requires higher-level / accountant review | Yes |
| Invalid location | Alert + correction required | — |
| Item not found at location | Alert; may indicate a data error to investigate | — |

**All adjustments require approval** — this workflow has no unapproved path.

## ERPNext Integration

- **Created**: Stock Reconciliation or another appropriate stock-affecting document.
- **Referenced**: Item, Warehouse, WMS Location (Zone/Aisle/Rack/Shelf/Bin).
- Stock increases/decreases with corresponding accounting entries for the value adjustment.

## Remarks & Attachments

- **Required for all adjustments**: detailed reason, root cause if known, preventive measures if applicable.
- **Required** for significant adjustments: investigation reports, photos, supporting documentation, evidence of discrepancy.

## Audit Fields

Item code & description, adjustment quantity (+/-), location, reason, operator, approving manager, reviewing accountant (if applicable), timestamp, stock document reference, supporting documentation, remarks.

## Future Considerations (Mobile & Offline)

Mobile adjustment requests with photo capture. Offline: queue adjustment requests, sync item/location reference data, detect conflicts if stock was already adjusted, sync audit trail once online.
