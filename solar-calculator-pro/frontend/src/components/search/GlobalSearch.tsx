/**
 * Global Search Component
 * 
 * Provides comprehensive search functionality across all entities
 * Features:
 * - Real-time search with debouncing
 * - Fuzzy matching
 * - Search suggestions
 * - Entity type filtering
 * - Search history
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { MultiSelect } from 'primereact/multiselect';
import { Checkbox } from 'primereact/checkbox';
import { ProgressSpinner } from 'primereact/progressspinner';
import { AutoComplete } from 'primereact/autocomplete';
import { Badge } from 'primereact/badge';
import { Divider } from 'primereact/divider';
import './GlobalSearch.css';

interface SearchResult {
  id: number;
  entity_type: string;
  title: string;
  description?: string;
  metadata: Record<string, any>;
  relevance_score: number;
}

interface GlobalSearchProps {
  onResultClick?: (result: SearchResult) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

const ENTITY_TYPES = [
  { label: 'Projects', value: 'projects', icon: 'pi pi-folder' },
  { label: 'Customers', value: 'customers', icon: 'pi pi-users' },
  { label: 'Products', value: 'products', icon: 'pi pi-box' },
  { label: 'Documents', value: 'documents', icon: 'pi pi-file' },
  { label: 'Offers', value: 'offers', icon: 'pi pi-file-edit' },
  { label: 'Contracts', value: 'contracts', icon: 'pi pi-file-check' }
];

export const GlobalSearch: React.FC<GlobalSearchProps> = ({
  onResultClick,
  placeholder = 'Search across all entities...',
  autoFocus = false
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Record<string, SearchResult[]>>({});
  const [loading, setLoading] = useState(false);
  const [selectedEntityTypes, setSelectedEntityTypes] = useState<string[]>([]);
  const [fuzzyEnabled, setFuzzyEnabled] = useState(true);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [executionTime, setExecutionTime] = useState<number>(0);
  
  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced search
  const performSearch = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setResults({});
      setShowResults(false);
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch('/api/v1/search/global', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          entity_types: selectedEntityTypes.length > 0 ? selectedEntityTypes : null,
          limit: 50,
          fuzzy: fuzzyEnabled
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data.results);
        setExecutionTime(data.execution_time_ms);
        setShowResults(true);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedEntityTypes, fuzzyEnabled]);

  // Handle query change with debouncing
  const handleQueryChange = (value: string) => {
    setQuery(value);

    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Set new timeout for search
    searchTimeoutRef.current = setTimeout(() => {
      performSearch(value);
    }, 300);

    // Get suggestions immediately
    if (value.length >= 2) {
      fetchSuggestions(value);
    } else {
      setSuggestions([]);
    }
  };

  // Fetch search suggestions
  const fetchSuggestions = async (partialQuery: string) => {
    try {
      const response = await fetch(
        `/api/v1/search/suggestions?query=${encodeURIComponent(partialQuery)}&limit=10`
      );
      
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      console.error('Suggestions error:', error);
    }
  };

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion: string) => {
    setQuery(suggestion);
    performSearch(suggestion);
  };

  // Calculate total results
  const totalResults = Object.values(results).reduce(
    (sum, items) => sum + items.length,
    0
  );

  // Get entity type label
  const getEntityTypeLabel = (type: string): string => {
    const entity = ENTITY_TYPES.find(e => e.value === type);
    return entity?.label || type;
  };

  // Get entity type icon
  const getEntityTypeIcon = (type: string): string => {
    const entity = ENTITY_TYPES.find(e => e.value === type);
    return entity?.icon || 'pi pi-circle';
  };

  // Handle result click
  const handleResultClick = (result: SearchResult) => {
    setShowResults(false);
    if (onResultClick) {
      onResultClick(result);
    }
  };

  // Handle click outside to close results
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.global-search-container')) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="global-search-container">
      <div className="search-input-wrapper">
        <span className="p-input-icon-left p-input-icon-right">
          <i className="pi pi-search" />
          <InputText
            ref={inputRef}
            value={query}
            onChange={(e) => handleQueryChange(e.target.value)}
            placeholder={placeholder}
            className="global-search-input"
            autoFocus={autoFocus}
            onFocus={() => query.length >= 2 && setShowResults(true)}
          />
          {loading && (
            <i className="pi pi-spin pi-spinner" style={{ right: '10px' }} />
          )}
        </span>

        {/* Search suggestions */}
        {suggestions.length > 0 && query.length >= 2 && (
          <div className="search-suggestions">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="suggestion-item"
                onClick={() => handleSuggestionSelect(suggestion)}
              >
                <i className="pi pi-history" />
                <span>{suggestion}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Search options */}
      <div className="search-options">
        <MultiSelect
          value={selectedEntityTypes}
          options={ENTITY_TYPES}
          onChange={(e) => setSelectedEntityTypes(e.value)}
          placeholder="All entity types"
          display="chip"
          className="entity-type-selector"
        />

        <div className="fuzzy-toggle">
          <Checkbox
            inputId="fuzzy-search"
            checked={fuzzyEnabled}
            onChange={(e) => setFuzzyEnabled(e.checked || false)}
          />
          <label htmlFor="fuzzy-search">Fuzzy matching</label>
        </div>
      </div>

      {/* Search results */}
      {showResults && query.length >= 2 && (
        <div className="search-results-panel">
          {loading ? (
            <div className="search-loading">
              <ProgressSpinner style={{ width: '50px', height: '50px' }} />
              <p>Searching...</p>
            </div>
          ) : totalResults > 0 ? (
            <>
              <div className="results-header">
                <span className="results-count">
                  {totalResults} result{totalResults !== 1 ? 's' : ''} found
                </span>
                <span className="execution-time">
                  {executionTime.toFixed(2)}ms
                </span>
              </div>

              <Divider />

              {Object.entries(results).map(([entityType, items]) => (
                items.length > 0 && (
                  <div key={entityType} className="entity-results-group">
                    <div className="entity-group-header">
                      <i className={getEntityTypeIcon(entityType)} />
                      <span>{getEntityTypeLabel(entityType)}</span>
                      <Badge value={items.length} />
                    </div>

                    <div className="entity-results-list">
                      {items.map((result) => (
                        <div
                          key={result.id}
                          className="result-item"
                          onClick={() => handleResultClick(result)}
                        >
                          <div className="result-title">{result.title}</div>
                          {result.description && (
                            <div className="result-description">
                              {result.description}
                            </div>
                          )}
                          <div className="result-metadata">
                            {Object.entries(result.metadata).map(([key, value]) => (
                              <span key={key} className="metadata-item">
                                {key}: {String(value)}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              ))}
            </>
          ) : (
            <div className="no-results">
              <i className="pi pi-search" />
              <p>No results found for "{query}"</p>
              <p className="no-results-hint">
                Try different keywords or enable fuzzy matching
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GlobalSearch;
