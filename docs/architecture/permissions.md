# Permissions

## Permission Strategy

Use Frappe's built-in role and permission system. Do not build an independent permission engine.

## Initial Roles

### Administrator
- Full system access
- Can modify all documents
- Can manage users and roles
- Can configure system settings

### Warehouse Manager
- Manage warehouse operations
- Approve warehouse transactions
- Configure warehouse locations
- View all warehouse reports
- Manage warehouse users

### Warehouse Operator
- Perform warehouse operations
- Receive goods
- Putaway items
- Transfer items
- Perform stock counts
- View assigned warehouse data

### Purchasing Manager
- Manage purchase operations
- Approve purchase orders
- View purchasing reports
- Integrate with receiving

### Purchasing Staff
- Create purchase orders
- Manage supplier relationships
- View purchase documents

### Sales Manager
- Manage sales operations
- Approve sales orders
- View sales reports
- Integrate with fulfillment

### Sales Staff
- Create sales orders
- Manage customer relationships
- View sales documents

### Cashier
- Process POS transactions
- Handle returns
- View POS reports

### Accountant
- View accounting entries
- Reconcile accounts
- View financial reports
- Access audit trails

## Permission Levels

### Document-Level Permissions
- Create
- Read
- Write
- Delete
- Submit
- Cancel
- Amend

### Field-Level Permissions
- Read-only fields
- Hidden fields
- Mandatory fields

### Row-Level Permissions (Future)
- Warehouse restrictions
- Branch restrictions
- Company restrictions

## Warehouse/Company/Branch Restrictions

### Current Status
**Not implemented in bootstrap phase.**

### Future Design
The system should support:
- Restrict users to specific warehouses
- Restrict users to specific branches
- Restrict users to specific companies

### Design Principle
Restrictions should be **optional**, not mandatory. Small single-warehouse operations should not need to configure complex restrictions.

## Approval Permissions

### Approval Categories
- Purchase approval
- Transfer approval
- Adjustment approval
- Stock count approval
- Return approval
- Discount approval

### Approval Thresholds
- Configurable per role
- Configurable per document type
- Multi-level approval support

## Data Access

### Read Access
- Users can read documents they have permission for
- Reports respect role permissions
- API access respects role permissions

### Write Access
- Users can only modify documents they have permission for
- Submit/cancel operations require specific permissions
- Critical operations require approval

## Audit Trail

### Permission Changes
- All permission changes logged
- Role assignments tracked
- Permission modifications audited

### Document Access
- Document access logged (configurable)
- Critical operations always logged
- Audit trail viewable by authorized users

## Integration with ERPNext Permissions

### ERPNext Roles
- WMS roles extend or complement ERPNext roles
- Existing ERPNext roles can be used
- Custom WMS roles for warehouse-specific operations

### ERPNext Permissions
- Respect ERPNext document permissions
- Extend ERPNext permissions for WMS documents
- Do not bypass ERPNext permission system

## Security Best Practices

### Principle of Least Privilege
- Users get minimum required permissions
- Permissions granted based on role
- Regular permission audits

### Separation of Duties
- Separate roles for incompatible operations
- Approval workflows for critical operations
- Audit trail for sensitive operations

### Role Management
- Document role definitions
- Regular role reviews
- Clear role responsibilities
