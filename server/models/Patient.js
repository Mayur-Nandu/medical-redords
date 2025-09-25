const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Patient = sequelize.define('Patient', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  
  // Personal Information
  firstName: {
    type: DataTypes.STRING(100),
    allowNull: false,
    validate: {
      notEmpty: true,
      len: [1, 100]
    }
  },
  lastName: {
    type: DataTypes.STRING(100),
    allowNull: false,
    validate: {
      notEmpty: true,
      len: [1, 100]
    }
  },
  middleName: {
    type: DataTypes.STRING(100),
    allowNull: true
  },
  dateOfBirth: {
    type: DataTypes.DATEONLY,
    allowNull: false,
    validate: {
      isDate: true,
      isBefore: new Date().toISOString().split('T')[0]
    }
  },
  gender: {
    type: DataTypes.ENUM('male', 'female', 'other', 'prefer_not_to_say'),
    allowNull: false
  },
  ssn: {
    type: DataTypes.STRING(11),
    allowNull: true,
    unique: true,
    validate: {
      is: /^\d{3}-\d{2}-\d{4}$/
    }
  },
  
  // Contact Information
  email: {
    type: DataTypes.STRING(255),
    allowNull: true,
    validate: {
      isEmail: true
    }
  },
  phone: {
    type: DataTypes.STRING(20),
    allowNull: true,
    validate: {
      is: /^[\+]?[1-9][\d]{0,15}$/
    }
  },
  address: {
    type: DataTypes.JSON,
    allowNull: true
  },
  
  // Demographics
  ethnicity: {
    type: DataTypes.STRING(100),
    allowNull: true
  },
  race: {
    type: DataTypes.STRING(100),
    allowNull: true
  },
  preferredLanguage: {
    type: DataTypes.STRING(50),
    allowNull: true,
    defaultValue: 'English'
  },
  religion: {
    type: DataTypes.STRING(100),
    allowNull: true
  },
  
  // Emergency Contact
  emergencyContact: {
    type: DataTypes.JSON,
    allowNull: true
  },
  
  // Insurance Information
  insuranceInfo: {
    type: DataTypes.JSON,
    allowNull: true
  },
  
  // Medical Record Number
  medicalRecordNumber: {
    type: DataTypes.STRING(50),
    allowNull: false,
    unique: true
  },
  
  // Status
  status: {
    type: DataTypes.ENUM('active', 'inactive', 'deceased'),
    defaultValue: 'active'
  },
  
  // HIPAA Compliance
  consentGiven: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },
  consentDate: {
    type: DataTypes.DATE,
    allowNull: true
  },
  dataSharingPreferences: {
    type: DataTypes.JSON,
    allowNull: true
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
  tableName: 'patients',
  indexes: [
    {
      fields: ['medicalRecordNumber']
    },
    {
      fields: ['lastName', 'firstName']
    },
    {
      fields: ['dateOfBirth']
    },
    {
      fields: ['status']
    }
  ]
});

module.exports = Patient;