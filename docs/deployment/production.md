# Production Environment

## Purpose
Deploy WMS for production use with high availability and security.

## Infrastructure

```
VMware Virtual Machine (or bare metal)
  ?
Ubuntu Server LTS
  ?
Frappe Bench (Production Mode)
  ?
Frappe v16
  ?
ERPNext v16
  ?
WMS (production version)
```

## Server Requirements

### Minimum Specifications
- CPU: 4 cores
- RAM: 8 GB
- Disk: 200 GB (SSD recommended)
- Network: 1 Gbps
- Backup storage: Additional 200 GB

### Recommended Specifications
- CPU: 8+ cores
- RAM: 16+ GB
- Disk: 500+ GB (SSD)
- Network: 1 Gbps+
- Backup storage: 500+ GB
- Redundant power supply

## High-Availability Architecture (Future)

### Single Server (Initial)
```
[Production Server]
  +-- Frappe/ERPNext/WMS
  +-- MariaDB
  +-- Redis
  +-- Nginx
```

### Multi-Server (Future)
```
[Load Balancer]
  +-- [Web Server 1]
  +-- [Web Server 2]
  +-- [Web Server N]
       ?
[Database Server]
  +-- MariaDB Master
  +-- MariaDB Replica(s)
       ?
[Redis Server]
  +-- Redis Cluster
```

## Security

### Network Security
```bash
# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH (restrict to specific IPs)
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Install fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### SSL/TLS
```bash
# Use Let's Encrypt or commercial certificate
bench config lets_encrypt
bench --site production-wms.example.com set-ssl-certificate /path/to/cert
bench --site production-wms.example.com set-ssl-key /path/to/key
```

### Database Security
- Strong database passwords
- Restrict database access to localhost
- Regular database user audits
- Encrypted backups

### Application Security
- Disable developer mode
- Enable maintenance mode during updates
- Regular security updates
- Security monitoring

## Setup

### Base OS Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-dev python3-venv python3-pip python3-setuptools
sudo apt install nodejs npm
sudo apt install mariadb-server redis-server
sudo apt install git nginx htop
sudo apt install fail2ban
sudo apt install certbot python3-certbot-nginx
```

### MariaDB Configuration
```bash
# Edit MariaDB configuration
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf

# Recommended settings:
# innodb_buffer_pool_size = 4G
# innodb_log_file_size = 512M
# max_connections = 200

# Restart MariaDB
sudo systemctl restart mariadb
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

# Initialize bench in production mode
bench init frappe-v16 --frappe-branch version-16 --production

# Get apps
cd frappe-v16
bench get-app erpnext --branch version-16
bench get-app wms --git-url https://github.com/silverefendy/wms.git --branch main

# Create production site
bench new-site production-wms.example.com

# Install apps
bench --site production-wms.example.com install-app erpnext
bench --site production-wms.example.com install-app wms

# Configure
bench set-nginx-port production-wms.example.com 80
bench set-ssl-certificate production-wms.example.com /path/to/cert
bench set-ssl-key production-wms.example.com /path/to/key

# Configure production settings
bench --site production-wms.example.com set-config maintenance_mode 0
bench --site production-wms.example.com set-config developer_mode 0

# Build and start
bench build
sudo bench setup production frappe
bench start
```

## Monitoring

### System Monitoring
- CPU usage
- Memory usage
- Disk usage
- Network traffic
- Service health

### Application Monitoring
- Frappe health checks
- Queue length
- Database connections
- Response times
- Error rates

### Monitoring Tools
- Uptime monitoring
- Log aggregation
- Alerting system
- Performance metrics

## Deployment Process

### Deployment Checklist
1. Test in staging environment
2. Create backup before deployment
3. Notify users of maintenance window
4. Deploy during low-traffic period
5. Verify deployment success
6. Monitor for issues
7. Rollback if necessary

### Deployment Steps
```bash
# Create backup
bench --site production-wms.example.com backup

# Pull latest code
cd ~/frappe-bench/frappe-v16/apps/wms
git pull origin main

# Run migrations
cd ~/frappe-bench/frappe-v16
bench --site production-wms.example.com migrate

# Rebuild
bench build

# Restart
sudo supervisorctl restart frappe:
sudo supervisorctl restart frappe-redis:
sudo supervisorctl restart frappe-web:
```

### Rollback Procedure
```bash
# Restore from backup
bench --site production-wms.example.com restore /path/to/backup

# Or revert code
cd ~/frappe-bench/frappe-v16/apps/wms
git checkout previous-commit
bench build
sudo supervisorctl restart frappe:
```

## Maintenance

### Regular Tasks
- Daily backups
- Weekly log rotation
- Monthly security updates
- Quarterly performance review

### Updates
- Frappe framework updates
- ERPNext updates
- WMS updates
- OS updates

## Disaster Recovery

### Recovery Time Objective (RTO)
- Target: 4 hours

### Recovery Point Objective (RPO)
- Target: 1 hour (last backup)

### Recovery Procedures
See [recovery.md](recovery.md)

## Documentation

### Maintain
- Network diagram
- Configuration documentation
- Runbook for common issues
- Contact information
- Vendor contracts
