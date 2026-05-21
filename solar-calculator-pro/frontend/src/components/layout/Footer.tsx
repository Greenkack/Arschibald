/**
 * Footer Component
 * 
 * Application footer with copyright and links
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Footer.css';

export const Footer: React.FC = () => {
  const navigate = useNavigate();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-left">
          <span className="copyright">
            &copy; {currentYear} Solar Calculator Pro. All rights reserved.
          </span>
        </div>

        <div className="footer-center">
          <button
            className="footer-link"
            onClick={() => navigate('/about')}
          >
            About
          </button>
          <span className="footer-separator">•</span>
          <button
            className="footer-link"
            onClick={() => navigate('/privacy')}
          >
            Privacy Policy
          </button>
          <span className="footer-separator">•</span>
          <button
            className="footer-link"
            onClick={() => navigate('/terms')}
          >
            Terms of Service
          </button>
          <span className="footer-separator">•</span>
          <button
            className="footer-link"
            onClick={() => navigate('/help')}
          >
            Help
          </button>
        </div>

        <div className="footer-right">
          <span className="build-info">
            Build: {import.meta.env.VITE_APP_VERSION || '1.0.0'}
          </span>
        </div>
      </div>
    </footer>
  );
};
