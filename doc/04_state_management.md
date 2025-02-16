# State Management in Odoo

## State Flow Patterns

### 1. Basic State Flow
```python
class Document(models.Model):
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ], default='draft', tracking=True)
```

### 2. State Transitions Matrix
```
Current State │ Possible Next States
─────────────┼────────────────────────────────
Draft        │ Submitted
Submitted    │ Approved, Rejected, Expired
Approved     │ Expired, Rejected
Rejected     │ Draft, Submitted
Expired      │ Draft
```

### 3. State Validation Rules
```python
# Define allowed transitions
STATE_TRANSITIONS = {
    'draft': ['submitted'],
    'submitted': ['approved', 'rejected', 'expired'],
    'approved': ['expired', 'rejected'],
    'rejected': ['draft', 'submitted'],
    'expired': ['draft']
}

# State validation method
def _validate_state_transition(self, new_state):
    self.ensure_one()
    if new_state not in self.STATE_TRANSITIONS[self.state]:
        raise ValidationError(
            f'Cannot transition from {self.state} to {new_state}'
        )
```

## State Actions

### 1. Action Methods
```python
def action_submit(self):
    """Submit document for approval"""
    for record in self:
        if record.state not in ['draft', 'rejected']:
            raise ValidationError(
                'Only draft or rejected documents can be submitted!'
            )
        record.state = 'submitted'
    return True

def action_approve(self):
    """Approve document"""
    for record in self:
        if record.state not in ['submitted', 'expired']:
            raise ValidationError(
                'Only submitted or expired documents can be approved!'
            )
        record.state = 'approved'
    return True

def action_reject(self):
    """Reject document"""
    for record in self:
        if record.state not in ['submitted', 'approved']:
            raise ValidationError(
                'Only submitted or approved documents can be rejected!'
            )
        record.state = 'rejected'
    return True
```

### 2. State-based Validations
```python
@api.constrains('state', 'approver_id')
def _check_approval_requirements(self):
    for record in self:
        if record.state == 'approved' and not record.approver_id:
            raise ValidationError(
                'Approver is required for approved documents'
            )

@api.constrains('state', 'expiry_date')
def _check_expiry_date(self):
    for record in self:
        if record.state != 'expired' and record.expiry_date:
            if record.expiry_date < fields.Date.today():
                raise ValidationError(
                    'Document has expired'
                )
```

## View Integration

### 1. Form View Header
```xml
<header>
    <div class="d-flex justify-content-between align-items-center w-100">
        <div class="btn-group" role="group">
            <!-- Draft -> Submit -->
            <button name="action_submit" type="object"
                    string="Submit" class="btn btn-primary"
                    attrs="{'invisible': [('state', 'not in', ['draft', 'rejected'])]}"/>

            <!-- Submitted -> Approve/Reject -->
            <button name="action_approve" type="object"
                    string="Approve" class="btn btn-success"
                    attrs="{'invisible': [('state', 'not in', ['submitted', 'expired'])]}"/>
            <button name="action_reject" type="object"
                    string="Reject" class="btn btn-danger"
                    attrs="{'invisible': [('state', 'not in', ['submitted', 'approved'])]}"/>

            <!-- Reset to Draft -->
            <button name="action_reset_to_draft" type="object"
                    string="Reset to Draft" class="btn btn-secondary"
                    attrs="{'invisible': [('state', 'not in', ['submitted', 'rejected', 'expired'])]}"/>
        </div>
    </div>
    <field name="state" widget="statusbar"
           statusbar_visible="draft,submitted,approved,rejected,expired"/>
</header>
```

### 2. Kanban View State Management
```xml
<kanban>
    <field name="state"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <!-- State-based styling -->
                <div t-attf-class="oe_kanban_content
                    #{record.state.raw_value == 'approved' ? 'bg-success' :
                      record.state.raw_value == 'rejected' ? 'bg-danger' :
                      record.state.raw_value == 'expired' ? 'bg-warning' : ''}">

                    <!-- State-based actions -->
                    <div class="btn-group">
                        <button name="action_submit" type="object"
                                t-if="record.state.raw_value in ['draft', 'rejected']"
                                class="btn btn-primary btn-sm">Submit</button>
                        <!-- Other state-based buttons -->
                    </div>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

## State-based Business Logic

### 1. Computed Fields
```python
@api.depends('state')
def _compute_is_editable(self):
    for record in self:
        record.is_editable = record.state in ['draft', 'rejected']

