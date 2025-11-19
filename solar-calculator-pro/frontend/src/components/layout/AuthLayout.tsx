/**
 * Auth Layout Component
 * 
 * Layout for authentication pages (login, register, etc.)
 */

import React from 'react';
import { Outlet } from 'react-router-dom';

const AuthLayout: React.FC = () => {
  return (
    <div className="auth-layout">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Solar Calculator Pro</h1>
        </div>

        <div className="auth-content">
          <Outlet />
        </div>

        <div className="auth-footer">
          <p>&copy; 2024 Solar Calculator Pro</p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
