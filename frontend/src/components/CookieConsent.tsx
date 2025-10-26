import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  Collapse,
  Link,
} from '@mui/material';
import {
  Close as CloseIcon,
  Cookie as CookieIcon,
} from '@mui/icons-material';
import Cookies from 'js-cookie';

const CookieConsent: React.FC = () => {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Check if user has already given consent
    const consent = Cookies.get('cookie_consent');
    if (!consent) {
      // Show banner after a short delay for better UX
      setTimeout(() => setShowBanner(true), 1000);
    }
  }, []);

  const handleAccept = () => {
    // Set consent cookie (expires in 1 year)
    Cookies.set('cookie_consent', 'accepted', {
      expires: 365,
      sameSite: 'strict',
      secure: process.env.NODE_ENV === 'production',
    });
    setShowBanner(false);
  };

  const handleDecline = () => {
    // Set decline cookie (expires in 30 days)
    Cookies.set('cookie_consent', 'declined', {
      expires: 30,
      sameSite: 'strict',
      secure: process.env.NODE_ENV === 'production',
    });
    setShowBanner(false);
  };

  return (
    <Collapse in={showBanner}>
      <Box
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 9999,
          p: 2,
        }}
      >
        <Paper
          elevation={8}
          sx={{
            maxWidth: 800,
            mx: 'auto',
            p: 3,
            borderRadius: 3,
            backgroundColor: 'background.paper',
            boxShadow: '0 -4px 20px rgba(0,0,0,0.15)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
            <CookieIcon
              sx={{
                fontSize: 40,
                color: 'primary.main',
                mr: 2,
                flexShrink: 0,
              }}
            />
            <Box sx={{ flexGrow: 1 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}
              >
                We use cookies
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                ProctorIQ uses cookies to enhance your experience, keep you logged in,
                and remember your preferences. We use secure, encrypted cookies that
                expire after 24 hours for authentication. By clicking "Accept", you
                agree to our use of cookies.{' '}
                <Link href="#" underline="hover" sx={{ fontWeight: 500 }}>
                  Learn more about our Privacy Policy
                </Link>
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="medium"
                  onClick={handleAccept}
                  sx={{ minWidth: 120 }}
                >
                  Accept All
                </Button>
                <Button
                  variant="outlined"
                  size="medium"
                  onClick={handleDecline}
                  sx={{ minWidth: 120 }}
                >
                  Decline
                </Button>
              </Box>
            </Box>
            <IconButton
              onClick={handleDecline}
              size="small"
              sx={{ ml: 1, flexShrink: 0 }}
            >
              <CloseIcon />
            </IconButton>
          </Box>
        </Paper>
      </Box>
    </Collapse>
  );
};

export default CookieConsent;
