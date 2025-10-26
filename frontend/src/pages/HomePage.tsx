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
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  CloudUpload,
  Assessment,
  Speed,
  Security,
  CheckCircle,
  AutoAwesome,
  Group,
} from '@mui/icons-material';

const HomePage: React.FC = () => {
  const features = [
    {
      icon: <CloudUpload />,
      title: 'Multi-File Upload',
      description: 'Upload code files and project writeups in various formats',
    },
    {
      icon: <AutoAwesome />,
      title: 'Code Quality Analysis',
      description: 'Automated analysis of code complexity, style, and security',
    },
    {
      icon: <Speed />,
      title: 'Plagiarism Detection',
      description: 'Advanced similarity detection across submissions',
    },
    {
      icon: <Security />,
      title: 'Secure & Private',
      description: 'Enterprise-grade security for student submissions',
    },
  ];

  const steps = [
    'Upload your code or project writeup',
    'AI analyzes code quality and style',
    'Plagiarism check against other submissions',
    'Get detailed feedback and improvements',
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
          ProctorIQ
        </Typography>
        <Typography
          variant="h5"
          component="h2"
          gutterBottom
          sx={{ color: 'text.secondary', mb: 4 }}
        >
          Automated Exam Evaluation System
        </Typography>
        <Typography variant="body1" sx={{ maxWidth: 600, mx: 'auto', mb: 4 }}>
          Transform the way you evaluate exams with AI-powered assessment. 
          Upload answer sheets and get detailed, consistent evaluations in minutes.
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
            Single Upload
          </Button>
          <Button
            component={Link}
            to="/batch-upload"
            variant="contained"
            color="secondary"
            size="large"
            startIcon={<Group />}
            sx={{ px: 4, py: 1.5 }}
          >
            Batch Upload
          </Button>
          <Button
            component={Link}
            to="/history"
            variant="outlined"
            size="large"
            startIcon={<Assessment />}
            sx={{ px: 4, py: 1.5 }}
          >
            View History
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Box sx={{ mb: 6 }}>
        <Typography
          variant="h4"
          component="h2"
          textAlign="center"
          gutterBottom
          sx={{ mb: 4 }}
        >
          Key Features
        </Typography>
        <Grid container spacing={3}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
                <CardContent>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>
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
      </Box>

      {/* How It Works Section */}
      <Box sx={{ mb: 6 }}>
        <Typography
          variant="h4"
          component="h2"
          textAlign="center"
          gutterBottom
          sx={{ mb: 4 }}
        >
          How It Works
        </Typography>
        <Paper sx={{ p: 3 }}>
          <List>
            {steps.map((step, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <CheckCircle color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={`Step ${index + 1}`}
                  secondary={step}
                  primaryTypographyProps={{ fontWeight: 600 }}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Box>

      {/* Call to Action */}
      <Paper
        sx={{
          p: 4,
          textAlign: 'center',
          background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
          color: 'white',
        }}
      >
        <Typography variant="h5" gutterBottom>
          Ready to get started?
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }}>
          Upload your first answer sheet and experience the power of AI evaluation.
        </Typography>
        <Button
          component={Link}
          to="/upload"
          variant="contained"
          size="large"
          sx={{
            backgroundColor: 'white',
            color: 'primary.main',
            '&:hover': {
              backgroundColor: 'grey.100',
            },
          }}
        >
          Upload Answer Sheet
        </Button>
      </Paper>
    </Container>
  );
};

export default HomePage;
