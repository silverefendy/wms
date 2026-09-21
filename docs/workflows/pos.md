# POS Workflow

## Purpose
Process point-of-sale transactions with warehouse integration for stock updates.

## Actors
- Cashier
- Store Manager

## Inputs
- Customer
- Items to purchase
- Payment method

## Normal Flow

1. **Start Transaction**
   - Cashier initiates POS transaction
   - System creates new POS Invoice

2. **Scan Items**
   - Cashier scans item barcode
   - System displays item and price
   - System checks stock availability

3. **Add to Cart**
   - Item added to transaction
   - System updates total
   - System validates stock

4. **Process Payment**
   - Cashier selects payment method
   - Cashier processes payment
   - System confirms payment

5. **Complete Transaction**
   - Cashier completes transaction
   - System submits POS Invoice
   - ERPNext processes the POS Invoice through its standard stock flow
   - ERPNext updates the Stock Ledger through normal document processing
   - System prints receipt

## Exceptions

### Out of Stock
- Item has insufficient stock
- System alerts cashier
- Transaction cannot proceed for that item
- Cashier may remove item from transaction

### Invalid Barcode
- Barcode not recognized
- System alerts cashier
- Cashier may enter item manually
- Manual entry may require manager approval

### Payment Failure
- Payment processing fails
- System alerts cashier
- Cashier retries payment
- May require alternative payment method

### Price Discrepancy
- Scanned price differs from marked price
- System alerts cashier
- Manager approval required for price override
- Discount approval workflow

## Approval

### Approval Triggers
- Manual item entry
- Price overrides
- Discounts above threshold
- Returns

### Approval Process
- Manager reviews request
- Manager approves or rejects
- System records approval decision

## ERPNext Integration

### Documents Created
- POS Invoice (ERPNext)
- POS Invoice (ERPNext) - standard POS stock flow

### Documents Referenced
- Item (ERPNext)
- Warehouse (ERPNext)
- Customer (ERPNext)
- Payment Method (ERPNext)

### Stock Ledger Impact
- POS Invoice updates stock through normal ERPNext processing
- Stock decreased from warehouse
- Accounting entries created

## Remarks

### Normal Transaction
- Optional remarks field

### Exception Transaction
- **Required** remarks for:
  - Price overrides
  - Manual entries
  - Returns
  - Any deviation from standard process

## Attachments

- Receipts
- Return documentation

## Audit Requirements

Record for each POS transaction:
- Transaction ID
- Items sold
- Quantities
- Prices
- Payment method
- Customer
- Cashier
- Timestamp
- POS Invoice reference
- Stock Entry reference
- Any exceptions
- Approval if required
- Remarks

## Future Mobile Considerations

- Mobile POS interface
- Barcode scanning
- Receipt printing
- Offline POS queue
- Sync when connectivity returns

## Future Offline Considerations

- Queue POS transactions offline
- Sync item data for offline reference
- Sync price data for offline reference
- Sync stock data for offline reference
- Conflict detection if stock already sold
- Sync audit trail when online
