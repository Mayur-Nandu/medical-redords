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
  Alert,
} from '@mui/material';
import {
  Add,
  MedicalServices,
  Warning,
  History,
  CheckCircle,
} from '@mui/icons-material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import axios from 'axios';

interface MedicalHistoryEntry {
  id: string;
  patientId: string;
  historyType: string;
  title: string;
  description: string;
  onsetDate?: string;
  endDate?: string;
  status: string;
  priority: string;
  dataSource: string;
  reliabilityScore?: number;
  createdAt: string;
  patient?: {
    firstName: string;
    lastName: string;
    medicalRecordNumber: string;
  };
}

const MedicalHistory: React.FC = () => {
  const [medicalHistories, setMedicalHistories] = useState<MedicalHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    historyType: '',
    status: '',
    priority: '',
  });

  useEffect(() => {
    fetchMedicalHistories();
  }, []);

  const fetchMedicalHistories = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.historyType) params.append('historyType', filters.historyType);
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);

      const response = await axios.get(`/api/medical-history?${params.toString()}`);
      setMedicalHistories(response.data.medicalHistories || []);
    } catch (error) {
      console.error('Error fetching medical histories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field: string, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const getHistoryTypeIcon = (type: string) => {
    switch (type) {
      case 'allergies':
        return <Warning color="error" />;
      case 'medications':
        return <MedicalServices color="primary" />;
      case 'past_medical_history':
        return <History color="info" />;
      default:
        return <MedicalServices />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'patient',
      headerName: 'Patient',
      width: 200,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ width: 32, height: 32, mr: 1 }}>
            {params.row.patient?.firstName?.[0]}{params.row.patient?.lastName?.[0]}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.patient?.firstName} {params.row.patient?.lastName}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.patient?.medicalRecordNumber}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'title',
      headerName: 'Title',
      width: 250,
    },
    {
      field: 'historyType',
      headerName: 'Type',
      width: 150,
      renderCell: (params) => (
        <Chip
          label={params.value.replace(/_/g, ' ').toUpperCase()}
          size="small"
          color="primary"
          variant="outlined"
        />
      ),
    },
    {
      field: 'priority',
      headerName: 'Priority',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value.toUpperCase()}
          size="small"
          color={getPriorityColor(params.value) as any}
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
      field: 'dataSource',
      headerName: 'Source',
      width: 150,
      renderCell: (params) => (
        <Chip
          label={params.value.replace(/_/g, ' ').toUpperCase()}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'createdAt',
      headerName: 'Created',
      width: 120,
      renderCell: (params) => new Date(params.value).toLocaleDateString(),
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Medical History</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => window.location.href = '/medical-history/new'}
        >
          Add Medical History
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>History Type</InputLabel>
                <Select
                  value={filters.historyType}
                  onChange={(e) => handleFilterChange('historyType', e.target.value)}
                  label="History Type"
                >
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="chief_complaint">Chief Complaint</MenuItem>
                  <MenuItem value="history_of_present_illness">History of Present Illness</MenuItem>
                  <MenuItem value="past_medical_history">Past Medical History</MenuItem>
                  <MenuItem value="family_history">Family History</MenuItem>
                  <MenuItem value="social_history">Social History</MenuItem>
                  <MenuItem value="medications">Medications</MenuItem>
                  <MenuItem value="allergies">Allergies</MenuItem>
                  <MenuItem value="review_of_systems">Review of Systems</MenuItem>
                  <MenuItem value="vital_signs">Vital Signs</MenuItem>
                  <MenuItem value="immunizations">Immunizations</MenuItem>
                  <MenuItem value="preventive_care">Preventive Care</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="resolved">Resolved</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={filters.priority}
                  onChange={(e) => handleFilterChange('priority', e.target.value)}
                  label="Priority"
                >
                  <MenuItem value="">All Priorities</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button
                variant="outlined"
                onClick={fetchMedicalHistories}
                fullWidth
                sx={{ height: '56px' }}
              >
                Apply Filters
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Medical History Table */}
      <Card>
        <CardContent>
          <Box sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={medicalHistories}
              columns={columns}
              pageSize={10}
              rowsPerPageOptions={[10, 25, 50]}
              disableSelectionOnClick
              loading={loading}
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MedicalHistory;