# Receiving Workflow

**Actors**: Warehouse Operator, Warehouse Manager, Purchasing Staff
**Inputs**: Purchase Order (ERPNext), supplier delivery note, physical goods, barcodes/labels

## Flow

1. Operator selects a Purchase Order awaiting receiving.
2. Operator scans each item barcode; system verifies against the PO and shows expected quantity.
3. Operator confirms received quantity; system highlights over/under discrepancies.
4. Operator records exceptions (damage, shortage) with photos if required.
5. Operator confirms receipt; system creates ERPNext **Purchase Receipt** and triggers the Putaway workflow.

## Exceptions & Approval

| Exception | Handling | Requires Approval |
|---|---|---|
| Damaged goods | Record damage details + photos, exception document | Above threshold |
| Short receipt | Record shortage, flag for follow-up | Above threshold |
| Over receipt | Record excess, flag for follow-up | Always |
| Unknown item | Manual entry | Always |

Approval process: Manager reviews the exception, approves/rejects, decision is recorded.

## ERPNext Integration

- **Created**: Purchase Receipt; the appropriate stock-affecting document is created later via Putaway.
- **Referenced**: Purchase Order, Item, Warehouse.

## Remarks & Attachments

- Optional remarks for normal receiving.
- **Required** remarks for any deviation from the Purchase Order (damage, short/over receipt).
- Attachments: photos of damaged goods, supplier delivery note, quality check documents.

## Audit Fields

Item code & description, quantity received, PO reference, Purchase Receipt reference, operator, timestamp, receiving-area location, exceptions, approval, remarks.

## Future Considerations (Mobile & Offline)

Mobile scanning interface with camera-based photo capture. Offline: queue receiving transactions and PO reference data locally; detect conflicts if multiple users receive the same order; sync audit trail once online.
