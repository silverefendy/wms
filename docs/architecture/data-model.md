# Data Model

## Conceptual Model

### Warehouse Location Hierarchy

```
Company
  ?
Branch
  ?
Warehouse
  ?
Zone (optional)
  ?
Aisle (optional)
  ?
Rack (optional)
  ?
Shelf (optional)
  ?
Bin (optional)
```

**Design Principle:** Lower-level locations are optional to allow small businesses to configure only the levels they need.

### Item Master Relationships

```
ERPNext Item
  +-- Variant Template
  +-- Item Variants
  +-- Barcodes
  +-- Serial Numbers
  +-- Batch/Lot Numbers
  +-- UOM Conversions
  +-- Default Warehouse
  +-- Stock Parameters
      +-- Reorder Level
      +-- Safety Stock
      +-- Min Stock
      +-- Max Stock
```

## ERPNext Documents Used

### Core ERPNext Documents
- **Item**: Product master data
- **Item Variant**: Product variants
- **Warehouse**: Storage location
- **Stock Entry**: Stock movement
- **Stock Ledger**: Stock balance history
- **Purchase Order**: Purchasing request
- **Purchase Receipt**: Goods receipt
- **Sales Order**: Sales request
- **Delivery Note**: Goods delivery
- **Sales Invoice**: Sales billing
- **POS Invoice**: POS transaction
- **Accounting Entry**: Financial transaction

### ERPNext Extended Documents
- **Warehouse**: Extended with WMS location hierarchy
- **Stock Entry**: Extended with WMS workflow references

## WMS Custom Documents (Future)

### Planned Custom DocTypes
**Note:** These will be created in future phases as needed. Not created in bootstrap phase.

#### Warehouse Location Extensions
- **WMS Zone**: Warehouse zone
- **WMS Aisle**: Warehouse aisle
- **WMS Rack**: Warehouse rack
- **WMS Shelf**: Warehouse shelf
- **WMS Bin**: Warehouse bin (lowest storage unit)

#### Workflow Documents
- **WMS Receiving**: Receiving workflow
- **WMS Putaway**: Putaway workflow
- **WMS Transfer**: Internal transfer workflow
- **WMS Stock Count**: Stock count workflow
- **WMS Adjustment**: Stock adjustment workflow
- **WMS Picking**: Picking workflow
- **WMS Packing**: Packing workflow

#### Exception Documents
- **WMS Exception**: Exception record
- **WMS Exception Resolution**: Exception resolution

## Data Model Principles

### Before Creating a Custom DocType

Ask these questions:
1. Does ERPNext already provide this?
2. Can ERPNext standard functionality be extended?
3. Is the custom DocType actually required?
4. Will it create duplicate state?
5. Does it have a clear business lifecycle?

### Custom DocType Criteria

Create a custom DocType only if:
- ERPNext does not provide equivalent functionality
- Extension through hooks is insufficient
- The document has a clear business lifecycle
- It does not duplicate ERPNext state
- It integrates cleanly with ERPNext documents

### Data Relationships

#### Stock Movement
```
WMS Workflow Document
  ? References ERPNext Stock Entry
  ? References ERPNext Stock Ledger (via Stock Entry)
  ? References ERPNext Item
  ? References ERPNext Warehouse
  ? References WMS Locations (Zone/Aisle/Rack/Shelf/Bin)
```

#### Purchasing Integration
```
ERPNext Purchase Order
  ? ERPNext Purchase Receipt
  ? WMS Receiving Document
  ? WMS Putaway Document
  ? ERPNext Stock Entry
```

#### Sales Integration
```
ERPNext Sales Order
  ? WMS Picking Document
  ? WMS Packing Document
  ? ERPNext Delivery Note
  ? ERPNext Stock Entry
```

## Data Integrity

### Constraints
- All stock movements must create ERPNext Stock Entry
- Stock balances must only be updated via ERPNext Stock Entry
- WMS documents must reference valid ERPNext documents
- Location hierarchy must be valid (parent must exist)

### Validation
- Validate ERPNext document references
- Validate location hierarchy
- Validate quantity consistency
- Validate serial/batch number assignments

## Data Migration

### Initial Setup
- No migration required for new installations
- Existing ERPNext warehouses can be extended with WMS locations
- Existing ERPNext items require no changes

### Future Migration
- WMS-specific data can be exported/imported
- ERPNext core data remains in ERPNext
- No direct database manipulation required
