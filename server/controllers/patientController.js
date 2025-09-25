const { Patient, MedicalHistory, User } = require('../models');
const { Op } = require('sequelize');

class PatientController {
  // Create new patient
  async createPatient(req, res) {
    try {
      const patientData = req.body;
      
      // Generate medical record number
      const medicalRecordNumber = await this.generateMedicalRecordNumber();
      
      const patient = await Patient.create({
        ...patientData,
        medicalRecordNumber,
        createdBy: req.user.id
      });

      // Log patient creation
      console.log('AUDIT: Patient created', {
        patientId: patient.id,
        medicalRecordNumber: patient.medicalRecordNumber,
        createdBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.status(201).json({
        message: 'Patient created successfully',
        patient: {
          id: patient.id,
          medicalRecordNumber: patient.medicalRecordNumber,
          firstName: patient.firstName,
          lastName: patient.lastName,
          dateOfBirth: patient.dateOfBirth
        }
      });
    } catch (error) {
      console.error('Create patient error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Get all patients with pagination and search
  async getPatients(req, res) {
    try {
      const {
        page = 1,
        limit = 20,
        search,
        status = 'active',
        sortBy = 'lastName',
        sortOrder = 'ASC'
      } = req.query;

      const offset = (page - 1) * limit;
      const whereClause = { status };

      // Add search functionality
      if (search) {
        whereClause[Op.or] = [
          { firstName: { [Op.iLike]: `%${search}%` } },
          { lastName: { [Op.iLike]: `%${search}%` } },
          { medicalRecordNumber: { [Op.iLike]: `%${search}%` } },
          { email: { [Op.iLike]: `%${search}%` } }
        ];
      }

      const { count, rows: patients } = await Patient.findAndCountAll({
        where: whereClause,
        order: [[sortBy, sortOrder.toUpperCase()]],
        limit: parseInt(limit),
        offset: parseInt(offset),
        attributes: [
          'id',
          'firstName',
          'lastName',
          'dateOfBirth',
          'gender',
          'medicalRecordNumber',
          'status',
          'createdAt'
        ]
      });

      res.json({
        patients,
        pagination: {
          currentPage: parseInt(page),
          totalPages: Math.ceil(count / limit),
          totalPatients: count,
          hasNext: offset + limit < count,
          hasPrev: page > 1
        }
      });
    } catch (error) {
      console.error('Get patients error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Get patient by ID
  async getPatientById(req, res) {
    try {
      const { patientId } = req.params;

      const patient = await Patient.findByPk(patientId, {
        include: [
          {
            model: MedicalHistory,
            as: 'medicalHistories',
            order: [['createdAt', 'DESC']]
          }
        ]
      });

      if (!patient) {
        return res.status(404).json({ error: 'Patient not found' });
      }

      // Log patient access
      console.log('AUDIT: Patient record accessed', {
        patientId: patient.id,
        accessedBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ patient });
    } catch (error) {
      console.error('Get patient error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Update patient information
  async updatePatient(req, res) {
    try {
      const { patientId } = req.params;
      const updateData = req.body;

      const patient = await Patient.findByPk(patientId);
      if (!patient) {
        return res.status(404).json({ error: 'Patient not found' });
      }

      // Store old values for audit
      const oldValues = patient.toJSON();

      await patient.update({
        ...updateData,
        lastModifiedBy: req.user.id
      });

      // Log patient update
      console.log('AUDIT: Patient updated', {
        patientId: patient.id,
        updatedBy: req.user.id,
        oldValues,
        newValues: updateData,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'Patient updated successfully', patient });
    } catch (error) {
      console.error('Update patient error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Add medical history entry
  async addMedicalHistory(req, res) {
    try {
      const { patientId } = req.params;
      const historyData = req.body;

      // Verify patient exists
      const patient = await Patient.findByPk(patientId);
      if (!patient) {
        return res.status(404).json({ error: 'Patient not found' });
      }

      const medicalHistory = await MedicalHistory.create({
        ...historyData,
        patientId,
        createdBy: req.user.id
      });

      // Log medical history addition
      console.log('AUDIT: Medical history added', {
        patientId,
        historyId: medicalHistory.id,
        historyType: medicalHistory.historyType,
        addedBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.status(201).json({
        message: 'Medical history added successfully',
        medicalHistory
      });
    } catch (error) {
      console.error('Add medical history error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Get medical history for a patient
  async getMedicalHistory(req, res) {
    try {
      const { patientId } = req.params;
      const { historyType, status } = req.query;

      const whereClause = { patientId };
      if (historyType) whereClause.historyType = historyType;
      if (status) whereClause.status = status;

      const medicalHistories = await MedicalHistory.findAll({
        where: whereClause,
        order: [['createdAt', 'DESC']],
        include: [
          {
            model: User,
            as: 'creator',
            attributes: ['firstName', 'lastName', 'role']
          }
        ]
      });

      // Log medical history access
      console.log('AUDIT: Medical history accessed', {
        patientId,
        accessedBy: req.user.id,
        filters: { historyType, status },
        timestamp: new Date().toISOString()
      });

      res.json({ medicalHistories });
    } catch (error) {
      console.error('Get medical history error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Update medical history entry
  async updateMedicalHistory(req, res) {
    try {
      const { patientId, historyId } = req.params;
      const updateData = req.body;

      const medicalHistory = await MedicalHistory.findOne({
        where: { id: historyId, patientId }
      });

      if (!medicalHistory) {
        return res.status(404).json({ error: 'Medical history entry not found' });
      }

      // Store old values for audit
      const oldValues = medicalHistory.toJSON();

      await medicalHistory.update({
        ...updateData,
        lastModifiedBy: req.user.id
      });

      // Log medical history update
      console.log('AUDIT: Medical history updated', {
        patientId,
        historyId,
        updatedBy: req.user.id,
        oldValues,
        newValues: updateData,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'Medical history updated successfully', medicalHistory });
    } catch (error) {
      console.error('Update medical history error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Generate unique medical record number
  async generateMedicalRecordNumber() {
    const prefix = 'MR';
    const year = new Date().getFullYear();
    const randomNum = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
    return `${prefix}${year}${randomNum}`;
  }

  // Search patients with advanced filters
  async searchPatients(req, res) {
    try {
      const {
        query,
        ageRange,
        gender,
        status = 'active',
        hasAllergies,
        hasMedications,
        lastVisitDate
      } = req.query;

      const whereClause = { status };

      // Text search
      if (query) {
        whereClause[Op.or] = [
          { firstName: { [Op.iLike]: `%${query}%` } },
          { lastName: { [Op.iLike]: `%${query}%` } },
          { medicalRecordNumber: { [Op.iLike]: `%${query}%` } }
        ];
      }

      // Gender filter
      if (gender) {
        whereClause.gender = gender;
      }

      // Age range filter
      if (ageRange) {
        const [minAge, maxAge] = ageRange.split('-').map(Number);
        const maxDate = new Date();
        maxDate.setFullYear(maxDate.getFullYear() - minAge);
        const minDate = new Date();
        minDate.setFullYear(minDate.getFullYear() - maxAge);
        
        whereClause.dateOfBirth = {
          [Op.between]: [minDate, maxDate]
        };
      }

      const patients = await Patient.findAll({
        where: whereClause,
        include: [
          {
            model: MedicalHistory,
            as: 'medicalHistories',
            where: {
              [Op.or]: [
                hasAllergies ? { historyType: 'allergies' } : null,
                hasMedications ? { historyType: 'medications' } : null
              ].filter(Boolean)
            },
            required: hasAllergies || hasMedications
          }
        ],
        order: [['lastName', 'ASC']]
      });

      res.json({ patients });
    } catch (error) {
      console.error('Search patients error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}

module.exports = new PatientController();