const { Patient, MedicalHistory, User, AuditLog } = require('./index');

// Define associations between models

// Patient associations
Patient.hasMany(MedicalHistory, {
  foreignKey: 'patientId',
  as: 'medicalHistories',
  onDelete: 'CASCADE'
});

Patient.belongsTo(User, {
  foreignKey: 'createdBy',
  as: 'creator'
});

Patient.belongsTo(User, {
  foreignKey: 'lastModifiedBy',
  as: 'lastModifier'
});

// MedicalHistory associations
MedicalHistory.belongsTo(Patient, {
  foreignKey: 'patientId',
  as: 'patient',
  onDelete: 'CASCADE'
});

MedicalHistory.belongsTo(User, {
  foreignKey: 'createdBy',
  as: 'creator'
});

MedicalHistory.belongsTo(User, {
  foreignKey: 'lastModifiedBy',
  as: 'lastModifier'
});

// User associations
User.hasMany(Patient, {
  foreignKey: 'createdBy',
  as: 'createdPatients'
});

User.hasMany(Patient, {
  foreignKey: 'lastModifiedBy',
  as: 'lastModifiedPatients'
});

User.hasMany(MedicalHistory, {
  foreignKey: 'createdBy',
  as: 'createdMedicalHistories'
});

User.hasMany(MedicalHistory, {
  foreignKey: 'lastModifiedBy',
  as: 'lastModifiedMedicalHistories'
});

// AuditLog associations
AuditLog.belongsTo(User, {
  foreignKey: 'userId',
  as: 'user'
});

AuditLog.belongsTo(Patient, {
  foreignKey: 'patientId',
  as: 'patient'
});

module.exports = {
  Patient,
  MedicalHistory,
  User,
  AuditLog
};