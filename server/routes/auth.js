const express = require('express');
const { body } = require('express-validator');
const authController = require('../controllers/authController');
const securityMiddleware = require('../middleware/security');

const router = express.Router();

// Validation middleware
const registerValidation = [
  body('username')
    .isLength({ min: 3, max: 50 })
    .withMessage('Username must be between 3 and 50 characters')
    .isAlphanumeric()
    .withMessage('Username must contain only letters and numbers'),
  body('email')
    .isEmail()
    .withMessage('Please provide a valid email address'),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'),
  body('firstName')
    .notEmpty()
    .withMessage('First name is required'),
  body('lastName')
    .notEmpty()
    .withMessage('Last name is required'),
  body('role')
    .isIn(['admin', 'physician', 'nurse', 'medical_assistant', 'healthcare_administrator', 'patient'])
    .withMessage('Invalid role specified')
];

const loginValidation = [
  body('username')
    .notEmpty()
    .withMessage('Username is required'),
  body('password')
    .notEmpty()
    .withMessage('Password is required')
];

const twoFactorValidation = [
  body('token')
    .isLength({ min: 6, max: 6 })
    .withMessage('Two-factor authentication code must be 6 digits')
    .isNumeric()
    .withMessage('Two-factor authentication code must be numeric')
];

// Routes
router.post('/register', 
  securityMiddleware.authRateLimit,
  registerValidation,
  authController.register
);

router.post('/login',
  securityMiddleware.authRateLimit,
  loginValidation,
  authController.login
);

router.post('/logout',
  securityMiddleware.verifyToken,
  authController.logout
);

router.get('/profile',
  securityMiddleware.verifyToken,
  authController.getProfile
);

router.put('/profile',
  securityMiddleware.verifyToken,
  [
    body('firstName').optional().notEmpty(),
    body('lastName').optional().notEmpty(),
    body('email').optional().isEmail(),
    body('phone').optional().isMobilePhone()
  ],
  authController.updateProfile
);

router.get('/2fa/setup',
  securityMiddleware.verifyToken,
  authController.setupTwoFactor
);

router.post('/2fa/enable',
  securityMiddleware.verifyToken,
  twoFactorValidation,
  authController.enableTwoFactor
);

module.exports = router;