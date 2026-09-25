# Packing Workflow

**Actors**: Warehouse Operator (Packer), Warehouse Manager
**Inputs**: Completed picking, picked items, shipping requirements

## Flow

1. Packer receives the packing list (items, quantities, shipping info) for assigned picked items.
2. Packer selects and confirms packaging (suggestion is a future capability).
3. Packer places and scans items to confirm against the packing list.
4. Packer adds packing materials (recorded as a future capability).
5. Packer weighs the package and enters the weight (shipping cost calculation: future).
6. System generates a shipping label with tracking number; packer attaches it.
7. Packer confirms packing complete; system validates all items packed and triggers **Delivery Note** creation.

## Exceptions & Approval

| Exception | Handling | Requires Approval |
|---|---|---|
| Insufficient packaging | Record exception; packing delayed until resolved | — |
| Item damaged during packing | Record damage, exception document; item may need replacement | Yes |
| Wrong item scanned | Alert, rescan required | — |
| Weight discrepancy | Alert; may indicate missing items | If significant |

## ERPNext Integration

- **Created**: Delivery Note, and the corresponding stock-affecting document via the Delivery Note.
- **Referenced**: Sales Order, Item, Warehouse, Customer.
- Stock decreases from the warehouse through normal ERPNext processing.

## Remarks & Attachments

- Optional remarks for normal packing.
- **Required** for damage, weight discrepancy, missing items, packaging issues, or any deviation.
- Attachments: photos of damaged items, packaging documentation, shipping labels.

## Audit Fields

Item code & description, quantity packed, packaging type, package weight, tracking number, Sales Order reference, packer, timestamp, Delivery Note reference, exceptions, approval, remarks.

## Future Considerations (Mobile & Offline)

Mobile packing with barcode scanning, label printing, and weight-scale integration. Offline: queue packing transactions, sync packing list/shipping data, detect conflicts if already packed, sync audit trail once online.
