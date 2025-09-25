# Medical History App API Documentation

## Overview

The Medical History App provides a comprehensive REST API for managing patient data, medical histories, and user authentication. All endpoints are secured with JWT authentication and include comprehensive audit logging for HIPAA compliance.

## Base URL

- Development: `http://localhost:3001/api`
- Production: `https://yourdomain.com/api`

## Authentication

All API endpoints (except login/register) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "pagination": { ... } // For paginated responses
}
```

Error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": { ... } // Optional additional error details
}
```

## Authentication Endpoints

### POST /auth/login

Login with username and password.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "twoFactorCode": "string" // Optional, required if 2FA is enabled
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "jwt-token",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "firstName": "string",
    "lastName": "string",
    "role": "string",
    "twoFactorEnabled": boolean
  }
}
```

### POST /auth/logout

Logout current user.

**Headers:** Authorization required

**Response:**
```json
{
  "message": "Logout successful"
}
```

### GET /auth/profile

Get current user profile.

**Headers:** Authorization required

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "firstName": "string",
    "lastName": "string",
    "role": "string",
    "isActive": boolean,
    "lastLogin": "datetime",
    "twoFactorEnabled": boolean
  }
}
```

### PUT /auth/profile

Update current user profile.

**Headers:** Authorization required

**Request Body:**
```json
{
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "phone": "string",
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zip": "string"
  }
}
```

### GET /auth/2fa/setup

Setup two-factor authentication.

**Headers:** Authorization required

**Response:**
```json
{
  "secret": "base32-secret",
  "qrCode": "data:image/png;base64,...",
  "manualEntryKey": "base32-key"
}
```

### POST /auth/2fa/enable

Enable two-factor authentication.

**Headers:** Authorization required

**Request Body:**
```json
{
  "secret": "base32-secret",
  "token": "123456"
}
```

## Patient Endpoints

### GET /patients

Get list of patients with pagination and search.

**Headers:** Authorization required

**Query Parameters:**
- `page` (number): Page number (default: 1)
- `limit` (number): Items per page (default: 20, max: 100)
- `search` (string): Search term
- `status` (string): Filter by status (active, inactive, deceased)
- `sortBy` (string): Sort field (firstName, lastName, dateOfBirth, createdAt)
- `sortOrder` (string): Sort order (ASC, DESC)

**Response:**
```json
{
  "patients": [
    {
      "id": "uuid",
      "firstName": "string",
      "lastName": "string",
      "dateOfBirth": "date",
      "gender": "string",
      "medicalRecordNumber": "string",
      "status": "string",
      "createdAt": "datetime"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalPatients": 100,
    "hasNext": true,
    "hasPrev": false
  }
}
```

### POST /patients

Create new patient.

**Headers:** Authorization required

**Request Body:**
```json
{
  "firstName": "string",
  "lastName": "string",
  "middleName": "string", // Optional
  "dateOfBirth": "date",
  "gender": "male|female|other|prefer_not_to_say",
  "ssn": "string", // Optional, format: XXX-XX-XXXX
  "email": "string", // Optional
  "phone": "string", // Optional
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zip": "string",
    "country": "string"
  }, // Optional
  "ethnicity": "string", // Optional
  "race": "string", // Optional
  "preferredLanguage": "string", // Optional, default: English
  "religion": "string", // Optional
  "emergencyContact": {
    "name": "string",
    "relationship": "string",
    "phone": "string",
    "email": "string"
  }, // Optional
  "insuranceInfo": {
    "provider": "string",
    "policyNumber": "string",
    "groupNumber": "string"
  } // Optional
}
```

**Response:**
```json
{
  "message": "Patient created successfully",
  "patient": {
    "id": "uuid",
    "medicalRecordNumber": "string",
    "firstName": "string",
    "lastName": "string",
    "dateOfBirth": "date"
  }
}
```

### GET /patients/:id

Get patient details.

**Headers:** Authorization required

