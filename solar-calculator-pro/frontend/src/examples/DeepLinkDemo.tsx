/**
 * Deep Link Demo Component
 * 
 * Demonstrates deep linking functionality in Solar Calculator Pro
 * Shows how to generate, test, and use deep links
 */

import React, { useState, useEffect } from 'react';
import { useDeepLink } from '../hooks/useDeepLink';
import './DeepLinkDemo.css';

interface DeepLinkExample {
  name: string;
  description: string;
  action: string;
  params?: Record<string, string | number>;
  pathSegments?: string[];
}

export const DeepLinkDemo: React.FC = () => {
  const {
    generateDeepLink,
    copyDeepLinkToClipboard,
    testDeepLink,
    getRegisteredHandlers,
    isProtocolRegistered,
    isElectron,
  } = useDeepLink();

  const [generatedLink, setGeneratedLink] = useState<string>('');
  const [testUrl, setTestUrl] = useState<string>('');
  const [handlers, setHandlers] = useState<string[]>([]);
  const [isRegistered, setIsRegistered] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info');

  // Deep link examples
  const examples: DeepLinkExample[] = [
    {
      name: 'Open Project',
      description: 'Open a specific project by ID',
      action: 'open-project',
      params: { id: '12345' },
    },
    {
      name: 'Solar Calculator',
      description: 'Open solar calculator with pre-filled data',
      action: 'solar-calculator',
      params: {
        roofArea: '50',
        roofType: 'flat',
        location: 'Berlin',
      },
    },
    {
      name: 'Customer Details',
      description: 'Open specific customer in CRM',
      action: 'customer',
      pathSegments: ['67890'],
    },
    {
      name: 'Generate PDF',
      description: 'Generate PDF for a project',
      action: 'generate-pdf',
      params: {
        project: '12345',
        template: 'standard',
      },
    },
    {
      name: 'Email Compose',
      description: 'Open email compose with pre-filled data',
      action: 'email',
      params: {
        to: 'customer@example.com',
        subject: 'Solar Calculator Quote',
      },
    },
    {
      name: 'Settings',
      description: 'Open settings page',
      action: 'settings',
      params: { section: 'notifications' },
    },
    {
      name: '3D Visualization',
      description: 'Open 3D view for a project',
      action: '3d-view',
      params: { project: '12345' },
    },
    {
      name: 'Price Matrix',
      description: 'Open price matrix management',
      action: 'price-matrix',
    },
    {
      name: 'New Project',
      description: 'Create new solar project',
      action: 'new-project',
      params: { type: 'solar' },
    },
    {
      name: 'Dashboard',
      description: 'Navigate to dashboard',
      action: 'dashboard',
    },
  ];

  // Load handlers and registration status on mount
  useEffect(() => {
    const loadInfo = async () => {
      const handlersResult = await getRegisteredHandlers();
      if (handlersResult.success) {
        setHandlers(handlersResult.handlers);
      }

      const registrationResult = await isProtocolRegistered();
      if (registrationResult.success) {
        setIsRegistered(registrationResult.isRegistered);
      }
    };

    loadInfo();
  }, [getRegisteredHandlers, isProtocolRegistered]);

  const showMessage = (msg: string, type: 'success' | 'error' | 'info' = 'info') => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => setMessage(''), 5000);
  };

  const handleGenerateLink = async (example: DeepLinkExample) => {
    const result = await generateDeepLink(
      example.action,
      example.params || {},
      example.pathSegments || []
    );

    if (result.success && result.deepLink) {
      setGeneratedLink(result.deepLink);
      showMessage('Deep link generated successfully!', 'success');
    } else {
      showMessage(`Error: ${result.error}`, 'error');
    }
  };

  const handleCopyLink = async (example: DeepLinkExample) => {
    const result = await copyDeepLinkToClipboard(
      example.action,
      example.params || {},
      example.pathSegments || []
    );

    if (result.success && result.deepLink) {
      setGeneratedLink(result.deepLink);
      showMessage('Deep link copied to clipboard!', 'success');
    } else {
      showMessage(`Error: ${result.error}`, 'error');
    }
  };

  const handleTestLink = async () => {
    if (!testUrl) {
      showMessage('Please enter a URL to test', 'error');
      return;
    }

    const result = await testDeepLink(testUrl);

    if (result.success) {
      showMessage('Deep link tested successfully!', 'success');
    } else {
      showMessage(`Error: ${result.error}`, 'error');
    }
  };

  if (!isElectron) {
    return (
      <div className="deep-link-demo">
        <div className="not-electron-warning">
          <h2>⚠️ Not Running in Electron</h2>
          <p>Deep linking features are only available in the Electron desktop application.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="deep-link-demo">
      <div className="demo-header">
        <h1>🔗 Deep Link Demo</h1>
        <p>
          Explore deep linking functionality in Solar Calculator Pro. Generate, test, and use
          custom URL protocols to navigate and interact with the application.
        </p>
      </div>

      {message && (
        <div className={`message message-${messageType}`}>
          {message}
        </div>
      )}

      <div className="demo-section">
        <h2>📊 Protocol Status</h2>
        <div className="status-grid">
          <div className="status-item">
            <span className="status-label">Protocol:</span>
            <span className="status-value">solarcalc://</span>
          </div>
          <div className="status-item">
            <span className="status-label">Registered:</span>
            <span className={`status-value ${isRegistered ? 'registered' : 'not-registered'}`}>
              {isRegistered ? '✅ Yes' : '❌ No'}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Handlers:</span>
            <span className="status-value">{handlers.length} registered</span>
          </div>
        </div>
      </div>

      <div className="demo-section">
        <h2>📝 Deep Link Examples</h2>
        <div className="examples-grid">
          {examples.map((example, index) => (
            <div key={index} className="example-card">
              <h3>{example.name}</h3>
              <p>{example.description}</p>
              <div className="example-details">
                <div className="detail-row">
                  <span className="detail-label">Action:</span>
                  <code>{example.action}</code>
                </div>
                {example.params && Object.keys(example.params).length > 0 && (
                  <div className="detail-row">
                    <span className="detail-label">Params:</span>
                    <code>{JSON.stringify(example.params, null, 2)}</code>
                  </div>
                )}
                {example.pathSegments && example.pathSegments.length > 0 && (
                  <div className="detail-row">
                    <span className="detail-label">Path:</span>
                    <code>{example.pathSegments.join('/')}</code>
                  </div>
                )}
              </div>
              <div className="example-actions">
                <button
                  className="btn btn-primary"
                  onClick={() => handleGenerateLink(example)}
                >
                  Generate Link
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleCopyLink(example)}
                >
                  Copy to Clipboard
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {generatedLink && (
        <div className="demo-section">
          <h2>🔗 Generated Link</h2>
          <div className="generated-link-container">
            <code className="generated-link">{generatedLink}</code>
            <button
              className="btn btn-copy"
              onClick={() => {
                navigator.clipboard.writeText(generatedLink);
                showMessage('Link copied to clipboard!', 'success');
              }}
            >
              📋 Copy
            </button>
          </div>
        </div>
      )}

      <div className="demo-section">
        <h2>🧪 Test Deep Link</h2>
        <p>Enter a deep link URL to test it:</p>
        <div className="test-container">
          <input
            type="text"
            className="test-input"
            placeholder="solarcalc://open-project?id=12345"
            value={testUrl}
            onChange={(e) => setTestUrl(e.target.value)}
          />
          <button className="btn btn-primary" onClick={handleTestLink}>
            Test Link
          </button>
        </div>
      </div>

      <div className="demo-section">
        <h2>📚 Registered Handlers</h2>
        <div className="handlers-list">
          {handlers.length > 0 ? (
            <ul>
              {handlers.map((handler, index) => (
                <li key={index}>
                  <code>solarcalc://{handler}</code>
                </li>
              ))}
            </ul>
          ) : (
            <p>No handlers registered</p>
          )}
        </div>
      </div>

      <div className="demo-section">
        <h2>📖 Usage Examples</h2>
        <div className="usage-examples">
          <div className="usage-example">
            <h3>From Email</h3>
            <p>
              Include deep links in emails to allow customers to open specific projects or
              calculations directly:
            </p>
            <code>
              &lt;a href="solarcalc://open-project?id=12345"&gt;View Your Solar Project&lt;/a&gt;
            </code>
          </div>

          <div className="usage-example">
            <h3>From Website</h3>
            <p>
              Add deep links to your website to launch the application with pre-filled data:
            </p>
            <code>
              &lt;a href="solarcalc://solar-calculator?roofArea=50&location=Berlin"&gt;Calculate
              Now&lt;/a&gt;
            </code>
          </div>

          <div className="usage-example">
            <h3>From Command Line</h3>
            <p>Launch the application with a deep link from the command line:</p>
            <code>start solarcalc://dashboard</code>
            <p className="note">Windows</p>
            <code>open solarcalc://dashboard</code>
            <p className="note">macOS</p>
            <code>xdg-open solarcalc://dashboard</code>
            <p className="note">Linux</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeepLinkDemo;
