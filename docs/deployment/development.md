# Development Environment

## Purpose
Setup a local development environment for WMS development and testing.

## Infrastructure

```
Local Development Machine
  ?
Frappe Bench
  ?
Frappe v16
  ?
ERPNext v16
  ?
WMS (development version)
```

## Prerequisites

### System Requirements
- Operating System: Debian 13+, Ubuntu 24.04+, or Windows with WSL2
- Python 3.14
- Node.js 24
- MariaDB 11.8
- Redis/Valkey 6+
- Git

Use the exact patch/minor versions and supported host packages from the current official Frappe v16 installation guidance.

### Software Installation

#### Ubuntu/WSL2
```bash
# Install dependencies
sudo apt update
sudo apt install python3-dev python3-venv python3-pip python3-setuptools
sudo apt install nodejs npm
sudo apt install mariadb-server redis-server
sudo apt install git
sudo apt install libffi-dev libssl-dev

# Install bench
pip3 install frappe-bench

# Create bench directory
mkdir ~/frappe-bench
cd ~/frappe-bench

# Initialize bench
bench init frappe-v16 --frappe-branch version-16
```

#### Windows (Native)
- Use WSL2 for best compatibility
- Or use Docker with Frappe container

## Setup Development Bench

```bash
# Navigate to bench
cd ~/frappe-bench/frappe-v16

# Get ERPNext v16
bench get-app erpnext --branch version-16

# Get WMS (development)
# Option 1: From local repository
bench get-app wms --git-url https://github.com/silverefendy/wms.git

# Option 2: From local directory (for development)
# ln -s /path/to/local/wms apps/wms

# Create development site
bench new-site dev-wms.local

# Install ERPNext
bench --site dev-wms.local install-app erpnext

# Install WMS
bench --site dev-wms.local install-app wms

# Build assets
bench build

# Start development server
bench start
```

## Development Workflow

### Running the Server
```bash
# Start bench in development mode
bench start

# Access site
# http://dev-wms.local:8000
```

### Making Changes
```bash
# After code changes
bench build

# After database changes (migrations)
bench migrate

# Restart server
bench restart
```

### Debugging
```bash
# Enable developer mode
bench --site dev-wms.local set-config developer_mode 1

# View logs
bench doctor

# Console access
bench --site dev-wms.local console
```

## Development Tools

### Code Quality
```bash
# Python linting (if configured)
flake8 wms/

# JavaScript linting (if configured)
eslint wms/
```

### Testing
```bash
# Run tests
bench --site dev-wms.local run-tests --app wms

# Run specific test
bench --site dev-wms.local run-tests --app wms --module wms.test_module
```

## Database Management

### Backup
```bash
# Backup site
bench --site dev-wms.local backup

# Restore site
bench --site dev-wms.local restore /path/to/backup
```

### Reset
```bash
# Drop and recreate site (WARNING: deletes all data)
bench drop-site dev-wms.local
bench new-site dev-wms.local
bench --site dev-wms.local install-app erpnext
bench --site dev-wms.local install-app wms
```

## Configuration

### site_config.json
Located in `sites/dev-wms.local/site_config.json`:
```json
{
  "db_name": "dev_wms",
  "db_password": "your_password",
  "developer_mode": true,
  "frappe_user": "administrator",
  "admin_password": "admin"
}
```

## Common Issues

### Port Already in Use
```bash
# Change port in site_config.json
# "frappe_port": 8001
```

### Permission Errors
```bash
# Fix permissions
sudo chown -R $USER:$USER ~/frappe-bench
```

### Module Import Errors
```bash
# Clear cache
bench clear-cache

# Rebuild
bench build --app wms
```

## Git Workflow

### Branching
```bash
# Create feature branch
cd apps/wms
git checkout -b feature/your-feature

# Make changes
git add .
git commit -m "feat: your feature description"

# Push to GitHub
git push origin feature/your-feature
```

### Updating from Main
```bash
# Pull latest changes
git pull origin main

# Update in bench
bench get-app wms --git-url https://github.com/silverefendy/wms.git --branch main

# Run migrations
bench migrate
```
