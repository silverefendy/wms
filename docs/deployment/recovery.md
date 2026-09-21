# Recovery Procedures

## Purpose
Restore system operations after data loss, corruption, or disaster.

## Recovery Scenarios

### Scenario 1: Database Corruption
**Symptoms:**
- Database errors
- Data inconsistencies
- Application crashes

**Recovery Steps:**
1. Identify corruption extent
2. Stop application
3. Restore from last known good backup
4. Verify data integrity
5. Restart application
6. Monitor for issues

### Scenario 2: Accidental Data Deletion
**Symptoms:**
- Missing records
- User reports deleted data

**Recovery Steps:**
1. Identify deletion time
2. Select appropriate backup
3. Restore to temporary environment
4. Extract deleted data
5. Import to production
6. Verify data

### Scenario 3: Server Failure
**Symptoms:**
- Server unresponsive
- Hardware failure
- Complete system outage

**Recovery Steps:**
1. Assess hardware damage
2. Procure replacement hardware
3. Install base OS
4. Restore from backup
5. Verify functionality
6. Switch DNS if needed

### Scenario 4: Ransomware/Malware
**Symptoms:**
- Encrypted files
- Ransom demands
- Suspicious activity

**Recovery Steps:**
1. Isolate affected systems
2. Identify malware
3. Wipe affected systems
4. Rebuild from clean backups
5. Scan for persistence
6. Update security measures

## Recovery Procedures

### Frappe Site Restore
```bash
# List available backups
bench --site <site-name> backup-list

# Restore from backup
bench --site <site-name> restore /path/to/backup/<backup-file>

# Restore with files
bench --site <site-name> restore --with-files /path/to/backup/<backup-file>
```

### Database Restore
```bash
# Stop application
sudo supervisorctl stop frappe:

# Restore database
mysql -u root -p <database_name> < backup.sql

# Or from compressed backup
gunzip < backup.sql.gz | mysql -u root -p <database_name>

# Start application
sudo supervisorctl start frappe:
```

### File Restore
```bash
# Restore site files
tar -xzf site-files-backup.tar.gz -C sites/<site-name>/public

# Restore configuration
tar -xzf config-backup.tar.gz -C sites/<site-name>/
```

## Recovery Testing

### Test Environment
- Use staging environment for recovery testing
- Test recovery procedures monthly
- Document any issues encountered
- Update procedures based on lessons learned

### Recovery Validation
After recovery, verify:
- Database integrity
- Application functionality
- User access
- Data completeness
- Configuration correctness

## Recovery Time Objectives

### RTO Targets
- Database corruption: 2 hours
- Data deletion: 4 hours
- Server failure: 8 hours
- Complete disaster: 24 hours

### RPO Targets
- Database corruption: 1 hour (last backup)
- Data deletion: Point-in-time recovery if possible
- Server failure: 1 hour (last backup)
- Complete disaster: 24 hours (last offsite backup)

## Communication

### During Recovery
- Notify stakeholders of incident
- Provide regular status updates
- Set expectations for recovery time
- Document all actions taken

### After Recovery
- Conduct post-incident review
- Document root cause
- Update procedures
- Implement preventive measures

## Documentation

### Recovery Log
Maintain a record of:
- Incident date and time
- Incident type
- Recovery actions taken
- Recovery time
- Personnel involved
- Lessons learned
- Preventive measures implemented

## Prevention

### Regular Maintenance
- Monitor system health
- Update software regularly
- Test backups regularly
- Review security measures

### Redundancy
- Consider redundant hardware
- Consider database replication
- Consider load balancing
- Consider geographic distribution

### Security
- Regular security audits
- Penetration testing
- Security training
- Incident response plan