@api.depends('state', 'expiry_date')
def _compute_status_info(self):
    for record in self:
        if record.state == 'expired':
            record.status_info = 'Expired'
        elif record.state == 'approved':
            if record.expiry_date:
                days = (record.expiry_date - fields.Date.today()).days
                record.status_info = f'Expires in {days} days'
            else:
                record.status_info = 'Approved'
        else:
            record.status_info = dict(record._fields['state'].selection).get(record.state)
```

### 2. State-based Domain Rules
```python
@api.model
def _search_valid_documents(self, operator, value):
    valid_states = ['approved']
    if operator == '=':
        domain = [('state', 'in', valid_states)]
    else:
        domain = [('state', 'not in', valid_states)]
    return domain

is_valid = fields.Boolean(
    string='Valid',
    compute='_compute_is_valid',
    search='_search_valid_documents'
)
```

### 3. Automatic State Updates
```python
@api.model
def _check_expired_documents(self):
    """Cron job to check and expire documents"""
    domain = [
        ('state', '=', 'approved'),
        ('expiry_date', '!=', False),
        ('expiry_date', '<', fields.Date.today())
    ]
    documents = self.search(domain)
    if documents:
        documents.write({'state': 'expired'})
        documents.message_post(
            body='Document automatically expired',
            message_type='notification'
        )
```

## State-based Security

### 1. Record Rules
```xml
<record id="rule_document_state_based" model="ir.rule">
    <field name="name">State-based Document Access</field>
    <field name="model_id" ref="model_module_document"/>
    <field name="domain_force">[
        '|',
        ('state', 'in', ['approved', 'expired']),
        '&amp;',
        ('state', 'not in', ['approved', 'expired']),
        ('create_uid', '=', user.id)
    ]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### 2. Method Access
```python
def action_approve(self):
    """Approve document with security check"""
    if not self.env.user.has_group('module.group_document_approver'):
        raise AccessError('Only approvers can approve documents')
    self._validate_state_transition('approved')
    self.write({
        'state': 'approved',
        'approver_id': self.env.user.id,
        'approval_date': fields.Datetime.now()
    })
```

## Testing State Management

### 1. State Transition Tests
```python
@tagged('post_install', '-at_install')
class TestDocumentStates(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.document = self.env['module.document'].create({
            'name': 'Test Document',
            'state': 'draft'
        })

    def test_submit_document(self):
        """Test document submission flow"""
        # Test submission
        self.document.action_submit()
        self.assertEqual(self.document.state, 'submitted')

        # Test invalid transition
        with self.assertRaises(ValidationError):
            self.document.action_submit()

    def test_complete_flow(self):
        """Test complete document flow"""
        # Draft -> Submitted
        self.document.action_submit()
        self.assertEqual(self.document.state, 'submitted')

        # Submitted -> Approved
        self.document.action_approve()
        self.assertEqual(self.document.state, 'approved')

        # Approved -> Expired
        self.document.action_expire()
        self.assertEqual(self.document.state, 'expired')

        # Expired -> Draft
        self.document.action_reset_to_draft()
        self.assertEqual(self.document.state, 'draft')
```

### 2. State Constraint Tests
```python
def test_state_constraints(self):
    """Test state-based constraints"""
    # Create document without required fields
    with self.assertRaises(ValidationError):
        self.env['module.document'].create({
            'name': 'Test',
            'state': 'approved'  # Should fail without approver
        })

    # Test expiry date constraint
    with self.assertRaises(ValidationError):
        self.document.write({
            'state': 'approved',
            'expiry_date': fields.Date.today() - timedelta(days=1)
        })
