const { Sequelize } = require('sequelize');
const config = require('./config');

// Database configuration with security best practices
const sequelize = new Sequelize(config.database.name, config.database.user, config.database.password, {
  host: config.database.host,
  port: config.database.port,
  dialect: 'postgres',
  logging: config.database.logging,
  pool: {
    max: 20,
    min: 0,
    acquire: 30000,
    idle: 10000
  },
  dialectOptions: {
    ssl: config.database.ssl ? {
      require: true,
      rejectUnauthorized: false
    } : false
  },
  define: {
    timestamps: true,
    paranoid: true, // Soft deletes for audit trail
    underscored: true,
    freezeTableName: true
  }
});

module.exports = sequelize;