const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');
const { User } = require('../models');
const config = require('../config/config');
const { auditLog } = require('../middleware/security');

class AuthController {
  // User registration
  async register(req, res) {
    try {
      const {
        username,
        email,
        password,
        firstName,
        lastName,
        role,
        licenseNumber,
        specialty,
        department
      } = req.body;

      // Check if user already exists
      const existingUser = await User.findOne({
        where: {
          $or: [{ email }, { username }]
        }
      });

      if (existingUser) {
        return res.status(400).json({
          error: 'User with this email or username already exists'
        });
      }

      // Hash password
      const saltRounds = 12;
      const hashedPassword = await bcrypt.hash(password, saltRounds);

      // Create user
      const user = await User.create({
        username,
        email,
        password: hashedPassword,
        firstName,
        lastName,
        role,
        licenseNumber,
        specialty,
        department,
        createdBy: req.user?.id || null
      });

      // Generate JWT token
      const token = jwt.sign(
        {
          id: user.id,
          username: user.username,
          role: user.role,
          accessiblePatients: user.accessiblePatients
        },
        config.security.jwtSecret,
        { expiresIn: config.security.jwtExpiresIn }
      );

      // Log registration
      console.log('AUDIT: User registered', {
        userId: user.id,
        username: user.username,
        role: user.role,
        timestamp: new Date().toISOString()
      });

      res.status(201).json({
        message: 'User registered successfully',
        token,
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          role: user.role
        }
      });
    } catch (error) {
      console.error('Registration error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // User login
  async login(req, res) {
    try {
      const { username, password, twoFactorCode } = req.body;

      // Find user
      const user = await User.findOne({
        where: { username }
      });

      if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }

      // Check if account is locked
      if (user.lockoutUntil && user.lockoutUntil > new Date()) {
        return res.status(423).json({
          error: 'Account is temporarily locked due to multiple failed login attempts'
        });
      }

      // Verify password
      const isValidPassword = await bcrypt.compare(password, user.password);
      if (!isValidPassword) {
        // Increment login attempts
        await user.increment('loginAttempts');
        
        // Lock account after 5 failed attempts
        if (user.loginAttempts >= 4) {
          await user.update({
            lockoutUntil: new Date(Date.now() + 30 * 60 * 1000) // 30 minutes
          });
        }

        return res.status(401).json({ error: 'Invalid credentials' });
      }

      // Check if 2FA is enabled
      if (user.twoFactorEnabled) {
        if (!twoFactorCode) {
          return res.status(200).json({
            message: 'Two-factor authentication required',
            requiresTwoFactor: true
          });
        }

        // Verify 2FA code
        const verified = speakeasy.totp.verify({
          secret: user.twoFactorSecret,
          encoding: 'base32',
          token: twoFactorCode,
          window: 2
        });

        if (!verified) {
          return res.status(401).json({ error: 'Invalid two-factor authentication code' });
        }
      }

      // Reset login attempts and update last login
      await user.update({
        loginAttempts: 0,
        lockoutUntil: null,
        lastLogin: new Date()
      });

      // Generate JWT token
      const token = jwt.sign(
        {
          id: user.id,
          username: user.username,
          role: user.role,
          accessiblePatients: user.accessiblePatients
        },
        config.security.jwtSecret,
        { expiresIn: config.security.jwtExpiresIn }
      );

      // Log successful login
      console.log('AUDIT: User logged in', {
        userId: user.id,
        username: user.username,
        role: user.role,
        ipAddress: req.ip,
        timestamp: new Date().toISOString()
      });

      res.json({
        message: 'Login successful',
        token,
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          role: user.role,
          twoFactorEnabled: user.twoFactorEnabled
        }
      });
    } catch (error) {
      console.error('Login error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Setup two-factor authentication
  async setupTwoFactor(req, res) {
    try {
      const userId = req.user.id;
      const user = await User.findByPk(userId);

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      // Generate secret
      const secret = speakeasy.generateSecret({
        name: `Medical History App (${user.email})`,
        issuer: 'Medical History App'
      });

      // Generate QR code
      const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);

      res.json({
        secret: secret.base32,
        qrCode: qrCodeUrl,
        manualEntryKey: secret.base32
      });
    } catch (error) {
      console.error('2FA setup error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Enable two-factor authentication
  async enableTwoFactor(req, res) {
    try {
      const { token } = req.body;
      const userId = req.user.id;
      const user = await User.findByPk(userId);

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      // Verify token
      const verified = speakeasy.totp.verify({
        secret: user.twoFactorSecret || req.body.secret,
        encoding: 'base32',
        token: token,
        window: 2
      });

      if (!verified) {
        return res.status(400).json({ error: 'Invalid verification code' });
      }

      // Enable 2FA
      await user.update({
        twoFactorSecret: req.body.secret,
        twoFactorEnabled: true
      });

      // Log 2FA enablement
      console.log('AUDIT: Two-factor authentication enabled', {
        userId: user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'Two-factor authentication enabled successfully' });
    } catch (error) {
      console.error('2FA enable error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Logout
  async logout(req, res) {
    try {
      // Log logout
      console.log('AUDIT: User logged out', {
        userId: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'Logout successful' });
    } catch (error) {
      console.error('Logout error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Get current user profile
  async getProfile(req, res) {
    try {
      const user = await User.findByPk(req.user.id, {
        attributes: { exclude: ['password', 'twoFactorSecret'] }
      });

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json({ user });
    } catch (error) {
      console.error('Get profile error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Update user profile
  async updateProfile(req, res) {
    try {
      const { firstName, lastName, email, phone, address } = req.body;
      const userId = req.user.id;

      const user = await User.findByPk(userId);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      // Update user
      await user.update({
        firstName,
        lastName,
        email,
        phone,
        address,
        lastModifiedBy: userId
      });

      // Log profile update
      console.log('AUDIT: User profile updated', {
        userId: user.id,
        changes: req.body,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'Profile updated successfully' });
    } catch (error) {
      console.error('Update profile error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}

module.exports = new AuthController();