# ERPNext vs WMS Boundary

## Responsibility Matrix

| Area | ERPNext | WMS |
|------|---------|-----|
| **Item Master** | System of record | Extend/use |
| **Item Variant** | System of record | Use |
| **UOM** | System of record | Use |
| **Warehouse** | System of record | Extend for operational hierarchy |
| **Stock Ledger** | System of record | Do not duplicate |
| **Stock Valuation** | System of record | Use |
| **Stock Entry** | System of record | Trigger/use |
| **Purchase Order** | System of record | Use |
| **Purchase Receipt** | System of record | Warehouse workflow around it |
| **Sales Order** | System of record | Use |
| **Sales Invoice** | System of record | Use |
| **POS Invoice** | System of record | Use |
| **Accounting Ledger** | System of record | Use |
| **Receiving** | Base transaction | Operational workflow |
| **Putaway** | Limited/standard foundation | WMS workflow |
| **Picking** | ERP process/document integration | WMS workflow |
| **Packing** | ERP process/document integration | WMS workflow |
| **Stock Count workflow** | Base stock functionality | WMS operational workflow |
| **Mobile warehouse UI** | Not primary | WMS |
| **Offline synchronization** | Not assumed | WMS (future) |
| **Zone/Aisle/Rack/Shelf/Bin** | Not standard | WMS extension |
| **Warehouse operational rules** | Limited | WMS |
| **Exception handling** | Basic | WMS enhanced |

## Design Boundary Notes

This is a **design boundary**, not a statement that ERPNext has zero functionality in these areas.

### ERPNext Has Some Functionality
ERPNext does have:
- Basic receiving through Purchase Receipt
- Basic stock transfers through Stock Entry
- Basic stock count functionality
- Limited warehouse location support

### WMS Extends These Areas
WMS provides:
- Enhanced receiving workflows with barcode scanning
- Structured putaway with location assignment
- Optimized picking with route planning
- Structured packing workflows
- Granular location hierarchy (Zone ? Bin)
- Mobile-first interfaces
- Exception handling and approval workflows
- Future offline capability

## Integration Approach

### WMS Does NOT
- Create a second stock ledger
- Maintain competing stock quantities
- Directly manipulate ERPNext stock via SQL
- Replace ERPNext accounting
- Duplicate ERPNext master data

### WMS DOES
- Use ERPNext Stock Entry for all stock movements
- Trigger ERPNext documents from WMS workflows
- Extend ERPNext Warehouse with operational hierarchy
- Provide warehouse-specific user interfaces
- Handle warehouse operational exceptions
- Future: queue transactions for offline sync

## Data Ownership

### Owned by ERPNext
- Item master data
- Stock balances
- Stock ledger entries
- Accounting entries
- Customer data
- Supplier data
- Purchase documents
- Sales documents
- POS documents

### Owned by WMS
- Warehouse location hierarchy (Zone, Aisle, Rack, Shelf, Bin)
- Warehouse workflow documents
- Mobile-specific configurations
- Exception records
- Future: offline transaction queue

## API Boundaries

### WMS Calls ERPNext
- Stock Entry creation
- Stock Ledger queries
- Item data retrieval
- Warehouse data retrieval
- Purchase/Sales document queries

### ERPNext Calls WMS
- Custom hooks for stock entry events
- Custom hooks for document events
- Custom API endpoints for warehouse operations

## Migration Path

When moving from ERPNext-only to ERPNext+WMS:
- Existing ERPNext data remains authoritative
- WMS extends existing warehouses
- No data migration required for core ERPNext documents
- WMS-specific data added incrementally
