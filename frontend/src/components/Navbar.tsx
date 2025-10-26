import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
} from '@mui/material';
import {
  School,
  CloudUpload,
  History,
} from '@mui/icons-material';

const Navbar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { label: 'Home', path: '/', icon: <School /> },
    { label: 'Submit Work', path: '/upload', icon: <CloudUpload /> },
    { label: 'My Submissions', path: '/history', icon: <History /> },
  ];

  return (
    <AppBar position="static" elevation={2}>
      <Container maxWidth="lg">
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <School sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
              ProctorIQ - Peer Review
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            {navItems.map((item) => (
              <Button
                key={item.path}
                component={Link}
                to={item.path}
                color="inherit"
                startIcon={item.icon}
                sx={{
                  backgroundColor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(255,255,255,0.1)',
                  },
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;
