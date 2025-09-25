const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const MedicalHistory = sequelize.define('MedicalHistory', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  
  patientId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'patients',
      key: 'id'
    }
  },
  
  // History Type
  historyType: {
    type: DataTypes.ENUM(
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
    ),
    allowNull: false
  },
  
  // Content
  title: {
    type: DataTypes.STRING(255),
    allowNull: false
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  content: {
    type: DataTypes.JSON,
    allowNull: true
  },
  
  // Medical Coding
  icd10Codes: {
    type: DataTypes.JSON,
    allowNull: true
  },
  cptCodes: {
    type: DataTypes.JSON,
    allowNull: true
  },
  snomedCodes: {
    type: DataTypes.JSON,
    allowNull: true
  },
  
  // Temporal Information
  onsetDate: {
    type: DataTypes.DATE,
    allowNull: true
  },
  endDate: {
    type: DataTypes.DATE,
    allowNull: true
  },
  isCurrent: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  
  // Data Source and Reliability
  dataSource: {
    type: DataTypes.ENUM(
      'patient_interview',
      'family_report',
      'previous_records',
      'physician_observation',
      'laboratory_results',
      'imaging_results',
      'other'
    ),
    allowNull: false
  },
  reliabilityScore: {
    type: DataTypes.INTEGER,
    allowNull: true,
    validate: {
      min: 1,
      max: 5
    }
  },
  notes: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  
  // Status
  status: {
    type: DataTypes.ENUM('active', 'resolved', 'inactive'),
    defaultValue: 'active'
  },
  
  // Priority
  priority: {
    type: DataTypes.ENUM('low', 'medium', 'high', 'critical'),
    defaultValue: 'medium'
  },
  
  // Audit Fields
  createdBy: {
    type: DataTypes.UUID,
    allowNull: false
  },
  lastModifiedBy: {
    type: DataTypes.UUID,
    allowNull: true
  }
}, {
  tableName: 'medical_histories',
  indexes: [
    {
      fields: ['patientId']
    },
    {
      fields: ['historyType']
    },
    {
      fields: ['onsetDate']
    },
    {
      fields: ['status']
    },
    {
      fields: ['priority']
    }
  ]
});

module.exports = MedicalHistory;