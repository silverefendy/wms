# Backup Strategy

## Purpose
Ensure data can be recovered in case of data loss, corruption, or disaster.

## Backup Types

### Database Backups
- Full database backups
- Incremental backups (future)
- Transaction log backups (future)

### File Backups
- Site files
- Public files
- Private files
- Configuration files

### Application Backups
- Application code
- Customizations
- Migrations

## Backup Schedule

### Development
- On-demand backups before major changes
- No scheduled backups required

### Staging
- Daily backups
- Retention: 7 days

### Production
- Daily full backups
- Retention: 30 days
- Weekly backup to offsite storage
- Retention: 12 weeks

## Backup Commands

### Frappe Backup
```bash
# Standard backup (database + files)
bench --site <site-name> backup

# Backup with files
bench --site <site-name> backup --with-files

# Backup to specific directory
bench --site <site-name> backup --backup-path /path/to/backup/dir
```

### Manual Database Backup
```bash
# MariaDB backup
mysqldump -u root -p <database_name> > backup.sql

# Compressed backup
mysqldump -u root -p <database_name> | gzip > backup.sql.gz
```

### File Backup
```bash
# Backup site files
tar -czf site-files-backup.tar.gz sites/<site-name>/public

# Backup configuration
tar -czf config-backup.tar.gz sites/<site-name>/site_config.json
```

## Backup Storage

### Local Storage
- Primary backup location
- Fast access for quick recovery
- Disk space must be monitored

### Offsite Storage
- Secondary backup location
- Protects against site-wide disaster
- Cloud storage or remote server
- Encrypted during transfer and storage

### Backup Rotation
- Automatic deletion of old backups
- Configurable retention periods
- Manual override for critical backups

## Backup Automation

### Cron Jobs
```bash
# Daily backup at 2 AM
0 2 * * * cd ~/frappe-bench/frappe-v16 && bench --site production-wms.example.com backup

# Weekly offsite backup on Sunday at 3 AM
0 3 * * 0 cd ~/frappe-bench/frappe-v16 && bench --site production-wms.example.com backup && rsync -avz ~/frappe-bench/frappe-v16/sites/production-wms.example.com/private/backups/ user@remote-server:/backups/
```

### Backup Scripts
Create automated backup scripts with:
- Pre-backup validation
- Backup execution
- Post-backup verification
- Notification on failure
- Cleanup of old backups

## Backup Verification

### Integrity Checks
- Verify backup file integrity
- Test restore to non-production environment
- Verify database consistency
- Verify file completeness

### Regular Testing
- Monthly restore test
- Quarterly disaster recovery drill
- Annual full recovery test

## Backup Security

### Encryption
- Encrypt backups at rest
- Encrypt backups during transfer
- Secure encryption keys
- Key rotation policy

### Access Control
- Restrict backup access to authorized personnel
- Audit backup access logs
- Secure backup storage locations
- No backup credentials in code

## Backup Retention Policy

### Development
- No scheduled retention
- Manual cleanup as needed

### Staging
- 7 daily backups
- 4 weekly backups
- Manual cleanup of old backups

### Production
- 30 daily backups
- 12 weekly backups
- 12 monthly backups
- 1 yearly backup
- Manual override for critical backups

## Backup Documentation

### Backup Catalog
Maintain a record of:
- Backup date and time
- Backup type
- Backup location
- Backup size
- Backup checksum
- Retention period
- Restoration test results

## Recovery

### Recovery Procedures
See [recovery.md](recovery.md)

## Monitoring

### Backup Monitoring
- Monitor backup job success/failure
- Monitor backup storage space
- Monitor backup duration
- Alert on backup failures

### Metrics
- Backup success rate
- Backup duration
- Backup size
- Storage utilization
- Recovery time
