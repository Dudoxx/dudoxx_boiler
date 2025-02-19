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

from odoo import models, api
from odoo.exceptions import ValidationError

class ClientServices(models.Model):
    """Service layer for client model providing business logic and validations.

    This class extends the client model with additional services including:
    - Email and phone format validation
    - Document management functionality
    - Status management
    - Document count and summary features

    The service layer pattern separates business logic from field definitions,
    making the code more maintainable and easier to test.
    """
    _inherit = 'dudoxx_boiler.client'

    @api.constrains('email')
    def _check_email_format(self):
        """Validate email format using basic validation.

        This constraint ensures that email addresses contain an '@' symbol.
        For more complex validation, consider using email_validator library.

        Raises:
            ValidationError: If email format is invalid

        Example:
            >>> client.email = 'invalid-email'  # Raises ValidationError
            >>> client.email = 'valid@email.com'  # Passes validation
        """
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError('Invalid email format!')

    @api.constrains('phone')
    def _check_phone_format(self):
        """Validate phone number format using basic validation.

        This constraint ensures phone numbers only contain:
        - Digits (0-9)
        - Plus symbol (+) for country codes
        - Spaces for formatting

        For more complex validation, consider using phonenumbers library.

        Raises:
            ValidationError: If phone format is invalid

        Example:
            >>> client.phone = 'abc123'  # Raises ValidationError
            >>> client.phone = '+1 234 567 8900'  # Passes validation
        """
        for record in self:
            if record.phone and not record.phone.replace('+', '').replace(' ', '').isdigit():
                raise ValidationError('Phone number should only contain digits, spaces, and + symbol!')

    def toggle_active(self):
        """Toggle the active status of the client.

        This method provides a simple way to archive/unarchive clients.
        Archived clients are hidden from most searches and views.

        Returns:
            bool: True after toggling status

        Example:
            >>> client.active  # True
            >>> client.toggle_active()
            >>> client.active  # False
        """
        for record in self:
            record.active = not record.active
        return True

    def count_documents(self):
        """Count the number of documents associated with the client.

        This method provides a direct count of linked documents,
        useful for quick checks without loading the full recordset.

        Returns:
            int: Number of linked documents

        Example:
            >>> client.count_documents()
            5  # Client has 5 documents
        """
        for record in self:
            return len(record.document_ids)

    def get_document_summary(self):
        """Get a summary of client's documents.

        This method returns a dictionary containing:
        - Total number of documents
        - List of document names

        Returns:
            dict: Document summary with keys:
                - total_documents (int)
                - document_names (list)

        Example:
            >>> client.get_document_summary()
            {
                'total_documents': 3,
                'document_names': ['Doc1', 'Doc2', 'Doc3']
            }
        """
        self.ensure_one()
        return {
            'total_documents': len(self.document_ids),
            'document_names': self.document_ids.mapped('name'),
        }

    def action_view_documents(self):
        """Open documents view for this client.

        This method returns a window action to display the client's
        documents in a dedicated view. The view supports:
        - Kanban display for visual document management
        - List view for detailed information
        - Form view for document editing

        The action includes:
        - Domain filter to show only this client's documents
        - Context for creating new documents linked to this client
        - Default active filter enabled

        Returns:
            dict: Window action configuration

        Example:
            >>> action = client.action_view_documents()
            >>> action['type']
            'ir.actions.act_window'
        """
        self.ensure_one()
        return {
            'name': 'Client Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'dudoxx_boiler.client_document',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.document_ids.ids)],
            'context': {
                'default_client_ids': [(6, 0, [self.id])],
                'search_default_active': 1
            },
            'target': 'current',
        }
