const express = require('express');
const { body, param, query } = require('express-validator');
const patientController = require('../controllers/patientController');
const securityMiddleware = require('../middleware/security');

const router = express.Router();

// Validation middleware
const createPatientValidation = [
  body('firstName')
    .notEmpty()
    .withMessage('First name is required')
    .isLength({ max: 100 })
    .withMessage('First name must be less than 100 characters'),
  body('lastName')
    .notEmpty()
    .withMessage('Last name is required')
    .isLength({ max: 100 })
    .withMessage('Last name must be less than 100 characters'),
  body('dateOfBirth')
    .isISO8601()
    .withMessage('Date of birth must be a valid date')
    .custom((value) => {
      if (new Date(value) > new Date()) {
        throw new Error('Date of birth cannot be in the future');
      }
      return true;
    }),
  body('gender')
    .isIn(['male', 'female', 'other', 'prefer_not_to_say'])
    .withMessage('Invalid gender specified'),
  body('email')
    .optional()
    .isEmail()
    .withMessage('Please provide a valid email address'),
  body('phone')
    .optional()
    .isMobilePhone()
    .withMessage('Please provide a valid phone number'),
  body('ssn')
    .optional()
    .matches(/^\d{3}-\d{2}-\d{4}$/)
    .withMessage('SSN must be in format XXX-XX-XXXX')
];

const medicalHistoryValidation = [
  body('historyType')
    .isIn([
      'chief_complaint',
      'history_of_present_illness',
      'past_medical_history',
      'family_history',
      'social_history',
      'medications',
      'allergies',
      'review_of_systems',
      'vital_signs',
      'immunizations',
      'preventive_care'
    ])
    .withMessage('Invalid history type'),
  body('title')
    .notEmpty()
    .withMessage('Title is required')
    .isLength({ max: 255 })
    .withMessage('Title must be less than 255 characters'),
  body('dataSource')
    .isIn([
      'patient_interview',
      'family_report',
      'previous_records',
      'physician_observation',
      'laboratory_results',
      'imaging_results',
      'other'
    ])
    .withMessage('Invalid data source'),
  body('reliabilityScore')
    .optional()
    .isInt({ min: 1, max: 5 })
    .withMessage('Reliability score must be between 1 and 5'),
  body('onsetDate')
    .optional()
    .isISO8601()
    .withMessage('Onset date must be a valid date'),
  body('endDate')
    .optional()
    .isISO8601()
    .withMessage('End date must be a valid date')
];

// All routes require authentication
router.use(securityMiddleware.verifyToken);

// Patient routes
router.post('/',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant']),
  createPatientValidation,
  securityMiddleware.auditLog('CREATE', 'PATIENT'),
  patientController.createPatient
);

router.get('/',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant', 'healthcare_administrator']),
  [
    query('page').optional().isInt({ min: 1 }),
    query('limit').optional().isInt({ min: 1, max: 100 }),
    query('search').optional().isLength({ max: 100 }),
    query('status').optional().isIn(['active', 'inactive', 'deceased']),
    query('sortBy').optional().isIn(['firstName', 'lastName', 'dateOfBirth', 'createdAt']),
    query('sortOrder').optional().isIn(['ASC', 'DESC'])
  ],
  patientController.getPatients
);

router.get('/search',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant', 'healthcare_administrator']),
  patientController.searchPatients
);

router.get('/:patientId',
  securityMiddleware.requirePatientAccess,
  [
    param('patientId').isUUID().withMessage('Invalid patient ID')
  ],
  securityMiddleware.auditLog('READ', 'PATIENT'),
  patientController.getPatientById
);

router.put('/:patientId',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant']),
  securityMiddleware.requirePatientAccess,
  [
    param('patientId').isUUID().withMessage('Invalid patient ID')
  ],
  securityMiddleware.auditLog('UPDATE', 'PATIENT'),
  patientController.updatePatient
);

// Medical history routes
router.post('/:patientId/medical-history',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant']),
  securityMiddleware.requirePatientAccess,
  [
    param('patientId').isUUID().withMessage('Invalid patient ID')
  ],
  medicalHistoryValidation,
  securityMiddleware.auditLog('CREATE', 'MEDICAL_HISTORY'),
  patientController.addMedicalHistory
);

router.get('/:patientId/medical-history',
  securityMiddleware.requirePatientAccess,
  [
    param('patientId').isUUID().withMessage('Invalid patient ID'),
    query('historyType').optional().isIn([
      'chief_complaint',
      'history_of_present_illness',
      'past_medical_history',
      'family_history',
      'social_history',
      'medications',
      'allergies',
      'review_of_systems',
      'vital_signs',
      'immunizations',
      'preventive_care'
    ]),
    query('status').optional().isIn(['active', 'resolved', 'inactive'])
  ],
  securityMiddleware.auditLog('READ', 'MEDICAL_HISTORY'),
  patientController.getMedicalHistory
);

router.put('/:patientId/medical-history/:historyId',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant']),
  securityMiddleware.requirePatientAccess,
  [
    param('patientId').isUUID().withMessage('Invalid patient ID'),
    param('historyId').isUUID().withMessage('Invalid history ID')
  ],
  securityMiddleware.auditLog('UPDATE', 'MEDICAL_HISTORY'),
  patientController.updateMedicalHistory
);

module.exports = router;