**Response:**
```json
{
  "patient": {
    "id": "uuid",
    "firstName": "string",
    "lastName": "string",
    "middleName": "string",
    "dateOfBirth": "date",
    "gender": "string",
    "ssn": "string",
    "email": "string",
    "phone": "string",
    "address": { ... },
    "ethnicity": "string",
    "race": "string",
    "preferredLanguage": "string",
    "religion": "string",
    "emergencyContact": { ... },
    "insuranceInfo": { ... },
    "medicalRecordNumber": "string",
    "status": "string",
    "consentGiven": boolean,
    "consentDate": "datetime",
    "dataSharingPreferences": { ... },
    "createdAt": "datetime",
    "updatedAt": "datetime",
    "medicalHistories": [
      {
        "id": "uuid",
        "historyType": "string",
        "title": "string",
        "description": "string",
        "onsetDate": "date",
        "endDate": "date",
        "status": "string",
        "priority": "string",
        "dataSource": "string",
        "reliabilityScore": number,
        "createdAt": "datetime"
      }
    ]
  }
}
```

### PUT /patients/:id

Update patient information.

**Headers:** Authorization required

**Request Body:** Same as POST /patients

**Response:**
```json
{
  "message": "Patient updated successfully",
  "patient": { ... } // Updated patient object
}
```

### GET /patients/search

Advanced patient search with filters.

**Headers:** Authorization required

**Query Parameters:**
- `query` (string): Search term
- `ageRange` (string): Age range filter (e.g., "18-65")
- `gender` (string): Gender filter
- `status` (string): Status filter
- `hasAllergies` (boolean): Filter patients with allergies
- `hasMedications` (boolean): Filter patients with medications
- `lastVisitDate` (date): Filter by last visit date

## Medical History Endpoints

### GET /medical-history

Get medical history entries with filters.

**Headers:** Authorization required

**Query Parameters:**
- `patientId` (uuid): Filter by patient ID
- `historyType` (string): Filter by history type
- `status` (string): Filter by status
- `priority` (string): Filter by priority
- `page` (number): Page number
- `limit` (number): Items per page

**Response:**
```json
{
  "medicalHistories": [
    {
      "id": "uuid",
      "patientId": "uuid",
      "historyType": "string",
      "title": "string",
      "description": "string",
      "content": { ... }, // JSON content
      "icd10Codes": [ ... ],
      "cptCodes": [ ... ],
      "snomedCodes": [ ... ],
      "onsetDate": "date",
      "endDate": "date",
      "isCurrent": boolean,
      "dataSource": "string",
      "reliabilityScore": number,
      "notes": "string",
      "status": "string",
      "priority": "string",
      "createdAt": "datetime",
      "patient": {
        "id": "uuid",
        "firstName": "string",
        "lastName": "string",
        "medicalRecordNumber": "string"
      },
      "creator": {
        "id": "uuid",
        "firstName": "string",
        "lastName": "string",
        "role": "string"
      }
    }
  ],
  "pagination": { ... }
}
```

### POST /medical-history

Create new medical history entry.

**Headers:** Authorization required

**Request Body:**
```json
{
  "patientId": "uuid",
  "historyType": "chief_complaint|history_of_present_illness|past_medical_history|family_history|social_history|medications|allergies|review_of_systems|vital_signs|immunizations|preventive_care",
  "title": "string",
  "description": "string",
  "content": { ... }, // JSON content
  "icd10Codes": [ "string" ],
  "cptCodes": [ "string" ],
  "snomedCodes": [ "string" ],
  "onsetDate": "date",
  "endDate": "date",
  "isCurrent": boolean,
  "dataSource": "patient_interview|family_report|previous_records|physician_observation|laboratory_results|imaging_results|other",
  "reliabilityScore": number, // 1-5
  "notes": "string",
  "priority": "low|medium|high|critical"
}
```

### GET /medical-history/:id

Get specific medical history entry.

**Headers:** Authorization required

