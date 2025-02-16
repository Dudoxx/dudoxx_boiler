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

import requests
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DudoxxAPI:
    """Client for interacting with Dudoxx Boiler REST API."""

    def __init__(self, base_url="http://localhost:8069", db="odoo", username="admin", password="admin"):
        """Initialize API client.

        Args:
            base_url (str): Odoo server URL
            db (str): Database name
            username (str): User login
            password (str): User password
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

        # Authenticate
        auth_url = f"{self.base_url}/web/session/authenticate"
        auth_data = {
            "jsonrpc": "2.0",
            "params": {
                "db": db,
                "login": username,
                "password": password,
                "base_location": self.base_url
            }
        }

        response = self.session.post(auth_url, json=auth_data)
        response.raise_for_status()

        result = response.json()
        if not result.get('result'):
            raise Exception("Authentication failed")

        # Get session info after authentication using JSON-RPC
        session_info_url = f"{self.base_url}/web/session/get_session_info"
        session_info_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {}
        }
        session_info = self.session.post(session_info_url, json=session_info_data)
        session_info.raise_for_status()

        # Set CSRF token if available in session info response
        session_result = session_info.json().get('result', {})
        if session_result:
            csrf_token = session_result.get('csrf_token')
            if csrf_token:
                self.session.headers.update({'X-CSRFToken': csrf_token})

    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request to API endpoint.

        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            **kwargs: Additional request parameters

        Returns:
            dict: Response data
        """
        url = f"{self.base_url}{endpoint}"

        # Prepare headers
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Add CSRF token from session if available
        csrf_token = self.session.headers.get('X-CSRFToken')
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token

        # Handle file uploads
        if 'files' in kwargs:
            headers.pop('Content-Type', None)
        elif 'data' in kwargs:
            # Convert data to JSON for non-file requests
            kwargs['json'] = kwargs.pop('data')

        kwargs['headers'] = headers
        response = self.session.request(method, url, **kwargs)

        if response.status_code == 404:
            raise requests.exceptions.HTTPError(
                f"API endpoint not found: {endpoint}. "
                "Make sure the Odoo server is running and the module is installed."
            )

        response.raise_for_status()
        return response.json()

    # Client Operations
    def list_clients(self, search=None, limit=80, offset=0):
        """List clients with optional filtering."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if search:
            params["search"] = search
        return self._make_request("GET", "/api/v1/clients", params=params)

    def get_client(self, client_id):
        """Get detailed client information."""
        return self._make_request("GET", f"/api/v1/clients/{client_id}")

    def create_client(self, data):
        """Create new client."""
        return self._make_request("POST", "/api/v1/clients", json=data)

    def update_client(self, client_id, data):
        """Update client information."""
        return self._make_request("PUT", f"/api/v1/clients/{client_id}", json=data)

    def delete_client(self, client_id):
        """Delete client record."""
        return self._make_request("DELETE", f"/api/v1/clients/{client_id}")

    def list_client_documents(self, client_id):
        """List documents associated with client."""
        return self._make_request("GET", f"/api/v1/clients/{client_id}/documents")

    # Document Operations
    def list_documents(self, search=None, document_type=None, category=None, state=None):
        """List documents with optional filtering."""
        params = {}
        if search:
            params["search"] = search
        if document_type:
            params["document_type"] = document_type
        if category:
            params["category"] = category
        if state:
            params["state"] = state
        return self._make_request("GET", "/api/v1/documents", params=params)

    def get_document(self, document_id):
        """Get detailed document information."""
        return self._make_request("GET", f"/api/v1/documents/{document_id}")

    def create_document(self, name, document_type, category, file_path, client_ids=None):
        """Create new document with file upload."""
        files = {
            'file': open(file_path, 'rb')
        }
        data = {
            'name': name,
            'document_type': document_type,
            'category': category
        }
        if client_ids:
            data['client_ids'] = ','.join(map(str, client_ids))

        return self._make_request("POST", "/api/v1/documents", files=files, data=data)

    def download_document(self, document_id, save_path):
        """Download document file."""
        url = f"{self.base_url}/api/v1/documents/{document_id}/download"
        response = self.session.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return save_path

    def update_document_state(self, document_id, action):
        """Update document state."""
        data = {'action': action}
        return self._make_request(
            "PUT",
            f"/api/v1/documents/{document_id}/state",
            json=data
        )

def main():
    """Example usage of the Dudoxx API client."""

    # Initialize API client with environment variables
    api = DudoxxAPI(
        base_url=os.getenv('ODOO_SERVER', 'http://localhost:8069'),
        db=os.getenv('ODOO_DB', 'odoo16'),
        username=os.getenv('ODOO_USER', 'admin'),
        password=os.getenv('ODOO_PASSWORD', 'admin')
    )

    try:
        # Create a new client with unique email
        timestamp = int(datetime.now().timestamp())
        client_data = {
            "name": "John Doe",
            "email": f"john.doe.{timestamp}@example.com",
            "phone": "+1234567890",
            "client_type": "individual"
        }
        client = api.create_client(client_data)
        print("Created client:", client)

        # List clients
        clients = api.list_clients(search="John")
        print("\nFound clients:", clients)

        # Create a document for the client
        document = api.create_document(
            name="Contract 2024",
            document_type="contract",
            category="legal",
            file_path="Patient_Report_Kardiologie Test.pdf",
            client_ids=[client['id']]
        )
        print("\nCreated document:", document)

        # List client's documents
        documents = api.list_client_documents(client['id'])
        print("\nClient documents:", documents)

        # Update document state
        state_update = api.update_document_state(document['id'], 'submit')
        print("\nUpdated document state:", state_update)

        # Download document
        downloaded_file = api.download_document(
            document['id'],
            "downloaded_contract.pdf"
        )
        print("\nDownloaded document to:", downloaded_file)

    except requests.exceptions.RequestException as e:
        print("API Error:", e)

if __name__ == "__main__":
    main()
