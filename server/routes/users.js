const express = require('express');
const { body, param, query } = require('express-validator');
const userController = require('../controllers/userController');
const securityMiddleware = require('../middleware/security');

const router = express.Router();

// All routes require authentication
router.use(securityMiddleware.verifyToken);

// User validation
const updateUserValidation = [
  body('firstName').optional().notEmpty().isLength({ max: 100 }),
  body('lastName').optional().notEmpty().isLength({ max: 100 }),
  body('email').optional().isEmail(),
  body('phone').optional().isMobilePhone(),
  body('role').optional().isIn([
    'admin',
    'physician',
    'nurse',
    'medical_assistant',
    'healthcare_administrator',
    'patient'
  ]),
  body('isActive').optional().isBoolean(),
  body('permissions').optional().isObject(),
  body('accessiblePatients').optional().isArray()
];

// Routes
router.get('/',
  securityMiddleware.requireRole(['admin', 'healthcare_administrator']),
  [
    query('page').optional().isInt({ min: 1 }),
    query('limit').optional().isInt({ min: 1, max: 100 }),
    query('role').optional().isIn([
      'admin',
      'physician',
      'nurse',
      'medical_assistant',
      'healthcare_administrator',
      'patient'
    ]),
    query('isActive').optional().isBoolean(),
    query('search').optional().isLength({ max: 100 })
  ],
  securityMiddleware.auditLog('READ', 'USER'),
  userController.getUsers
);

router.get('/:id',
  securityMiddleware.requireRole(['admin', 'healthcare_administrator']),
  [
    param('id').isUUID().withMessage('Invalid user ID')
  ],
  securityMiddleware.auditLog('READ', 'USER'),
  userController.getUserById
);

router.put('/:id',
  securityMiddleware.requireRole(['admin', 'healthcare_administrator']),
  [
    param('id').isUUID().withMessage('Invalid user ID')
  ],
  updateUserValidation,
  securityMiddleware.auditLog('UPDATE', 'USER'),
  userController.updateUser
);

router.delete('/:id',
  securityMiddleware.requireRole(['admin']),
  [
    param('id').isUUID().withMessage('Invalid user ID')
  ],
  securityMiddleware.auditLog('DELETE', 'USER'),
  userController.deleteUser
);

router.post('/:id/reset-password',
  securityMiddleware.requireRole(['admin', 'healthcare_administrator']),
  [
    param('id').isUUID().withMessage('Invalid user ID')
  ],
  securityMiddleware.auditLog('RESET_PASSWORD', 'USER'),
  userController.resetUserPassword
);

router.post('/:id/activate',
  securityMiddleware.requireRole(['admin', 'healthcare_administrator']),
  [
    param('id').isUUID().withMessage('Invalid user ID')
  ],
  securityMiddleware.auditLog('ACTIVATE_USER', 'USER'),
  userController.activateUser
);

router.post('/:id/deactivate',
  securityMiddleware.requireRole(['admin', 'healthcare_administrator']),
  [
    param('id').isUUID().withMessage('Invalid user ID')
  ],
  securityMiddleware.auditLog('DEACTIVATE_USER', 'USER'),
  userController.deactivateUser
);

module.exports = router;