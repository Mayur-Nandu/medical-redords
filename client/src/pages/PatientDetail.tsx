import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Avatar,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
} from '@mui/material';
import {
  Edit,
  Add,
  Person,
  MedicalServices,
  History,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import axios from 'axios';

interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: string;
  medicalRecordNumber: string;
  status: string;
  email?: string;
  phone?: string;
  address?: any;
  emergencyContact?: any;
  insuranceInfo?: any;
  createdAt: string;
}

interface MedicalHistory {
  id: string;
  historyType: string;
  title: string;
  description: string;
  onsetDate?: string;
  endDate?: string;
  status: string;
  priority: string;
  createdAt: string;
}

const PatientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [medicalHistories, setMedicalHistories] = useState<MedicalHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (id) {
      fetchPatientDetails();
    }
  }, [id]);

  const fetchPatientDetails = async () => {
    try {
      const response = await axios.get(`/api/patients/${id}`);
      setPatient(response.data.patient);
      setMedicalHistories(response.data.patient.medicalHistories || []);
    } catch (error) {
      console.error('Error fetching patient details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
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

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  if (!patient) {
    return <Alert severity="error">Patient not found</Alert>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ width: 64, height: 64, mr: 2 }}>
            {patient.firstName[0]}{patient.lastName[0]}
          </Avatar>
          <Box>
            <Typography variant="h4">
              {patient.firstName} {patient.lastName}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              {patient.medicalRecordNumber} • {patient.gender} • Born {new Date(patient.dateOfBirth).toLocaleDateString()}
            </Typography>
          </Box>
        </Box>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Edit />}
            onClick={() => navigate(`/patients/${id}/edit`)}
            sx={{ mr: 1 }}
          >
            Edit Patient
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate(`/patients/${id}/medical-history/new`)}
          >
            Add Medical History
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Patient Information */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Patient Information
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <Person />
                  </ListItemIcon>
                  <ListItemText
                    primary="Status"
                    secondary={
                      <Chip
                        label={patient.status.charAt(0).toUpperCase() + patient.status.slice(1)}
                        color={patient.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    }
                  />
                </ListItem>
                {patient.email && (
                  <ListItem>
                    <ListItemText
                      primary="Email"
                      secondary={patient.email}
                    />
                  </ListItem>
                )}
                {patient.phone && (
                  <ListItem>
                    <ListItemText
                      primary="Phone"
                      secondary={patient.phone}
                    />
                  </ListItem>
                )}
                {patient.address && (
                  <ListItem>
                    <ListItemText
                      primary="Address"
                      secondary={`${patient.address.street}, ${patient.address.city}, ${patient.address.state} ${patient.address.zip}`}
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>

          {/* Emergency Contact */}
          {patient.emergencyContact && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Emergency Contact
                </Typography>
                <Typography variant="body2">
                  {patient.emergencyContact.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {patient.emergencyContact.relationship}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {patient.emergencyContact.phone}
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Medical History */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={activeTab} onChange={handleTabChange}>
                  <Tab label="All History" />
                  <Tab label="Allergies" />
                  <Tab label="Medications" />
                  <Tab label="Past Medical History" />
                </Tabs>
              </Box>

              <Box sx={{ mt: 2 }}>
                {medicalHistories.length === 0 ? (
                  <Typography color="text.secondary">
                    No medical history recorded yet.
                  </Typography>
                ) : (
                  <List>
                    {medicalHistories.map((history, index) => (
                      <React.Fragment key={history.id}>
                        <ListItem>
                          <ListItemIcon>
                            {getHistoryTypeIcon(history.historyType)}
                          </ListItemIcon>
                          <ListItemText
                            primary={history.title}
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {history.description}
                                </Typography>
                                <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                                  <Chip
                                    label={history.historyType.replace(/_/g, ' ').toUpperCase()}
                                    size="small"
                                    variant="outlined"
                                  />
                                  <Chip
                                    label={history.priority.toUpperCase()}
                                    size="small"
                                    color={getPriorityColor(history.priority) as any}
                                  />
                                  <Chip
                                    label={history.status.charAt(0).toUpperCase() + history.status.slice(1)}
                                    size="small"
                                    color={history.status === 'active' ? 'success' : 'default'}
                                  />
                                </Box>
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < medicalHistories.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PatientDetail;