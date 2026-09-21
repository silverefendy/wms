# ADR-0002: WMS Application Boundary

## Status
Accepted

## Context
WMS is being developed as a Frappe application alongside ERPNext. We need to define the boundary between WMS and ERPNext to avoid overlap and ensure clear separation of concerns.

## Decision
**WMS is an operational warehouse layer, not a replacement ERP.**

WMS extends ERPNext with warehouse-specific workflows and interfaces while ERPNext remains the core ERP system.

## Rationale

### Clear Separation of Concerns
- ERPNext handles ERP functions (accounting, purchasing, sales, POS)
- WMS handles warehouse operations (receiving, putaway, picking, packing)
- Each system focuses on its strengths

### Avoid Reimplementation
- ERPNext already has robust ERP functionality
- Reimplementing ERP features would be wasteful
- Leverage existing, tested ERPNext features

### Maintain Upgrade Path
- Clear boundary makes ERPNext upgrades easier
- Less risk of breaking changes
- Easier to maintain compatibility

### Future Flexibility
- WMS can be used with different ERPNext configurations
- WMS can potentially work with other ERPs (future)
- Clear boundary enables modular architecture

## Consequences

### Positive
- Clear separation between ERP and WMS
- Easier to understand and maintain
- Better upgrade path
- Leverages ERPNext investment
- Modular architecture

### Negative
- WMS cannot replace ERPNext functionality
- Must work within ERPNext constraints
- Some warehouse operations may be limited by ERPNext
- Dependent on ERPNext capabilities

### WMS Scope
- Warehouse workflows (receiving, putaway, transfer, picking, packing)
- Warehouse location hierarchy (Zone, Aisle, Rack, Shelf, Bin)
- Mobile warehouse interfaces
- Exception handling for warehouse operations
- Future: offline synchronization

### ERPNext Scope
- Item master data
- Stock ledger
- Accounting
- Purchasing (Purchase Order, Purchase Receipt)
- Sales (Sales Order, Delivery Note, Sales Invoice)
- POS
- Customer and Supplier management

## Boundary Definition

### WMS Owns
- Warehouse location hierarchy
- Warehouse workflow documents
- Mobile-specific configurations
- Exception records
- Future: offline transaction queue

### ERPNext Owns
- Item master
- Stock ledger
- Accounting ledger
- Purchase documents
- Sales documents
- POS documents
- Customer and Supplier data

### Shared/Integrated
- Standard ERPNext stock-affecting documents (selected by business event, owned by ERPNext)
- Warehouse (extended by WMS, owned by ERPNext)
- Stock movements (triggered by WMS, recorded by ERPNext)

## Alternatives Considered

### Alternative 1: WMS as Complete ERP Replacement
- **Rejected**: Would require reimplementing all ERP functionality
- **Rejected**: Would lose ERPNext benefits
- **Rejected**: Would be massive effort

### Alternative 2: WMS as Standalone System with Integration
- **Rejected**: Would create duplication
- **Rejected**: Would require complex integration
- **Rejected**: Would have synchronization issues

## Implementation Notes

### Integration Points
- All stock-affecting WMS operations ultimately use the appropriate standard ERPNext stock-affecting document/API; WMS does not maintain or directly modify a competing stock ledger.
- WMS reads ERPNext documents for workflow context
- WMS extends ERPNext Warehouse with location hierarchy
- WMS uses Frappe hooks for event integration

### Extension Mechanisms
- Custom DocTypes for WMS-specific data
- Hooks for ERPNext document events
- Custom API endpoints for warehouse operations
- Extension of ERPNext Warehouse DocType

## Related Decisions
- [ADR-0001: ERPNext Stock as System of Record](ADR-0001-erpnext-stock-as-system-of-record.md)
- [ADR-0003: ERPNext Item and Variant Master](ADR-0003-erpnext-item-and-variant-master.md)

## References
- ERPNext documentation
- Frappe Framework documentation
- Microservices architecture patterns
