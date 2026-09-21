# Picking Workflow

## Purpose
Select and collect items from warehouse locations to fulfill sales orders.

## Actors
- Warehouse Operator (Picker)
- Warehouse Manager

## Inputs
- Sales Order (ERPNext)
- Picking list
- Item locations

## Normal Flow

1. **Receive Picking Assignment**
   - System assigns Sales Order to picker
   - Picker views picking list
   - Picking list shows items, quantities, and locations

2. **Navigate to Location**
   - System guides picker to first location
   - Optimal route calculation (future)
   - Picker scans location to confirm

3. **Scan Item**
   - Picker scans item barcode
   - System validates item matches picking list
   - System confirms item is in correct location

4. **Confirm Quantity**
   - Picker confirms quantity picked
   - System validates against picking list
   - System updates picked quantity

5. **Handle Exceptions**
   - If item not found, picker records exception
   - If insufficient quantity, picker records shortage
   - System flags for manager review

6. **Continue Picking**
   - System guides picker to next location
   - Repeat until all items picked

7. **Complete Picking**
   - Picker confirms picking complete
   - System validates all items picked
   - System triggers Packing workflow

## Exceptions

### Item Not Found
- Item not in expected location
- Picker records exception
- System searches other locations (future)
- Manager may need to locate item

### Insufficient Quantity
- Location has less than required quantity
- Picker records shortage
- System searches other locations (future)
- May require manager intervention

### Damaged Item
- Item is damaged
- Picker records damage
- Exception document created
- Manager approval required

### Wrong Item
- Picker scans wrong item
- System alerts picker
- Picker must scan correct item

## Approval

### Approval Triggers
- Significant shortages
- Damaged items
- Unable to locate items

### Approval Process
- Manager reviews picking exceptions
- Manager approves alternative actions
- System records approval decision

## ERPNext Integration

### Documents Referenced
- Sales Order (ERPNext)
- Item (ERPNext)
- Warehouse (ERPNext)
- WMS Location (Zone/Aisle/Rack/Shelf/Bin)
- Stock Ledger (ERPNext) - for available quantity

### Documents Created (Future)
- Delivery Note (ERPNext) - after packing
- Stock Entry (ERPNext) - after delivery

### Stock Reservation (Future)
- Reserve stock when picking starts
- Release reservation if picking fails
- Prevent double-picking

## Remarks

### Normal Picking
- Optional remarks field

### Exception Picking
- **Required** remarks for:
  - Item not found
  - Shortages
  - Damaged items
  - Any deviation from picking list

## Attachments

- Photos of damaged items
- Exception documentation

## Audit Requirements

Record for each pick:
- Item code and description
- Quantity picked
- Source location (full hierarchy)
- Sales Order reference
- Picker who performed pick
- Timestamp
- Any exceptions
- Approval if required
- Remarks

## Future Mobile Considerations

- Mobile picking interface
- Location barcode scanning
- Route guidance
- Voice picking (future)
- Offline picking queue
- Sync when connectivity returns

## Future Offline Considerations

- Queue picking transactions offline
- Sync picking list for offline reference
- Sync location data for offline reference
- Conflict detection if item already picked
- Sync audit trail when online
