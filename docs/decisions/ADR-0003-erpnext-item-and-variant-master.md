# ADR-0003: ERPNext Item and Variant Master

## Status
Accepted

## Context
WMS needs to manage items for warehouse operations. A key decision is whether WMS should maintain its own item master or use ERPNext's Item and Item Variant system.

## Decision
**ERPNext Item and Item Variant remain master data.**

WMS will use ERPNext's Item and Item Variant system without creating a competing item master.

## Rationale

### Avoid Duplication
- Duplicate item masters lead to inconsistencies
- Reconciliation between systems is complex
- Single source of truth simplifies operations

### Leverage ERPNext Strengths
- ERPNext has a mature item management system
- ERPNext Item Variants are well-designed
- ERPNext integrates items with stock, accounting, and pricing
- ERPNext provides item templates and variant templates

### Simplify Integration
- No need to sync items between systems
- No conflict resolution for item discrepancies
- Simpler data model
- Fewer integration points

### Maintain Consistency
- Items consistent across all ERPNext modules
- Pricing consistent across purchasing and sales
- Stock consistent across all operations
- Accounting consistent with item valuation

## Consequences

### Positive
- Single source of truth for items
- No item reconciliation needed
- Automatic integration with stock and accounting
- Leverages existing ERPNext functionality
- Simpler architecture

### Negative
- WMS must work within ERPNext item constraints
- Cannot customize item structure beyond ERPNext capabilities
- Dependent on ERPNext item system
- Limited ability to add item-specific warehouse data

### WMS Item Usage
- WMS reads ERPNext Item for warehouse operations
- WMS extends item with warehouse-specific attributes (via custom fields if needed)
- WMS uses item barcodes for scanning
- WMS respects item stock parameters

### ERPNext Item Responsibilities
- Maintain item master data
- Manage item variants
- Handle item pricing
- Manage item stock parameters
- Provide item reports

## Item Extensions

### Custom Fields
- WMS may add custom fields to ERPNext Item if needed
- Custom fields for warehouse-specific attributes
- Custom fields for WMS workflow data
- Must not conflict with ERPNext core fields

### Warehouse Location Assignment
- Default warehouse can be set in ERPNext Item
- WMS extends with location hierarchy
- WMS may add preferred location fields

## Alternatives Considered

### Alternative 1: Separate WMS Item Master
- **Rejected**: Would create duplication and reconciliation issues
- **Rejected**: Would complicate integration with ERPNext
- **Rejected**: Would break consistency with stock and accounting

### Alternative 2: Hybrid Approach
- **Rejected**: Would still have some duplication
- **Rejected**: Would be complex to implement correctly
- **Rejected**: Would still have reconciliation issues

## Implementation Notes

### Item Integration
- WMS queries ERPNext Item for item data
- WMS uses item barcodes for scanning
- WMS respects item stock parameters
- WMS does not modify ERPNext Item core fields

### Variant Integration
- WMS uses ERPNext Item Variants
- WMS scans variant-specific barcodes
- WMS respects variant stock parameters
- WMS does not create separate variant system

### Custom Fields
- Add custom fields to ERPNext Item if needed for WMS
- Document custom field purpose
- Ensure custom fields don't conflict with ERPNext
- Consider migration implications

## Related Decisions
- [ADR-0001: ERPNext Stock as System of Record](ADR-0001-erpnext-stock-as-system-of-record.md)
- [ADR-0002: WMS Application Boundary](ADR-0002-wms-application-boundary.md)

## References
- ERPNext Item documentation
- ERPNext Item Variant documentation
- Frappe Framework documentation
