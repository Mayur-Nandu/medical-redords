# Medical History Recording Application

A comprehensive, HIPAA-compliant medical history recording system designed for healthcare providers to efficiently capture, store, and manage patient medical histories and associated metadata.

## Features

### Core Functionality
- **Patient Management**: Complete patient demographics and contact information
- **Medical History**: Comprehensive medical history recording including HPI, past medical history, family history, and social history
- **Clinical Data**: Vital signs, lab results, diagnostic imaging, and clinical notes
- **Medication Management**: Current medications, allergies, and immunization records
- **Preventive Care**: Tracking of preventive care measures and quality indicators

### Security & Compliance
- **HIPAA Compliance**: Full adherence to healthcare data protection regulations
- **End-to-End Encryption**: All sensitive data encrypted at rest and in transit
- **Role-Based Access Control**: Granular permissions for different user types
- **Comprehensive Audit Logging**: Complete audit trail for all system activities
- **Session Management**: Automatic session timeout and security monitoring

### User Interfaces
- **Healthcare Provider Interface**: Intuitive forms for data entry and management
- **Patient Portal**: Self-service portal for patients to view and update their information
- **Administrative Dashboard**: System monitoring and compliance reporting
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices

### Reporting & Analytics
- **Patient Summary Reports**: Comprehensive patient reports for referrals
- **Population Health Analytics**: Aggregate data analysis for public health insights
- **Compliance Reports**: HIPAA compliance monitoring and reporting
- **Quality Metrics**: Healthcare quality indicators and outcome measures

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL with encrypted fields
- **Frontend**: Bootstrap 5, JavaScript, HTML5
- **Security**: OAuth2, JWT tokens, encryption
- **Monitoring**: Comprehensive audit logging
- **Deployment**: Docker-ready, cloud-compatible

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js (for frontend assets)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd medical-history-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/medical_history

# Redis
REDIS_URL=redis://localhost:6379/0

# HIPAA Compliance
ENCRYPTION_KEY=your-encryption-key-here

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Setup

1. Create PostgreSQL database:
   ```sql
   CREATE DATABASE medical_history;
   CREATE USER medical_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE medical_history TO medical_user;
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

### Security Configuration

1. **Generate encryption key**:
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```

2. **Configure HIPAA settings** in `settings.py`:
   ```python
   HIPAA_SETTINGS = {
       'ENCRYPTION_KEY': 'your-encryption-key',
       'AUDIT_LOG_RETENTION_DAYS': 2555,  # 7 years
       'SESSION_TIMEOUT_MINUTES': 30,
       'REQUIRE_MFA': True,
   }
   ```

## Usage

### Healthcare Provider Interface

1. **Login** to the system with your credentials
2. **Navigate** to the dashboard to see system overview
3. **Add patients** using the patient management interface
4. **Record medical history** using the comprehensive forms
5. **View clinical data** including vital signs and lab results
6. **Generate reports** for patient summaries and compliance

### Patient Portal

1. **Access** the patient portal with patient credentials
2. **View** medical history and clinical data
3. **Update** personal information as needed
4. **Schedule** appointments and view upcoming visits
5. **Communicate** with healthcare providers securely

### Administrative Functions

1. **Monitor** system activity through audit logs
2. **Generate** compliance reports for regulatory requirements
3. **Manage** user permissions and access controls
4. **Configure** system settings and integrations

## API Documentation

The system provides a comprehensive REST API for integration with other healthcare systems:

### Authentication
```bash
# Get access token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

### Patient Management
```bash
# Get all patients
curl -H "Authorization: Bearer your-token" \
  http://localhost:8000/api/v1/patients/

# Create new patient
curl -X POST -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "P001234", "first_name": "John", "last_name": "Doe"}' \
  http://localhost:8000/api/v1/patients/
```

### Medical History
```bash
# Get medical history for patient
curl -H "Authorization: Bearer your-token" \
  http://localhost:8000/api/v1/medical-history/?patient=P001234
```

## Security Considerations

### HIPAA Compliance
- All patient data is encrypted at rest using AES-256 encryption
- Data in transit is protected with TLS 1.3
- Comprehensive audit logging for all data access
- Role-based access control with minimum necessary access
- Automatic session timeout and security monitoring

### Data Protection
- Regular security assessments and penetration testing
- Multi-factor authentication for administrative access
- Secure backup and disaster recovery procedures
- Data retention policies compliant with healthcare regulations

### Access Control
- Granular permissions based on user roles
- Patient data access logging and monitoring
- Automatic logout on suspicious activity
- IP address restrictions for sensitive operations

## Deployment

### Production Deployment

1. **Configure production settings**:
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   SECURE_SSL_REDIRECT = True
   SECURE_HSTS_SECONDS = 31536000
   ```

2. **Setup reverse proxy** (Nginx):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Setup SSL certificates**:
   ```bash
   certbot --nginx -d your-domain.com
   ```

### Docker Deployment

1. **Build Docker image**:
   ```bash
   docker build -t medical-history-system .
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

## Monitoring and Maintenance

### Health Checks
- Database connectivity monitoring
- Redis cache status monitoring
- SSL certificate expiration monitoring
- Disk space and memory usage monitoring

### Backup Procedures
- Daily automated database backups
- Encrypted backup storage
- Regular backup restoration testing
- Disaster recovery procedures

### Security Monitoring
- Real-time security event monitoring
- Failed login attempt tracking
- Unusual access pattern detection
- Automated security alerts

## Support and Documentation

### User Documentation
- Comprehensive user guides for all user types
- Video tutorials for common tasks
- FAQ section for common questions
- Contact information for technical support

### Developer Documentation
- API documentation with examples
- Code documentation and comments
- Development setup instructions
- Contributing guidelines

### Compliance Documentation
- HIPAA compliance checklist
- Security assessment reports
- Audit trail documentation
- Data retention policies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Contact

For questions, support, or feature requests, please contact:
- Email: support@medicalhistorysystem.com
- Documentation: https://docs.medicalhistorysystem.com
- Issues: https://github.com/your-org/medical-history-system/issues

---

**Important**: This system handles sensitive healthcare data and must be deployed with appropriate security measures and compliance with all applicable healthcare regulations.