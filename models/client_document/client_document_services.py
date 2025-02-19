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

from odoo import models, api, fields
from odoo.exceptions import ValidationError

class ClientDocumentServices(models.Model):
    """Service layer for client document model providing business logic.

    This class extends the client document model with additional services:
    - File validation and management
    - Document state workflow
    - Client relationship management
    - Automatic expiry handling
    - Document download functionality

    The service layer pattern separates business logic from field definitions,
    making the code more maintainable and easier to test.
    """
    _inherit = 'dudoxx_boiler.client_document'

    @api.constrains('file', 'file_name')
    def _check_file(self):
        """Validate file and filename requirements.

        This constraint ensures:
        - Files have associated filenames
        - Filenames are not empty strings
        - Basic file validation

        Raises:
            ValidationError: If validation fails with specific message

        Example:
            >>> doc.file = binary_data
            >>> doc.file_name = ''  # Raises ValidationError
            >>> doc.file_name = 'document.pdf'  # Valid
        """
        for record in self:
            if record.file and not record.file_name:
                raise ValidationError('File name is required when uploading a file!')

            if record.file_name and not record.file_name.strip():
                raise ValidationError('File name cannot be empty!')

    def toggle_active(self):
        """Toggle the active status of the document.

        This method provides a simple way to archive/unarchive documents.
        Archived documents are hidden from most searches and views.

        Returns:
            bool: True after toggling status

        Example:
            >>> doc.active  # True
            >>> doc.toggle_active()
            >>> doc.active  # False
        """
        for record in self:
            record.active = not record.active
        return True

    def count_clients(self):
        """Count the number of clients associated with the document.

        This method provides a direct count of linked clients,
        useful for quick checks without loading the full recordset.

        Returns:
            int: Number of linked clients

        Example:
            >>> doc.count_clients()
            3  # Document shared with 3 clients
        """
        for record in self:
            return len(record.client_ids)

    def get_file_info(self):
        """Get document file information.

        This method returns a dictionary containing:
        - File status
        - File name if present
        - Document type
        - File presence indicator

        Returns:
            dict: File information with keys:
                - status (str): 'no_file' or present implicitly
                - file_name (str): Name of the file
                - has_file (bool): File presence indicator
                - document_type (str): Type of document

        Example:
            >>> doc.get_file_info()
            {
                'file_name': 'contract.pdf',
                'has_file': True,
                'document_type': 'contract'
            }
        """
        self.ensure_one()
        if not self.file:
            return {'status': 'no_file'}

        return {
            'file_name': self.file_name,
            'has_file': bool(self.file),
            'document_type': self.document_type,
        }

    def action_download(self):
        """Download the document file.

        This method returns a URL action to download the document file.
        The URL is constructed to:
        - Use Odoo's web content controller
        - Include proper model and record identification
        - Force download behavior
        - Use correct filename

        Returns:
            dict: URL action configuration

        Raises:
            ValidationError: If no file is available

        Example:
            >>> action = doc.action_download()
            >>> action['type']
            'ir.actions.act_url'
        """
        self.ensure_one()
        if not self.file:
            raise ValidationError('No file available for download!')

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/file/{self.file_name}?download=true',
            'target': 'self',
        }

    def action_submit(self):
        """Submit document for approval.

        This method transitions the document to 'submitted' state.
        Only documents in 'draft' or 'rejected' states can be submitted.

        Returns:
            bool: True if submission successful

        Raises:
            ValidationError: If document is in invalid state

        Example:
            >>> doc.state = 'draft'
            >>> doc.action_submit()
            >>> doc.state  # 'submitted'
        """
        for record in self:
            if record.state not in ['draft', 'rejected']:
                raise ValidationError('Only draft or rejected documents can be submitted!')
            record.state = 'submitted'
        return True

    def action_approve(self):
        """Approve document.

        This method transitions the document to 'approved' state.
        Only documents in 'submitted' or 'expired' states can be approved.

        Returns:
            bool: True if approval successful

        Raises:
            ValidationError: If document is in invalid state

        Example:
            >>> doc.state = 'submitted'
            >>> doc.action_approve()
            >>> doc.state  # 'approved'
        """
        for record in self:
            if record.state not in ['submitted', 'expired']:
                raise ValidationError('Only submitted or expired documents can be approved!')
            record.state = 'approved'
        return True

    def action_reject(self):
        """Reject document.

        This method transitions the document to 'rejected' state.
        Only documents in 'submitted' or 'approved' states can be rejected.

        Returns:
            bool: True if rejection successful

        Raises:
            ValidationError: If document is in invalid state

        Example:
            >>> doc.state = 'submitted'
            >>> doc.action_reject()
            >>> doc.state  # 'rejected'
        """
        for record in self:
            if record.state not in ['submitted', 'approved']:
                raise ValidationError('Only submitted or approved documents can be rejected!')
            record.state = 'rejected'
        return True

    def action_reset_to_draft(self):
        """Reset document back to draft state.

        This method transitions the document to 'draft' state.
        Only documents in 'submitted', 'rejected', or 'expired' states
        can be reset to draft.

        Returns:
            bool: True if reset successful

        Raises:
            ValidationError: If document is in invalid state

        Example:
            >>> doc.state = 'rejected'
            >>> doc.action_reset_to_draft()
            >>> doc.state  # 'draft'
        """
        for record in self:
            if record.state not in ['submitted', 'rejected', 'expired']:
                raise ValidationError('Only submitted, rejected, or expired documents can be reset to draft!')
            record.state = 'draft'
        return True

    def action_expire(self):
        """Mark document as expired.

        This method transitions the document to 'expired' state.
        Only documents in 'approved' or 'submitted' states can be expired.

        Returns:
            bool: True if expiry successful

        Raises:
            ValidationError: If document is in invalid state

        Example:
            >>> doc.state = 'approved'
            >>> doc.action_expire()
            >>> doc.state  # 'expired'
        """
        for record in self:
            if record.state not in ['approved', 'submitted']:
                raise ValidationError('Only approved or submitted documents can be expired!')
            record.state = 'expired'
        return True

    def action_reactivate(self):
        """Reactivate expired or rejected document.

        This method transitions the document to 'submitted' state.
        Only documents in 'expired' or 'rejected' states can be reactivated.

        Returns:
            bool: True if reactivation successful

        Raises:
            ValidationError: If document is in invalid state

        Example:
            >>> doc.state = 'expired'
            >>> doc.action_reactivate()
            >>> doc.state  # 'submitted'
        """
        for record in self:
            if record.state not in ['expired', 'rejected']:
                raise ValidationError('Only expired or rejected documents can be reactivated!')
            record.state = 'submitted'
        return True

    @api.model
    def _check_expiry(self):
        """Cron job to check and expire documents.

        This method is designed to run as a scheduled action to:
        - Find approved documents past their expiry date
        - Automatically mark them as expired
        - Handle expiry in batch for efficiency

        The method searches for:
        - Approved documents only
        - Documents with expiry dates
        - Documents past their expiry date

        Returns:
            bool: True after processing

        Example:
            >>> # In cron configuration:
            >>> model._check_expiry()  # Expires eligible documents
        """
        today = fields.Date.today()
        domain = [
            ('state', '=', 'approved'),
            ('expiry_date', '!=', False),
            ('expiry_date', '<', today)
        ]
        expired_docs = self.search(domain)
        expired_docs.action_expire()
        return True

    @api.onchange('file')
    def _onchange_file(self):
        """Clear filename when file is removed.

        This onchange method ensures consistency between:
        - The binary file field
        - The filename field

        When the file is removed, the filename is automatically cleared
        to prevent orphaned filenames.

        Example:
            >>> doc.file = False  # Triggers onchange
            >>> doc.file_name  # False
        """
        if not self.file:
            self.file_name = False
