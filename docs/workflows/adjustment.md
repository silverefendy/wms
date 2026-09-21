# Adjustment Workflow

## Purpose
Correct stock quantities when discrepancies are discovered outside of formal stock count process.

## Actors
- Warehouse Operator
- Warehouse Manager
- Accountant

## Inputs
- Adjustment request
- Item(s) to adjust
- Reason for adjustment
- Adjustment quantity

## Normal Flow

1. **Create Adjustment Request**
   - Operator or manager initiates adjustment
   - Operator selects item(s)
   - Operator enters adjustment quantity (+ or -)
   - Operator selects location

2. **Specify Reason**
   - Operator selects reason from predefined list
   - Operator provides detailed explanation
   - **Required** remarks for all adjustments

3. **Attach Documentation**
   - Operator attaches supporting documents
   - Photos, reports, or other evidence
   - Documentation required for significant adjustments

4. **Submit for Approval**
   - Operator submits adjustment request
   - System routes to manager for approval

5. **Manager Review**
   - Manager reviews adjustment request
   - Manager verifies documentation
   - Manager investigates if needed

6. **Approval Decision**
   - Manager approves or rejects
   - If rejected, request returned with reason
   - If approved, adjustment proceeds

7. **Create Stock Entry**
   - System creates ERPNext Stock Entry
   - Stock Entry adjusts Stock Ledger
   - Accounting entries created
   - Adjustment marked as complete

## Exceptions

### Insufficient Justification
- Adjustment lacks proper documentation
- Manager rejects request
- Operator must provide additional documentation

### Adjustment Above Threshold
- Adjustment quantity exceeds threshold
- Requires higher-level approval
- May require accountant review

### Invalid Location
- Operator selects invalid location
- System alerts and requires correction

### Item Not Found
- Item does not exist in location
- System alerts operator
- May indicate data error requiring investigation

## Approval

### Approval Triggers
- All adjustments require approval
- Threshold-based approval levels
- Accountant approval for value adjustments above threshold

### Approval Process
- Manager reviews adjustment
- Manager approves or rejects
- Accountant may review for financial impact
- System records approval decision

## ERPNext Integration

### Documents Created
- Stock Entry (ERPNext) - Stock Adjustment type

### Documents Referenced
- Item (ERPNext)
- Warehouse (ERPNext)
- WMS Location (Zone/Aisle/Rack/Shelf/Bin)

### Stock Ledger Impact
- Stock Entry updates Stock Ledger
- Stock increased or decreased
- Accounting entries created for value adjustment

## Remarks

### **Required for All Adjustments**
- Detailed explanation of reason
- Root cause if known
- Preventive measures if applicable

## Attachments

- **Required** for significant adjustments:
  - Investigation reports
  - Photos
  - Supporting documentation
  - Evidence of discrepancy

## Audit Requirements

Record for each adjustment:
- Item code and description
- Adjustment quantity (+ or -)
- Location
- Reason for adjustment
- Operator who requested
- Manager who approved
- Accountant who reviewed (if applicable)
- Timestamp
- Stock Entry reference
- Supporting documentation
- Remarks

## Future Mobile Considerations

- Mobile adjustment request interface
- Photo capture via mobile camera
- Offline adjustment queue
- Sync when connectivity returns

## Future Offline Considerations

- Queue adjustment requests offline
- Sync item/location data for offline reference
- Conflict detection if stock already adjusted
- Sync audit trail when online
