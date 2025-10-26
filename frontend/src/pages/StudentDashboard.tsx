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
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  CloudUpload,
  Assessment,
  CheckCircle,
  Schedule,
  TrendingUp,
  Assignment,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { peerReviewAPI, Submission } from '../services/api';

const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    pending: 0,
    avgScore: 0,
    avgOriginality: 0,
  });

  useEffect(() => {
    const fetchSubmissions = async () => {
      if (!user?.student_id) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await peerReviewAPI.getStudentSubmissions(user.student_id);
        setSubmissions(data);

        // Calculate statistics
        const total = data.length;
        const completed = data.filter((s: Submission) => s.status === 'completed').length;
        const pending = data.filter((s: Submission) => s.status === 'pending' || s.status === 'processing').length;
        
        // Calculate average code quality from submissions
        let totalScore = 0;
        let scoreCount = 0;
        let totalOriginality = 0;
        let originalityCount = 0;
        
        data.forEach((submission: Submission) => {
          // Try to get code quality score from metadata
          const metadata = submission.metadata as any;
          if (metadata?.average_score) {
            totalScore += metadata.average_score;
            scoreCount++;
          }
          // Try to get originality score
          if (metadata?.originality_score) {
            totalOriginality += metadata.originality_score;
            originalityCount++;
          }
        });

        const avgScore = scoreCount > 0 ? Math.round(totalScore / scoreCount) : 0;
        const avgOriginality = originalityCount > 0 ? Math.round(totalOriginality / originalityCount) : 0;

        setStats({
          total,
          completed,
          pending,
          avgScore,
          avgOriginality,
        });
      } catch (error) {
        console.error('Failed to fetch submissions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSubmissions();
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
          <Avatar sx={{ width: 64, height: 64, bgcolor: 'primary.main', mr: 2, fontSize: 28 }}>
            {user?.name?.[0]?.toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              Welcome back, {user?.name?.split(' ')[0]}!
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
              <Chip label="🎓 Student" size="small" color="primary" />
              <Chip label={`ID: ${user?.student_id}`} size="small" variant="outlined" />
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
                <Assignment sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {stats.total}
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
                <CheckCircle sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {stats.completed}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Reviewed
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Schedule sx={{ color: 'warning.main', mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {stats.pending}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                In Progress
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ color: 'info.main', mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {stats.avgScore}%
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Avg Score
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
              <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                Submit New Work
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Upload your assignment or project for AI-powered review
              </Typography>
              <Button
                component={Link}
                to="/upload"
                variant="contained"
                size="large"
                startIcon={<CloudUpload />}
              >
                Upload Files
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card elevation={3} sx={{ height: '100%', borderRadius: 3 }}>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Assessment sx={{ fontSize: 64, color: 'secondary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                View Results
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Check your submission history and detailed feedback
              </Typography>
              <Button
                component={Link}
                to="/history"
                variant="outlined"
                size="large"
                startIcon={<Assessment />}
              >
                View History
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Submissions */}
      <Card elevation={2} sx={{ borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
            Recent Submissions
          </Typography>
          {submissions.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Assignment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary" gutterBottom>
                No submissions yet
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload your first assignment to get started
              </Typography>
              <Button
                component={Link}
                to="/upload"
                variant="contained"
                startIcon={<CloudUpload />}
              >
                Submit Work
              </Button>
            </Box>
          ) : (
            <List>
              {submissions.slice(0, 5).map((submission, index) => (
                <React.Fragment key={submission.submission_id}>
                  {index > 0 && <Divider />}
                  <ListItem
                    component={Link}
                    to={`/results/${submission.submission_id}`}
                    sx={{ 
                      textDecoration: 'none',
                      color: 'inherit',
                      '&:hover': { bgcolor: 'action.hover' },
                      cursor: 'pointer'
                    }}
                  >
                    <ListItemText
                      primary={submission.metadata?.title || submission.files[0]?.original_name || 'Untitled Submission'}
                      secondary={
                        <>
                          <Typography component="span" variant="body2" color="text.secondary">
                            {`${submission.files.length} file${submission.files.length !== 1 ? 's' : ''}`}
                          </Typography>
                          {' • '}
                          <Typography component="span" variant="body2" color="text.secondary">
                            {new Date(submission.created_at).toLocaleDateString()}
                          </Typography>
                        </>
                      }
                    />
                    <Chip
                      label={submission.status.charAt(0).toUpperCase() + submission.status.slice(1)}
                      color={
                        submission.status === 'completed' ? 'success' : 
                        submission.status === 'processing' ? 'warning' : 
                        'default'
                      }
                      size="small"
                    />
                  </ListItem>
                </React.Fragment>
              ))}
              {submissions.length > 5 && (
                <Box sx={{ textAlign: 'center', mt: 2 }}>
                  <Button component={Link} to="/history" variant="text">
                    View All Submissions ({submissions.length})
                  </Button>
                </Box>
              )}
            </List>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default StudentDashboard;
