import React from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  CloudUpload,
  Assessment,
  Security,
  CheckCircle,
  AutoAwesome,
  Code,
  BugReport,
} from '@mui/icons-material';

const HomePageNew: React.FC = () => {
  const features = [
    {
      icon: <Code />,
      title: 'Code Quality Analysis',
      description: 'Automated analysis of complexity, maintainability, and style compliance',
    },
    {
      icon: <BugReport />,
      title: 'Security Scanning',
      description: 'Detect common security vulnerabilities and anti-patterns',
    },
    {
      icon: <Security />,
      title: 'Plagiarism Detection',
      description: 'Advanced similarity detection using semantic and structural analysis',
    },
    {
      icon: <AutoAwesome />,
      title: 'AI-Powered Feedback',
      description: 'Get constructive improvement suggestions from GPT-4',
    },
  ];

  const steps = [
    'Upload your code or project writeup',
    'AI analyzes code quality, complexity, and style',
    'Plagiarism check against other submissions',
    'Receive detailed feedback and improvement suggestions',
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          sx={{ fontWeight: 700, color: 'primary.main' }}
        >
          ProctorIQ - Peer Review Platform
        </Typography>
        <Typography
          variant="h5"
          component="h2"
          gutterBottom
          sx={{ color: 'text.secondary', mb: 4 }}
        >
          AI-Driven Code Review & Plagiarism Detection
        </Typography>
        <Typography variant="body1" sx={{ maxWidth: 700, mx: 'auto', mb: 4 }}>
          Submit your programming assignments and project writeups for instant automated feedback.
          Get detailed code quality metrics, security insights, and originality verification.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button
            component={Link}
            to="/upload"
            variant="contained"
            size="large"
            startIcon={<CloudUpload />}
            sx={{ px: 4, py: 1.5 }}
          >
            Submit Your Work
          </Button>
          <Button
            component={Link}
            to="/history"
            variant="outlined"
            size="large"
            startIcon={<Assessment />}
            sx={{ px: 4, py: 1.5 }}
          >
            View Submissions
          </Button>
        </Box>
      </Box>

      {/* Features Grid */}
      <Grid container spacing={4} sx={{ mb: 6 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    mb: 2,
                    color: 'primary.main',
                  }}
                >
                  {React.cloneElement(feature.icon, { sx: { fontSize: 48 } })}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* How It Works */}
      <Card sx={{ mb: 6 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom textAlign="center" sx={{ mb: 4 }}>
            How It Works
          </Typography>
          <List>
            {steps.map((step, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <CheckCircle color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="h6" component="span">
                      {index + 1}. {step}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Metrics Section */}
      <Grid container spacing={3} sx={{ mb: 6 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Code sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Code Quality Metrics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Cyclomatic complexity, maintainability index, and PEP 8 compliance
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Security sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Originality Verification
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Multi-method plagiarism detection with semantic similarity analysis
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <AutoAwesome sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                AI Feedback
              </Typography>
              <Typography variant="body2" color="text.secondary">
                GPT-4 powered suggestions for code improvements and best practices
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Call to Action */}
      <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            Ready to Get Started?
          </Typography>
          <Typography variant="body1" sx={{ mb: 3 }}>
            Submit your first project and receive instant automated feedback
          </Typography>
          <Button
            component={Link}
            to="/upload"
            variant="contained"
            color="secondary"
            size="large"
            startIcon={<CloudUpload />}
          >
            Upload Now
          </Button>
        </CardContent>
      </Card>
    </Container>
  );
};

export default HomePageNew;
