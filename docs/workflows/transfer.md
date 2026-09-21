# Transfer Workflow

## Purpose
Move stock between locations within the same warehouse or between warehouses.

## Actors
- Warehouse Operator
- Warehouse Manager

## Inputs
- Transfer request
- Source location
- Destination location
- Items to transfer

## Normal Flow

1. **Create Transfer Request**
   - Operator initiates transfer
   - Operator selects source location
   - Operator selects destination location

2. **Select Items**
   - System shows available stock in source location
   - Operator selects items to transfer
   - Operator confirms quantities

3. **Scan Source**
   - Operator scans source location
   - System validates source has sufficient stock
   - System confirms source location

4. **Pick Items**
   - Operator picks items from source location
   - Operator scans item barcodes
   - System validates items against transfer list

5. **Scan Destination**
   - Operator scans destination location
   - System validates destination exists
   - System confirms destination is available

6. **Place Items**
   - Operator places items in destination
   - Operator confirms quantities placed

7. **Complete Transfer**
   - Operator confirms transfer complete
   - System creates ERPNext Stock Entry
   - ERPNext updates the Stock Ledger through the standard stock-affecting document flow
   - Stock moved from source to destination

## Exceptions

### Insufficient Stock
- Source location does not have sufficient stock
- System alerts operator
- Transfer cannot proceed until resolved

### Invalid Source Location
- Operator scans invalid source location
- System alerts and requires rescan

### Invalid Destination Location
- Operator scans invalid destination location
- System alerts and requires rescan

### Quantity Mismatch
- Picked quantity does not match transfer quantity
- System alerts operator
- May require manager approval

### Damaged During Transfer
- Operator records damage
- Exception document created
- Manager approval required

## Approval

### Approval Triggers
- Inter-warehouse transfer (if restricted)
- Quantity mismatch
- Damage during transfer
- High-value items

### Approval Process
- Manager reviews transfer
- Manager approves or rejects
- System records approval decision

## ERPNext Integration

### Documents Created
- Stock Entry (ERPNext) - Material Transfer type

### Documents Referenced
- Item (ERPNext)
- Warehouse (ERPNext)
- WMS Location (Zone/Aisle/Rack/Shelf/Bin)

### Stock Ledger Impact
- Stock Entry updates Stock Ledger
- Stock decreased in source location
- Stock increased in destination location

## Remarks

### Normal Transfer
- Optional remarks field

### Exception Transfer
- **Required** remarks for:
  - Inter-warehouse transfer
  - Quantity mismatch
  - Damage during transfer
  - Any deviation from standard process

## Attachments

- Photos of damage (if applicable)
- Transfer authorization documents

## Audit Requirements

Record for each transfer:
- Item code and description
- Quantity transferred
- Source location (full hierarchy)
- Destination location (full hierarchy)
- Operator who performed transfer
- Timestamp
- Stock Entry reference
- Any exceptions
- Approval if required
- Remarks

## Future Mobile Considerations

- Mobile scanning interface
- Location barcode scanning
- Available stock display
- Offline transfer queue
- Sync when connectivity returns

## Future Offline Considerations

- Queue transfer transactions offline
- Sync stock data for offline reference
- Conflict detection if stock already transferred
- Sync audit trail when online
