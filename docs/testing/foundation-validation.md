# Foundation Validation

Validation date: 2026-09-22

This record covers a disposable WSL Bench only. No production site or existing user site was used.

## Environment

| Component | Actual version |
|---|---|
| Frappe | 16.34.0 (`version-16`) |
| ERPNext | 16.35.0 (`version-16`) |
| Python | 3.14.4 (Bench WSL environment) |
| Node.js | 24.21.0 |
| MariaDB | 11.8.6 |
| Redis/Valkey | Redis 8.0.5 |
| Yarn | 1.22.22 |
| pip | 26.2.1 (Bench environment) |
| Bench | 5.31.0 |
| Disposable Bench | `/home/wmsgate/wms-foundation-gate` |
| Disposable Site | `wms.test` |

## Validation

| Check | Result | Evidence |
|---|---|---|
| Bench initialization | PASS | `bench init --frappe-branch version-16 wms-foundation-gate` |
| Frappe installation | PASS | `bench version` reports Frappe 16.34.0 |
| ERPNext installation | PASS | `bench get-app --branch version-16 ...erpnext.git`; site install succeeded |
| WMS fetch from GitHub | PASS | `bench get-app --branch main https://github.com/silverefendy/wms.git` |
| WMS package installation | PASS | Bench installed the editable package from the fetched GitHub checkout |
| Test site creation | PASS | `bench new-site wms.test` |
| ERPNext site installation | PASS | `bench --site wms.test install-app erpnext` |
| WMS site installation | PASS | `bench --site wms.test install-app wms` |
| App discovery | PASS | `bench --site wms.test list-apps` reports `frappe`, `erpnext`, and `wms` |
| Migration | PASS | `bench --site wms.test migrate` completed without errors |
| Asset build | PASS | `bench build --app wms` completed successfully |
| Site startup | PASS | `bench start` started web, socketio, worker, scheduler, and Redis services |
| HTTP smoke test | PASS | `curl -H 'Host: wms.test' http://127.0.0.1:8000` returned HTTP 200 |

## Findings Repaired During Gate

- README encoding was normalized to UTF-8 so the declared `readme` could be read by the Flit build backend.
- `wms/modules.txt` was emptied because the bootstrap has no custom modules or DocTypes; the previous `wms` entry pointed to a nonexistent `wms.wms` package.

## Scope Confirmation

- No Phase 1 business functionality was implemented.
- No operational custom DocTypes were added.
- No competing stock ledger or stock quantity engine exists.
- No Frappe or ERPNext core code was modified.
