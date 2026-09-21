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
Stock Entry (ERPNext)
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

#### Stock Entry
- WMS Putaway creates ERPNext Stock Entry
- Stock Entry updates Stock Ledger
- Stock Entry triggers accounting entries

### WMS Responsibilities
- Receiving workflow with barcode scanning
- Putaway workflow with location assignment
- Exception handling during receiving
- Quality check workflow (future)

### ERPNext Responsibilities
- Purchase Order management
- Purchase Receipt creation
- Stock Entry processing
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
- Delivery Note creates Stock Entry
- Stock Entry updates Stock Ledger

### WMS Responsibilities
- Picking workflow with location guidance
- Packing workflow
- Exception handling during fulfillment
- Route optimization (future)

### ERPNext Responsibilities
- Sales Order management
- Delivery Note creation
- Stock Entry processing
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
Stock Entry (ERPNext)
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
- POS Invoice triggers Stock Entry
- Stock Entry updates Stock Ledger
- Stock Entry triggers accounting entries

### WMS Responsibilities
- Custom POS UI (future)
- Barcode scanning in POS
- Exception handling in POS
- Mobile POS interface (future)

### ERPNext Responsibilities
- POS Invoice creation
- Stock Entry processing
- Stock Ledger updates
- Accounting entries
- Payment processing

## Stock Entry Integration

### Direct Stock Entry
- Users can create Stock Entry directly in ERPNext
- WMS does not prevent direct Stock Entry
- WMS provides workflow around Stock Entry for complex operations

### WMS-Triggered Stock Entry
- WMS workflows create Stock Entry
- Stock Entry is created via Frappe API
- Stock Entry follows ERPNext validation
- Stock Entry updates Stock Ledger

## Stock Ledger Integration

### Read Access
- WMS reads Stock Ledger for stock queries
- WMS does not modify Stock Ledger directly
- WMS uses Frappe API for queries

### Write Access
- Stock Ledger is only updated via Stock Entry
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
