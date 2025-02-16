# Installation Guide

## Prerequisites

- Odoo 16.0
- Python 3.8+
- pip (Python package installer)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/dudoxx/dudoxx-boiler.git
```

### 2. Install Dependencies

```bash
cd dudoxx-boiler
pip install -r requirements.txt
```

### 3. Add to Odoo Addons Path

Add the module path to your Odoo configuration file (`odoo.conf`):

```conf
[options]
addons_path = /path/to/existing/addons,/path/to/dudoxx-boiler
```

Or start Odoo with the addons path:

```bash
./odoo-bin --addons-path=/path/to/existing/addons,/path/to/dudoxx-boiler
```

### 4. Update Odoo Apps List

1. Enable developer mode in Odoo
2. Go to Apps menu
3. Click 'Update Apps List'
4. Click 'Update'

### 5. Install the Module

1. Go to Apps menu
2. Search for "Dudoxx Boiler"
3. Click Install

## Configuration

### 1. Access Rights

After installation, configure user access rights:

1. Go to Settings → Users & Companies → Users
2. Select user to configure
3. Under "Access Rights" tab, find "Dudoxx Boiler"
4. Set appropriate access levels

### 2. General Settings

Configure module settings:

1. Go to Settings → Dudoxx Boiler
2. Configure available options:
   - Document Types
   - Workflow Settings
   - Security Levels

## Verification

Verify successful installation:

1. Check for new menu items:
   - Documents
   - Clients
2. Create test records
3. Verify workflow functionality

## Troubleshooting

### Common Issues

1. Module Not Visible
   - Verify addons path
   - Update apps list
   - Check access rights

2. Database Errors
   - Run database updates
   ```bash
   ./odoo-bin -d your_database -u dudoxx_boiler
   ```

3. Permission Issues
   - Check user access rights
   - Verify file permissions

### Getting Help

If you encounter issues:

1. Check logs:
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   ```

2. Contact Support:
   - Create GitHub issue
   - Visit [dudoxx.com](https://www.dudoxx.com)
   - Email support@dudoxx.com

## Upgrading

To upgrade the module:

1. Update code:
   ```bash
   git pull origin master
   ```

2. Update module:
   ```bash
   ./odoo-bin -d your_database -u dudoxx_boiler
   ```

3. Verify changes in Odoo interface

## Development Setup

For development:

1. Enable developer mode
2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Setup pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Security Notes

- Keep Odoo and Python updated
- Regularly check for module updates
- Follow security best practices
- Maintain proper access controls
