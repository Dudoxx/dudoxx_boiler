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
import base64
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import AccessError, ValidationError

class ClientDocumentAPI(http.Controller):
    """REST API Controller for Client Document Operations.

    This controller provides REST endpoints for:
    - Document CRUD operations
    - File upload and download
    - Document state management
    - Document metadata operations

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

    @http.route('/api/v1/documents', type='http', auth='user', methods=['GET'], csrf=False)
    def list_documents(self, **kwargs):
        """List documents with optional filtering.

        Query Parameters:
            search (str): Search term for name/reference
            document_type (str): Filter by document type
            category (str): Filter by category
            state (str): Filter by state
            limit (int): Max number of records
            offset (int): Number of records to skip
            order (str): Sort order

        Returns:
            json: List of document records
        """
        try:
            domain = []
            if kwargs.get('search'):
                domain += [
                    '|',
                    ('name', 'ilike', kwargs['search']),
                    ('reference', 'ilike', kwargs['search'])
                ]
            if kwargs.get('document_type'):
                domain.append(('document_type', '=', kwargs['document_type']))
            if kwargs.get('category'):
                domain.append(('category', '=', kwargs['category']))
            if kwargs.get('state'):
                domain.append(('state', '=', kwargs['state']))

            Document = request.env['dudoxx_boiler.client_document']
            documents = Document.search(
                domain,
                limit=int(kwargs.get('limit', 80)),
                offset=int(kwargs.get('offset', 0)),
                order=kwargs.get('order', 'create_date desc')
            )

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
            } for doc in documents]

            return self._json_response({
                'count': len(result),
                'results': result
            })

        except Exception as e:
            return self._json_response({
                'error': str(e)
            }, status=400)

    @http.route('/api/v1/documents/<int:document_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_document(self, document_id):
        """Get detailed document information.

        Args:
            document_id (int): Document ID

        Returns:
            json: Document details with related data
        """
        try:
            document = request.env['dudoxx_boiler.client_document'].browse(document_id)
            if not document.exists():
                return self._json_response({
                    'error': 'Document not found'
                }, status=404)

            result = {
                'id': document.id,
                'name': document.name,
                'reference': document.reference,
                'document_type': document.document_type,
                'category': document.category,
                'state': document.state,
                'file_type': document.file_type,
                'file_size': document.file_size,
                'version': document.version,
                'access_level': document.access_level,
                'is_confidential': document.is_confidential,
                'expiry_date': document.expiry_date.isoformat() if document.expiry_date else None,
                'days_to_expire': document.days_to_expire,
                'clients': [{
                    'id': client.id,
                    'name': client.name,
                } for client in document.client_ids],
                'create_date': document.create_date.isoformat() if document.create_date else None,
                'write_date': document.write_date.isoformat() if document.write_date else None,
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

    @http.route('/api/v1/documents', type='http', auth='user', methods=['POST'], csrf=False)
    def create_document(self):
        """Create new document.

        Request Body (multipart/form-data):
            name (str): Document name
            document_type (str): Document type
            category (str): Category
            file (binary): Document file
            client_ids (list): Associated client IDs
            ...

        Returns:
            json: Created document data
        """
        try:
            # Handle file upload
            file = request.httprequest.files.get('file')
            if not file:
                return self._json_response({
                    'error': 'No file provided'
                }, status=400)

            # Prepare document data
            data = {
                'name': request.params.get('name'),
                'document_type': request.params.get('document_type'),
                'category': request.params.get('category'),
                'file': base64.b64encode(file.read()),
                'file_name': file.filename,
                'client_ids': [(6, 0, [int(id) for id in request.params.get('client_ids', '').split(',') if id])]
            }

            document = request.env['dudoxx_boiler.client_document'].create(data)
            return self._json_response({
                'id': document.id,
                'name': document.name,
                'reference': document.reference,
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

    @http.route('/api/v1/documents/<int:document_id>/download', type='http', auth='user', methods=['GET'])
    def download_document(self, document_id):
        """Download document file.

        Args:
            document_id (int): Document ID

        Returns:
            http: File download response
        """
        try:
            document = request.env['dudoxx_boiler.client_document'].browse(document_id)
            if not document.exists():
                return self._json_response({
                    'error': 'Document not found'
                }, status=404)

            if not document.file:
                return self._json_response({
                    'error': 'No file available'
                }, status=404)

            return request.make_response(
                base64.b64decode(document.file),
                headers=[
                    ('Content-Type', 'application/octet-stream'),
                    ('Content-Disposition', f'attachment; filename="{document.file_name}"')
                ]
            )

        except AccessError:
            return self._json_response({
                'error': 'Access Denied'
            }, status=403)
        except Exception as e:
            return self._json_response({
                'error': str(e)
            }, status=400)

    @http.route('/api/v1/documents/<int:document_id>/state', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_document_state(self, document_id):
        """Update document state.

        Args:
            document_id (int): Document ID

        Request Body:
            {
                "action": "submit|approve|reject|expire|reactivate"
            }

        Returns:
            json: Updated document state
        """
        try:
            document = request.env['dudoxx_boiler.client_document'].browse(document_id)
            if not document.exists():
                return self._json_response({
                    'error': 'Document not found'
                }, status=404)

            data = self._get_json_data()
            action = data.get('action')
            if not action:
                return self._json_response({
                    'error': 'No action provided'
                }, status=400)

            # Map action to method
            action_method = {
                'submit': document.action_submit,
                'approve': document.action_approve,
                'reject': document.action_reject,
                'expire': document.action_expire,
                'reactivate': document.action_reactivate
            }.get(action)

            if not action_method:
                return self._json_response({
                    'error': 'Invalid action'
                }, status=400)

            action_method()
            return self._json_response({
                'id': document.id,
                'state': document.state
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
