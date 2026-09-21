# WMS — Inventory & Warehouse Management System

## Overview

WMS is a custom Frappe application built on ERPNext v16 that provides warehouse management capabilities while keeping ERPNext as the authoritative system of record for inventory and accounting.

## Core Principle

**ERPNext remains the source of truth for inventory and accounting.**

WMS extends ERPNext with warehouse workflows, operational interfaces, and mobile capabilities without duplicating stock ledgers or accounting data.

## Scope Status

### Architecture Scope

- Warehouse operational workflows layered on ERPNext
- Warehouse location hierarchy and warehouse-specific UI
- Mobile, exception, offline synchronization, and RFID integration boundaries
- Integration with ERPNext master data and standard stock-affecting documents

### Planned

- Receiving, putaway, transfer, picking, packing, stock count, and adjustment workflows
- Barcode/QR workflows, mobile UI, offline synchronization, RFID integration, and reporting
- Purchasing, sales, POS, manufacturing, reservation, and reorder integrations

### Implemented

- Frappe application scaffold and metadata
- Foundation and architecture documentation

### Not Yet Implemented

- All operational WMS workflows and custom operational DocTypes
- Mobile UI, offline synchronization, RFID integration, and business APIs

## Architecture

```mermaid
graph TD
    A[Users] --> B[Desktop]
    A --> C[Mobile]
    A --> D[POS/Kiosk]
    B --> E[Custom WMS App]
    C --> E
    D --> E
    E --> F[Warehouse Workflows]
    E --> G[Operational Rules]
    E --> H[Mobile Workflows]
    E --> I[Exceptions]
    E --> J[Offline Sync]
    F --> K[ERPNext]
    G --> K
    H --> K
    I --> K
    J --> K
    K --> L[Item]
    K --> M[Warehouse]
    K --> N[Stock Ledger]
    K --> O[Standard Stock-Affecting Documents]
    K --> P[Purchase]
    K --> Q[Sales]
    K --> R[POS]
    K --> S[Accounting]
```

## Requirements

- Frappe Framework v16
- ERPNext v16
- Python 3.14
- Node.js 24
- MariaDB 11.8
- Redis/Valkey 6+
- Yarn 1.22+
- pip 25.3+

These requirements follow the current official Frappe v16 installation guidance. Use its exact current patch/minor versions and supported host packages when setting up a Bench.

## Installation

```bash
# Get the app
bench get-app https://github.com/silverefendy/wms.git

# Install on your site
bench --site <site-name> install-app wms

# Build assets
bench build --app wms
```

## Development Status

- **Current Phase**: Foundation / Bootstrap
- See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed status
- See [ROADMAP.md](ROADMAP.md) for implementation phases
- See [docs/](docs/) for complete documentation

## Development Principles

1. **No Frappe core modifications** - Extend, do not modify
2. **No ERPNext core modifications** - Use standard APIs and hooks
3. **No duplicate stock ledger** - ERPNext Stock Ledger is authoritative
4. **Standard ERPNext documents** - Use existing DocTypes where possible
5. **Document architectural decisions** - All important decisions recorded as ADRs
6. **Tests required** - Non-trivial business logic must have tests
7. **Clean, minimal code** - Avoid premature abstractions and frameworks

## Documentation

- [Project Status](PROJECT_STATUS.md)
- [Roadmap](ROADMAP.md)
- [Business Requirements](docs/requirements/business-requirements.md)
- [Functional Requirements](docs/requirements/functional-requirements.md)
- [Non-Functional Requirements](docs/requirements/non-functional-requirements.md)
- [Architecture](docs/architecture/architecture.md)
- [ERPNext vs WMS](docs/architecture/erpnext-vs-wms.md)
- [Data Model](docs/architecture/data-model.md)
- [Permissions](docs/architecture/permissions.md)
- [Integration](docs/architecture/integration.md)
- [Workflows](docs/workflows/)
- [Deployment](docs/deployment/)
- [Mobile/Offline](docs/mobile/offline-sync.md)
- [Architecture Decisions](docs/decisions/)

## License

License status: Decision pending. Current repository classification is proprietary / all rights reserved unless a license is explicitly added. See [license.txt](wms/license.txt) for details.

## Repository

https://github.com/silverefendy/wms
