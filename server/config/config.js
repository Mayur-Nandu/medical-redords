require('dotenv').config();

const config = {
  // Server configuration
  server: {
    port: process.env.PORT || 3001,
    env: process.env.NODE_ENV || 'development'
  },

  // Database configuration
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    name: process.env.DB_NAME || 'medical_history_db',
    user: process.env.DB_USER || 'medical_user',
    password: process.env.DB_PASSWORD,
    ssl: process.env.NODE_ENV === 'production',
    logging: process.env.NODE_ENV === 'development' ? console.log : false
  },

  // Security configuration
  security: {
    jwtSecret: process.env.JWT_SECRET,
    jwtExpiresIn: process.env.JWT_EXPIRES_IN || '24h',
    encryptionKey: process.env.ENCRYPTION_KEY,
    sessionSecret: process.env.SESSION_SECRET,
    rateLimitWindowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000, // 15 minutes
    rateLimitMaxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
    autoLogoutMinutes: parseInt(process.env.AUTO_LOGOUT_MINUTES) || 30
  },

  // File upload configuration
  upload: {
    maxFileSize: parseInt(process.env.MAX_FILE_SIZE) || 10485760, // 10MB
    uploadPath: process.env.UPLOAD_PATH || './uploads',
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
  },

  // Email configuration
  email: {
    host: process.env.SMTP_HOST,
    port: process.env.SMTP_PORT || 587,
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS
  },

  // Audit logging configuration
  audit: {
    level: process.env.AUDIT_LOG_LEVEL || 'info',
    logFile: process.env.AUDIT_LOG_FILE || './logs/audit.log'
  },

  // HIPAA compliance configuration
  hipaa: {
    dataRetentionYears: parseInt(process.env.DATA_RETENTION_YEARS) || 7,
    encryptionRequired: true,
    auditTrailRequired: true,
    accessLoggingRequired: true
  }
};

module.exports = config;