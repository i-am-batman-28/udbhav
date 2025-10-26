import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  CloudUpload,
  Visibility,
  Refresh,
  CheckCircle,
  Schedule,
  Error,
  Search,
  Code,
  Description,
} from '@mui/icons-material';

import { apiService, type StudentDashboard } from '../services/api';
import { useAuth } from '../context/AuthContext';

const HistoryPageNew: React.FC = () => {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState<StudentDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Use the logged-in user's student ID
    if (user?.student_id) {
      fetchDashboard(user.student_id);
    } else {
      setLoading(false);
      setError('Please log in to view your submissions');
    }
  }, [user]);

  const fetchDashboard = async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getStudentDashboard(id);
      setDashboard(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch dashboard');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusChip = (status: string) => {
    if (status === 'completed') {
      return <Chip icon={<CheckCircle />} label="Completed" color="success" size="small" />;
    } else if (status === 'under_review' || status === 'processing') {
      return <Chip icon={<Schedule />} label="Under Review" color="warning" size="small" />;
    } else if (status === 'flagged') {
      return <Chip icon={<Error />} label="Flagged" color="error" size="small" />;
    } else if (status === 'submitted') {
      return <Chip icon={<CheckCircle />} label="Submitted" color="info" size="small" />;
    } else {
      return <Chip icon={<Schedule />} label="Pending" color="default" size="small" />;
    }
  };

  const getTypeIcon = (type: string) => {
    if (type === 'code') return <Code fontSize="small" />;
    if (type === 'writeup') return <Description fontSize="small" />;
    return <Code fontSize="small" />;
  };

  const filteredSubmissions = dashboard?.recent_submissions?.filter((sub) => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    const title = sub.metadata?.title?.toLowerCase() || '';
    const name = sub.student_name?.toLowerCase() || '';
    const filename = sub.files?.[0]?.original_name?.toLowerCase() || '';
    return title.includes(searchLower) || name.includes(searchLower) || filename.includes(searchLower);
  }) || [];

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading dashboard...
        </Typography>
      </Container>
    );
  }

  if (error || !dashboard) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert
          severity="error"
          action={
            user?.student_id && (
              <Button onClick={() => user.student_id && fetchDashboard(user.student_id)} color="inherit" size="small">
                Retry
              </Button>
            )
          }
        >
          {error || 'Failed to load dashboard'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            My Submissions
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Welcome back, {dashboard?.student_name || 'Student'}!
          </Typography>
        </Box>
        <Box>
          <Tooltip title="Refresh">
            <IconButton onClick={() => user?.student_id && fetchDashboard(user.student_id)} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button
            component={Link}
            to="/upload"
            variant="contained"
            startIcon={<CloudUpload />}
            sx={{ ml: 1 }}
          >
            New Submission
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="primary" gutterBottom>
                {dashboard?.total_submissions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Submissions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="success.main" gutterBottom>
                {dashboard?.submissions_completed || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main" gutterBottom>
                {dashboard?.submissions_under_review || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Under Review
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="error.main" gutterBottom>
                {dashboard?.submissions_flagged || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Flagged
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Summary */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Average Code Quality
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="h3" color="primary" sx={{ mr: 2 }}>
                  {dashboard?.average_code_quality_score?.toFixed(1) || '0.0'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  / 100
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Average Originality
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="h3" color="success.main" sx={{ mr: 2 }}>
                  {dashboard?.average_originality_score?.toFixed(1) || '0.0'}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Original Content
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filter */}
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search submissions by title or name..."
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
      </Box>

      {/* Submissions Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Submissions
          </Typography>
          {filteredSubmissions.length === 0 ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              {searchTerm ? 'No submissions match your search.' : 'No submissions yet. Upload your first submission!'}
            </Alert>
          ) : (
            <TableContainer component={Paper} variant="outlined" sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Type</strong></TableCell>
                    <TableCell><strong>Title</strong></TableCell>
                    <TableCell><strong>Submitted</strong></TableCell>
                    <TableCell><strong>Files</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell align="right"><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredSubmissions.map((submission) => (
                    <TableRow key={submission.submission_id} hover>
                      <TableCell>
                        <Chip
                          icon={getTypeIcon(submission.submission_type)}
                          label={submission.submission_type.toUpperCase()}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {submission.metadata.title}
                        </Typography>
                        {submission.metadata.tags && submission.metadata.tags.length > 0 && (
                          <Box sx={{ mt: 0.5 }}>
                            {submission.metadata.tags.slice(0, 2).map((tag, idx) => (
                              <Chip key={idx} label={tag} size="small" sx={{ mr: 0.5, fontSize: '0.65rem' }} />
                            ))}
                          </Box>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {formatDate(submission.metadata.submission_date)}
                        </Typography>
                      </TableCell>
                      <TableCell>{submission.files.length}</TableCell>
                      <TableCell>{getStatusChip(submission.status)}</TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Results">
                          <IconButton
                            component={Link}
                            to={`/results/${submission.submission_id}`}
                            color="primary"
                            size="small"
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default HistoryPageNew;
