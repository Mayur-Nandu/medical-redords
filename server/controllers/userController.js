const { User } = require('../models');
const { Op } = require('sequelize');
const bcrypt = require('bcryptjs');

class UserController {
  // Get all users with pagination and filters
  async getUsers(req, res) {
    try {
      const {
        page = 1,
        limit = 20,
        role,
        isActive,
        search
      } = req.query;

      const offset = (page - 1) * limit;
      const whereClause = {};

      if (role) whereClause.role = role;
      if (isActive !== undefined) whereClause.isActive = isActive === 'true';

      // Add search functionality
      if (search) {
        whereClause[Op.or] = [
          { firstName: { [Op.iLike]: `%${search}%` } },
          { lastName: { [Op.iLike]: `%${search}%` } },
          { username: { [Op.iLike]: `%${search}%` } },
          { email: { [Op.iLike]: `%${search}%` } }
        ];
      }

      const { count, rows: users } = await User.findAndCountAll({
        where: whereClause,
        attributes: { exclude: ['password', 'twoFactorSecret'] },
        order: [['lastName', 'ASC']],
        limit: parseInt(limit),
        offset: parseInt(offset)
      });

      res.json({
        users,
        pagination: {
          currentPage: parseInt(page),
          totalPages: Math.ceil(count / limit),
          totalUsers: count,
          hasNext: offset + limit < count,
          hasPrev: page > 1
        }
      });
    } catch (error) {
      console.error('Get users error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Get user by ID
  async getUserById(req, res) {
    try {
      const { id } = req.params;

      const user = await User.findByPk(id, {
        attributes: { exclude: ['password', 'twoFactorSecret'] }
      });

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      // Log user access
      console.log('AUDIT: User profile accessed', {
        targetUserId: user.id,
        accessedBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ user });
    } catch (error) {
      console.error('Get user error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Update user
  async updateUser(req, res) {
    try {
      const { id } = req.params;
      const updateData = req.body;

      const user = await User.findByPk(id);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      // Store old values for audit
      const oldValues = user.toJSON();

      await user.update({
        ...updateData,
        lastModifiedBy: req.user.id
      });

      // Log user update
      console.log('AUDIT: User updated', {
        targetUserId: user.id,
        updatedBy: req.user.id,
        oldValues,
        newValues: updateData,
        timestamp: new Date().toISOString()
      });

      res.json({
        message: 'User updated successfully',
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          role: user.role,
          isActive: user.isActive
        }
      });
    } catch (error) {
      console.error('Update user error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Delete user (soft delete)
  async deleteUser(req, res) {
    try {
      const { id } = req.params;

      // Prevent self-deletion
      if (id === req.user.id) {
        return res.status(400).json({ error: 'Cannot delete your own account' });
      }

      const user = await User.findByPk(id);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      // Soft delete
      await user.destroy();

      // Log user deletion
      console.log('AUDIT: User deleted', {
        targetUserId: user.id,
        deletedBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'User deleted successfully' });
    } catch (error) {
      console.error('Delete user error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Reset user password
  async resetUserPassword(req, res) {
    try {
      const { id } = req.params;
      const { newPassword } = req.body;

      if (!newPassword) {
        return res.status(400).json({ error: 'New password is required' });
      }

      const user = await User.findByPk(id);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      // Hash new password
      const saltRounds = 12;
      const hashedPassword = await bcrypt.hash(newPassword, saltRounds);

      await user.update({
        password: hashedPassword,
        loginAttempts: 0,
        lockoutUntil: null,
        lastModifiedBy: req.user.id
      });

      // Log password reset
      console.log('AUDIT: User password reset', {
        targetUserId: user.id,
        resetBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'Password reset successfully' });
    } catch (error) {
      console.error('Reset password error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Activate user
  async activateUser(req, res) {
    try {
      const { id } = req.params;

      const user = await User.findByPk(id);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      await user.update({
        isActive: true,
        lastModifiedBy: req.user.id
      });

      // Log user activation
      console.log('AUDIT: User activated', {
        targetUserId: user.id,
        activatedBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'User activated successfully' });
    } catch (error) {
      console.error('Activate user error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  // Deactivate user
  async deactivateUser(req, res) {
    try {
      const { id } = req.params;

      // Prevent self-deactivation
      if (id === req.user.id) {
        return res.status(400).json({ error: 'Cannot deactivate your own account' });
      }

      const user = await User.findByPk(id);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      await user.update({
        isActive: false,
        lastModifiedBy: req.user.id
      });

      // Log user deactivation
      console.log('AUDIT: User deactivated', {
        targetUserId: user.id,
        deactivatedBy: req.user.id,
        timestamp: new Date().toISOString()
      });

      res.json({ message: 'User deactivated successfully' });
    } catch (error) {
      console.error('Deactivate user error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}

module.exports = new UserController();