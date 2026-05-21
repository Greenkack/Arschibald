/**
 * Email Configuration Component
 * 
 * Email settings and SMTP configuration
 */

import React, { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { Password } from 'primereact/password';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { InputSwitch } from 'primereact/inputswitch';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Dialog } from 'primereact/dialog';
import api from '@services/api';

interface EmailSettingsData {
  provider: string;
  smtp_host: string | null;
  smtp_port: number | null;
  smtp_username: string | null;
  smtp_use_tls: boolean;
  smtp_use_ssl: boolean;
  from_email: string;
  from_name: string;
  reply_to_email: string | null;
  region: string | null;
  is_configured: boolean;
  last_test_at: string | null;
  last_test_success: boolean | null;
  updated_at: string;
}

interface EmailConfigurationProps {
  onUpdate?: () => void;
}

const EmailConfiguration: React.FC<EmailConfigurationProps> = ({ onUpdate }) => {
  const [settings, setSettings] = useState<EmailSettingsData | null>(null);
  const [password, setPassword] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [showTestDialog, setShowTestDialog] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [message, setMessage] = useState<{ severity: 'success' | 'error' | 'info'; text: string } | null>(null);

  const providerOptions = [
    { label: 'SMTP', value: 'smtp' },
    { label: 'SendGrid', value: 'sendgrid' },
    { label: 'Mailgun', value: 'mailgun' },
    { label: 'AWS SES', value: 'aws_ses' },
  ];

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/system-settings/email');
      setSettings(response.data);
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to load settings: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;

    try {
      setSaving(true);
      setMessage(null);
      
      const updateData: any = { ...settings };
      if (password) {
        updateData.smtp_password = password;
      }
      if (apiKey) {
        updateData.api_key = apiKey;
      }
      
      const response = await api.put('/api/v1/system-settings/email', updateData);
      setSettings(response.data);
      setPassword('');
      setApiKey('');
      
      setMessage({
        severity: 'success',
        text: 'Email settings saved successfully'
      });
      
      if (onUpdate) {
        onUpdate();
      }
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to save settings: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    if (!testEmail) {
      setMessage({
        severity: 'error',
        text: 'Please enter a test email address'
      });
      return;
    }

    try {
      setTesting(true);
      setMessage(null);
      
      const response = await api.post('/api/v1/system-settings/email/test', {
        to_email: testEmail,
        subject: 'Test Email from Solar Calculator Pro',
        body: 'This is a test email to verify your email configuration is working correctly.'
      });
      
      if (response.data.success) {
        setMessage({
          severity: 'success',
          text: 'Test email sent successfully! Please check your inbox.'
        });
        setShowTestDialog(false);
        loadSettings(); // Reload to get updated test status
      } else {
        setMessage({
          severity: 'error',
          text: response.data.message
        });
      }
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to send test email: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setTesting(false);
    }
  };

  const handleReset = () => {
    loadSettings();
    setPassword('');
    setApiKey('');
    setMessage(null);
  };

  if (loading) {
    return (
      <div className="settings-loading">
        <ProgressSpinner />
        <p>Loading email settings...</p>
      </div>
    );
  }

  if (!settings) {
    return <Message severity="error" text="Failed to load settings" />;
  }

  const isSMTP = settings.provider === 'smtp';

  return (
    <div className="email-configuration">
      {message && (
        <Message 
          severity={message.severity} 
          text={message.text} 
          className="settings-message"
        />
      )}

      <div className="settings-section">
        <h3>Email Provider</h3>
        
        <div className="p-field">
          <label htmlFor="provider">Provider</label>
          <Dropdown
            id="provider"
            value={settings.provider}
            options={providerOptions}
            onChange={(e) => setSettings({ ...settings, provider: e.value })}
            className="w-full"
          />
        </div>
      </div>

      {isSMTP ? (
        <>
          <div className="settings-section">
            <h3>SMTP Configuration</h3>
            
            <div className="p-field">
              <label htmlFor="smtp_host">SMTP Host</label>
              <InputText
                id="smtp_host"
                value={settings.smtp_host || ''}
                onChange={(e) => setSettings({ ...settings, smtp_host: e.target.value })}
                placeholder="smtp.example.com"
                className="w-full"
              />
            </div>

            <div className="p-field">
              <label htmlFor="smtp_port">SMTP Port</label>
              <InputNumber
                id="smtp_port"
                value={settings.smtp_port || 587}
                onValueChange={(e) => setSettings({ ...settings, smtp_port: e.value || 587 })}
                min={1}
                max={65535}
                className="w-full"
              />
              <small>Common ports: 25 (unencrypted), 587 (TLS), 465 (SSL)</small>
            </div>

            <div className="p-field">
              <label htmlFor="smtp_username">SMTP Username</label>
              <InputText
                id="smtp_username"
                value={settings.smtp_username || ''}
                onChange={(e) => setSettings({ ...settings, smtp_username: e.target.value })}
                className="w-full"
              />
            </div>

            <div className="p-field">
              <label htmlFor="smtp_password">SMTP Password</label>
              <Password
                id="smtp_password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter new password to change"
                feedback={false}
                toggleMask
                className="w-full"
              />
              <small>Leave empty to keep current password</small>
            </div>

            <div className="p-field-checkbox">
              <InputSwitch
                id="smtp_use_tls"
                checked={settings.smtp_use_tls}
                onChange={(e) => setSettings({ ...settings, smtp_use_tls: e.value })}
              />
              <label htmlFor="smtp_use_tls">Use TLS</label>
            </div>

            <div className="p-field-checkbox">
              <InputSwitch
                id="smtp_use_ssl"
                checked={settings.smtp_use_ssl}
                onChange={(e) => setSettings({ ...settings, smtp_use_ssl: e.value })}
              />
              <label htmlFor="smtp_use_ssl">Use SSL</label>
            </div>
          </div>
        </>
      ) : (
        <div className="settings-section">
          <h3>API Configuration</h3>
          
          <div className="p-field">
            <label htmlFor="api_key">API Key</label>
            <Password
              id="api_key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter API key"
              feedback={false}
              toggleMask
              className="w-full"
            />
          </div>

          {settings.provider === 'aws_ses' && (
            <div className="p-field">
              <label htmlFor="region">AWS Region</label>
              <InputText
                id="region"
                value={settings.region || ''}
                onChange={(e) => setSettings({ ...settings, region: e.target.value })}
                placeholder="us-east-1"
                className="w-full"
              />
            </div>
          )}
        </div>
      )}

      <div className="settings-section">
        <h3>Email Settings</h3>
        
        <div className="p-field">
          <label htmlFor="from_email">From Email</label>
          <InputText
            id="from_email"
            value={settings.from_email}
            onChange={(e) => setSettings({ ...settings, from_email: e.target.value })}
            placeholder="noreply@example.com"
            className="w-full"
          />
        </div>

        <div className="p-field">
          <label htmlFor="from_name">From Name</label>
          <InputText
            id="from_name"
            value={settings.from_name}
            onChange={(e) => setSettings({ ...settings, from_name: e.target.value })}
            placeholder="Solar Calculator Pro"
            className="w-full"
          />
        </div>

        <div className="p-field">
          <label htmlFor="reply_to_email">Reply-To Email (Optional)</label>
          <InputText
            id="reply_to_email"
            value={settings.reply_to_email || ''}
            onChange={(e) => setSettings({ ...settings, reply_to_email: e.target.value })}
            placeholder="support@example.com"
            className="w-full"
          />
        </div>
      </div>

      {settings.last_test_at && (
        <div className="settings-section">
          <h3>Last Test</h3>
          <div className="test-status">
            <i className={`pi ${settings.last_test_success ? 'pi-check-circle' : 'pi-times-circle'}`} 
               style={{ color: settings.last_test_success ? 'green' : 'red', marginRight: '8px' }}></i>
            <span>
              {settings.last_test_success ? 'Success' : 'Failed'} - {new Date(settings.last_test_at).toLocaleString()}
            </span>
          </div>
        </div>
      )}

      <div className="settings-actions">
        <Button
          label="Save Changes"
          icon="pi pi-check"
          onClick={handleSave}
          loading={saving}
          className="p-button-success"
        />
        <Button
          label="Test Email"
          icon="pi pi-send"
          onClick={() => setShowTestDialog(true)}
          className="p-button-info"
          disabled={!settings.is_configured}
        />
        <Button
          label="Reset"
          icon="pi pi-refresh"
          onClick={handleReset}
          className="p-button-secondary"
          disabled={saving}
        />
      </div>

      {settings.updated_at && (
        <div className="settings-footer">
          <small>Last updated: {new Date(settings.updated_at).toLocaleString()}</small>
        </div>
      )}

      <Dialog
        header="Test Email Configuration"
        visible={showTestDialog}
        style={{ width: '450px' }}
        onHide={() => setShowTestDialog(false)}
        footer={
          <div>
            <Button
              label="Cancel"
              icon="pi pi-times"
              onClick={() => setShowTestDialog(false)}
              className="p-button-text"
            />
            <Button
              label="Send Test Email"
              icon="pi pi-send"
              onClick={handleTest}
              loading={testing}
              autoFocus
            />
          </div>
        }
      >
        <div className="p-field">
          <label htmlFor="test_email">Test Email Address</label>
          <InputText
            id="test_email"
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
            placeholder="your@email.com"
            className="w-full"
          />
          <small>A test email will be sent to this address</small>
        </div>
      </Dialog>
    </div>
  );
};

export default EmailConfiguration;
