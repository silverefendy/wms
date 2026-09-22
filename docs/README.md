# WMS Documentation

This directory contains the complete documentation for the WMS project.

## Documentation Structure

### [Requirements](requirements/)
- [Business Requirements](requirements/business-requirements.md) - Business context and objectives
- [Functional Requirements](requirements/functional-requirements.md) - System functionality
- [Non-Functional Requirements](requirements/non-functional-requirements.md) - Quality attributes

### [Architecture](architecture/)
- [Architecture Overview](architecture/architecture.md) - System architecture
- [ERPNext vs WMS](architecture/erpnext-vs-wms.md) - Boundary definition
- [Data Model](architecture/data-model.md) - Conceptual data model
- [Permissions](architecture/permissions.md) - Access control design
- [Integration](architecture/integration.md) - ERPNext integration points
- [WMS Location Model](architecture/wms-location-model.md) - Physical location hierarchy

### [Workflows](workflows/)
- [Receiving](workflows/receiving.md)
- [Putaway](workflows/putaway.md)
- [Transfer](workflows/transfer.md)
- [Stock Count](workflows/stock-count.md)
- [Adjustment](workflows/adjustment.md)
- [Picking](workflows/picking.md)
- [Packing](workflows/packing.md)
- [POS](workflows/pos.md)

### [Deployment](deployment/)
- [Development](deployment/development.md)
- [Staging](deployment/staging.md)
- [Production](deployment/production.md)
- [Backup](deployment/backup.md)
- [Recovery](deployment/recovery.md)

### [Mobile](mobile/)
- [Offline Sync](mobile/offline-sync.md) - Offline synchronization architecture

### [Architecture Decisions](decisions/)
- [ADR-0001](decisions/ADR-0001-erpnext-stock-as-system-of-record.md) - ERPNext stock as system of record
- [ADR-0002](decisions/ADR-0002-wms-application-boundary.md) - WMS application boundary
- [ADR-0003](decisions/ADR-0003-erpnext-item-and-variant-master.md) - ERPNext item and variant master
- [ADR-0004](decisions/ADR-0004-offline-first-design.md) - Offline-first design
- [ADR-0005](decisions/ADR-0005-wms-physical-location-model.md) - WMS physical location model

### [Testing](testing/)
- [Foundation Validation](testing/foundation-validation.md) - Disposable Frappe/ERPNext installation gate
