# Medical History Recording Application

A comprehensive, HIPAA-compliant medical history recording application designed for healthcare providers to efficiently capture, store, and manage patient medical histories and associated metadata.

## Features

### Core Functionality
- **Patient Management**: Complete patient demographics and contact information
- **Medical History Recording**: Comprehensive medical history categories including:
  - Chief Complaint
  - History of Present Illness (HPI)
  - Past Medical History
  - Family History
  - Social History
  - Medications
  - Allergies
  - Review of Systems (ROS)
  - Vital Signs
  - Immunizations
  - Preventive Care

### Security & Compliance
- **HIPAA Compliant**: Full adherence to healthcare data protection regulations
- **End-to-End Encryption**: Data encrypted in transit and at rest
- **Role-Based Access Control**: Multi-level user permissions
- **Audit Logging**: Comprehensive activity tracking
- **Two-Factor Authentication**: Enhanced security for user accounts
- **Data Backup**: Automated secure backup and disaster recovery

### User Interface
- **Healthcare Provider Dashboard**: Intuitive interface for medical professionals
- **Patient Portal**: Self-service portal for patients
- **Mobile Responsive**: Works on all devices
- **Real-time Validation**: Medical coding and data validation
- **Advanced Search**: Powerful search and filtering capabilities

## Technology Stack

### Backend
- **Node.js** with Express.js
- **PostgreSQL** database
- **Sequelize** ORM
- **JWT** authentication
- **bcryptjs** password hashing
- **Helmet** security middleware
- **Winston** logging

### Frontend
- **React** with TypeScript
- **Material-UI** component library
- **React Router** for navigation
- **Axios** for API calls
- **React Hook Form** for form handling

## Installation

### Prerequisites
- Node.js (v16 or higher)
- PostgreSQL (v12 or higher)
- npm or yarn

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd medical-history-app
   ```

2. **Install dependencies**
   ```bash
   # Install backend dependencies
   npm install
   
   # Install frontend dependencies
   cd client
   npm install
   cd ..
   ```

3. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb medical_history_db
   
   # Create database user
   psql -c "CREATE USER medical_user WITH PASSWORD 'secure_password_here';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE medical_history_db TO medical_user;"
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Edit .env file with your configuration
   nano .env
   ```

5. **Database Migration**
   ```bash
   npm run migrate
   ```

6. **Start the application**
   ```bash
   # Development mode (runs both backend and frontend)
   npm run dev
   
   # Or start individually
   npm start          # Backend only
   cd client && npm start  # Frontend only
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | medical_history_db |
| `DB_USER` | Database user | medical_user |
| `DB_PASSWORD` | Database password | - |
| `JWT_SECRET` | JWT signing secret | - |
| `ENCRYPTION_KEY` | Data encryption key | - |
| `PORT` | Server port | 3001 |
| `NODE_ENV` | Environment | development |

### Security Configuration

The application includes several security features:

- **Rate Limiting**: Prevents brute force attacks
- **CORS Protection**: Configurable cross-origin resource sharing
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Content Security Policy headers

## Usage

### Default Admin Account
After running the migration, a default admin account is created:
- **Username**: admin
- **Password**: Admin123!

**Important**: Change the default password immediately after first login.

### User Roles

1. **Admin**: Full system access
2. **Physician**: Patient and medical history management
3. **Nurse**: Patient care and history recording
4. **Medical Assistant**: Basic patient data entry
5. **Healthcare Administrator**: User and system management
6. **Patient**: Self-service portal access

### Key Features

#### Patient Management
- Add new patients with complete demographics
- Search and filter patient records
- View patient medical history timeline
- Update patient information

#### Medical History Recording
- Record comprehensive medical histories
- Categorize by history type
- Set priority levels and status
- Track data source and reliability
- Medical coding integration (ICD-10, CPT, SNOMED CT)

#### Security Features
- Two-factor authentication setup
- Role-based access control
- Comprehensive audit logging
- Data encryption at rest and in transit

## API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Patient Endpoints
- `GET /api/patients` - List patients
- `POST /api/patients` - Create patient
- `GET /api/patients/:id` - Get patient details
- `PUT /api/patients/:id` - Update patient

### Medical History Endpoints
- `GET /api/medical-history` - List medical histories
- `POST /api/medical-history` - Create medical history
- `GET /api/medical-history/:id` - Get medical history
- `PUT /api/medical-history/:id` - Update medical history

## Development

### Project Structure
```
medical-history-app/
├── server/                 # Backend application
│   ├── config/           # Configuration files
│   ├── controllers/      # Route controllers
│   ├── middleware/       # Custom middleware
│   ├── models/          # Database models
│   ├── routes/          # API routes
│   └── scripts/         # Utility scripts
├── client/               # Frontend application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── contexts/    # React contexts
│   │   ├── pages/       # Page components
│   │   └── utils/       # Utility functions
└── uploads/              # File uploads directory
```

### Running Tests
```bash
npm test
```

### Linting
```bash
npm run lint
```

## Deployment

### Production Considerations

1. **Environment Variables**: Set all production environment variables
2. **Database Security**: Use strong passwords and SSL connections
3. **HTTPS**: Enable SSL/TLS encryption
4. **Firewall**: Configure appropriate firewall rules
5. **Backup**: Set up automated database backups
6. **Monitoring**: Implement application monitoring
7. **Updates**: Regular security updates

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d
```

## Compliance

### HIPAA Compliance Features
- **Access Controls**: Role-based permissions
- **Audit Logs**: Complete activity tracking
- **Data Encryption**: End-to-end encryption
- **Backup & Recovery**: Secure data backup
- **User Authentication**: Multi-factor authentication
- **Data Integrity**: Input validation and verification

### Data Retention
- Patient data retained for 7 years (configurable)
- Audit logs maintained for compliance
- Secure data deletion procedures

## Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Review the documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security

If you discover a security vulnerability, please:
1. Do not create a public issue
2. Contact the security team directly
3. Provide detailed information about the vulnerability

---

**Important**: This application handles sensitive medical data. Ensure proper security measures are in place before deployment to production.