/**
 * System Tray Integration Demo
 * Demonstrates all tray features and API usage
 */

import React, { useState, useEffect } from 'react';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { InputSwitch } from 'primereact/inputswitch';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Message } from 'primereact/message';
import { Divider } from 'primereact/divider';
import { useTray, useTrayOperation, useTrayPreferences } from '../hooks/useTray';
import './TrayIntegrationDemo.css';

export const TrayIntegrationDemo: React.FC = () => {
  const {
    isAvailable,
    preferences,
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    updateIcon,
    flash,
    updateTooltip,
    addRecentProject,
  } = useTray();

  const { executeOperation } = useTrayOperation();
  const {
    preferences: trayPrefs,
    isLoading: prefsLoading,
    togglePreference,
    setPreference,
  } = useTrayPreferences();

  const [notificationTitle, setNotificationTitle] = useState('Test Notification');
  const [notificationBody, setNotificationBody] = useState('This is a test notification');
  const [notificationType, setNotificationType] = useState<'info' | 'success' | 'warning' | 'error'>('info');
  const [iconState, setIconState] = useState<'normal' | 'busy' | 'error' | 'warning'>('normal');
  const [tooltipText, setTooltipText] = useState('Solar Calculator Pro');
  const [flashDuration, setFlashDuration] = useState(3000);

  const notificationTypes = [
    { label: 'Info', value: 'info' },
    { label: 'Success', value: 'success' },
    { label: 'Warning', value: 'warning' },
    { label: 'Error', value: 'error' },
  ];

  const iconStates = [
    { label: 'Normal', value: 'normal' },
    { label: 'Busy', value: 'busy' },
    { label: 'Error', value: 'error' },
    { label: 'Warning', value: 'warning' },
  ];

  // Check if running in Electron
  if (!isAvailable) {
    return (
      <div className="tray-demo">
        <Message
          severity="warn"
          text="System tray is not available. This feature only works in the Electron desktop app."
        />
      </div>
    );
  }

  const handleShowNotification = async () => {
    await showNotification({
      title: notificationTitle,
      body: notificationBody,
      type: notificationType,
    });
  };

  const handleUpdateIcon = async () => {
    await updateIcon(iconState);
  };

  const handleFlash = async () => {
    await flash(flashDuration);
  };

  const handleUpdateTooltip = async () => {
    await updateTooltip(tooltipText);
  };

  const handleAddRecentProject = async () => {
    await addRecentProject({
      id: `project-${Date.now()}`,
      name: `Test Project ${new Date().toLocaleTimeString()}`,
      date: new Date().toISOString(),
    });
  };

  const handleLongOperation = async () => {
    await executeOperation(
      async () => {
        // Simulate long operation
        await new Promise((resolve) => setTimeout(resolve, 3000));
        return 'Operation completed';
      },
      {
        busyMessage: 'Performing calculation...',
        successTitle: 'Calculation Complete',
        successMessage: 'Your solar system calculation is ready',
        errorTitle: 'Calculation Failed',
      }
    );
  };

  const handleErrorOperation = async () => {
    try {
      await executeOperation(
        async () => {
          // Simulate error
          await new Promise((resolve) => setTimeout(resolve, 1000));
          throw new Error('Simulated error for testing');
        },
        {
          busyMessage: 'Processing...',
          errorTitle: 'Operation Failed',
        }
      );
    } catch (error) {
      // Error already handled by executeOperation
    }
  };

  return (
    <div className="tray-demo">
      <h1>System Tray Integration Demo</h1>
      <p className="subtitle">
        Test and explore all system tray features
      </p>

      {/* Notifications Section */}
      <Card title="📢 Notifications" className="demo-card">
        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="notif-title">Title</label>
            <InputText
              id="notif-title"
              value={notificationTitle}
              onChange={(e) => setNotificationTitle(e.target.value)}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="notif-body">Body</label>
            <InputText
              id="notif-body"
              value={notificationBody}
              onChange={(e) => setNotificationBody(e.target.value)}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="notif-type">Type</label>
            <Dropdown
              id="notif-type"
              value={notificationType}
              options={notificationTypes}
              onChange={(e) => setNotificationType(e.value)}
              className="w-full"
            />
          </div>
        </div>

        <div className="button-group">
          <Button
            label="Show Notification"
            icon="pi pi-bell"
            onClick={handleShowNotification}
          />
          <Button
            label="Show Success"
            icon="pi pi-check"
            severity="success"
            onClick={() => showSuccess('Success!', 'Operation completed successfully')}
          />
          <Button
            label="Show Error"
            icon="pi pi-times"
            severity="danger"
            onClick={() => showError('Error!', 'Something went wrong')}
          />
          <Button
            label="Show Warning"
            icon="pi pi-exclamation-triangle"
            severity="warning"
            onClick={() => showWarning('Warning!', 'Please review your inputs')}
          />
          <Button
            label="Show Info"
            icon="pi pi-info-circle"
            severity="info"
            onClick={() => showInfo('Info', 'Here is some information')}
          />
        </div>
      </Card>

      {/* Icon Management Section */}
      <Card title="🎨 Icon Management" className="demo-card">
        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="icon-state">Icon State</label>
            <Dropdown
              id="icon-state"
              value={iconState}
              options={iconStates}
              onChange={(e) => setIconState(e.value)}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="tooltip">Tooltip</label>
            <InputText
              id="tooltip"
              value={tooltipText}
              onChange={(e) => setTooltipText(e.target.value)}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="flash-duration">Flash Duration (ms)</label>
            <InputText
              id="flash-duration"
              type="number"
              value={flashDuration.toString()}
              onChange={(e) => setFlashDuration(parseInt(e.target.value) || 3000)}
              className="w-full"
            />
          </div>
        </div>

        <div className="button-group">
          <Button
            label="Update Icon"
            icon="pi pi-image"
            onClick={handleUpdateIcon}
          />
          <Button
            label="Flash Icon"
            icon="pi pi-bolt"
            onClick={handleFlash}
          />
          <Button
            label="Update Tooltip"
            icon="pi pi-comment"
            onClick={handleUpdateTooltip}
          />
        </div>
      </Card>

      {/* Operations Section */}
      <Card title="⚙️ Operations with Tray Integration" className="demo-card">
        <p>
          These buttons demonstrate automatic tray status updates during operations.
        </p>

        <div className="button-group">
          <Button
            label="Simulate Long Operation"
            icon="pi pi-spin pi-spinner"
            onClick={handleLongOperation}
          />
          <Button
            label="Simulate Error"
            icon="pi pi-times-circle"
            severity="danger"
            onClick={handleErrorOperation}
          />
          <Button
            label="Add Recent Project"
            icon="pi pi-plus"
            onClick={handleAddRecentProject}
          />
        </div>
      </Card>

      {/* Preferences Section */}
      <Card title="⚙️ Tray Preferences" className="demo-card">
        {trayPrefs && (
          <div className="preferences-grid">
            <div className="preference-item">
              <label htmlFor="minimize-to-tray">Minimize to Tray</label>
              <InputSwitch
                id="minimize-to-tray"
                checked={trayPrefs.minimizeToTray}
                onChange={() => togglePreference('minimizeToTray')}
                disabled={prefsLoading}
              />
            </div>

            <div className="preference-item">
              <label htmlFor="close-to-tray">Close to Tray</label>
              <InputSwitch
                id="close-to-tray"
                checked={trayPrefs.closeToTray}
                onChange={() => togglePreference('closeToTray')}
                disabled={prefsLoading}
              />
            </div>

            <div className="preference-item">
              <label htmlFor="show-notifications">Show Notifications</label>
              <InputSwitch
                id="show-notifications"
                checked={trayPrefs.showNotifications}
                onChange={() => togglePreference('showNotifications')}
                disabled={prefsLoading}
              />
            </div>

            <div className="preference-item">
              <label htmlFor="notification-sound">Notification Sound</label>
              <InputSwitch
                id="notification-sound"
                checked={trayPrefs.notificationSound}
                onChange={() => togglePreference('notificationSound')}
                disabled={prefsLoading}
              />
            </div>
          </div>
        )}

        <Divider />

        <div className="info-section">
          <h4>Recent Projects ({trayPrefs?.recentProjects?.length || 0})</h4>
          {trayPrefs?.recentProjects && trayPrefs.recentProjects.length > 0 ? (
            <ul className="recent-projects-list">
              {trayPrefs.recentProjects.slice(0, 5).map((project) => (
                <li key={project.id}>
                  <strong>{project.name}</strong>
                  {project.date && (
                    <span className="project-date">
                      {' '}
                      - {new Date(project.date).toLocaleString()}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted">No recent projects</p>
          )}
        </div>

        <Divider />

        <div className="info-section">
          <h4>Quick Actions ({trayPrefs?.quickActions?.filter(a => a.enabled).length || 0} enabled)</h4>
          {trayPrefs?.quickActions && trayPrefs.quickActions.length > 0 ? (
            <ul className="quick-actions-list">
              {trayPrefs.quickActions.map((action) => (
                <li key={action.id} className={action.enabled ? 'enabled' : 'disabled'}>
                  <span className="action-label">{action.label}</span>
                  <span className="action-route">{action.route}</span>
                  <span className={`action-status ${action.enabled ? 'enabled' : 'disabled'}`}>
                    {action.enabled ? '✓ Enabled' : '✗ Disabled'}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted">No quick actions configured</p>
          )}
        </div>
      </Card>

      {/* Usage Examples Section */}
      <Card title="📖 Usage Examples" className="demo-card">
        <div className="code-examples">
          <h4>Show Notification</h4>
          <pre>
            <code>{`await window.electronAPI.tray.showNotification(
  'Title',
  'Message body',
  'success'
);`}</code>
          </pre>

          <h4>Update Icon State</h4>
          <pre>
            <code>{`await window.electronAPI.tray.updateIcon('busy');`}</code>
          </pre>

          <h4>Add Recent Project</h4>
          <pre>
            <code>{`await window.electronAPI.tray.addRecentProject({
  id: 'project-123',
  name: 'Solar Installation',
  date: new Date().toISOString()
});`}</code>
          </pre>

          <h4>Using the Hook</h4>
          <pre>
            <code>{`const { showSuccess, updateIcon } = useTray();

async function handleCalculate() {
  await updateIcon('busy');
  const result = await calculate();
  await updateIcon('normal');
  await showSuccess('Complete', 'Calculation finished');
}`}</code>
          </pre>
        </div>
      </Card>

      {/* Tips Section */}
      <Card title="💡 Tips" className="demo-card">
        <ul className="tips-list">
          <li>
            <strong>Minimize to Tray:</strong> When enabled, minimizing the window will hide it to the tray instead of the taskbar.
          </li>
          <li>
            <strong>Close to Tray:</strong> When enabled, closing the window will hide it to the tray instead of quitting the app.
          </li>
          <li>
            <strong>Notifications:</strong> Use sparingly to avoid overwhelming users. Choose appropriate types (info, success, warning, error).
          </li>
          <li>
            <strong>Icon States:</strong> Update icon state during long operations to provide visual feedback.
          </li>
          <li>
            <strong>Recent Projects:</strong> Automatically managed, showing the 10 most recent projects.
          </li>
          <li>
            <strong>Quick Actions:</strong> Configure shortcuts to frequently used features in the tray menu.
          </li>
        </ul>
      </Card>
    </div>
  );
};

export default TrayIntegrationDemo;
