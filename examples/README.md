# Dudoxx API Usage Examples

This directory contains examples demonstrating how to use the Dudoxx Boiler REST API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your Odoo server details
```

## API Client Usage

The `api_usage.py` script demonstrates how to:
- Authenticate with the Odoo server
- Perform CRUD operations on clients
- Manage documents and files
- Handle document state transitions

### Basic Usage

```python
from api_usage import DudoxxAPI

# Initialize API client
api = DudoxxAPI(
    base_url="http://localhost:8069",
    db="odoo16",
    username="admin",
    password="admin"
)

# Create a client
client = api.create_client({
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "client_type": "individual"
})

# Upload a document
document = api.create_document(
    name="Contract 2024",
    document_type="contract",
    category="legal",
    file_path="path/to/contract.pdf",
    client_ids=[client['id']]
)

# Download document
api.download_document(document['id'], "downloaded_contract.pdf")
```

### Error Handling

The API client handles common errors:
- Authentication failures
- Invalid requests
- Server errors
- File operation errors

Example error handling:
```python
try:
    client = api.create_client(data)
except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")
```

## Available Endpoints

### Client Endpoints
- `GET /api/v1/clients` - List clients
- `GET /api/v1/clients/{id}` - Get client details
- `POST /api/v1/clients` - Create client
- `PUT /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client
- `GET /api/v1/clients/{id}/documents` - List client documents

### Document Endpoints
- `GET /api/v1/documents` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `POST /api/v1/documents` - Create document
- `GET /api/v1/documents/{id}/download` - Download document
- `PUT /api/v1/documents/{id}/state` - Update document state

## Security

The API uses Odoo's built-in authentication. Make sure to:
- Use HTTPS in production
- Keep credentials secure
- Follow proper session management
- Handle sensitive data appropriately

## Testing

To run the example:
```bash
python api_usage.py
```

This will demonstrate the full workflow of:
1. Creating a client
2. Uploading a document
3. Managing document state
4. Downloading the document

## Documentation

For complete API documentation, see:
- [REST API Documentation](../doc/06_rest_api.md)
- [Odoo Development Setup](../doc/odoo_dev_setup.md)
