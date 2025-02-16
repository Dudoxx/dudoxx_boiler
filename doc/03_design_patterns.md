# Odoo Design Patterns

## 1. Service Layer Pattern

### Description
Separate business logic from field definitions by using a service layer pattern.

### Implementation
```python
# fields.py - Field definitions only
class Document(models.Model):
    _name = 'module.document'

    name = fields.Char(required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ], default='draft')

# services.py - Business logic
class DocumentServices(models.Model):
    _inherit = 'module.document'

    def action_submit(self):
        self.ensure_one()
        self._validate_submission()
        self._process_submission()
        self._notify_stakeholders()
```

## 2. State Machine Pattern

### Description
Manage complex state transitions with a clear state machine pattern.

### Implementation
```python
class Document(models.Model):
    # State definitions
    STATES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ]

    # State transition rules
    STATE_TRANSITIONS = {
        'draft': ['submitted'],
        'submitted': ['approved', 'rejected', 'expired'],
        'approved': ['expired', 'rejected'],
        'rejected': ['draft', 'submitted'],
        'expired': ['draft']
    }

    def _validate_state_transition(self, new_state):
        self.ensure_one()
        if new_state not in self.STATE_TRANSITIONS[self.state]:
            raise ValidationError(
                f'Cannot transition from {self.state} to {new_state}'
            )
```

## 3. Observer Pattern

### Description
Use Odoo's built-in message system for the observer pattern.

### Implementation
```python
class Document(models.Model):
    _name = 'module.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([...], tracking=True)

    def action_approve(self):
        self.state = 'approved'
        self.message_post(
            body='Document approved',
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
```

## 4. Factory Pattern

### Description
Use factory methods to create complex objects with proper defaults.

### Implementation
```python
class Document(models.Model):
    @api.model
    def create_from_template(self, template_id, **kwargs):
        """Factory method to create document from template"""
        template = self.env['document.template'].browse(template_id)
        vals = template._prepare_document_values()
        vals.update(kwargs)
        return self.create(vals)

    @api.model
    def create_draft(self, **kwargs):
        """Factory method for draft documents"""
        vals = {
            'state': 'draft',
            'create_date': fields.Datetime.now(),
        }
        vals.update(kwargs)
        return self.create(vals)
```

## 5. Composite Pattern

### Description
Handle hierarchical structures like document categories.

### Implementation
```python
class Category(models.Model):
    _name = 'module.category'
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(required=True)
    parent_id = fields.Many2one('module.category', string='Parent Category')
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('module.category', 'parent_id', string='Child Categories')

    def get_full_path(self):
        """Get category path from root"""
        self.ensure_one()
        path = []
        current = self
        while current:
            path.insert(0, current.name)
            current = current.parent_id
        return ' / '.join(path)
```

## 6. Strategy Pattern

### Description
Use different strategies for different document types.

### Implementation
```python
class Document(models.Model):
    _name = 'module.document'

    document_type = fields.Selection([
        ('simple', 'Simple'),
        ('complex', 'Complex')
    ], required=True)

    def process_document(self):
        """Process document based on type"""
        strategy = self._get_processing_strategy()
        return strategy.process()

    def _get_processing_strategy(self):
        strategies = {
            'simple': SimpleProcessingStrategy(self),
            'complex': ComplexProcessingStrategy(self)
        }
        return strategies[self.document_type]

class ProcessingStrategy:
    def __init__(self, document):
        self.document = document

    def process(self):
        raise NotImplementedError()

class SimpleProcessingStrategy(ProcessingStrategy):
    def process(self):
        # Simple processing logic
        pass
```

## 7. Decorator Pattern

### Description
Add functionality to models using inheritance and delegation.

### Implementation
```python
class DocumentBase(models.Model):
    _name = 'module.document.base'

    name = fields.Char(required=True)

    def process(self):
        return {'status': 'processed'}

class DocumentWithApproval(models.Model):
    _name = 'module.document.approval'
    _inherit = 'module.document.base'

    approver_id = fields.Many2one('res.users')

    def process(self):
        result = super().process()
        if self.approver_id:
            result['approver'] = self.approver_id.name
        return result
```

## 8. Command Pattern

### Description
Encapsulate actions as objects for better reusability.

### Implementation
```python
class DocumentCommand:
    def __init__(self, env):
        self.env = env

    def execute(self):
        raise NotImplementedError()

    def rollback(self):
        raise NotImplementedError()

class SubmitDocumentCommand(DocumentCommand):
    def __init__(self, env, document_id):
        super().__init__(env)
        self.document = self.env['module.document'].browse(document_id)

    def execute(self):
        self.document.state = 'submitted'
        self.document.submission_date = fields.Datetime.now()

    def rollback(self):
        self.document.state = 'draft'
        self.document.submission_date = False
```

## 9. Template Method Pattern

### Description
Define skeleton of operations allowing subclasses to override specific steps.

### Implementation
```python
class DocumentProcessor(models.AbstractModel):
    _name = 'module.document.processor'

    def process_document(self, document):
        """Template method"""
        self._validate(document)
        self._preprocess(document)
        self._process(document)
        self._postprocess(document)

    def _validate(self, document):
        """Hook method"""
        pass

    def _preprocess(self, document):
        """Hook method"""
        pass

    def _process(self, document):
        """Required override"""
        raise NotImplementedError()

    def _postprocess(self, document):
        """Hook method"""
        pass

class InvoiceProcessor(models.Model):
    _name = 'module.invoice.processor'
    _inherit = 'module.document.processor'

    def _process(self, document):
        # Specific invoice processing logic
        pass
```

## 10. Repository Pattern

### Description
Encapsulate data access logic in repository classes.

### Implementation
```python
class DocumentRepository(models.AbstractModel):
    _name = 'module.document.repository'

    def find_by_reference(self, reference):
        return self.env['module.document'].search(
            [('reference', '=', reference)], limit=1
        )

    def find_all_active(self):
        return self.env['module.document'].search([
            ('active', '=', True)
        ])

    def find_by_state(self, state, limit=None):
        domain = [('state', '=', state)]
        return self.env['module.document'].search(
            domain, limit=limit
        )
```

## 11. Builder Pattern

### Description
Construct complex objects step by step.

### Implementation
```python
class DocumentBuilder:
    def __init__(self, env):
        self.env = env
        self.vals = {}

    def set_name(self, name):
        self.vals['name'] = name
        return self

    def set_type(self, doc_type):
        self.vals['document_type'] = doc_type
        return self

    def set_partner(self, partner_id):
        self.vals['partner_id'] = partner_id
        return self

    def add_line(self, product_id, quantity):
        if 'line_ids' not in self.vals:
            self.vals['line_ids'] = []
        self.vals['line_ids'].append((0, 0, {
            'product_id': product_id,
            'quantity': quantity
        }))
        return self

    def build(self):
        return self.env['module.document'].create(self.vals)
```

## Best Practices for Pattern Usage

1. **Pattern Selection**
   - Choose patterns based on actual needs
   - Don't over-engineer simple solutions
   - Consider maintenance implications

2. **Implementation**
   - Keep pattern implementations consistent
   - Document pattern usage clearly
   - Use patterns to improve code organization

3. **Testing**
   - Test pattern implementations thoroughly
   - Include pattern-specific test cases
   - Verify pattern behavior in edge cases

4. **Documentation**
   - Document pattern purpose and usage
   - Include example implementations
   - Explain pattern benefits and tradeoffs
