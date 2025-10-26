import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  SupervisorAccount,
  Assessment,
  People,
  Warning,
  TrendingUp,
  CheckCircle,
  CloudUpload,
  FileUpload,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

interface StudentSubmission {
  id: string;
  student_name: string;
  student_id: string;
  filename: string;
  status: string;
  created_at: string;
  plagiarism_score?: number;
  quality_score?: number;
}

const TeacherDashboard: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [submissions, setSubmissions] = useState<StudentSubmission[]>([]);
  const [stats, setStats] = useState({
    totalStudents: 0,
    totalSubmissions: 0,
    flaggedSubmissions: 0,
    avgQuality: 0,
  });

  useEffect(() => {
    // TODO: Fetch all student submissions from API
    // This is placeholder data
    setLoading(false);
    setSubmissions([]);
    setStats({
      totalStudents: 0,
      totalSubmissions: 0,
      flaggedSubmissions: 0,
      avgQuality: 0,
    });
  }, [user]);

  if (loading) {
    return (
      <Container sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Welcome Section */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ width: 64, height: 64, bgcolor: 'secondary.main', mr: 2, fontSize: 28 }}>
            {user?.name?.[0]?.toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              Teacher Dashboard
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
              <Chip label="👨‍🏫 Teacher" size="small" color="secondary" />
              <Chip label={user?.name} size="small" variant="outlined" />
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <People sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {stats.totalStudents}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Total Students
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Assessment sx={{ color: 'info.main', mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {stats.totalSubmissions}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Total Submissions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Warning sx={{ color: 'warning.main', mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {stats.flaggedSubmissions}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Flagged for Review
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {stats.avgQuality}%
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Avg Quality Score
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card elevation={3} sx={{ height: '100%', borderRadius: 3 }}>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <FileUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                Batch Upload
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Upload multiple student submissions at once for bulk review
              </Typography>
              <Button
                component={Link}
                to="/batch-upload"
                variant="contained"
                size="large"
                startIcon={<CloudUpload />}
              >
                Batch Upload
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card elevation={3} sx={{ height: '100%', borderRadius: 3 }}>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Assessment sx={{ fontSize: 64, color: 'secondary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                View All Results
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Access detailed analytics and review all student submissions
              </Typography>
              <Button
                component={Link}
                to="/history"
                variant="outlined"
                size="large"
                startIcon={<Assessment />}
              >
                View Analytics
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Submissions Table */}
      <Card elevation={2} sx={{ borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
              <Tab label="All Submissions" />
              <Tab label="Flagged" icon={<Warning />} iconPosition="end" />
              <Tab label="Completed" icon={<CheckCircle />} iconPosition="end" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            {submissions.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <SupervisorAccount sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  No student submissions yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Students haven't submitted any work for review
                </Typography>
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Student</TableCell>
                      <TableCell>Student ID</TableCell>
                      <TableCell>File</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Quality</TableCell>
                      <TableCell>Plagiarism</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {submissions.map((submission) => (
                      <TableRow key={submission.id}>
                        <TableCell>{submission.student_name}</TableCell>
                        <TableCell>{submission.student_id}</TableCell>
                        <TableCell>{submission.filename}</TableCell>
                        <TableCell>
                          {new Date(submission.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={submission.status}
                            size="small"
                            color={submission.status === 'completed' ? 'success' : 'warning'}
                          />
                        </TableCell>
                        <TableCell>
                          {submission.quality_score ? `${submission.quality_score}%` : '-'}
                        </TableCell>
                        <TableCell>
                          {submission.plagiarism_score ? (
                            <Chip
                              label={`${submission.plagiarism_score}%`}
                              size="small"
                              color={submission.plagiarism_score > 50 ? 'error' : 'success'}
                            />
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell>
                          <Button size="small" variant="outlined">
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No flagged submissions
              </Typography>
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No completed submissions
              </Typography>
            </Box>
          </TabPanel>
        </CardContent>
      </Card>
    </Container>
  );
};

export default TeacherDashboard;
