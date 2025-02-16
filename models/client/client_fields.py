# -*- coding: utf-8 -*-
###############################################################################
#
#    Dudoxx, Odoo Implementation
#    Copyright (C) 2024-TODAY Dudoxx (<https://www.dudoxx.com>)
#    Author: Walid Boudabbous
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api
from datetime import date

class ClientFields(models.Model):
    """Client model implementing comprehensive client management.

    This model provides a complete client management system with support for:
    - Personal and business information
    - Contact details and addresses
    - Financial tracking
    - Document management
    - Section visibility control

    Technical Details:
    - Inherits mail.thread for message history
    - Inherits mail.activity.mixin for activity management
    - Uses automatic sequences for references
    - Implements computed fields for age and document count
    - Enforces unique constraints on email and reference
    """
    _name = 'dudoxx_boiler.client'
    _description = 'Dudoxx Client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Section Visibility Fields
    show_basic_info = fields.Boolean(string="Show Basic Info", default=True)
    show_contact_info = fields.Boolean(string="Show Contact Info", default=True)
    show_address = fields.Boolean(string="Show Address", default=True)
    show_personal_info = fields.Boolean(string="Show Personal Info", default=True)
    show_business_info = fields.Boolean(string="Show Business Info", default=True)
    show_financial_info = fields.Boolean(string="Show Financial Info", default=True)
    show_documents = fields.Boolean(string="Show Documents", default=True)

    def action_toggle_section(self):
        """Toggle visibility of a form section.

        This method handles the collapsible sections in the form view.
        It toggles the visibility state of the specified section based
        on the context.

        Returns:
            bool: Always returns True

        Context Keys:
            section (str): The section identifier to toggle (e.g., 'basic_info')

        Example:
            >>> # Toggle basic info section
            >>> record.with_context(section='basic_info').action_toggle_section()
        """
        self.ensure_one()
        section = self.env.context.get('section')
        if section:
            field_name = f'show_{section}'
            if hasattr(self, field_name):
                self[field_name] = not self[field_name]
        return True

    # Basic Information
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help='Client full name'
    )

    reference = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        default='New',
        help='Unique client reference'
    )

    email = fields.Char(
        string='Email',
        tracking=True,
        help='Client email address'
    )

    phone = fields.Char(
        string='Phone',
        tracking=True,
        help='Client phone number'
    )

    # Additional Contact Information
    mobile = fields.Char(
        string='Mobile',
        help='Mobile phone number'
    )

    website = fields.Char(
        string='Website',
        help='Client website URL'
    )

    # Address Information
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one(
        'res.country',
        string='Country'
    )

    # Personal Information
    birthdate = fields.Date(
        string='Date of Birth',
        help='Client birthdate'
    )

    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=True,
        help='Automatically computed age'
    )

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')

    # Business Information
    company_name = fields.Char(
        string='Company',
        help='Client company name if applicable'
    )

    job_position = fields.Char(
        string='Job Position',
        help='Client job position'
    )

    industry = fields.Selection([
        ('tech', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('other', 'Other')
    ], string='Industry')

    # Financial Information
    credit_limit = fields.Float(
        string='Credit Limit',
        default=0.0,
        help='Maximum credit allowed for this client'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    balance = fields.Monetary(
        string='Balance',
        currency_field='currency_id',
        default=0.0,
        help='Current balance for this client'
    )

    # Status and Classification
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help='Set to false to archive the client'
    )

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='1')

    client_type = fields.Selection([
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('government', 'Government'),
        ('non_profit', 'Non Profit')
    ], string='Client Type', default='individual')

    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed')
    ], string='Status', default='draft', tracking=True)

    # Tags and Categories
    tag_ids = fields.Many2many(
        'res.partner.category',
        string='Tags',
        help='Categories/tags for this client'
    )

    # Communication
    language_id = fields.Many2one(
        'res.lang',
        string='Language',
        default=lambda self: self.env['res.lang'].search([('code', '=', self.env.user.lang)], limit=1)
    )

    # Documents and Notes
    document_ids = fields.Many2many(
        comodel_name='dudoxx_boiler.client_document',
        relation='dudoxx_boiler_client_document_rel',
        column1='client_id',
        column2='document_id',
        string='Documents',
        tracking=True,
        help='Documents associated with this client'
    )

    notes = fields.Html(
        string='Notes',
        help='Rich-text notes about the client'
    )

    # Metrics
    document_count = fields.Integer(
        string='Document Count',
        compute='_compute_document_count',
        store=True,
        help='Number of documents attached'
    )

    last_contact_date = fields.Datetime(
        string='Last Contact',
        readonly=True,
        help='Date and time of last contact with client'
    )

    # Image
    image = fields.Binary(
        string='Image',
        attachment=True,
        help='Client photo or company logo'
    )

    # Computed Fields
    @api.depends('birthdate')
    def _compute_age(self):
        """Compute client age based on birthdate.

        This method calculates the exact age considering:
        - Year difference
        - Month and day for accuracy
        - Handles leap years correctly

        The age is stored for performance in searches and reports.

        Dependencies:
            - birthdate field
        """
        for record in self:
            if record.birthdate:
                today = date.today()
                record.age = today.year - record.birthdate.year - \
                    ((today.month, today.day) < (record.birthdate.month, record.birthdate.day))
            else:
                record.age = 0

    @api.depends('document_ids')
    def _compute_document_count(self):
        """Compute total number of documents linked to the client.

        This method maintains an accurate count of associated documents
        for quick access in views and reports.

        Dependencies:
            - document_ids field (many2many)
        """
        for record in self:
            record.document_count = len(record.document_ids)

    # Constraints
    _sql_constraints = [
        ('unique_email', 'unique(email)', 'Email address must be unique!'),
        ('unique_reference', 'unique(reference)', 'Client reference must be unique!')
    ]

    # Sequence Generation
    @api.model_create_multi
    def create(self, vals_list):
        """Create new client records with automatic reference generation.

        This method ensures each client gets a unique reference number
        using Odoo's sequence mechanism.

        Args:
            vals_list (list): List of value dictionaries for creation

        Returns:
            recordset: Newly created client records

        Example:
            >>> self.env['dudoxx_boiler.client'].create({
            ...     'name': 'John Doe',
            ...     'email': 'john@example.com'
            ... })
            dudoxx_boiler.client(1,)
        """
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('dudoxx_boiler.client') or 'New'
        return super().create(vals_list)
