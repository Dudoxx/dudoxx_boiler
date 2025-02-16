# File Organization Guide

## Directory Structure

```
dudoxx_boiler/
├── data/                    # Data files
│   ├── sequences.xml       # ID sequences
│   └── sample_data.xml     # Demo/sample data
├── models/                  # Model definitions
│   ├── client/             # Client-related models
│   │   ├── __init__.py
│   │   ├── client_fields.py      # Fields definitions
│   │   └── client_services.py    # Business logic/methods
│   └── client_document/    # Document-related models
│       ├── __init__.py
│       ├── client_document_fields.py
│       └── client_document_services.py
├── security/               # Security configurations
│   └── ir.model.access.csv
├── static/                # Static assets
│   ├── description/      # Module assets
│   │   └── icon.png
│   └── src/             # Source assets
│       ├── css/         # Stylesheets
│       └── assets/      # Images and other assets
├── views/                # View definitions
│   ├── client/          # Client views
│   │   ├── client_actions.xml
│   │   ├── client_form_view.xml
│   │   ├── client_kanban_view.xml
│   │   ├── client_search_view.xml
│   │   └── client_tree_view.xml
│   ├── client_document/ # Document views
│   │   └── ...
│   └── menus/          # Menu definitions
│       └── main_menu.xml
└── doc/                # Documentation
    ├── 01_file_organization.md
    ├── 02_best_practices.md
    ├── 03_design_patterns.md
    ├── 04_state_management.md
    └── 05_common_pitfalls.md
```

## Organization Principles

### 1. Feature-based Structure
- Group related files by feature (client, document)
- Separate fields from business logic
- Keep views organized by type and feature

### 2. Model Organization
- Split models into fields and services
- Fields files contain only field definitions
- Services files contain business logic and methods

### 3. View Organization
- Separate views by type (form, tree, kanban)
- Group related views in feature folders
- Keep menu definitions separate

### 4. Asset Management
- Organize static assets by type
- Keep module assets separate from source assets
- Use clear naming conventions

### 5. Documentation
- Keep documentation in dedicated doc folder
- Use numbered files for clear ordering
- Separate concerns into different files

## File Naming Conventions

### 1. Python Files
- Use snake_case for all Python files
- Suffix files based on content type (_fields.py, _services.py)
- Use __init__.py for module organization

### 2. XML Files
- Use descriptive names indicating content
- Include view type in filename for view files
- Group related XML files in feature folders

### 3. Asset Files
- Use lowercase with hyphens for CSS files
- Use descriptive names for images
- Include purpose in filename (e.g., client_avatar_1.png)

## Import Organization

### 1. Python Imports
```python
# Standard library imports
from datetime import date, datetime

# Odoo imports
from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Module imports
from . import client_fields
```

### 2. XML File Order
```xml
<!-- Load in this order -->
1. Security files
2. Data files
3. Views (form, tree, kanban, search)
4. Actions
5. Menu items
```

## Best Practices

1. **Modularity**
   - Keep files focused and single-purpose
   - Split large files into logical components
   - Use proper inheritance patterns

2. **Naming**
   - Use consistent naming across files
   - Make names descriptive and clear
   - Follow Odoo conventions

3. **Organization**
   - Group related files together
   - Maintain clear separation of concerns
   - Keep directory structure clean

4. **Documentation**
   - Document file purpose in header
   - Include relevant examples
   - Keep documentation up-to-date

5. **Dependencies**
   - Minimize cross-feature dependencies
   - Use proper import organization
   - Document required dependencies
