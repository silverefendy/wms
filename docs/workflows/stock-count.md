# Stock Count Workflow

## Purpose
Physically count stock in a location and reconcile with system records.

## Actors
- Warehouse Operator
- Warehouse Manager
- Accountant

## Inputs
- Stock count request
- Location to count
- Expected stock quantities

## Normal Flow

1. **Create Stock Count**
   - Manager initiates stock count
   - Manager selects location(s) to count
   - Manager assigns operator(s)

2. **Freeze Location**
   - System freezes location for stock count
   - No transfers allowed during count
   - Optional: freeze entire warehouse

3. **Count Items**
   - Operator scans location
   - Operator scans each item
   - Operator enters counted quantity
   - System records count

4. **Verify Count**
   - Operator reviews counted items
   - Operator confirms count is complete
   - System compares with expected quantity

5. **Submit Count**
   - Operator submits stock count
   - System highlights discrepancies
   - System unfreezes location

6. **Review Discrepancies**
   - Manager reviews discrepancies
   - Manager investigates causes
   - Manager approves adjustment if needed

7. **Create Adjustment**
   - If discrepancy approved, system creates Stock Entry
   - Stock Entry adjusts Stock Ledger
   - Stock count marked as complete

## Exceptions

### Cannot Freeze Location
- Location has pending transfers
- System alerts manager
- Manager must resolve pending operations first

### Discrepancy Above Threshold
- Count discrepancy exceeds configured threshold
- Requires manager investigation
- Requires manager approval for adjustment

### Item Not Found
- Physical item not found in system
- Operator records as missing
- Exception document created
- Manager approval required

### Extra Item Found
- Physical item found but not in system
- Operator records as extra
- Exception document created
- Manager approval required

## Approval

### Approval Triggers
- Stock count initiation (manager)
- Discrepancy above threshold
- Missing items
- Extra items
- Adjustment creation

### Approval Process
- Manager reviews discrepancies
- Manager approves or rejects adjustment
- Accountant may review financial impact
- System records approval decision

## ERPNext Integration

### Documents Created
- Stock Entry (ERPNext) - Stock Adjustment type
- Stock Reconciliation (ERPNext) - alternative approach

### Documents Referenced
- Item (ERPNext)
- Warehouse (ERPNext)
- WMS Location (Zone/Aisle/Rack/Shelf/Bin)
- Stock Ledger (ERPNext) - for expected quantity

### Stock Ledger Impact
- Stock Entry updates Stock Ledger
- Stock adjusted to counted quantity
- Accounting entries created for value adjustment

## Remarks

### Normal Stock Count
- Optional remarks field

### Exception Stock Count
- **Required** remarks for:
  - Discrepancies above threshold
  - Missing items
  - Extra items
  - Any unusual findings

## Attachments

- Count sheets
- Photos of discrepancies
- Investigation notes

## Audit Requirements

Record for each stock count:
- Location counted
- Item code and description
- Expected quantity
- Counted quantity
- Discrepancy
- Operator who counted
- Manager who reviewed
- Timestamp
- Stock Entry reference (if adjustment made)
- Any exceptions
- Approval if required
- Remarks

## Future Mobile Considerations

- Mobile scanning interface
- Location barcode scanning
- Batch counting mode
- Offline stock count queue
- Sync when connectivity returns

## Future Offline Considerations

- Queue stock count transactions offline
- Sync expected stock data for offline reference
- Conflict detection if location already counted
- Sync audit trail when online
