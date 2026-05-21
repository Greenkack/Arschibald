/**
 * Dark Mode Toggle Component
 * Quick toggle between light and dark modes
 */

import React from 'react';
import { Button } from 'primereact/button';
import { useThemeStore } from '../../store/themeStore';
import './DarkModeToggle.css';

export const DarkModeToggle: React.FC = () => {
  const { theme, setMode } = useThemeStore();

  const toggleMode = () => {
    const newMode = theme.mode === 'dark' ? 'light' : 'dark';
    setMode(newMode);
  };

  const icon = theme.mode === 'dark' ? 'pi pi-sun' : 'pi pi-moon';
  const label = theme.mode === 'dark' ? 'Light Mode' : 'Dark Mode';

  return (
    <Button
      icon={icon}
      label={label}
      onClick={toggleMode}
      className="dark-mode-toggle p-button-outlined"
      tooltip={`Switch to ${theme.mode === 'dark' ? 'light' : 'dark'} mode`}
      tooltipOptions={{ position: 'bottom' }}
    />
  );
};
