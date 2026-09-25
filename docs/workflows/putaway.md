# Putaway Workflow

**Actors**: Warehouse Operator, Warehouse Manager
**Inputs**: Purchase Receipt (ERPNext), completed Receiving workflow, storage location assignments

## Flow

1. System lists items awaiting putaway; operator selects an item/batch.
2. System suggests a storage location (Warehouse → Zone → Aisle → Rack → Shelf → Bin); operator confirms or changes it.
3. Operator scans the location barcode; system validates it exists and is available.
4. Operator confirms the quantity against the received quantity.
5. Operator confirms putaway; system creates the appropriate ERPNext stock-affecting document, which updates the Stock Ledger.

## Exceptions & Approval

| Exception | Handling | Requires Approval |
|---|---|---|
| Location full | Operator selects an alternative location | Non-standard location |
| Invalid location | Alert + rescan required | — |
| Quantity mismatch | Alert operator | Yes |
| Damaged during putaway | Record damage, exception document | Yes |

## ERPNext Integration

- **Created**: the appropriate ERPNext stock-affecting document/API.
- **Referenced**: Purchase Receipt, Item, Warehouse, WMS Location (Zone/Aisle/Rack/Shelf/Bin).
- Stock recorded against the warehouse; location recorded in custom fields (see [ADR-0006](../decisions/ADR-0006-physical-stock-location-strategy.md)).

## Remarks & Attachments

- Optional remarks for normal putaway.
- **Required** for non-standard location, quantity mismatch, damage, or any process deviation.
- Attachments: photos of damage, location verification documents.

## Audit Fields

Item code & description, quantity, source (Purchase Receipt), destination location (full hierarchy), operator, timestamp, stock document reference, exceptions, approval, remarks.

## Future Considerations (Mobile & Offline)

Mobile scanning for locations and suggested-location display. Offline: queue putaway transactions, sync location reference data, detect conflicts when multiple users putaway the same item, sync audit trail once online.
