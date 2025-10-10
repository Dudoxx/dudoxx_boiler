from odoo import models, fields, api


class ClientDocumentFields(models.Model):
    _name = "dudoxx_boiler.client_document"
    _description = "Client Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # Section Visibility Fields
    show_basic_info = fields.Boolean(string="Show Basic Info", default=True)
    show_file_info = fields.Boolean(string="Show File Info", default=True)
    show_dates = fields.Boolean(string="Show Dates", default=True)
    show_status = fields.Boolean(string="Show Status", default=True)
    show_security = fields.Boolean(string="Show Security", default=True)
    show_version = fields.Boolean(string="Show Version", default=True)
    show_relations = fields.Boolean(string="Show Relations", default=True)
    show_notes = fields.Boolean(string="Show Notes", default=True)

    def action_toggle_section(self):
        """Toggle visibility of a section."""
        self.ensure_one()
        section = self.env.context.get("section")
        if section:
            field_name = f"show_{section}"
            if hasattr(self, field_name):
                self[field_name] = not self[field_name]
        return True

    # Basic Information
    name = fields.Char(string="Name", required=True, tracking=True, help="Document name")

    reference = fields.Char(
        string="Reference", readonly=True, copy=False, default="New", help="Unique document reference"
    )

    # Document Details
    document_type = fields.Selection(
        [
            ("contract", "Contract"),
            ("invoice", "Invoice"),
            ("report", "Report"),
            ("certificate", "Certificate"),
            ("legal", "Legal Document"),
            ("identification", "Identification"),
            ("other", "Other"),
        ],
        string="Document Type",
        required=True,
        default="other",
        tracking=True,
    )

    category = fields.Selection(
        [
            ("financial", "Financial"),
            ("legal", "Legal"),
            ("personal", "Personal"),
            ("business", "Business"),
            ("medical", "Medical"),
            ("other", "Other"),
        ],
        string="Category",
        default="other",
    )

    # File Management
    file = fields.Binary(string="File", attachment=True, tracking=True, help="Upload document file")

    file_name = fields.Char(string="File Name")

    file_type = fields.Selection(
        [("pdf", "PDF"), ("doc", "Word Document"), ("xls", "Excel Sheet"), ("img", "Image"), ("other", "Other")],
        string="File Type",
        compute="_compute_file_type",
        store=True,
    )

    file_size = fields.Float(
        string="File Size (MB)", compute="_compute_file_size", store=True, help="Size of the uploaded file in megabytes"
    )

    # Dates and Validity
    date = fields.Date(
        string="Document Date", default=fields.Date.context_today, tracking=True, help="Date of the document"
    )

    expiry_date = fields.Date(string="Expiry Date", help="Document expiry date if applicable")

    days_to_expire = fields.Integer(
        string="Days to Expire",
        compute="_compute_days_to_expire",
        store=True,
        help="Number of days until document expires",
    )

    creation_datetime = fields.Datetime(string="Creation Time", default=fields.Datetime.now, readonly=True)

    # Status and Classification
    active = fields.Boolean(string="Active", default=True, tracking=True, help="Set to false to archive the document")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("expired", "Expired"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    priority = fields.Selection(
        [("0", "Low"), ("1", "Medium"), ("2", "High"), ("3", "Very High")], string="Priority", default="1"
    )

    # Security and Access
    is_confidential = fields.Boolean(string="Confidential", help="Mark document as confidential")

    access_level = fields.Selection(
        [
            ("public", "Public"),
            ("internal", "Internal"),
            ("confidential", "Confidential"),
            ("restricted", "Restricted"),
        ],
        string="Access Level",
        default="internal",
    )

    # Version Control
    version = fields.Char(string="Version", default="1.0", help="Document version number")

    previous_version_id = fields.Many2one("dudoxx_boiler.client_document", string="Previous Version")

    # Related Fields
    client_ids = fields.Many2many(
        comodel_name="dudoxx_boiler.client",
        relation="dudoxx_boiler_client_document_rel",
        column1="document_id",
        column2="client_id",
        string="Clients",
        tracking=True,
        help="Clients associated with this document",
    )

    department_id = fields.Many2one(
        "hr.department", string="Department", help="Department responsible for this document"
    )

    # Additional Information
    notes = fields.Html(string="Notes", help="Rich-text notes about the document")

    keywords = fields.Char(string="Keywords", help="Search keywords for the document")

    summary = fields.Text(string="Summary", help="Brief summary of the document content")

    icon = fields.Binary(string="Icon", attachment=True, help="Document type icon")

    icon_name = fields.Char(string="Icon Name")

    # Computed Fields
    @api.depends("file_name")
    def _compute_file_type(self):
        for record in self:
            if record.file_name:
                extension = record.file_name.split(".")[-1].lower() if "." in record.file_name else ""
                if extension in ["pdf"]:
                    record.file_type = "pdf"
                elif extension in ["doc", "docx"]:
                    record.file_type = "doc"
                elif extension in ["xls", "xlsx"]:
                    record.file_type = "xls"
                elif extension in ["jpg", "jpeg", "png", "gif"]:
                    record.file_type = "img"
                else:
                    record.file_type = "other"
            else:
                record.file_type = False

    @api.depends("file")
    def _compute_file_size(self):
        for record in self:
            if record.file:
                # Convert to MB (approximate calculation)
                record.file_size = len(record.file) / (1024 * 1024)
            else:
                record.file_size = 0

    @api.depends("expiry_date")
    def _compute_days_to_expire(self):
        today = fields.Date.today()
        for record in self:
            if record.expiry_date:
                delta = record.expiry_date - today
                record.days_to_expire = delta.days
            else:
                record.days_to_expire = False

    # Sequence Generation
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code("dudoxx_boiler.client_document") or "New"
        return super().create(vals_list)

    # Constraints
    class ConstraintUniqueReference(models.Constraint):
        _sql = "unique(reference)"
        _message = "Document reference must be unique!"
