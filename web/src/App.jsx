import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { Toaster } from 'react-hot-toast';
import store from './redux/store';
import Login from './pages/Login';
import Register from './pages/Register';
import ChallengerDashboard from './pages/Challenger/Dashboard';
import StreamerDashboard from './pages/Streamer/Dashboard';
import AdminDashboard from './pages/Admin/Dashboard';
import PrivateRoute from './components/PrivateRoute';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'));
  const [userRole, setUserRole] = useState(localStorage.getItem('user_role'));

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role');
    if (token && role) {
      setIsAuthenticated(true);
      setUserRole(role);
    }
  }, []);

  return (
    <Provider store={store}>
      <Router>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* CHALLENGER Routes */}
          <Route
            path="/challenger/*"
            element={
              <PrivateRoute requiredRole="CHALLENGER">
                <ChallengerDashboard />
              </PrivateRoute>
            }
          />
          
          {/* STREAMER Routes */}
          <Route
            path="/streamer/*"
            element={
              <PrivateRoute requiredRole="STREAMER">
                <StreamerDashboard />
              </PrivateRoute>
            }
          />
          
          {/* ADMIN Routes */}
          <Route
            path="/admin/*"
            element={
              <PrivateRoute requiredRole="ADMIN">
                <AdminDashboard />
              </PrivateRoute>
            }
          />
          
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </Provider>
  );
}

export default App;
