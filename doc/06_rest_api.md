# REST API Documentation

## Overview

The Dudoxx Boiler module provides a comprehensive REST API for client and document management. All endpoints require user authentication and return responses in JSON format.

## Authentication

All API requests require authentication using Odoo's standard authentication mechanisms. You can authenticate using:
- Session authentication (for web clients)
- API key authentication (for external applications)

## Base URL

```
http://your-odoo-server/api/v1/
```

## Client Endpoints

### List Clients

```http
GET /api/v1/clients
```

Query Parameters:
- `search` (string): Search term for name/email
- `limit` (integer): Max number of records (default: 80)
- `offset` (integer): Number of records to skip
- `order` (string): Sort order (e.g., 'name asc')

Response:
```json
{
    "count": 2,
    "results": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "client_type": "individual",
            "status": "active",
            "document_count": 3,
            "create_date": "2024-02-16T14:30:00"
        }
    ]
}
```

### Get Client

```http
GET /api/v1/clients/{client_id}
```

Response:
```json
{
    "id": 1,
    "name": "John Doe",
    "reference": "CLI/2024/001",
    "email": "john@example.com",
    "phone": "+1234567890",
    "mobile": "+1234567891",
    "website": "www.example.com",
    "client_type": "individual",
    "status": "active",
    "priority": "1",
    "company_name": "Example Corp",
    "job_position": "Manager",
    "industry": "tech",
    "document_count": 3,
    "documents": [
        {
            "id": 1,
            "name": "Contract 2024",
            "document_type": "contract",
            "state": "approved"
        }
    ],
    "create_date": "2024-02-16T14:30:00",
    "write_date": "2024-02-16T15:45:00"
}
```

### Create Client

```http
POST /api/v1/clients
```

Request Body:
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "client_type": "individual"
}
```

Response:
```json
{
    "id": 1,
    "name": "John Doe",
    "reference": "CLI/2024/001"
}
```

### Update Client

```http
PUT /api/v1/clients/{client_id}
```

Request Body:
```json
{
    "name": "John Smith",
    "email": "john.smith@example.com"
}
```

Response:
```json
{
    "id": 1,
    "name": "John Smith",
    "reference": "CLI/2024/001"
}
```

### Delete Client

```http
DELETE /api/v1/clients/{client_id}
```

Response:
```json
{
    "message": "Client deleted successfully"
}
```

### List Client Documents

```http
GET /api/v1/clients/{client_id}/documents
```

Response:
```json
{
    "count": 2,
    "results": [
        {
            "id": 1,
            "name": "Contract 2024",
            "reference": "DOC/2024/001",
            "document_type": "contract",
            "category": "legal",
            "state": "approved",
            "file_type": "pdf",
            "file_size": 2.5,
            "create_date": "2024-02-16T14:30:00"
        }
    ]
}
```

## Document Endpoints

### List Documents

```http
GET /api/v1/documents
```

Query Parameters:
- `search` (string): Search term for name/reference
- `document_type` (string): Filter by document type
- `category` (string): Filter by category
- `state` (string): Filter by state
- `limit` (integer): Max number of records
- `offset` (integer): Number of records to skip
- `order` (string): Sort order

Response:
```json
{
    "count": 2,
    "results": [
        {
            "id": 1,
            "name": "Contract 2024",
            "reference": "DOC/2024/001",
            "document_type": "contract",
            "category": "legal",
            "state": "approved",
            "file_type": "pdf",
            "file_size": 2.5,
            "create_date": "2024-02-16T14:30:00"
        }
    ]
}
```

### Get Document

```http
GET /api/v1/documents/{document_id}
```

Response:
```json
{
    "id": 1,
    "name": "Contract 2024",
    "reference": "DOC/2024/001",
    "document_type": "contract",
    "category": "legal",
    "state": "approved",
    "file_type": "pdf",
    "file_size": 2.5,
    "version": "1.0",
    "access_level": "internal",
    "is_confidential": false,
    "expiry_date": "2025-02-16",
    "days_to_expire": 365,
    "clients": [
        {
            "id": 1,
            "name": "John Doe"
        }
    ],
    "create_date": "2024-02-16T14:30:00",
    "write_date": "2024-02-16T15:45:00"
}
```

### Create Document

```http
POST /api/v1/documents
```

Request Body (multipart/form-data):
- `name` (string): Document name
- `document_type` (string): Document type
- `category` (string): Category
- `file` (binary): Document file
- `client_ids` (string): Comma-separated client IDs

Response:
```json
{
    "id": 1,
    "name": "Contract 2024",
    "reference": "DOC/2024/001"
}
```

### Download Document

```http
GET /api/v1/documents/{document_id}/download
```

Response:
- File download with appropriate Content-Type and Content-Disposition headers

### Update Document State

```http
PUT /api/v1/documents/{document_id}/state
```

Request Body:
```json
{
    "action": "submit"  // submit|approve|reject|expire|reactivate
}
```

Response:
```json
{
    "id": 1,
    "state": "submitted"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

Error Response Format:
```json
{
    "error": "Error message description"
}
```

## Rate Limiting

API requests are subject to rate limiting:
- 1000 requests per hour per user
- 5000 requests per hour per API key

## Best Practices

1. Use appropriate HTTP methods
2. Include error handling
3. Validate input data
4. Use pagination for large datasets
5. Cache responses when appropriate
6. Handle file uploads efficiently
7. Implement proper security measures

## Security Considerations

1. Always use HTTPS
2. Validate all input data
3. Implement proper authentication
4. Use appropriate access controls
5. Handle sensitive data securely
6. Monitor API usage
7. Implement rate limiting
