# ADR-0001: ERPNext Stock as System of Record

## Status
Accepted

## Context
WMS is being built as a warehouse management layer on top of ERPNext. A key architectural decision is whether WMS should maintain its own stock ledger or rely on ERPNext's stock ledger.

## Decision
**ERPNext owns stock truth.**

WMS will NOT create a separate stock ledger. All stock balances and stock movements will be recorded in ERPNext's Stock Ledger.

## Rationale

### Avoid Duplication
- Duplicate stock ledgers lead to inconsistencies
- Reconciliation between systems is complex and error-prone
- Single source of truth simplifies operations

### Leverage ERPNext Strengths
- ERPNext has a mature, tested stock ledger
- ERPNext handles stock valuation automatically
- ERPNext integrates stock with accounting
- ERPNext provides stock reports and analytics

### Simplify Integration
- No need to sync stock between systems
- No conflict resolution for stock discrepancies
- Simpler data model
- Fewer integration points

### Maintain Audit Trail
- ERPNext stock ledger has built-in audit trail
- All stock movements are traceable
- Accounting integration is automatic

## Consequences

### Positive
- Single source of truth for stock
- No stock reconciliation needed
- Automatic accounting integration
- Leverages existing ERPNext functionality
- Simpler architecture

### Negative
- WMS must integrate through ERPNext transactions
- Cannot bypass ERPNext for stock operations
- Dependent on ERPNext stock ledger performance
- Limited ability to customize stock behavior

### WMS Integration Requirements
- All stock-affecting WMS operations must ultimately be recorded through the appropriate standard ERPNext stock-affecting document/API. The appropriate transaction depends on the business event and may include Purchase Receipt, Delivery Note, Sales Invoice with stock update, Purchase Invoice with stock update, Stock Entry, Stock Reconciliation, POS Invoice/stock flow, or manufacturing transactions.
- WMS workflows must trigger ERPNext transactions
- WMS cannot directly manipulate stock balances
- WMS must use Frappe APIs for stock operations
- No direct SQL to modify stock data

## Alternatives Considered

### Alternative 1: Separate WMS Stock Ledger
- **Rejected**: Would create duplication and reconciliation issues
- **Rejected**: Would complicate accounting integration
- **Rejected**: Would increase complexity significantly

### Alternative 2: Hybrid Approach
- **Rejected**: Would still have some duplication
- **Rejected**: Would be complex to implement correctly
- **Rejected**: Would still have reconciliation issues

## Implementation Notes

### Stock Movement Flow
```
WMS Workflow
  ? Appropriate ERPNext stock-affecting document/API
  ? ERPNext Stock Ledger
  ? ERPNext Accounting
```

### WMS Responsibilities
- Provide warehouse workflows around stock operations
- Extend warehouse location hierarchy
- Handle warehouse operational exceptions
- Provide mobile interfaces
- Future: offline transaction queue

### ERPNext Responsibilities
- Maintain stock ledger
- Calculate stock valuation
- Create accounting entries
- Provide stock reports
- Handle stock reservations (future)

## Related Decisions
- [ADR-0002: WMS Application Boundary](ADR-0002-wms-application-boundary.md)
- [ADR-0003: ERPNext Item and Variant Master](ADR-0003-erpnext-item-and-variant-master.md)

## References
- ERPNext Stock Ledger documentation
- ERPNext Stock Entry documentation
- Frappe Framework documentation
