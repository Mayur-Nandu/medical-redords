import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Avatar,
} from '@mui/material';
import {
  People,
  MedicalServices,
  Person,
  TrendingUp,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import axios from 'axios';

interface DashboardStats {
  totalPatients: number;
  activePatients: number;
  totalUsers: number;
  recentActivities: any[];
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalPatients: 0,
    activePatients: 0,
    totalUsers: 0,
    recentActivities: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch patients data
      const patientsResponse = await axios.get('/api/patients?limit=5');
      
      // Fetch users data
      const usersResponse = await axios.get('/api/users?limit=5');
      
      // Fetch medical history data
      const medicalHistoryResponse = await axios.get('/api/medical-history?limit=10');

      setStats({
        totalPatients: patientsResponse.data.pagination?.totalPatients || 0,
        activePatients: patientsResponse.data.patients?.filter((p: any) => p.status === 'active').length || 0,
        totalUsers: usersResponse.data.pagination?.totalUsers || 0,
        recentActivities: medicalHistoryResponse.data.medicalHistories || [],
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const recentActivitiesColumns: GridColDef[] = [
    {
      field: 'title',
      headerName: 'Activity',
      width: 200,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ width: 32, height: 32, mr: 1 }}>
            <MedicalServices />
          </Avatar>
          {params.value}
        </Box>
      ),
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
      field: 'createdAt',
      headerName: 'Date',
      width: 150,
      renderCell: (params) => new Date(params.value).toLocaleDateString(),
    },
  ];

  const StatCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    color: string;
  }> = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: color,
              borderRadius: 1,
              p: 1,
              mr: 2,
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {icon}
          </Box>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" color="primary">
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Patients"
            value={stats.totalPatients}
            icon={<People color="inherit" />}
            color="#e3f2fd"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Patients"
            value={stats.activePatients}
            icon={<CheckCircle color="inherit" />}
            color="#e8f5e8"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={stats.totalUsers}
            icon={<Person color="inherit" />}
            color="#fff3e0"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Recent Activities"
            value={stats.recentActivities.length}
            icon={<TrendingUp color="inherit" />}
            color="#f3e5f5"
          />
        </Grid>

        {/* Recent Activities */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Medical History Activities
            </Typography>
            <Box sx={{ height: 400, width: '100%' }}>
              <DataGrid
                rows={stats.recentActivities}
                columns={recentActivitiesColumns}
                pageSize={5}
                rowsPerPageOptions={[5]}
                disableSelectionOnClick
                loading={loading}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <People />
                </ListItemIcon>
                <ListItemText primary="Add New Patient" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <MedicalServices />
                </ListItemIcon>
                <ListItemText primary="Record Medical History" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Warning />
                </ListItemIcon>
                <ListItemText primary="View Alerts" />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;