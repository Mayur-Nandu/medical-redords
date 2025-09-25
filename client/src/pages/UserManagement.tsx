import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Avatar,
  IconButton,
  Menu,
  MenuItem as MenuItemComponent,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add,
  MoreVert,
  Edit,
  Delete,
  Person,
  AdminPanelSettings,
  MedicalServices,
  PersonAdd,
} from '@mui/icons-material';
import { DataGrid, GridColDef, GridActionsCellItem } from '@mui/x-data-grid';
import axios from 'axios';

interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  isActive: boolean;
  lastLogin?: string;
  createdAt: string;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (roleFilter) params.append('role', roleFilter);
      if (statusFilter) params.append('isActive', statusFilter);

      const response = await axios.get(`/api/users?${params.toString()}`);
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    fetchUsers();
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, user: User) => {
    setAnchorEl(event.currentTarget);
    setSelectedUser(user);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedUser(null);
  };

  const handleEditUser = () => {
    if (selectedUser) {
      // Navigate to edit user page
      console.log('Edit user:', selectedUser.id);
    }
    handleMenuClose();
  };

  const handleDeleteUser = async () => {
    if (selectedUser) {
      try {
        await axios.delete(`/api/users/${selectedUser.id}`);
        fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
    handleMenuClose();
  };

  const handleActivateUser = async () => {
    if (selectedUser) {
      try {
        await axios.post(`/api/users/${selectedUser.id}/activate`);
        fetchUsers();
      } catch (error) {
        console.error('Error activating user:', error);
      }
    }
    handleMenuClose();
  };

  const handleDeactivateUser = async () => {
    if (selectedUser) {
      try {
        await axios.post(`/api/users/${selectedUser.id}/deactivate`);
        fetchUsers();
      } catch (error) {
        console.error('Error deactivating user:', error);
      }
    }
    handleMenuClose();
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin':
        return <AdminPanelSettings color="error" />;
      case 'physician':
        return <MedicalServices color="primary" />;
      case 'nurse':
        return <MedicalServices color="info" />;
      default:
        return <Person />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'physician':
        return 'primary';
      case 'nurse':
        return 'info';
      case 'medical_assistant':
        return 'secondary';
      case 'healthcare_administrator':
        return 'warning';
      default:
        return 'default';
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'user',
      headerName: 'User',
      width: 250,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ width: 32, height: 32, mr: 1 }}>
            {params.row.firstName[0]}{params.row.lastName[0]}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.firstName} {params.row.lastName}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.username} • {params.row.email}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'role',
      headerName: 'Role',
      width: 150,
      renderCell: (params) => (
        <Chip
          icon={getRoleIcon(params.value)}
          label={params.value.replace(/_/g, ' ').toUpperCase()}
          size="small"
          color={getRoleColor(params.value) as any}
        />
      ),
    },
    {
      field: 'isActive',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Active' : 'Inactive'}
          size="small"
          color={params.value ? 'success' : 'default'}
        />
      ),
    },
    {
      field: 'lastLogin',
      headerName: 'Last Login',
      width: 150,
      renderCell: (params) => 
        params.value ? new Date(params.value).toLocaleDateString() : 'Never',
    },
    {
      field: 'createdAt',
      headerName: 'Created',
      width: 120,
      renderCell: (params) => new Date(params.value).toLocaleDateString(),
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 100,
      getActions: (params) => [
        <GridActionsCellItem
          icon={<MoreVert />}
          label="More"
          onClick={(event) => handleMenuOpen(event, params.row)}
        />,
      ],
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">User Management</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => window.location.href = '/users/new'}
        >
          Add User
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  label="Role"
                >
                  <MenuItem value="">All Roles</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="physician">Physician</MenuItem>
                  <MenuItem value="nurse">Nurse</MenuItem>
                  <MenuItem value="medical_assistant">Medical Assistant</MenuItem>
                  <MenuItem value="healthcare_administrator">Healthcare Administrator</MenuItem>
                  <MenuItem value="patient">Patient</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="true">Active</MenuItem>
                  <MenuItem value="false">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                variant="outlined"
                onClick={handleSearch}
                fullWidth
                sx={{ height: '56px' }}
              >
                Search
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardContent>
          <Box sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={users}
              columns={columns}
              pageSize={10}
              rowsPerPageOptions={[10, 25, 50]}
              disableSelectionOnClick
              loading={loading}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItemComponent onClick={handleEditUser}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit User</ListItemText>
        </MenuItemComponent>
        {selectedUser?.isActive ? (
          <MenuItemComponent onClick={handleDeactivateUser}>
            <ListItemIcon>
              <PersonAdd fontSize="small" />
            </ListItemIcon>
            <ListItemText>Deactivate User</ListItemText>
          </MenuItemComponent>
        ) : (
          <MenuItemComponent onClick={handleActivateUser}>
            <ListItemIcon>
              <PersonAdd fontSize="small" />
            </ListItemIcon>
            <ListItemText>Activate User</ListItemText>
          </MenuItemComponent>
        )}
        <MenuItemComponent onClick={handleDeleteUser} sx={{ color: 'error.main' }}>
          <ListItemIcon>
            <Delete fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Delete User</ListItemText>
        </MenuItemComponent>
      </Menu>
    </Box>
  );
};

export default UserManagement;