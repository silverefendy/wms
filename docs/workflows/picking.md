# Picking Workflow

**Actors**: Warehouse Operator (Picker), Warehouse Manager
**Inputs**: Sales Order (ERPNext), picking list, item locations

## Flow

1. System assigns a Sales Order to a picker; picker views the picking list (items, quantities, locations).
2. System guides the picker to each location (route optimization: future); picker scans location to confirm.
3. Picker scans the item barcode; system validates it matches the picking list and location.
4. Picker confirms quantity picked against the picking list.
5. Exceptions (not found / short) are recorded and flagged for manager review.
6. Picker repeats until all items are picked, then confirms completion, triggering the Packing workflow.

## Exceptions & Approval

| Exception | Handling | Requires Approval |
|---|---|---|
| Item not found at expected location | Record exception; system searches other locations (future) | Significant cases |
| Insufficient quantity | Record shortage | Significant cases |
| Damaged item | Record damage, exception document | Yes |
| Wrong item scanned | Alert, rescan required | — |

## ERPNext Integration

- **Referenced**: Sales Order, Item, Warehouse, WMS Location, Stock Ledger (available quantity).
- **Created (future)**: Delivery Note and the corresponding stock-affecting document, after packing.
- Stock reservation on pick start is a future capability, to prevent double-picking.

## Remarks & Attachments

- Optional remarks for normal picking.
- **Required** for item-not-found, shortages, damage, or any deviation from the picking list.
- Attachments: photos of damaged items, exception documentation.

## Audit Fields

Item code & description, quantity picked, source location (full hierarchy), Sales Order reference, picker, timestamp, exceptions, approval, remarks.

## Future Considerations (Mobile & Offline)

Mobile picking with route guidance and (future) voice picking. Offline: queue picking transactions, sync picking list and location data, detect conflicts if an item was already picked, sync audit trail once online.
