import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Cookie configuration
const COOKIE_OPTIONS = {
  expires: 1, // 1 day
  secure: process.env.NODE_ENV === 'production', // Only HTTPS in production
  sameSite: 'strict' as const,
  path: '/',
};

// Check if user has given cookie consent
const hasCookieConsent = (): boolean => {
  const consent = Cookies.get('cookie_consent');
  return consent === 'accepted';
};

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'teacher';
  student_id?: string;
  created_at?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string, role: 'student' | 'teacher', studentId?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Axios interceptor setup
axios.interceptors.request.use(
  (config) => {
    let token = Cookies.get('auth_token');
    // Fallback to sessionStorage
    if (!token) {
      token = sessionStorage.getItem('auth_token') || undefined;
    }
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors globally
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear all storage
      Cookies.remove('auth_token', { path: '/' });
      Cookies.remove('user', { path: '/' });
      sessionStorage.removeItem('auth_token');
      sessionStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from cookies
  useEffect(() => {
    const initAuth = async () => {
      let storedToken = Cookies.get('auth_token');
      let storedUserStr = Cookies.get('user');

      // Fallback to sessionStorage if no cookies
      if (!storedToken) {
        storedToken = sessionStorage.getItem('auth_token') || undefined;
        storedUserStr = sessionStorage.getItem('user') || undefined;
      }

      if (storedToken && storedUserStr) {
        try {
          const storedUser = JSON.parse(storedUserStr);
          setToken(storedToken);
          setUser(storedUser);
          
          // Verify token is still valid
          await axios.get(`${API_BASE_URL}/api/auth/me`, {
            headers: { Authorization: `Bearer ${storedToken}` }
          });
        } catch (error) {
          // Token invalid, clear all storage
          Cookies.remove('auth_token', { path: '/' });
          Cookies.remove('user', { path: '/' });
          sessionStorage.removeItem('auth_token');
          sessionStorage.removeItem('user');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        email,
        password,
      });

      const { token: newToken, user: userData } = response.data;

      // Store in state
      setToken(newToken);
      setUser(userData);

      // Only store in cookies if user has given consent
      if (hasCookieConsent()) {
        Cookies.set('auth_token', newToken, COOKIE_OPTIONS);
        Cookies.set('user', JSON.stringify(userData), COOKIE_OPTIONS);
      } else {
        // Fallback to sessionStorage if no consent (clears on tab close)
        sessionStorage.setItem('auth_token', newToken);
        sessionStorage.setItem('user', JSON.stringify(userData));
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const register = async (
    email: string,
    password: string,
    name: string,
    role: 'student' | 'teacher',
    studentId?: string
  ) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
        email,
        password,
        name,
        role,
        student_id: studentId,
      });

      // After successful registration, log the user in
      await login(email, password);
    } catch (error: any) {
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          throw new Error(detail);
        } else if (Array.isArray(detail)) {
          throw new Error(detail.map((e: any) => e.msg).join(', '));
        }
      }
      throw new Error('Registration failed');
    }
  };

  const logout = async () => {
    try {
      // Call backend logout endpoint to clear server-side cookies
      await axios.post(`${API_BASE_URL}/api/auth/logout`);
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API call failed:', error);
    } finally {
      // Clear client-side state and all storage
      setUser(null);
      setToken(null);
      Cookies.remove('auth_token', { path: '/' });
      Cookies.remove('user', { path: '/' });
      sessionStorage.removeItem('auth_token');
      sessionStorage.removeItem('user');
    }
  };

  const checkAuth = async () => {
    if (!token) return;

    try {
      const res = await axios.get(`${API_BASE_URL}/api/auth/me`);
      setUser(res.data.user);
      
      // Update storage based on consent
      if (hasCookieConsent()) {
        Cookies.set('user', JSON.stringify(res.data.user), COOKIE_OPTIONS);
      } else {
        sessionStorage.setItem('user', JSON.stringify(res.data.user));
      }
    } catch (error) {
      logout();
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    register,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
