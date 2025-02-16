from odoo import models, api
from odoo.exceptions import ValidationError

class ClientDocumentServices(models.Model):
    _inherit = 'dudoxx_boiler.client_document'

    @api.constrains('file', 'file_name')
    def _check_file(self):
        """Validate file and filename"""
        for record in self:
            if record.file and not record.file_name:
                raise ValidationError('File name is required when uploading a file!')

            if record.file_name and not record.file_name.strip():
                raise ValidationError('File name cannot be empty!')

    def toggle_active(self):
        """Toggle the active status of the document"""
        for record in self:
            record.active = not record.active

    def count_clients(self):
        """Count the number of clients associated with the document"""
        for record in self:
            return len(record.client_ids)

    def get_file_info(self):
        """Get document file information"""
        self.ensure_one()
        if not self.file:
            return {'status': 'no_file'}

        return {
            'file_name': self.file_name,
            'has_file': bool(self.file),
            'document_type': self.document_type,
        }

    def action_download(self):
        """Download the document file"""
        self.ensure_one()
        if not self.file:
            raise ValidationError('No file available for download!')

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/file/{self.file_name}?download=true',
            'target': 'self',
        }

    def action_submit(self):
        """Submit document for approval"""
        for record in self:
            if record.state not in ['draft', 'rejected']:
                raise ValidationError('Only draft or rejected documents can be submitted!')
            record.state = 'submitted'
        return True

    def action_approve(self):
        """Approve document"""
        for record in self:
            if record.state not in ['submitted', 'expired']:
                raise ValidationError('Only submitted or expired documents can be approved!')
            record.state = 'approved'
        return True

    def action_reject(self):
        """Reject document"""
        for record in self:
            if record.state not in ['submitted', 'approved']:
                raise ValidationError('Only submitted or approved documents can be rejected!')
            record.state = 'rejected'
        return True

    def action_reset_to_draft(self):
        """Reset document back to draft"""
        for record in self:
            if record.state not in ['submitted', 'rejected', 'expired']:
                raise ValidationError('Only submitted, rejected, or expired documents can be reset to draft!')
            record.state = 'draft'
        return True

    def action_expire(self):
        """Mark document as expired"""
        for record in self:
            if record.state not in ['approved', 'submitted']:
                raise ValidationError('Only approved or submitted documents can be expired!')
            record.state = 'expired'
        return True

    def action_reactivate(self):
        """Reactivate document"""
        for record in self:
            if record.state not in ['expired', 'rejected']:
                raise ValidationError('Only expired or rejected documents can be reactivated!')
            record.state = 'submitted'
        return True

    @api.model
    def _check_expiry(self):
        """Cron job to check and expire documents"""
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
        """Clear filename if file is removed"""
        if not self.file:
            self.file_name = False
