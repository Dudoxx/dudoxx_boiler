# Common Pitfalls and Solutions in Odoo Development

## 1. Model Definition Pitfalls

### Incorrect Inheritance
```python
# WRONG - Missing _inherit or _name
class MyModel(models.Model):
    # No _name or _inherit defined
    name = fields.Char()

# CORRECT
class MyModel(models.Model):
    _name = 'module.model'
    _description = 'My Model'
    _inherit = ['mail.thread']
```

### Field Definition Issues
```python
# WRONG - Inefficient indexing
partner_id = fields.Many2one('res.partner', index=True)  # Index on rarely searched field
create_date = fields.Datetime(index=True)  # Redundant index

# CORRECT
partner_id = fields.Many2one('res.partner')  # No index needed if rarely searched
name = fields.Char(index=True)  # Index on frequently searched field
```

## 2. View Definition Pitfalls

### XML Syntax Issues
```xml
<!-- WRONG - Missing field attributes -->
<field name="partner_id"/>

<!-- CORRECT - Proper field definition -->
<field name="partner_id"
       options="{'no_create': True}"
       context="{'default_type': 'contact'}"
       domain="[('type', '=', 'contact')]"/>

<!-- WRONG - Incorrect attrs syntax -->
<field name="name" attrs="{'invisible': state == 'draft'}"/>

<!-- CORRECT - Proper attrs syntax -->
<field name="name" attrs="{'invisible': [('state', '=', 'draft')]}"/>
```

### Form View Structure
```xml
<!-- WRONG - Missing required elements -->
<form>
    <field name="name"/>
</form>

<!-- CORRECT - Proper form structure -->
<form>
    <header>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <div class="oe_title">
            <h1><field name="name"/></h1>
        </div>
        <!-- Content -->
    </sheet>
</form>
```

## 3. Business Logic Pitfalls

### Recordset Operations
```python
# WRONG - Inefficient looping
for record in self:
    for line in record.line_ids:
        line.write({'state': 'done'})

# CORRECT - Batch operations
self.mapped('line_ids').write({'state': 'done'})

# WRONG - Multiple writes
def process_lines(self):
    for line in self.line_ids:
        line.write({'state': 'done'})
        line.write({'processed': True})

# CORRECT - Single write
def process_lines(self):
    self.line_ids.write({
        'state': 'done',
        'processed': True
    })
```

### Compute Methods
```python
# WRONG - Inefficient compute
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        total = 0
        for line in record.line_ids:
            total += line.amount
        record.total = total

# CORRECT - Efficient compute
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

## 4. Security Pitfalls

### Access Rights
```python
# WRONG - No security checks
def approve_document(self):
    self.state = 'approved'

# CORRECT - With security checks
def approve_document(self):
    if not self.env.user.has_group('module.group_approver'):
        raise AccessError(_('Only approvers can approve documents'))
    self.state = 'approved'
```

### Record Rules
```xml
<!-- WRONG - Too permissive rule -->
<record id="rule_documents" model="ir.rule">
    <field name="domain_force">[(1, '=', 1)]</field>
</record>

<!-- CORRECT - Proper security rule -->
<record id="rule_documents" model="ir.rule">
    <field name="domain_force">[
        '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
    ]</field>
</record>
```

## 5. Performance Pitfalls

### Search Operations
```python
# WRONG - Inefficient search
partners = self.env['res.partner'].search([])
filtered = partners.filtered(lambda p: p.name.startswith('A'))

# CORRECT - Efficient search
partners = self.env['res.partner'].search([
    ('name', 'like', 'A%')
])
```

### Lazy Loading
```python
# WRONG - Eager loading all fields
records = self.search([]).read()

# CORRECT - Load only needed fields
records = self.search([]).read(['name', 'date'])
```

## 6. UI/UX Pitfalls

### Button States
```xml
<!-- WRONG - No state indication -->
<button name="action_approve" type="object" string="Approve"/>

<!-- CORRECT - Clear state indication -->
<button name="action_approve" type="object"
        string="Approve" class="btn-primary"
        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

### Field Visibility
```xml
<!-- WRONG - Confusing visibility rules -->
<field name="partner_id"
       attrs="{'invisible': [('type', '!=', 'contact')],
              'readonly': [('state', '!=', 'draft')]}"/>

<!-- CORRECT - Clear visibility rules -->
<field name="partner_id"
       attrs="{'invisible': [('type', '!=', 'contact')],
              'readonly': [('state', 'in', ['confirmed', 'done'])]}"
       options="{'no_create': True}"/>
```

## 7. Data Handling Pitfalls

### Default Values
```python
# WRONG - Mutable default
_defaults = {
    'line_ids': []  # Mutable default
}

# CORRECT - Using default method
@api.model
def default_get(self, fields):
    res = super().default_get(fields)
    if 'line_ids' in fields:
        res['line_ids'] = []
    return res
```

### Data Migration
```python
# WRONG - Unsafe migration
def migrate(cr, version):
    cr.execute("UPDATE table SET field = 'value'")

# CORRECT - Safe migration
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    records = env['module.model'].search([])
    records.write({'field': 'value'})
```

## 8. Testing Pitfalls

### Test Setup
```python
# WRONG - Missing setup
class TestModel(common.TransactionCase):
    def test_something(self):
        # Direct test without setup
        pass

# CORRECT - Proper setup
class TestModel(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner'
        })

    def test_something(self):
        # Test with proper setup
        pass
```

### Test Isolation
```python
# WRONG - Test dependencies
def test_create(self):
    # Depends on previous test
    self.partner.write({'name': 'New Name'})

# CORRECT - Independent tests
def test_create(self):
    partner = self.env['res.partner'].create({
        'name': 'Test Partner'
    })
    partner.write({'name': 'New Name'})
```

## 9. Common Solutions

### 1. Use Proper Tools
- Use Odoo's development mode
- Utilize debug logging
- Implement proper error handling

### 2. Follow Best Practices
- Use conventional naming
- Implement proper security
- Write comprehensive tests
- Document your code

### 3. Performance Optimization
- Use indexed fields appropriately
- Implement batch operations
- Optimize search operations
- Use computed fields wisely

### 4. Security Implementation
- Always check access rights
- Implement proper record rules
- Use proper security groups
- Validate user input

### 5. Code Organization
- Separate business logic
- Use proper inheritance
- Implement proper view structure
- Follow Odoo conventions
