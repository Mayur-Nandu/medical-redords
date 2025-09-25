const sequelize = require('../config/database');
const { Patient, MedicalHistory, User, AuditLog } = require('../models');

async function migrate() {
  try {
    console.log('Starting database migration...');
    
    // Test database connection
    await sequelize.authenticate();
    console.log('Database connection established successfully.');
    
    // Sync all models (create tables)
    await sequelize.sync({ force: false });
    console.log('Database tables synchronized successfully.');
    
    // Create default admin user if it doesn't exist
    const adminExists = await User.findOne({ where: { username: 'admin' } });
    if (!adminExists) {
      const bcrypt = require('bcryptjs');
      const hashedPassword = await bcrypt.hash('Admin123!', 12);
      
      await User.create({
        username: 'admin',
        email: 'admin@medicalhistoryapp.com',
        password: hashedPassword,
        firstName: 'System',
        lastName: 'Administrator',
        role: 'admin',
        isActive: true,
        isEmailVerified: true
      });
      
      console.log('Default admin user created (username: admin, password: Admin123!)');
    }
    
    console.log('Database migration completed successfully.');
    process.exit(0);
  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  }
}

// Run migration if called directly
if (require.main === module) {
  migrate();
}

module.exports = migrate;