# Odoo Development Environment Setup Guide

This guide explains how to set up a complete Odoo development environment using Miniconda, Python 3.11, and VSCode.

## 1. Miniconda Installation

### Install Miniconda
1. Download Miniconda from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
2. Install for your platform (macOS, Linux, or Windows)

### Create Odoo Environment
```bash
# Create new environment with Python 3.11
conda create -n odoo-16-env python=3.11

# Activate environment
conda activate odoo-16-env

# Install required packages
pip install debugpy
pip install psycopg2-binary
pip install wheel
pip install -r requirements.txt  # from Odoo source
```

## 2. Odoo Source Installation

### Clone Odoo Source
```bash
# Set up directory structure
export ODOO_INSTALLATION=/Users/yourusername/dev/projects/odoo-boiler
mkdir -p $ODOO_INSTALLATION
cd $ODOO_INSTALLATION

# Clone Odoo 16.0
git clone https://github.com/odoo/odoo.git -b 16.0 --depth=1
```

### Install Dependencies
```bash
cd odoo
pip install -r requirements.txt
```

## 3. PostgreSQL Setup

### Install PostgreSQL
```bash
# macOS (using Homebrew)
brew install postgresql@14

# Start PostgreSQL
brew services start postgresql@14
```

### Create Database User
```sql
CREATE USER dudoxx_user WITH PASSWORD 'admin' CREATEDB;
```

## 4. Odoo Configuration

Create `odoo_16.conf` in your project directory:

```ini
[options]
addons_path = /Users/yourusername/dev/projects/odoo-boiler/odoo/addons,/Users/yourusername/dev/projects/your_project

db_host = localhost
db_port = 5432
db_user = dudoxx_user
db_password = admin
db_name = your_database
data_dir = /Users/yourusername/dudoxx/data_dir_your_project

xmlrpc_port = 8069
xmlrpc_interface = 0.0.0.0
proxy_mode = True
log_level = warn
odoo_env = /Users/yourusername/dev/projects/your_project/your_env.env

gevent_port = 8072
without_demo = all
limit_time_real = 1200
limit_memory_hard = 31457280000
limit_memory_soft = 29360128000
db_maxconn = 60
cache_timeout = 10800
query_cache_max = 8192
query_cache_size = 40960
http_enable = True
http_expire = 300
http_static_cache_time = 86400

#max_cron_threads = 1
#workers = 2

load_language = en_US
```

Note: The configuration includes:
- Project-specific data directory
- Environment file support
- Optimized memory settings
- Cache configuration
- Optional worker configuration (commented)

## 5. VSCode Setup

### Install Extensions
1. Python extension
2. Debugpy
3. Pylint
4. XML Tools

### Configure launch.json
Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Dudoxx Extensions Install",
      "type": "debugpy",
      "request": "launch",
      "program": "${env:ODOO_INSTALLATION}/odoo/odoo-bin",
      "args": [
        "-c",
        "${workspaceFolder}/odoo_16.conf",
        "-i",
        "base,your_module",
        "--dev",
        "xml"
      ],
      "env": {
        "PYTHONPATH": "${env:ODOO_INSTALLATION}/odoo"
      },
      "console": "integratedTerminal",
      "justMyCode": true,
      "cwd": "${workspaceFolder}",
      "python": "/Users/yourusername/miniconda3/envs/odoo-16-env/bin/python"
    },
    {
      "name": "Dudoxx Extensions Update",
      "type": "debugpy",
      "request": "launch",
      "program": "${env:ODOO_INSTALLATION}/odoo/odoo-bin",
      "args": [
        "-c",
        "${workspaceFolder}/odoo_16.conf",
        "-u",
        "your_module1,your_module2",
        "--dev",
        "xml"
      ],
      "env": {
        "PYTHONPATH": "${env:ODOO_INSTALLATION}/odoo"
      },
      "console": "integratedTerminal",
      "justMyCode": true,
      "cwd": "${workspaceFolder}",
      "python": "/Users/yourusername/miniconda3/envs/odoo-16-env/bin/python"
    }
  ]
}
```

Note: Set the ODOO_INSTALLATION environment variable:
```bash
export ODOO_INSTALLATION=/Users/yourusername/dev/projects/odoo-boiler
```

### Configure settings.json
Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "/Users/yourusername/miniconda3/envs/odoo-16-env/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.analysis.extraPaths": [
    "/Users/yourusername/dev/projects/odoo-boiler/odoo"
  ],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "[xml]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "redhat.vscode-xml"
  }
}
```

## 6. Directory Structure

Recommended project structure:

```
your_project/
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── odoo_16.conf
├── requirements.txt
└── your_modules/
    └── your_module/
        ├── __init__.py
        ├── __manifest__.py
        ├── models/
        ├── views/
        └── security/
```

## 7. Running Odoo

### First Time Setup
1. Activate conda environment:
   ```bash
   conda activate odoo-16-env
   ```

2. Create database:
   ```bash
   createdb -U dudoxx_user your_database
   ```

3. Install base modules:
   - Use VSCode debugger "Odoo Install" configuration
   - Or run from terminal:
     ```bash
     ./odoo-bin -c /path/to/odoo_16.conf -i base --dev xml
     ```

### Development Workflow
1. Make changes to your module
2. Use VSCode debugger "Odoo Update" configuration to update
3. Set breakpoints in VSCode for debugging
4. Access Odoo at http://localhost:8069

## 8. Debugging Tips

1. Use `--dev xml` for XML auto-reload
2. Set breakpoints in Python code
3. Use VSCode's Debug Console
4. Check Odoo logs in Terminal
5. Use developer mode in Odoo web interface

## 9. Common Issues

### Database Connection
- Verify PostgreSQL is running
- Check database user permissions
- Confirm database exists

### Module Not Found
- Check addons_path in config
- Verify module structure
- Clear browser cache

### Python Path Issues
- Verify PYTHONPATH in launch.json
- Check conda environment activation
- Confirm Python interpreter in VSCode

## 10. Best Practices

1. Always use conda environment
2. Keep modules organized
3. Use version control
4. Follow Odoo coding standards
5. Regular database backups
6. Document your code
7. Use proper debugging tools
