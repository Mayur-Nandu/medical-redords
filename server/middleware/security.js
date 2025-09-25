const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const config = require('../config/config');

// HIPAA-compliant security middleware
const securityMiddleware = {
  // Helmet configuration for security headers
  helmet: helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
        connectSrc: ["'self'"],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true
    },
    noSniff: true,
    xssFilter: true,
    referrerPolicy: { policy: 'strict-origin-when-cross-origin' }
  }),

  // Rate limiting for API endpoints
  rateLimit: rateLimit({
    windowMs: config.security.rateLimitWindowMs,
    max: config.security.rateLimitMaxRequests,
    message: {
      error: 'Too many requests from this IP, please try again later.',
      retryAfter: Math.ceil(config.security.rateLimitWindowMs / 1000)
    },
    standardHeaders: true,
    legacyHeaders: false,
  }),

  // Strict rate limiting for authentication endpoints
  authRateLimit: rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // 5 attempts per window
    message: {
      error: 'Too many authentication attempts, please try again later.',
      retryAfter: 900
    },
    skipSuccessfulRequests: true
  }),

  // Data encryption utility
  encrypt: (text) => {
    const algorithm = 'aes-256-gcm';
    const key = crypto.scryptSync(config.security.encryptionKey, 'salt', 32);
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher(algorithm, key);
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  },

  // Data decryption utility
  decrypt: (encryptedData) => {
    const algorithm = 'aes-256-gcm';
    const key = crypto.scryptSync(config.security.encryptionKey, 'salt', 32);
    const decipher = crypto.createDecipher(algorithm, key);
    
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  },

  // JWT token verification middleware
  verifyToken: (req, res, next) => {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ error: 'Access denied. No token provided.' });
    }

    try {
      const decoded = jwt.verify(token, config.security.jwtSecret);
      req.user = decoded;
      next();
    } catch (error) {
      res.status(400).json({ error: 'Invalid token.' });
    }
  },

  // Role-based access control
  requireRole: (roles) => {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Authentication required.' });
      }

      if (!roles.includes(req.user.role)) {
        return res.status(403).json({ error: 'Insufficient permissions.' });
      }

      next();
    };
  },

  // Patient data access control
  requirePatientAccess: (req, res, next) => {
    const patientId = req.params.patientId || req.body.patientId;
    
    if (!patientId) {
      return res.status(400).json({ error: 'Patient ID required.' });
    }

    // Check if user has access to this patient
    if (req.user.role === 'admin' || req.user.role === 'physician') {
      return next();
    }

    // For other roles, check if they have specific access to this patient
    if (req.user.accessiblePatients && req.user.accessiblePatients.includes(patientId)) {
      return next();
    }

    return res.status(403).json({ error: 'Access denied to this patient record.' });
  },

  // Audit logging middleware
  auditLog: (action, resource) => {
    return (req, res, next) => {
      const originalSend = res.send;
      
      res.send = function(data) {
        // Log the action for audit trail
        const auditEntry = {
          timestamp: new Date().toISOString(),
          userId: req.user?.id,
          userRole: req.user?.role,
          action: action,
          resource: resource,
          ipAddress: req.ip,
          userAgent: req.get('User-Agent'),
          statusCode: res.statusCode,
          patientId: req.params.patientId || req.body.patientId
        };

        // Log to audit trail (implement logging service)
        console.log('AUDIT:', JSON.stringify(auditEntry));
        
        originalSend.call(this, data);
      };
      
      next();
    };
  }
};

module.exports = securityMiddleware;