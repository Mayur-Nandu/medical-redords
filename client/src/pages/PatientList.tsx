import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  TextField,
  Card,
  CardContent,
  Grid,
  Chip,
  Avatar,
  IconButton,
  InputAdornment,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add,
  Search,
  MoreVert,
  Edit,
  Visibility,
  Person,
} from '@mui/icons-material';
import { DataGrid, GridColDef, GridActionsCellItem } from '@mui/x-data-grid';
import axios from 'axios';

interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: string;
  medicalRecordNumber: string;
  status: string;
  createdAt: string;
}

const PatientList: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await axios.get('/api/patients');
      setPatients(response.data.patients || []);
    } catch (error) {
      console.error('Error fetching patients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      const response = await axios.get(`/api/patients?search=${searchTerm}`);
      setPatients(response.data.patients || []);
    } catch (error) {
      console.error('Error searching patients:', error);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, patient: Patient) => {
    setAnchorEl(event.currentTarget);
    setSelectedPatient(patient);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedPatient(null);
  };

  const handleViewPatient = () => {
    if (selectedPatient) {
      navigate(`/patients/${selectedPatient.id}`);
    }
    handleMenuClose();
  };

  const handleEditPatient = () => {
    if (selectedPatient) {
      navigate(`/patients/${selectedPatient.id}/edit`);
    }
    handleMenuClose();
  };

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Patient',
      width: 200,
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
              {params.row.medicalRecordNumber}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'dateOfBirth',
      headerName: 'Date of Birth',
      width: 120,
      renderCell: (params) => new Date(params.value).toLocaleDateString(),
    },
    {
      field: 'gender',
      headerName: 'Gender',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value.charAt(0).toUpperCase() + params.value.slice(1)}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value.charAt(0).toUpperCase() + params.value.slice(1)}
          size="small"
          color={params.value === 'active' ? 'success' : 'default'}
        />
      ),
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
        <Typography variant="h4">Patients</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate('/patients/new')}
        >
          Add Patient
        </Button>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                placeholder="Search patients..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Button
                variant="outlined"
                onClick={handleSearch}
                sx={{ height: '56px' }}
              >
                Search
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Box sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={patients}
              columns={columns}
              pageSize={10}
              rowsPerPageOptions={[10, 25, 50]}
              disableSelectionOnClick
              loading={loading}
              onRowClick={(params) => navigate(`/patients/${params.id}`)}
            />
          </Box>
        </CardContent>
      </Card>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleViewPatient}>
          <ListItemIcon>
            <Visibility fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleEditPatient}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit Patient</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default PatientList;