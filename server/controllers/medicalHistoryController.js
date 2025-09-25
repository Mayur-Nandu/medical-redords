const { MedicalHistory, Patient, User } = require('../models');
const { Op } = require('sequelize');

class MedicalHistoryController {
  // Create new medical history entry
  async createMedicalHistory(req, res) {
    try {
      const historyData = req.body;
      
      // Verify patient exists
      const patient = await Patient.findByPk(historyData.patientId);
      if (!patient) {
        return res.status(404).json({ error: 'Patient not found' });
      }

      const medicalHistory = await MedicalHistory.create({
        ...historyData,
        createdBy: req.user.id
      });

      // Log medical history creation
      console.log('AUDIT: Medical history created', {
        historyId: medicalHistory.id,
        patientId: medicalHistory.patientId,
        historyType: medicalHistory.historyType,
        createdBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.status(201).json({
        message: 'Medical history created successfully',
        medicalHistory
      });
    } catch (error) {
      console.error('Create medical history error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Get medical histories with filters
  async getMedicalHistories(req, res) {
    try {
      const {
        patientId,
        historyType,
        status = 'active',
        priority,
        page = 1,
        limit = 20
      } = req.query;

      const offset = (page - 1) * limit;
      const whereClause = {};

      if (patientId) whereClause.patientId = patientId;
      if (historyType) whereClause.historyType = historyType;
      if (status) whereClause.status = status;
      if (priority) whereClause.priority = priority;

      const { count, rows: medicalHistories } = await MedicalHistory.findAndCountAll({
        where: whereClause,
        include: [
          {
            model: Patient,
            as: 'patient',
            attributes: ['id', 'firstName', 'lastName', 'medicalRecordNumber']
          },
          {
            model: User,
            as: 'creator',
            attributes: ['id', 'firstName', 'lastName', 'role']
          }
        ],
        order: [['createdAt', 'DESC']],
        limit: parseInt(limit),
        offset: parseInt(offset)
      });

      res.json({
        medicalHistories,
        pagination: {
          currentPage: parseInt(page),
          totalPages: Math.ceil(count / limit),
          totalEntries: count,
          hasNext: offset + limit < count,
          hasPrev: page > 1
        }
      });
    } catch (error) {
      console.error('Get medical histories error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Get medical history by ID
  async getMedicalHistoryById(req, res) {
    try {
      const { id } = req.params;

      const medicalHistory = await MedicalHistory.findByPk(id, {
        include: [
          {
            model: Patient,
            as: 'patient',
            attributes: ['id', 'firstName', 'lastName', 'medicalRecordNumber']
          },
          {
            model: User,
            as: 'creator',
            attributes: ['id', 'firstName', 'lastName', 'role']
          }
        ]
      });

      if (!medicalHistory) {
        return res.status(404).json({ error: 'Medical history not found' });
      }

      // Log medical history access
      console.log('AUDIT: Medical history accessed', {
        historyId: medicalHistory.id,
        patientId: medicalHistory.patientId,
        accessedBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ medicalHistory });
    } catch (error) {
      console.error('Get medical history error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Update medical history
  async updateMedicalHistory(req, res) {
    try {
      const { id } = req.params;
      const updateData = req.body;

      const medicalHistory = await MedicalHistory.findByPk(id);
      if (!medicalHistory) {
        return res.status(404).json({ error: 'Medical history not found' });
      }

      // Store old values for audit
      const oldValues = medicalHistory.toJSON();

      await medicalHistory.update({
        ...updateData,
        lastModifiedBy: req.user.id
      });

      // Log medical history update
      console.log('AUDIT: Medical history updated', {
        historyId: medicalHistory.id,
        patientId: medicalHistory.patientId,
        updatedBy: req.user.id,
        oldValues,
        newValues: updateData,
        timestamp: new Date().toISOString()
      });

      res.json({
        message: 'Medical history updated successfully',
        medicalHistory
      });
    } catch (error) {
      console.error('Update medical history error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Delete medical history (soft delete)
  async deleteMedicalHistory(req, res) {
    try {
      const { id } = req.params;

      const medicalHistory = await MedicalHistory.findByPk(id);
      if (!medicalHistory) {
        return res.status(404).json({ error: 'Medical history not found' });
      }

      // Soft delete
      await medicalHistory.destroy();

      // Log medical history deletion
      console.log('AUDIT: Medical history deleted', {
        historyId: medicalHistory.id,
        patientId: medicalHistory.patientId,
        deletedBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'Medical history deleted successfully' });
    } catch (error) {
      console.error('Delete medical history error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Get medical history statistics
  async getMedicalHistoryStats(req, res) {
    try {
      const { patientId } = req.params;

      const stats = await MedicalHistory.findAll({
        where: { patientId },
        attributes: [
          'historyType',
          [sequelize.fn('COUNT', sequelize.col('id')), 'count']
        ],
        group: ['historyType']
      });

      res.json({ stats });
    } catch (error) {
      console.error('Get medical history stats error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}

module.exports = new MedicalHistoryController();