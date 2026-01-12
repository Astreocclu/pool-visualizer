import { useState, useEffect, useCallback } from 'react';
import { Routes, Route, useNavigate, Navigate, useLocation } from 'react-router-dom';
import './App.css';
import { ConfigProvider } from './context/ConfigContext';
import ResultsPage from './pages/ResultsPage';
import ResultDetailPage from './pages/ResultDetailPage';
import QuoteSuccessPage from './pages/QuoteSuccessPage';
import UploadPage from './pages/UploadPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ScreenTypesPage from './pages/ScreenTypesPage';

function App() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true); // Block rendering until session ready
  const [screenTypes, setScreenTypes] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = useCallback(async (credentials) => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        // Store tokens in localStorage
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        navigate('/');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // Create anonymous guest session for beta testing
  const createGuestSession = useCallback(async () => {
    try {
      const response = await fetch('/api/auth/guest/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const guestUser = { ...data.user, is_guest: true };
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('user_data', JSON.stringify(guestUser));
        setUser(guestUser);
      }
    } catch (err) {
      // Silent fail - will retry on next load
    } finally {
      setInitializing(false);
    }
  }, []);

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user_data');

    if (token && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        // Only restore valid guest sessions (username starts with guest_)
        if (userData.username && userData.username.startsWith('guest_')) {
          setUser(userData);
          setInitializing(false);
          return;
        }
      } catch (e) {
        // Invalid JSON - fall through to create guest
      }
      // Clear old/invalid session
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_data');
    }

    // Create fresh guest session
    createGuestSession();

    // Fetch screen types for global use
    const fetchScreenTypes = async () => {
      try {
        const response = await fetch('/api/screentypes/');
        if (response.ok) {
          const data = await response.json();
          setScreenTypes(data.results || []);
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Error fetching screen types:', error);
      }
    };
    fetchScreenTypes();
  }, [createGuestSession]);

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    navigate('/login');
  };

  // Protected Route Wrapper - waits for guest session before deciding
  const ProtectedRoute = ({ children }) => {
    if (initializing) {
      // Show loading while creating guest session
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'white' }}>
          Loading...
        </div>
      );
    }
    if (!user) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
    return children;
  };

  return (
    <ConfigProvider>
      <div className="App">
        <div style={{ minHeight: '100vh', backgroundColor: 'var(--primary-navy)', padding: '20px' }}>
          <Routes>
            <Route path="/login" element={
              user ? <Navigate to="/" replace /> : <LoginPage onLogin={handleLogin} error={error} loading={loading} />
            } />

            <Route path="/" element={
              <ProtectedRoute>
                <DashboardPage user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } />

            {/* Single dynamic upload route for all tenants */}
            <Route path="/upload/:tenantId" element={
              <ProtectedRoute>
                <UploadPage />
              </ProtectedRoute>
            } />

            {/* Redirect /upload to /upload/pools for backwards compatibility */}
            <Route path="/upload" element={<Navigate to="/upload/pools" replace />} />

            <Route path="/screentypes" element={
              <ProtectedRoute>
                <ScreenTypesPage screenTypes={screenTypes} />
              </ProtectedRoute>
            } />

            <Route path="/results/:id" element={
              <ProtectedRoute>
                <ResultDetailPage />
              </ProtectedRoute>
            } />

            <Route path="/quote/success" element={
              <ProtectedRoute>
                <QuoteSuccessPage />
              </ProtectedRoute>
            } />
          </Routes>
        </div>
      </div>
    </ConfigProvider>
  );
}

export default App;
