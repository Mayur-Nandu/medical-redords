# Medical History Recording Application

A comprehensive, HIPAA-compliant medical history recording application for healthcare providers to efficiently capture, store, and manage patient medical histories with complete audit trails and security features.

## 🏥 Features

### Core Functionality
- **Patient Demographics & Management**: Complete patient information with encrypted sensitive data
- **Comprehensive Medical History**: Past medical history, family history, social history
- **Medication Management**: Current and past medications with drug interaction checking capabilities
- **Allergy Tracking**: Drug, food, and environmental allergies with severity levels
- **Review of Systems**: Systematic symptom review by body system
- **Clinical Data**: Vital signs, lab results, and imaging integration ready

### Security & Compliance
- **HIPAA Compliance**: Full adherence to healthcare data protection regulations
- **End-to-End Encryption**: Sensitive data encrypted at rest and in transit
- **Role-Based Access Control**: Physician, nurse, admin, patient roles with granular permissions
- **Comprehensive Audit Trail**: Every action logged with user, timestamp, and IP address
- **Multi-Factor Authentication**: Optional TOTP support for enhanced security
- **Session Management**: Secure session handling with automatic timeouts

### Technical Features
- **RESTful API**: Complete API with OpenAPI/Swagger documentation
- **Modern Architecture**: Django-based with PostgreSQL, Redis, and Celery
- **Scalable Design**: Built for growth with proper indexing and optimization
- **Integration Ready**: HL7 FHIR compatible, EHR integration endpoints
- **Responsive UI**: Bootstrap-based interface with mobile support

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching and task queue)

### Installation

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd medical_history_app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
Create a `.env` file:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=medical_history_db
DB_USER=medical_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
ENCRYPTION_KEY=your-encryption-key-here
```

3. **Database Setup**
```bash
# Create PostgreSQL database
createdb medical_history_db

# Run setup script (creates tables, superuser, sample data)
python setup_database.py
```

4. **Start Development Server**
```bash
python manage.py runserver
```

5. **Access the Application**
- Dashboard: http://localhost:8000/
- Admin Interface: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/api/docs/

### Default Login Credentials
- **Admin**: username=`admin`, password=`admin123`
- **Sample Physician**: username=`dr_smith`, password=`doctor123`

## 📋 API Endpoints

### Authentication
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout
- `POST /accounts/register/` - User registration
- `GET /accounts/profile/` - Get user profile
- `POST /accounts/change-password/` - Change password

### Patients
- `GET /api/v1/patients/` - List patients (with search)
- `POST /api/v1/patients/` - Create patient
- `GET /api/v1/patients/{id}/` - Get patient details
- `PUT /api/v1/patients/{id}/` - Update patient
- `DELETE /api/v1/patients/{id}/` - Soft delete patient
- `GET /api/v1/patients/{id}/alerts/` - Get patient alerts

### Medical Records
- `GET /api/v1/medical-records/{patient_id}/` - Get medical history
- `PUT /api/v1/medical-records/{patient_id}/` - Update medical history
- `GET /api/v1/medical-records/{patient_id}/summary/` - Get summary
- `GET/POST /api/v1/medical-records/{patient_id}/medications/` - Medications
- `GET/POST /api/v1/medical-records/{patient_id}/allergies/` - Allergies
- `GET/POST /api/v1/medical-records/{patient_id}/past-history/` - Past medical history

## 🔐 Security Features

### Data Protection
- **Encryption at Rest**: Sensitive fields encrypted using Fernet (AES 128)
- **Encryption in Transit**: HTTPS/TLS for all communications
- **Field-Level Encryption**: Patient names, SSN, medical details encrypted
- **Key Management**: Separate encryption keys for different data types

### Access Control
- **Role-Based Permissions**: Different access levels for different user types
- **Patient Data Isolation**: Patients can only access their own data
- **Provider Network Access**: Healthcare providers can access assigned patients
- **Administrative Oversight**: Admins have full access with audit trails

### Audit & Compliance
- **Complete Audit Trail**: Every data access and modification logged
- **HIPAA Logging**: Specialized logging for compliance requirements
- **Failed Access Attempts**: Automatic account locking after failed attempts
- **Session Tracking**: All user sessions monitored and logged
- **Data Breach Detection**: Automated alerts for suspicious activity

## 🏗️ Architecture

### Database Schema
- **Patient Management**: Encrypted demographics and identifiers
- **Medical Records**: Comprehensive medical history with versioning
- **Clinical Data**: Vital signs, lab results, imaging (extensible)
- **Audit Trail**: Complete logging of all system activities
- **User Management**: Role-based authentication with organizations

### Application Structure
```
medical_history_app/
├── core/                 # Core functionality and shared models
├── accounts/             # User management and authentication
├── patients/             # Patient demographics and management
├── medical_records/      # Medical history and clinical data
├── clinical_data/        # Vital signs, lab results, imaging
├── audit_trail/          # Comprehensive audit logging
├── templates/            # Web interface templates
└── medical_history/      # Django project settings
```

### Technology Stack
- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL with encrypted fields
- **Caching**: Redis for session storage and caching
- **Task Queue**: Celery for background processing
- **Security**: OAuth2, TOTP, bcrypt password hashing
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Documentation**: OpenAPI/Swagger

## 📊 User Roles & Permissions

### Patient
- View own medical records
- Update contact information
- Consent management
- Appointment history

### Medical Assistant
- Patient registration
- Basic demographic updates
- Vital signs entry
- Appointment scheduling

### Nurse
- All Medical Assistant permissions
- Medication administration
- Clinical note entry
- Patient education documentation

### Physician
- All Nurse permissions
- Diagnosis and treatment plans
- Prescription management
- Medical history updates
- E-prescribing (when integrated)

### Administrator
- User management
- System configuration
- Audit log access
- Backup and recovery
- Compliance reporting

## 🔧 Configuration

### Environment Variables
```bash
# Security
SECRET_KEY=django-secret-key
ENCRYPTION_KEY=fernet-encryption-key

