const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const AuditLog = sequelize.define('AuditLog', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  
  // User Information
  userId: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  userRole: {
    type: DataTypes.STRING(50),
    allowNull: true
  },
  
  // Action Information
  action: {
    type: DataTypes.STRING(100),
    allowNull: false
  },
  resource: {
    type: DataTypes.STRING(100),
    allowNull: false
  },
  resourceId: {
    type: DataTypes.UUID,
    allowNull: true
  },
  
  // Patient Information (if applicable)
  patientId: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'patients',
      key: 'id'
    }
  },
  
  // Request Information
  ipAddress: {
    type: DataTypes.STRING(45),
    allowNull: true
  },
  userAgent: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  requestMethod: {
    type: DataTypes.STRING(10),
    allowNull: true
  },
  requestUrl: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  
  // Response Information
  statusCode: {
    type: DataTypes.INTEGER,
    allowNull: true
  },
  responseTime: {
    type: DataTypes.INTEGER,
    allowNull: true
  },
  
  // Data Changes
  oldValues: {
    type: DataTypes.JSON,
    allowNull: true
  },
  newValues: {
    type: DataTypes.JSON,
    allowNull: true
  },
  
  // Additional Context
  details: {
    type: DataTypes.JSON,
    allowNull: true
  },
  severity: {
    type: DataTypes.ENUM('low', 'medium', 'high', 'critical'),
    defaultValue: 'medium'
  },
  
  // Timestamp
  timestamp: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW
  }
}, {
  tableName: 'audit_logs',
  indexes: [
    {
      fields: ['userId']
    },
    {
      fields: ['patientId']
    },
    {
      fields: ['action']
    },
    {
      fields: ['resource']
    },
    {
      fields: ['timestamp']
    },
    {
      fields: ['severity']
    }
  ],
  // Disable paranoid mode for audit logs to maintain complete history
  paranoid: false
});

module.exports = AuditLog;