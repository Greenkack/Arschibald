/**
 * Custom Hooks Demo
 * 
 * Comprehensive demonstration of all custom hooks:
 * - useAuth: Authentication operations
 * - useApi: API calls with loading and error handling
 * - useWebSocket: Real-time WebSocket communication
 * - useForm: Enhanced form management with validation and auto-save
 * - useDebounce: Debounced values for search inputs
 */

import React, { useState } from 'react';
import {
  useAuth,
  useApi,
  useWebSocket,
  useWebSocketConnection,
  useForm,
  useDebounce,
} from '../hooks';
import { z } from 'zod';
import './CustomHooksDemo.css';

// ============================================================================
// 1. useAuth Hook Demo
// ============================================================================

const AuthDemo: React.FC = () => {
  const { user, isAuthenticated, isLoading, error, login, logout } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    await login({ username, password });
  };

  return (
    <div className="demo-section">
      <h2>1. useAuth Hook</h2>
      <p>Manages authentication state and operations</p>

      {!isAuthenticated ? (
        <form onSubmit={handleLogin} className="auth-form">
          <div className="form-group">
            <label>Username:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
            />
          </div>
          <div className="form-group">
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
            />
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
          {error && <div className="error">{error}</div>}
        </form>
      ) : (
        <div className="user-info">
          <p>Welcome, {user?.username}!</p>
          <p>Email: {user?.email}</p>
          <p>Role: {user?.role}</p>
          <button onClick={logout}>Logout</button>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// 2. useApi Hook Demo
// ============================================================================

interface Project {
  id: number;
  name: string;
  status: string;
}

const ApiDemo: React.FC = () => {
  const [projectId, setProjectId] = useState('1');

  // Example API function
  const fetchProject = async (id: string): Promise<Project> => {
    const response = await fetch(`http://localhost:8000/api/v1/projects/${id}`);
    if (!response.ok) throw new Error('Failed to fetch project');
    return response.json();
  };

  const {
    data: project,
    isLoading,
    error,
    execute,
    reset,
  } = useApi(fetchProject, {
    showNotification: true,
    successMessage: 'Project loaded successfully!',
  });

  const handleFetch = () => {
    execute(projectId);
  };

  return (
    <div className="demo-section">
      <h2>2. useApi Hook</h2>
      <p>Handles API calls with loading states and error handling</p>

      <div className="api-controls">
        <input
          type="text"
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          placeholder="Project ID"
        />
        <button onClick={handleFetch} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Fetch Project'}
        </button>
        <button onClick={reset}>Reset</button>
      </div>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error.message}
        </div>
      )}

      {project && (
        <div className="project-info">
          <h3>Project Details:</h3>
          <p><strong>ID:</strong> {project.id}</p>
          <p><strong>Name:</strong> {project.name}</p>
          <p><strong>Status:</strong> {project.status}</p>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// 3. useWebSocket Hook Demo
// ============================================================================

const WebSocketDemo: React.FC = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const { isConnected, connect, disconnect } = useWebSocketConnection();

  // Listen for calculation updates
  const { emit: sendCalculation } = useWebSocket('calculation:update', (data) => {
    setMessages((prev) => [...prev, `Received: ${JSON.stringify(data)}`]);
  });

  // Listen for progress notifications
  useWebSocket('progress:update', (data) => {
    setMessages((prev) => [...prev, `Progress: ${data.percentage}%`]);
  });

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      sendCalculation({ message: inputMessage });
      setMessages((prev) => [...prev, `Sent: ${inputMessage}`]);
      setInputMessage('');
    }
  };

  return (
    <div className="demo-section">
      <h2>3. useWebSocket Hook</h2>
      <p>Real-time bidirectional communication</p>

      <div className="websocket-status">
        <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
        </span>
        <button onClick={isConnected ? disconnect : connect}>
          {isConnected ? 'Disconnect' : 'Connect'}
        </button>
      </div>

      <div className="message-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Enter message"
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <button onClick={handleSendMessage} disabled={!isConnected}>
          Send
        </button>
      </div>

      <div className="message-log">
        <h4>Message Log:</h4>
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className="message">
              {msg}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 4. useForm Hook Demo
// ============================================================================

// Validation schema
const solarFormSchema = z.object({
  roofArea: z.number().min(10, 'Roof area must be at least 10 m²'),
  roofType: z.enum(['flat', 'gable', 'hip'], {
    errorMap: () => ({ message: 'Please select a roof type' }),
  }),
  annualConsumption: z.number().min(1000, 'Consumption must be at least 1000 kWh'),
  location: z.string().min(2, 'Location is required'),
});

type SolarFormData = z.infer<typeof solarFormSchema>;

const FormDemo: React.FC = () => {
  const [savedData, setSavedData] = useState<SolarFormData | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    isAutoSaving,
    lastSaved,
    manualSave,
  } = useForm<SolarFormData>({
    schema: solarFormSchema,
    defaultValues: {
      roofArea: 50,
      roofType: 'flat',
      annualConsumption: 4000,
      location: 'Berlin',
    },
    autoSave: true,
    autoSaveInterval: 3000,
    onAutoSave: async (data) => {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      console.log('Auto-saved:', data);
    },
    onSubmitSuccess: (data) => {
      setSavedData(data);
    },
    showSuccessToast: true,
    successMessage: 'Form saved successfully!',
  });

  return (
    <div className="demo-section">
      <h2>4. useForm Hook</h2>
      <p>Enhanced form management with validation and auto-save</p>

      <form onSubmit={handleSubmit} className="solar-form">
        <div className="form-group">
          <label>Roof Area (m²):</label>
          <input
            type="number"
            {...register('roofArea', { valueAsNumber: true })}
          />
          {errors.roofArea && (
            <span className="error">{errors.roofArea.message}</span>
          )}
        </div>

        <div className="form-group">
          <label>Roof Type:</label>
          <select {...register('roofType')}>
            <option value="flat">Flat</option>
            <option value="gable">Gable</option>
            <option value="hip">Hip</option>
          </select>
          {errors.roofType && (
            <span className="error">{errors.roofType.message}</span>
          )}
        </div>

        <div className="form-group">
          <label>Annual Consumption (kWh):</label>
          <input
            type="number"
            {...register('annualConsumption', { valueAsNumber: true })}
          />
          {errors.annualConsumption && (
            <span className="error">{errors.annualConsumption.message}</span>
          )}
        </div>

        <div className="form-group">
          <label>Location:</label>
          <input type="text" {...register('location')} />
          {errors.location && (
            <span className="error">{errors.location.message}</span>
          )}
        </div>

        <div className="form-actions">
          <button type="submit">Submit</button>
          <button type="button" onClick={manualSave}>
            Save Now
          </button>
        </div>

        <div className="form-status">
          {isAutoSaving && <span className="saving">Auto-saving...</span>}
          {isDirty && <span className="dirty">Unsaved changes</span>}
          {lastSaved && (
            <span className="last-saved">
              Last saved: {lastSaved.toLocaleTimeString()}
            </span>
          )}
        </div>
      </form>

      {savedData && (
        <div className="saved-data">
          <h4>Submitted Data:</h4>
          <pre>{JSON.stringify(savedData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// 5. useDebounce Hook Demo
// ============================================================================

const DebounceDemo: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  
  // Debounce the search term
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  // Simulate search when debounced value changes
  React.useEffect(() => {
    if (debouncedSearchTerm) {
      setIsSearching(true);
      
      // Simulate API call
      setTimeout(() => {
        const mockResults = [
          `Result 1 for "${debouncedSearchTerm}"`,
          `Result 2 for "${debouncedSearchTerm}"`,
          `Result 3 for "${debouncedSearchTerm}"`,
        ];
        setSearchResults(mockResults);
        setIsSearching(false);
      }, 300);
    } else {
      setSearchResults([]);
    }
  }, [debouncedSearchTerm]);

  return (
    <div className="demo-section">
      <h2>5. useDebounce Hook</h2>
      <p>Debounces values to reduce API calls (500ms delay)</p>

      <div className="search-container">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Type to search..."
          className="search-input"
        />
        
        <div className="search-info">
          <p>Current input: <strong>{searchTerm || '(empty)'}</strong></p>
          <p>Debounced value: <strong>{debouncedSearchTerm || '(empty)'}</strong></p>
        </div>

        {isSearching && <div className="searching">Searching...</div>}

        {searchResults.length > 0 && (
          <div className="search-results">
            <h4>Search Results:</h4>
            <ul>
              {searchResults.map((result, index) => (
                <li key={index}>{result}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// Main Demo Component
// ============================================================================

const CustomHooksDemo: React.FC = () => {
  return (
    <div className="custom-hooks-demo">
      <header className="demo-header">
        <h1>Custom Hooks Demo</h1>
        <p>Comprehensive demonstration of all custom React hooks</p>
      </header>

      <div className="demo-container">
        <AuthDemo />
        <ApiDemo />
        <WebSocketDemo />
        <FormDemo />
        <DebounceDemo />
      </div>

      <footer className="demo-footer">
        <h3>Hook Summary:</h3>
        <ul>
          <li><strong>useAuth:</strong> Authentication state and operations</li>
          <li><strong>useApi:</strong> API calls with loading and error handling</li>
          <li><strong>useWebSocket:</strong> Real-time WebSocket communication</li>
          <li><strong>useForm:</strong> Enhanced form management with validation and auto-save</li>
          <li><strong>useDebounce:</strong> Debounced values for search inputs</li>
        </ul>
      </footer>
    </div>
  );
};

export default CustomHooksDemo;