# Database
DB_NAME=medical_history_db
DB_USER=medical_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Cache/Queue
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0

# Security Settings
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### HIPAA Compliance Settings
The application includes several HIPAA-specific configurations:

- **Minimum Password Requirements**: 12+ characters, complexity requirements
- **Session Timeouts**: Automatic logout after inactivity
- **Audit Logging**: All access attempts logged with IP addresses
- **Data Encryption**: PHI encrypted with FIPS 140-2 approved algorithms
- **Access Controls**: Role-based permissions with least privilege principle

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-django pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Data
The setup script creates sample data for testing:
- Sample organization and users
- Test patient with complete medical history
- Medical codes (ICD-10, CPT, RxNorm)
- Audit trail examples

## 📈 Production Deployment

### Prerequisites
- PostgreSQL 12+ with SSL
- Redis for caching and sessions
- Web server (Nginx recommended)
- HTTPS certificate (required for HIPAA)

### Security Checklist
- [ ] HTTPS/TLS enabled
- [ ] Database encryption at rest
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Access logs monitored
- [ ] Intrusion detection system
- [ ] Business Associate Agreements signed

### Performance Optimization
- Database indexing on frequently queried fields
- Redis caching for session storage
- Static file serving via CDN
- Database connection pooling
- Background task processing with Celery

## 📚 API Documentation

### Interactive Documentation
Visit `/api/docs/` for interactive Swagger documentation with:
- Complete endpoint documentation
- Request/response examples
- Authentication requirements
- Field descriptions and validation rules

### Authentication
The API uses OAuth2 for authentication. Include the access token in the Authorization header:
```
Authorization: Bearer your-access-token
```

### Rate Limiting
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Admin users: Unlimited

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Ensure HIPAA compliance for any PHI handling
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guide
- Include docstrings for all functions
- Write tests for new functionality
- Security review for PHI handling
- Performance testing for database queries

## 📄 License

This project is proprietary software for healthcare organizations. See LICENSE file for details.

## 🆘 Support

### Documentation
- API Documentation: `/api/docs/`
- Admin Guide: See admin interface help
- User Manual: Available in application

### Contact
- Technical Support: support@example.com
- Security Issues: security@example.com
- HIPAA Compliance: compliance@example.com

---

**⚠️ IMPORTANT**: This application handles Protected Health Information (PHI). Ensure proper HIPAA compliance measures are in place before deploying to production, including but not limited to: proper encryption, access controls, audit logging, and Business Associate Agreements with all service providers.