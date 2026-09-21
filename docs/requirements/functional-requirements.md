# Functional Requirements

## Item Management

### ERPNext Item as Master
- ERPNext Item remains the authoritative master data
- WMS extends and uses ERPNext Item, does not replace it
- Item Code, SKU, and identification fields are managed in ERPNext

### Item Identification
- **Item Code**: Unique identifier
- **SKU**: Stock Keeping Unit
- **Barcode**: Standard barcode support
- **QR Code**: QR code support
- **RFID**: RFID tag architecture (future capability)

### Item Attributes
- Categories and subcategories
- Model
- Brand
- Manufacturer
- Preferred supplier
- Color
- Size
- Dimensions (length, width, height)
- Weight
- Volume
- Country of origin

### Stock Parameters
- Minimum stock level
- Maximum stock level
- Reorder level
- Reorder quantity
- Safety stock
- Preferred supplier
- Default warehouse/location

### Item Types
Support for ERPNext item types:
- Stock items
- Non-stock items
- Service items
- Consumable items
- Asset items
- Bundle items
- Manufactured items
- Purchased items
- Sold items

## Item Variants

**Decision:** Use ERPNext standard Item Variants.

- Do not create a competing custom variant engine
- Leverage ERPNext's template and variant system
- WMS provides workflow around variant selection and scanning

## Unit of Measure (UOM)

### Multiple UOM Support
- Multiple UOMs per item
- Item-specific conversion ratios

### UOM Types
- Purchase UOM
- Stock UOM
- Selling UOM

### Conversion Examples
```
1 Box = 12 pcs
1 Roll = 50 meter
1 Carton = 24 box
1 Kg = 1000 gram
```

**Design principle:** Conversion ratio is Item-specific, not global.

## Identification Methods

### Barcode
- Standard barcode scanning
- Barcode generation
- Barcode printing

### QR Code
- QR code scanning
- QR code generation
- QR code printing

### RFID
- RFID tag reading architecture
- RFID as identification layer, not separate inventory engine
- Hardware integration (future)

## Stock Tracking

### Quantity Tracking
- Real-time quantity updates
- Per-location quantity tracking
- Aggregate quantity reporting

### Serial Number Tracking
- Unique serial number per item
- Serial number history
- Serial number tracking through warehouse

### Batch/Lot Tracking
- Batch/lot number assignment
- Batch/lot expiry tracking
- Batch/lot history
- FEFO (First Expired, First Out) support (future)

## Stock Operations

### Planned Operations
- **Receive**: Inbound goods receipt
- **Putaway**: Placement into storage locations
- **Transfer**: Movement between locations
- **Issue**: Outbound goods issue
- **Return**: Return of goods
- **Adjustment**: Stock quantity corrections
- **Stock Count**: Physical inventory counting
- **Pick**: Selection for outbound orders
- **Pack**: Preparation for shipment

## Remarks and Documentation

### Normal Transactions
- Optional remarks field
- Basic documentation

### Exceptional Operations
**Required meaningful remarks for:**
- Manual overrides
- Cancellations
- Rejections
- Adjustments
- Any operation that deviates from standard workflow

## Attachments

- Document/photo attachments for exceptions
- Proof of delivery/receipt
- Quality check documentation
- Damage photos

## Approval Workflows

### Initial Approval Categories
- Purchase operations
- Transfer operations
- Stock adjustments
- Stock count adjustments
- Returns processing
- Discount approvals

### Approval Thresholds
- Configurable approval thresholds
- Role-based approval rules
- Multi-level approval support
