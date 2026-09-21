# Putaway Workflow

## Purpose
Place received items into their designated storage locations within the warehouse.

## Actors
- Warehouse Operator
- Warehouse Manager

## Inputs
- Purchase Receipt (ERPNext)
- Receiving workflow completion
- Storage location assignments

## Normal Flow

1. **Initiate Putaway**
   - System lists items awaiting putaway
   - Operator selects item or batch to putaway

2. **Determine Location**
   - System suggests storage location based on rules
   - Operator confirms or changes location
   - Location hierarchy: Warehouse ? Zone ? Aisle ? Rack ? Shelf ? Bin

3. **Scan Location**
   - Operator scans location barcode
   - System validates location exists
   - System confirms location is available

4. **Confirm Quantity**
   - Operator confirms quantity to putaway
   - System validates against received quantity

5. **Complete Putaway**
   - Operator confirms putaway
   - System creates ERPNext Stock Entry
   - ERPNext updates the Stock Ledger through the appropriate standard document/API
   - Item marked as putaway

## Exceptions

### Location Full
- System alerts location is full
- Operator selects alternative location
- May require manager approval for non-standard location

### Invalid Location
- Operator scans invalid location
- System alerts and requires rescan
- Location must exist in hierarchy

### Quantity Mismatch
- Putaway quantity does not match received quantity
- System alerts operator
- May require manager approval

### Damaged During Putaway
- Operator records damage
- Exception document created
- Manager approval required

## Approval

### Approval Triggers
- Non-standard location assignment
- Quantity mismatch
- Damage during putaway

### Approval Process
- Manager reviews exception
- Manager approves or rejects
- System records approval decision

## ERPNext Integration

### Documents Created
- Appropriate ERPNext stock-affecting document/API

### Documents Referenced
- Purchase Receipt (ERPNext)
- Item (ERPNext)
- Warehouse (ERPNext)
- WMS Location (Zone/Aisle/Rack/Shelf/Bin)

### Stock Ledger Impact
- ERPNext updates the Stock Ledger through normal document processing
- Stock recorded in specific warehouse
- Location recorded in custom fields

## Remarks

### Normal Putaway
- Optional remarks field

### Exception Putaway
- **Required** remarks for:
  - Non-standard location
  - Quantity mismatch
  - Damage during putaway
  - Any deviation from standard process

## Attachments

- Photos of damage (if applicable)
- Location verification documents

## Audit Requirements

Record for each putaway:
- Item code and description
- Quantity putaway
- Source (Purchase Receipt)
- Destination location (full hierarchy)
- Operator who performed putaway
- Timestamp
- Stock Entry reference
- Any exceptions
- Approval if required
- Remarks

## Future Mobile Considerations

- Mobile scanning interface
- Location barcode scanning
- Suggested location display
- Offline putaway queue
- Sync when connectivity returns

## Future Offline Considerations

- Queue putaway transactions offline
- Sync location data for offline reference
- Conflict detection if multiple users putaway same item
- Sync audit trail when online