**Response:**
```json
{
  "medicalHistory": {
    "id": "uuid",
    "patientId": "uuid",
    "historyType": "string",
    "title": "string",
    "description": "string",
    "content": { ... },
    "icd10Codes": [ ... ],
    "cptCodes": [ ... ],
    "snomedCodes": [ ... ],
    "onsetDate": "date",
    "endDate": "date",
    "isCurrent": boolean,
    "dataSource": "string",
    "reliabilityScore": number,
    "notes": "string",
    "status": "string",
    "priority": "string",
    "createdAt": "datetime",
    "patient": { ... },
    "creator": { ... }
  }
}
```

### PUT /medical-history/:id

Update medical history entry.

**Headers:** Authorization required

**Request Body:** Same as POST /medical-history

### DELETE /medical-history/:id

Delete medical history entry (soft delete).

**Headers:** Authorization required

**Response:**
```json
{
  "message": "Medical history deleted successfully"
}
```

## User Management Endpoints

### GET /users

Get list of users with pagination and filters.

**Headers:** Authorization required (Admin/Healthcare Administrator only)

**Query Parameters:**
- `page` (number): Page number
- `limit` (number): Items per page
- `role` (string): Filter by role
- `isActive` (boolean): Filter by active status
- `search` (string): Search term

**Response:**
```json
{
  "users": [
    {
      "id": "uuid",
      "username": "string",
      "email": "string",
      "firstName": "string",
      "lastName": "string",
      "role": "string",
      "isActive": boolean,
      "lastLogin": "datetime",
      "createdAt": "datetime"
    }
  ],
  "pagination": { ... }
}
```

### GET /users/:id

Get user details.

**Headers:** Authorization required (Admin/Healthcare Administrator only)

### PUT /users/:id

Update user information.

**Headers:** Authorization required (Admin/Healthcare Administrator only)

### DELETE /users/:id

Delete user (soft delete).

**Headers:** Authorization required (Admin only)

### POST /users/:id/reset-password

Reset user password.

**Headers:** Authorization required (Admin/Healthcare Administrator only)

**Request Body:**
```json
{
  "newPassword": "string"
}
```

### POST /users/:id/activate

Activate user account.

**Headers:** Authorization required (Admin/Healthcare Administrator only)

### POST /users/:id/deactivate

Deactivate user account.

**Headers:** Authorization required (Admin/Healthcare Administrator only)

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limiting

- General API: 100 requests per 15 minutes
- Authentication: 5 attempts per 15 minutes
- File uploads: 10 requests per hour

## Security Headers

All responses include security headers:
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

## Audit Logging

All API requests are logged for compliance:
- User ID and role
- Action performed
- Resource accessed
- Timestamp
- IP address
- Request/response data (for sensitive operations)

## Data Validation

All input data is validated using Joi schemas:
- Required field validation
- Data type validation
- Format validation (email, phone, SSN)
- Medical coding validation
- Date range validation

## Examples

### Complete Patient Creation Flow

1. **Create Patient:**
```bash
curl -X POST http://localhost:3001/api/patients \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "1990-01-01",
    "gender": "male",
    "email": "john.doe@email.com",
    "phone": "555-123-4567"
  }'
```

2. **Add Medical History:**
```bash
curl -X POST http://localhost:3001/api/medical-history \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patientId": "patient-uuid",
    "historyType": "allergies",
    "title": "Penicillin Allergy",
    "description": "Patient reports severe allergic reaction to penicillin",
    "dataSource": "patient_interview",
    "reliabilityScore": 5,
    "priority": "high"
  }'
```

### Search and Filter Examples

**Search patients by name:**
```bash
curl "http://localhost:3001/api/patients?search=John&limit=10"
```

**Filter medical history by type:**
```bash
curl "http://localhost:3001/api/medical-history?historyType=allergies&status=active"
```

**Advanced patient search:**
```bash
curl "http://localhost:3001/api/patients/search?query=John&gender=male&hasAllergies=true"
```