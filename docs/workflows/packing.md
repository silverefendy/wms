# Packing Workflow

## Purpose
Prepare picked items for shipment, ensuring proper packaging and documentation.

## Actors
- Warehouse Operator (Packer)
- Warehouse Manager

## Inputs
- Completed picking
- Picked items
- Shipping requirements

## Normal Flow

1. **Receive Packing Assignment**
   - System assigns picked items to packer
   - Packer views packing list
   - Packing list shows items, quantities, and shipping info

2. **Select Packaging**
   - Packer selects appropriate packaging
   - System suggests packaging based on items (future)
   - Packer confirms packaging

3. **Pack Items**
   - Packer places items in packaging
   - Packer scans items to confirm
   - System validates against packing list

4. **Add Packing Materials**
   - Packer adds packing materials
   - Bubble wrap, dunnage, etc.
   - System records materials used (future)

5. **Weigh Package**
   - Packer weighs package
   - Packer enters weight
   - System calculates shipping cost (future)

6. **Generate Label**
   - System generates shipping label
   - Packer prints and attaches label
   - System records tracking number

7. **Complete Packing**
   - Packer confirms packing complete
   - System validates all items packed
   - System triggers Delivery Note creation

## Exceptions

### Insufficient Packaging
- No appropriate packaging available
- Packer records exception
- Manager must provide packaging
- Packing delayed until resolved

### Item Damaged During Packing
- Item damaged while packing
- Packer records damage
- Exception document created
- Manager approval required
- Item may need replacement

### Wrong Item
- Packer scans wrong item
- System alerts packer
- Packer must scan correct item

### Weight Discrepancy
- Package weight unexpected
- System alerts packer
- May indicate missing items
- May require re-verification

## Approval

### Approval Triggers
- Item damaged during packing
- Significant weight discrepancy
- Missing items

### Approval Process
- Manager reviews packing exceptions
- Manager approves corrective actions
- System records approval decision

## ERPNext Integration

### Documents Created
- Delivery Note (ERPNext)
- Standard ERPNext stock-affecting document - via Delivery Note

### Documents Referenced
- Sales Order (ERPNext)
- Item (ERPNext)
- Warehouse (ERPNext)
- Customer (ERPNext)

### Stock Ledger Impact
- Delivery Note updates stock through normal ERPNext processing
- Stock decreased from warehouse

## Remarks

### Normal Packing
- Optional remarks field

### Exception Packing
- **Required** remarks for:
  - Item damaged during packing
  - Weight discrepancies
  - Missing items
  - Packaging issues
  - Any deviation from standard process

## Attachments

- Photos of damaged items
- Packaging documentation
- Shipping labels

## Audit Requirements

Record for each pack:
- Item code and description
- Quantity packed
- Packaging type
- Package weight
- Tracking number
- Sales Order reference
- Packer who performed packing
- Timestamp
- Delivery Note reference
- Any exceptions
- Approval if required
- Remarks

## Future Mobile Considerations

- Mobile packing interface
- Barcode scanning
- Label printing
- Weight integration
- Offline packing queue
- Sync when connectivity returns

## Future Offline Considerations

- Queue packing transactions offline
- Sync packing list for offline reference
- Sync shipping data for offline reference
- Conflict detection if already packed
- Sync audit trail when online
