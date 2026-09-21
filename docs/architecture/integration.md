# Integration

## Integration Philosophy

WMS integrates with ERPNext through standard Frappe mechanisms:
- Document references
- Event hooks
- API calls
- Custom DocTypes that extend ERPNext functionality

## Purchasing Integration

### Flow

```
Supplier
  ?
Purchase Order (ERPNext)
  ?
Purchase Receipt (ERPNext)
  ?
Receiving Workflow (WMS)
  ?
Putaway Workflow (WMS)
  ?
Appropriate ERPNext stock-affecting document
  ?
Purchase Invoice (ERPNext)
  ?
Payment (ERPNext)
```

### Integration Points

#### Purchase Order
- ERPNext Purchase Order is the source document
- WMS reads Purchase Order for expected receipts
- WMS does not modify Purchase Order

#### Purchase Receipt
- ERPNext Purchase Receipt records goods receipt
- WMS Receiving workflow wraps Purchase Receipt
- WMS adds barcode scanning and location assignment
- WMS triggers Putaway workflow after receipt

#### Stock-affecting transaction
- WMS uses the standard ERPNext document appropriate to the business event
- ERPNext updates the Stock Ledger and accounting through normal document processing

### WMS Responsibilities
- Receiving workflow with barcode scanning
- Putaway workflow with location assignment
- Exception handling during receiving
- Quality check workflow (future)

### ERPNext Responsibilities
- Purchase Order management
- Purchase Receipt creation
- Standard stock-affecting document processing
- Stock Ledger updates
- Accounting entries
- Payment processing

## Sales Integration

### Flow

```
Customer
  ?
Sales Order (ERPNext)
  ?
Picking Workflow (WMS)
  ?
Packing Workflow (WMS)
  ?
Delivery Note (ERPNext)
  ?
Sales Invoice (ERPNext)
  ?
Payment (ERPNext)
```

### Integration Points

#### Sales Order
- ERPNext Sales Order is the source document
- WMS reads Sales Order for fulfillment
- WMS does not modify Sales Order

#### Picking
- WMS Picking workflow reads Sales Order
- WMS creates picking list with locations
- WMS guides picker through optimal route
- WMS reserves stock (future)

#### Packing
- WMS Packing workflow follows picking
- WMS creates packing list
- WMS generates shipping labels (future)

#### Delivery Note
- ERPNext Delivery Note records delivery
- WMS triggers Delivery Note creation after packing
- Delivery Note updates stock through normal ERPNext processing

### WMS Responsibilities
- Picking workflow with location guidance
- Packing workflow
- Exception handling during fulfillment
- Route optimization (future)

### ERPNext Responsibilities
- Sales Order management
- Delivery Note creation
- Standard stock-affecting document processing
- Stock Ledger updates
- Sales Invoice creation
- Payment processing

## POS Integration

### Flow

```
WMS/POS UI
  ?
ERPNext POS
  ?
POS Invoice (ERPNext)
  ?
Appropriate ERPNext stock-affecting document
  ?
Stock Ledger (ERPNext)
  ?
Accounting (ERPNext)
```

### Integration Points

#### POS Invoice
- ERPNext POS Invoice is the source document
- WMS may provide custom POS UI
- WMS does not create separate POS stock engine

#### Stock Updates
- POS Invoice uses the standard ERPNext POS stock flow
- ERPNext updates the Stock Ledger and accounting through normal document processing

### WMS Responsibilities
- Custom POS UI (future)
- Barcode scanning in POS
- Exception handling in POS
- Mobile POS interface (future)

### ERPNext Responsibilities
- POS Invoice creation
- Standard stock-affecting document processing
- Stock Ledger updates
- Accounting entries
- Payment processing

## Standard Stock-Affecting Document Integration

### Direct Stock Entry
- Users can create Stock Entry directly in ERPNext
- WMS does not prevent direct Stock Entry
- WMS provides workflow around Stock Entry for complex operations

### WMS-Triggered ERPNext Transactions
- WMS workflows use the standard ERPNext stock-affecting document appropriate to the business event
- Examples include Purchase Receipt, Delivery Note, Sales Invoice with stock update, Purchase Invoice with stock update, Stock Entry, Stock Reconciliation, POS Invoice/stock flow, and manufacturing transactions
- Documents are created or updated through the Frappe/ERPNext API and follow ERPNext validation
- The selected standard document updates ERPNext's Stock Ledger through normal ERPNext processing

## Stock Ledger Integration

### Read Access
- WMS reads Stock Ledger for stock queries
- WMS does not modify Stock Ledger directly
- WMS uses Frappe API for queries

### Write Access
- Stock Ledger is updated only through normal ERPNext processing of standard stock-affecting documents
- WMS does not write to Stock Ledger directly
- WMS does not use SQL to modify Stock Ledger

## Accounting Integration

### Automatic Accounting
- Stock Entry automatically creates accounting entries
- WMS does not modify accounting entries
- WMS does not bypass ERPNext accounting

### Financial Visibility
- WMS workflows reference financial documents
- WMS does not create independent financial records
- Accounting remains in ERPNext

## API Integration

### WMS API Endpoints
- Custom API endpoints for warehouse operations
- API endpoints respect Frappe permissions
- API endpoints use Frappe authentication

### ERPNext API Usage
- WMS calls ERPNext API for document operations
- WMS uses Frappe client API
- WMS does not bypass ERPNext validation

## Event Hooks

### Document Events
- WMS hooks into ERPNext document events
- Hooks used for workflow triggers
- Hooks used for validation
- Hooks used for notifications

### Stock Entry Events
- Before submit: Validate WMS workflow completion
- After submit: Trigger WMS next workflow step
- On cancel: Handle WMS workflow cancellation

## Error Handling

### Integration Errors
- WMS handles integration errors gracefully
- Errors logged with context
- Users notified of integration failures
- Retry mechanisms for transient failures

### Data Consistency
- WMS validates data before calling ERPNext
- WMS handles ERPNext validation errors
- Rollback mechanisms for failed operations
- Audit trail for all integration operations
