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

import json
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import AccessError, ValidationError

class ClientAPI(http.Controller):
    """REST API Controller for Client Operations.

    This controller provides REST endpoints for:
    - Client CRUD operations
    - Client document management
    - Client status updates
    - Related data retrieval

    All endpoints require proper authentication and
    return responses in JSON format.
    """

    def _get_json_data(self):
        """Extract JSON data from request.

        Returns:
            dict: Parsed JSON data
        """
        try:
            return json.loads(request.httprequest.data.decode())
        except json.JSONDecodeError:
            return {}

    def _json_response(self, data, status=200):
        """Create JSON response with proper headers.

        Args:
            data (dict): Response data
            status (int): HTTP status code

        Returns:
            Response: HTTP response object
        """
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )

    @http.route('/api/v1/clients', type='http', auth='user', methods=['GET'], csrf=False)
    def list_clients(self, **kwargs):
        """List clients with optional filtering.

        Query Parameters:
            search (str): Search term for name/email
            limit (int): Max number of records
            offset (int): Number of records to skip
            order (str): Sort order (e.g., 'name asc')

        Returns:
            json: List of client records
        """
        try:
            domain = []
            if kwargs.get('search'):
                domain += [
                    '|',
                    ('name', 'ilike', kwargs['search']),
                    ('email', 'ilike', kwargs['search'])
                ]

            Client = request.env['dudoxx_boiler.client']
            clients = Client.search(
                domain,
                limit=int(kwargs.get('limit', 80)),
                offset=int(kwargs.get('offset', 0)),
                order=kwargs.get('order', 'create_date desc')
            )

            result = [{
                'id': client.id,
                'name': client.name,
                'email': client.email,
                'phone': client.phone,
                'client_type': client.client_type,
                'status': client.status,
                'document_count': client.document_count,
                'create_date': client.create_date.isoformat() if client.create_date else None,
            } for client in clients]

            return self._json_response({
                'count': len(result),
                'results': result
            })

        except Exception as e:
            return self._json_response({
                'error': str(e)
            }, status=400)

    @http.route('/api/v1/clients/<int:client_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_client(self, client_id):
        """Get detailed client information.

        Args:
            client_id (int): Client ID

        Returns:
            json: Client details with related data
        """
        try:
            client = request.env['dudoxx_boiler.client'].browse(client_id)
            if not client.exists():
                return self._json_response({
                    'error': 'Client not found'
                }, status=404)

            result = {
                'id': client.id,
                'name': client.name,
                'reference': client.reference,
                'email': client.email,
                'phone': client.phone,
                'mobile': client.mobile,
                'website': client.website,
                'client_type': client.client_type,
                'status': client.status,
                'priority': client.priority,
                'company_name': client.company_name,
                'job_position': client.job_position,
                'industry': client.industry,
                'document_count': client.document_count,
                'documents': [{
                    'id': doc.id,
                    'name': doc.name,
                    'document_type': doc.document_type,
                    'state': doc.state,
                } for doc in client.document_ids],
                'create_date': client.create_date.isoformat() if client.create_date else None,
                'write_date': client.write_date.isoformat() if client.write_date else None,
            }

            return self._json_response(result)

        except AccessError:
            return self._json_response({
                'error': 'Access Denied'
            }, status=403)
        except Exception as e:
            return self._json_response({
                'error': str(e)
            }, status=400)

    @http.route('/api/v1/clients', type='http', auth='user', methods=['POST'], csrf=False)
    def create_client(self):
        """Create new client.

        Request Body:
            {
                "name": "string",
                "email": "string",
                "phone": "string",
                "client_type": "string",
                ...
            }

        Returns:
            json: Created client data
        """
        try:
            data = self._get_json_data()
            if not data:
                return self._json_response({
                    'error': 'No data provided'
                }, status=400)

            client = request.env['dudoxx_boiler.client'].create(data)
            return self._json_response({
                'id': client.id,
                'name': client.name,
                'reference': client.reference,
            }, status=201)

        except ValidationError as e:
            return self._json_response({
                'error': str(e)
            }, status=400)
        except AccessError:
            return self._json_response({
                'error': 'Access Denied'
            }, status=403)
        except Exception as e:
            return self._json_response({
                'error': str(e)
            }, status=400)

    @http.route('/api/v1/clients/<int:client_id>', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_client(self, client_id):
        """Update client information.

        Args:
            client_id (int): Client ID

        Request Body:
            {
                "name": "string",
                "email": "string",
                ...
            }

        Returns:
            json: Updated client data
        """
        try:
            client = request.env['dudoxx_boiler.client'].browse(client_id)
            if not client.exists():
                return self._json_response({
                    'error': 'Client not found'
                }, status=404)

            data = self._get_json_data()
            if not data:
                return self._json_response({
                    'error': 'No data provided'
                }, status=400)

            client.write(data)
            return self._json_response({
                'id': client.id,
                'name': client.name,
                'reference': client.reference,
            })

        except ValidationError as e:
            return self._json_response({
                'error': str(e)
            }, status=400)
        except AccessError:
            return self._json_response({
                'error': 'Access Denied'
            }, status=403)
        except Exception as e:
            return self._json_response({
                'error': str(e)
            }, status=400)

    @http.route('/api/v1/clients/<int:client_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_client(self, client_id):
        """Delete client record.

        Args:
            client_id (int): Client ID

        Returns:
            json: Success message
        """
        try:
            client = request.env['dudoxx_boiler.client'].browse(client_id)
            if not client.exists():
                return self._json_response({
                    'error': 'Client not found'
                }, status=404)

            client.unlink()
            return self._json_response({
                'message': 'Client deleted successfully'
            })

        except AccessError:
            return self._json_response({
                'error': 'Access Denied'
            }, status=403)
        except Exception as e:
            return self._json_response({
                'error': str(e)
            }, status=400)

    @http.route('/api/v1/clients/<int:client_id>/documents', type='http', auth='user', methods=['GET'], csrf=False)
    def list_client_documents(self, client_id):
        """List documents associated with client.

        Args:
            client_id (int): Client ID

        Returns:
            json: List of client documents
        """
        try:
            client = request.env['dudoxx_boiler.client'].browse(client_id)
            if not client.exists():
                return self._json_response({
                    'error': 'Client not found'
                }, status=404)

            result = [{
                'id': doc.id,
                'name': doc.name,
                'reference': doc.reference,
                'document_type': doc.document_type,
                'category': doc.category,
                'state': doc.state,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'create_date': doc.create_date.isoformat() if doc.create_date else None,
            } for doc in client.document_ids]

            return self._json_response({
                'count': len(result),
                'results': result
            })

        except AccessError:
            return self._json_response({
                'error': 'Access Denied'
            }, status=403)
        except Exception as e:
            return self._json_response({
                'error': str(e)
            }, status=400)
