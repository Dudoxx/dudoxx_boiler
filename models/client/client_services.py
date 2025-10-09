from odoo import models, api
from odoo.exceptions import ValidationError

class ClientServices(models.Model):
    _inherit = 'dudoxx_boiler.client'

    @api.constrains('email')
    def _check_email_format(self):
        """Validate email format"""
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError('Invalid email format!')

    @api.constrains('phone')
    def _check_phone_format(self):
        """Validate phone number format"""
        for record in self:
            if record.phone and not record.phone.replace('+', '').replace(' ', '').isdigit():
                raise ValidationError('Phone number should only contain digits, spaces, and + symbol!')

    def toggle_active(self):
        """Toggle the active status of the client"""
        for record in self:
            record.active = not record.active

    def count_documents(self):
        """Count the number of documents associated with the client"""
        for record in self:
            return len(record.document_ids)

    def get_document_summary(self):
        """Get a summary of client's documents"""
        self.ensure_one()
        return {
            'total_documents': len(self.document_ids),
            'document_names': self.document_ids.mapped('name'),
        }

    def action_view_documents(self):
        """Open documents view for this client."""
        self.ensure_one()
        return {
            'name': 'Client Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'dudoxx_boiler.client_document',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.document_ids.ids)],
            'context': {
                'default_client_ids': [(6, 0, [self.id])],
                'search_default_active': 1
            },
            'target': 'current',
        }
