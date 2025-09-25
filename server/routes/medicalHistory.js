const express = require('express');
const { body, query } = require('express-validator');
const medicalHistoryController = require('../controllers/medicalHistoryController');
const securityMiddleware = require('../middleware/security');

const router = express.Router();

// All routes require authentication
router.use(securityMiddleware.verifyToken);

// Medical history validation
const medicalHistoryValidation = [
  body('patientId')
    .isUUID()
    .withMessage('Invalid patient ID'),
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
  body('priority')
    .optional()
    .isIn(['low', 'medium', 'high', 'critical'])
    .withMessage('Invalid priority level')
];

// Routes
router.post('/',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant']),
  medicalHistoryValidation,
  securityMiddleware.auditLog('CREATE', 'MEDICAL_HISTORY'),
  medicalHistoryController.createMedicalHistory
);

router.get('/',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant', 'healthcare_administrator']),
  [
    query('patientId').optional().isUUID(),
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
    query('status').optional().isIn(['active', 'resolved', 'inactive']),
    query('priority').optional().isIn(['low', 'medium', 'high', 'critical']),
    query('page').optional().isInt({ min: 1 }),
    query('limit').optional().isInt({ min: 1, max: 100 })
  ],
  securityMiddleware.auditLog('READ', 'MEDICAL_HISTORY'),
  medicalHistoryController.getMedicalHistories
);

router.get('/:id',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant', 'healthcare_administrator']),
  securityMiddleware.auditLog('READ', 'MEDICAL_HISTORY'),
  medicalHistoryController.getMedicalHistoryById
);

router.put('/:id',
  securityMiddleware.requireRole(['admin', 'physician', 'nurse', 'medical_assistant']),
  securityMiddleware.auditLog('UPDATE', 'MEDICAL_HISTORY'),
  medicalHistoryController.updateMedicalHistory
);

router.delete('/:id',
  securityMiddleware.requireRole(['admin', 'physician']),
  securityMiddleware.auditLog('DELETE', 'MEDICAL_HISTORY'),
  medicalHistoryController.deleteMedicalHistory
);

module.exports = router;