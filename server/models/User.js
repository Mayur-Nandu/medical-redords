const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const User = sequelize.define('User', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  
  // Basic Information
  username: {
    type: DataTypes.STRING(50),
    allowNull: false,
    unique: true,
    validate: {
      len: [3, 50],
      isAlphanumeric: true
    }
  },
  email: {
    type: DataTypes.STRING(255),
    allowNull: false,
    unique: true,
    validate: {
      isEmail: true
    }
  },
  password: {
    type: DataTypes.STRING(255),
    allowNull: false
  },
  
  // Personal Information
  firstName: {
    type: DataTypes.STRING(100),
    allowNull: false
  },
  lastName: {
    type: DataTypes.STRING(100),
    allowNull: false
  },
  middleName: {
    type: DataTypes.STRING(100),
    allowNull: true
  },
  
  // Professional Information
  role: {
    type: DataTypes.ENUM(
      'admin',
      'physician',
      'nurse',
      'medical_assistant',
      'healthcare_administrator',
      'patient'
    ),
    allowNull: false
  },
  licenseNumber: {
    type: DataTypes.STRING(50),
    allowNull: true
  },
  specialty: {
    type: DataTypes.STRING(100),
    allowNull: true
  },
  department: {
    type: DataTypes.STRING(100),
    allowNull: true
  },
  
  // Security
  isActive: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  isEmailVerified: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },
  lastLogin: {
    type: DataTypes.DATE,
    allowNull: true
  },
  loginAttempts: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },
  lockoutUntil: {
    type: DataTypes.DATE,
    allowNull: true
  },
  
  // Two-Factor Authentication
  twoFactorSecret: {
    type: DataTypes.STRING(255),
    allowNull: true
  },
  twoFactorEnabled: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },
  
  // Permissions
  permissions: {
    type: DataTypes.JSON,
    allowNull: true
  },
  accessiblePatients: {
    type: DataTypes.JSON,
    allowNull: true
  },
  
  // Contact Information
  phone: {
    type: DataTypes.STRING(20),
    allowNull: true
  },
  address: {
    type: DataTypes.JSON,
    allowNull: true
  },
  
  // Audit Fields
  createdBy: {
    type: DataTypes.UUID,
    allowNull: true
  },
  lastModifiedBy: {
    type: DataTypes.UUID,
    allowNull: true
  }
}, {
  tableName: 'users',
  indexes: [
    {
      fields: ['username']
    },
    {
      fields: ['email']
    },
    {
      fields: ['role']
    },
    {
      fields: ['isActive']
    }
  ]
});

module.exports = User;