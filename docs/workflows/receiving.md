# Receiving Workflow

## Purpose
Process inbound goods from suppliers and record their receipt into the warehouse.

## Actors
- Warehouse Operator
- Warehouse Manager
- Purchasing Staff

## Inputs
- Purchase Order (ERPNext)
- Supplier delivery note
- Physical goods
- Barcodes/labels

## Normal Flow

1. **Receive Purchase Order**
   - System lists expected Purchase Orders
   - Operator selects Purchase Order for receiving

2. **Scan Items**
   - Operator scans item barcode
   - System verifies item against Purchase Order
   - System displays expected quantity

3. **Verify Quantity**
   - Operator confirms received quantity
   - System highlights discrepancies (over/under)

4. **Record Exceptions**
   - If damaged goods, operator records damage
   - If missing items, operator records shortage
   - Operator attaches photos if required

5. **Complete Receiving**
   - Operator confirms receipt
   - System creates ERPNext Purchase Receipt
   - System triggers Putaway workflow

## Exceptions

### Damaged Goods
- Operator records damage details
- Photos attached
- Exception document created
- Manager approval may be required

### Short Receipt
- Operator records shortage
- System flags for follow-up
- May require manager approval

### Over Receipt
- Operator records excess
- System flags for follow-up
- May require manager approval

### Unknown Item
- Operator cannot scan item
- Manual entry with manager approval
- Exception document created

## Approval

### Approval Triggers
- Damaged goods above threshold
- Short receipt above threshold
- Over receipt
- Unknown items

### Approval Process
- Manager reviews exception
- Manager approves or rejects
- System records approval decision

## ERPNext Integration

### Documents Created
- Purchase Receipt (ERPNext)
- Stock Entry (ERPNext) - via Putaway workflow

### Documents Referenced
- Purchase Order (ERPNext)
- Item (ERPNext)
- Warehouse (ERPNext)

## Remarks

### Normal Receiving
- Optional remarks field

### Exception Receiving
- **Required** remarks for:
  - Damaged goods
  - Short receipt
  - Over receipt
  - Any deviation from Purchase Order

## Attachments

- Photos of damaged goods
- Supplier delivery note
- Quality check documents

## Audit Requirements

Record for each item received:
- Item code and description
- Quantity received
- Purchase Order reference
- Purchase Receipt reference
- Operator who received
- Timestamp
- Location (receiving area)
- Any exceptions
- Approval if required
- Remarks

## Future Mobile Considerations

- Mobile scanning interface
- Photo capture via mobile camera
- Offline receiving queue
- Sync when connectivity returns

## Future Offline Considerations

- Queue receiving transactions offline
- Sync Purchase Order data for offline reference
- Conflict detection if multiple users receive same order
- Sync audit trail when online
