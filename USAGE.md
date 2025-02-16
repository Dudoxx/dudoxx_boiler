# Usage Guide

## Overview

Dudoxx Boiler provides a reference implementation for Odoo module development. This guide covers key features and their usage.

## Client Management

### Creating Clients

1. Navigate to Clients → Clients
2. Click 'Create'
3. Fill required fields:
   - Name
   - Contact Information
   - Client Type
4. Optional fields:
   - Additional Details
   - Custom Fields
5. Click 'Save'

### Client Views

#### Kanban View
- Drag and drop for status changes
- Quick access to key information
- Color coding by status
- Quick actions menu

#### List View
- Sortable columns
- Smart search
- Bulk actions
- Export functionality

#### Form View
- Organized sections
- Collapsible content
- Document attachments
- Activity tracking

## Document Management

### Creating Documents

1. Navigate to Documents → Documents
2. Click 'Create'
3. Fill required information:
   - Document Name
   - Type
   - Category
4. Upload file if needed
5. Set access levels
6. Click 'Save'

### Document Workflow

#### State Management
1. Draft
   ```python
   # Create draft document
   doc = env['dudoxx_boiler.document'].create({
       'name': 'Test Document',
       'state': 'draft'
   })
   ```

2. Submit
   ```python
   # Submit document
   doc.action_submit()
   ```

3. Approve/Reject
   ```python
   # Approve document
   doc.action_approve()

   # Or reject
   doc.action_reject()
   ```

4. Expire/Reactivate
   ```python
   # Expire document
   doc.action_expire()

   # Reactivate
   doc.action_reactivate()
   ```

### Access Control

#### Setting Access Levels
1. Go to document form
2. Set access level:
   - Public
   - Internal
   - Confidential
3. Add specific users/groups

#### Managing Permissions
```python
# Check access
if doc.can_access(user):
    # Perform operations
    pass
```

## API Usage

### Client API

```python
from odoo import api, fields, models

class ExternalSystem(models.Model):
    _name = 'external.system'

    def get_client_info(self, client_id):
        client = self.env['dudoxx_boiler.client'].browse(client_id)
        return {
            'name': client.name,
            'documents': client.document_ids.mapped('name'),
            'status': client.state
        }

    def create_client(self, values):
        return self.env['dudoxx_boiler.client'].create(values)
```

### Document API

```python
def process_document(self, document_id):
    doc = self.env['dudoxx_boiler.document'].browse(document_id)

    # Check state
    if doc.state == 'draft':
        # Process draft
        pass

    # Update document
    doc.write({
        'processed': True,
        'process_date': fields.Datetime.now()
    })
```

## Customization

### Adding Custom Fields

```python
class CustomClient(models.Model):
    _inherit = 'dudoxx_boiler.client'

    custom_field = fields.Char(
        string='Custom Field',
        help='Custom field description'
    )
```

### Extending Functionality

```python
def custom_action(self):
    self.ensure_one()
    # Custom logic
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'dudoxx_boiler.client',
        'view_mode': 'form',
        'res_id': self.id,
    }
```

## Best Practices

### 1. State Management
- Always use provided action methods
- Validate state transitions
- Handle errors properly

### 2. Security
- Check access rights
- Use proper record rules
- Validate user input

### 3. Performance
- Use indexed fields
- Implement batch operations
- Optimize searches

## Examples

### 1. Create Client with Documents

```python
def create_client_with_docs(self):
    # Create client
    client = self.env['dudoxx_boiler.client'].create({
        'name': 'Test Client',
        'email': 'test@example.com'
    })

    # Add documents
    docs = self.env['dudoxx_boiler.document'].create([{
        'name': f'Document {i}',
        'client_id': client.id,
        'state': 'draft'
    } for i in range(3)])

    return client
```

### 2. Process Documents

```python
def process_documents(self):
    docs = self.env['dudoxx_boiler.document'].search([
        ('state', '=', 'draft')
    ])

    for doc in docs:
        try:
            doc.action_submit()
        except ValidationError as e:
            _logger.error(f"Error processing {doc.name}: {e}")
```

## Troubleshooting

### Common Issues

1. State Transition Errors
   - Check current state
   - Verify transition rules
   - Check user permissions

2. Access Rights
   - Verify user groups
   - Check record rules
   - Review access levels

3. Performance Issues
   - Use proper indexes
   - Implement batching
   - Optimize queries

## Support

For additional support:

1. Check documentation
2. Review example code
3. Create GitHub issue
4. Contact support@dudoxx.com
