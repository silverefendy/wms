# Transfer Workflow

**Actors**: Warehouse Operator, Warehouse Manager
**Inputs**: Transfer request, source location, destination location, items to transfer

## Flow

1. Operator selects source and destination locations.
2. System shows available stock at the source; operator selects items and quantities.
3. Operator scans the source location; system validates sufficient stock.
4. Operator picks and scans items against the transfer list.
5. Operator scans the destination location; system validates it exists and is available.
6. Operator places items and confirms quantities.
7. Operator confirms the transfer; system creates a **Stock Entry (Material Transfer)**, updating the Stock Ledger.

## Exceptions & Approval

| Exception | Handling | Requires Approval |
|---|---|---|
| Insufficient stock at source | Block transfer until resolved | — |
| Invalid source/destination location | Alert + rescan | — |
| Quantity mismatch (picked vs. requested) | Alert operator | Yes |
| Damaged during transfer | Record damage, exception document | Yes |

Inter-warehouse transfers and high-value items may also require approval.

## ERPNext Integration

- **Created**: Stock Entry (Material Transfer type).
- **Referenced**: Item, Warehouse, WMS Location (Zone/Aisle/Rack/Shelf/Bin).
- Stock decreases at source location and increases at destination.

## Remarks & Attachments

- Optional remarks for normal transfers.
- **Required** for inter-warehouse transfer, quantity mismatch, damage, or any deviation.
- Attachments: photos of damage, transfer authorization documents.

## Audit Fields

Item code & description, quantity, source location (full hierarchy), destination location (full hierarchy), operator, timestamp, Stock Entry reference, exceptions, approval, remarks.

## Future Considerations (Mobile & Offline)

Mobile scanning with available-stock display. Offline: queue transfers, sync stock data locally, detect conflicts if stock was already transferred, sync audit trail once online.
