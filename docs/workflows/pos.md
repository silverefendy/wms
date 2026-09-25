# POS Workflow

**Actors**: Cashier, Store Manager
**Inputs**: Customer, items to purchase, payment method

## Flow

1. Cashier starts a transaction; system creates a new **POS Invoice**.
2. Cashier scans each item; system displays price and checks stock availability.
3. Item is added to the cart; system updates the total and validates stock.
4. Cashier processes payment and the system confirms it.
5. Cashier completes the transaction; system submits the POS Invoice, which ERPNext processes through its standard POS stock flow, updating the Stock Ledger through normal document processing; receipt is printed.

## Exceptions & Approval

| Exception | Handling | Requires Approval |
|---|---|---|
| Out of stock | Alert cashier; item cannot proceed, may be removed | — |
| Invalid barcode | Alert; manual entry option | Manual entry requires approval |
| Payment failure | Alert; retry or use an alternative method | — |
| Price discrepancy (scanned vs. marked) | Alert cashier | Yes, for override |

Discounts above threshold and returns also require approval.

## ERPNext Integration

- **Created**: POS Invoice, processed through the standard ERPNext POS stock flow.
- **Referenced**: Item, Warehouse, Customer, Payment Method.
- Stock decreases from the warehouse and accounting entries are created through normal ERPNext processing.

## Remarks & Attachments

- Optional remarks for a normal transaction.
- **Required** for price overrides, manual entries, returns, or any deviation.
- Attachments: receipts, return documentation.

## Audit Fields

Transaction ID, items sold, quantities, prices, payment method, customer, cashier, timestamp, POS Invoice reference, stock document reference, exceptions, approval, remarks.

## Future Considerations (Mobile & Offline)

Mobile POS with barcode scanning and receipt printing. Offline: queue POS transactions, sync item/price/stock data, detect conflicts if stock was already sold, sync audit trail once online.
