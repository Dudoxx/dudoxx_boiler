# Odoo Development Best Practices

## Model Development

### 1. Field Definitions
```python
class ModelName(models.Model):
    _name = 'module.model'
    _description = 'Human readable description'
    _inherit = ['mail.thread'] # Only if needed
    _order = 'sequence, id desc'

    # Always group fields by type/purpose with clear comments
    # Required/Basic fields first
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        index=True
    )

    # Status and state fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ], default='draft', tracking=True)

    # Relational fields
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        ondelete='restrict'
    )

    # Computed fields last
    total = fields.Float(
        compute='_compute_total',
        store=True,
        compute_sudo=True
    )
```

### 2. Method Organization
```python
class ModelName(models.Model):
    # CRUD Methods
    @api.model_create_multi
    def create(self, vals_list):
        # Always use create multi
        return super().create(vals_list)

    # Compute Methods
    @api.depends('line_ids.amount')
    def _compute_total(self):
        for record in self:
            record.total = sum(record.line_ids.mapped('amount'))

    # Onchange Methods
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.email = self.partner_id.email

    # Constraint Methods
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start > record.date_end:
                raise ValidationError('Start date must be before end date')

    # Action Methods
    def action_submit(self):
        self.ensure_one()
        # Always validate state
        if self.state != 'draft':
            raise ValidationError('Only draft records can be submitted')
        self.state = 'submitted'
```

## View Development

### 1. Form Views
```xml
<!-- Group fields logically -->
<form>
    <header>
        <!-- Status bar and buttons -->
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <!-- Title and primary fields -->
        <div class="oe_title">
            <h1><field name="name"/></h1>
        </div>

        <!-- Content in cards -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <!-- Use proper Bootstrap classes -->
                </div>
            </div>
        </div>
    </sheet>
</form>
```

### 2. Tree Views
```xml
<!-- Keep it simple and focused -->
<tree decoration-info="state == 'draft'"
      decoration-success="state == 'done'">
    <field name="name"/>
    <field name="date"/>
    <field name="state"/>
    <!-- Include only necessary fields -->
</tree>
```

### 3. Search Views
```xml
<search>
    <!-- Basic search fields -->
    <field name="name"/>

    <!-- Filters -->
    <filter string="Draft" name="draft"
            domain="[('state', '=', 'draft')]"/>

    <!-- Group By -->
    <group expand="0" string="Group By">
        <filter string="State" name="group_by_state"
                context="{'group_by': 'state'}"/>
    </group>
</search>
```

## Security Best Practices

### 1. Access Rights
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model_user,model_module_model,base.group_user,1,1,1,0
access_model_manager,model_manager,model_module_model,base.group_system,1,1,1,1
```

### 2. Record Rules
```xml
<record id="rule_model_own_records" model="ir.rule">
    <field name="name">Own Records Only</field>
    <field name="model_id" ref="model_module_model"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

## Performance Best Practices

### 1. Search Optimization
```python
# Use proper indexes
name = fields.Char(index=True)
partner_id = fields.Many2one(index=True)

# Efficient searching
def _get_records(self):
    domain = [('state', '=', 'draft')]
    return self.search(domain)
```

### 2. Computed Fields
```python
# Store computed fields when frequently accessed
total = fields.Float(
    compute='_compute_total',
    store=True  # Store if used in search/sort
)

# Use compute_sudo for performance
count = fields.Integer(
    compute='_compute_count',
    compute_sudo=True  # When no security concerns
)
```

### 3. Batch Processing
```python
# Process records in batches
def process_records(self):
    for batch in tools.split_every(100, self.ids):
        records = self.browse(batch)
        records._process_batch()
```

## Error Handling

### 1. Validation Errors
```python
from odoo.exceptions import ValidationError

def validate_data(self):
    if not self.name:
        raise ValidationError('Name is required')
```

### 2. User Messages
```python
def action_process(self):
    try:
        self._process()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Process completed successfully',
                'type': 'success'
            }
        }
    except Exception as e:
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': str(e),
                'type': 'danger'
            }
        }
```

## Testing

### 1. Test Cases
```python
@tagged('post_install', '-at_install')
class TestModel(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner'
        })

    def test_compute_total(self):
        record = self.env['module.model'].create({
            'name': 'Test',
            'partner_id': self.partner.id
        })
        self.assertEqual(record.total, 0.0)
```

### 2. Test Data
```xml
<record id="test_record" model="module.model">
    <field name="name">Test Record</field>
    <field name="state">draft</field>
</record>
```

## Documentation

### 1. Code Documentation
```python
class ModelName(models.Model):
    """
    Model description and purpose.

    Key features:
    - Feature 1
    - Feature 2

    Important methods:
    - method_name: purpose
    """

    def method_name(self):
        """
        Method description.

        Returns:
            type: description

        Raises:
            ValidationError: condition
        """
```

### 2. Module Documentation
```
doc/
├── technical/
│   ├── architecture.md
│   └── api.md
├── user/
│   ├── installation.md
│   └── usage.md
└── development/
    ├── guidelines.md
    └── testing.md
