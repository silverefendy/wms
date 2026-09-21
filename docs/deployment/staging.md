# Staging Environment

## Purpose
Provide a pre-production environment for testing WMS before production deployment.

## Infrastructure

```
VMware Virtual Machine
  ?
Ubuntu Server
  ?
Frappe Bench
  ?
Frappe v16
  ?
ERPNext v16
  ?
WMS (staging version)
```

## Server Requirements

### Minimum Specifications
- CPU: 2 cores
- RAM: 4 GB
- Disk: 50 GB
- Network: Standard

### Recommended Specifications
- CPU: 4 cores
- RAM: 8 GB
- Disk: 100 GB
- Network: High speed

## Setup

### Base OS Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-dev python3-venv python3-pip python3-setuptools
sudo apt install nodejs npm
sudo apt install mariadb-server redis-server
sudo apt install git nginx
sudo apt install htop
sudo apt install fail2ban
```

### Security Setup
```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Secure MariaDB
sudo mysql_secure_installation

# Create dedicated user
sudo adduser frappe
sudo usermod -aG sudo frappe
```

### Frappe Bench Setup
```bash
# Switch to frappe user
sudo su - frappe

# Install bench
pip3 install frappe-bench

# Create bench directory
mkdir ~/frappe-bench
cd ~/frappe-bench

# Initialize bench
bench init frappe-v16 --frappe-branch version-16 --production

# Get apps
cd frappe-v16
bench get-app erpnext --branch version-16
bench get-app wms --git-url https://github.com/silverefendy/wms.git --branch main

# Create staging site
bench new-site staging-wms.example.com

# Install apps
bench --site staging-wms.example.com install-app erpnext
bench --site staging-wms.example.com install-app wms

# Configure
bench set-nginx-port staging-wms.example.com 80
bench set-ssl-certificate staging-wms.example.com /path/to/cert
bench set-ssl-key staging-wms.example.com /path/to/key

# Build and start
bench build
bench start
```

## Configuration

### Production Mode
Staging should run in production mode to closely match production:
```bash
bench --site staging-wms.example.com set-config maintenance_mode 0
bench --site staging-wms.example.com set-config developer_mode 0
```

### Data Management
- Use anonymized or synthetic data for testing
- Do not use real customer data
- Regular data refresh from production (with anonymization)

## Monitoring

### System Monitoring
```bash
# Monitor resources
htop

# Monitor disk space
df -h

# Monitor logs
tail -f ~/frappe-bench/frappe-v16/logs/frappe-*.log
```

### Application Monitoring
- Monitor Frappe health
- Monitor queue length
- Monitor database connections
- Monitor response times

## Testing

### Before Production Deployment
1. Run all automated tests
2. Perform manual testing of critical workflows
3. Test data migrations
4. Test performance under load
5. Test rollback procedures

### Test Data
- Use representative test data
- Test with various item quantities
- Test with various user roles
- Test exception scenarios

## Deployment to Staging

### Automated Deployment (Recommended)
```bash
# From development
cd apps/wms
git push origin feature/branch

# On staging server
cd ~/frappe-bench/frappe-v16/apps/wms
git pull origin main
cd ~/frappe-bench/frappe-v16
bench migrate
bench build
bench restart
```

### Manual Deployment
```bash
# Pull latest code
cd ~/frappe-bench/frappe-v16/apps/wms
git pull origin main

# Run migrations
cd ~/frappe-bench/frappe-v16
bench --site staging-wms.example.com migrate

# Rebuild
bench build

# Restart
bench restart
```

## Backup and Recovery

### Regular Backups
```bash
# Automated daily backups
bench --site staging-wms.example.com backup

# Backup script in cron
0 2 * * * cd ~/frappe-bench/frappe-v16 && bench --site staging-wms.example.com backup
```

### Recovery
```bash
# Restore from backup
bench --site staging-wms.example.com restore /path/to/backup
```

## Access Control

### User Access
- Limited access to authorized developers
- SSH key authentication required
- No direct root access
- Audit trail for all access

### Network Access
- VPN or whitelist for access
- No public access unless required
- Separate authentication for testing

## Documentation

### Keep Updated
- Document any configuration changes
- Document any customizations
- Document any issues encountered
- Document resolution procedures
