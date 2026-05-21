/**
 * Release Notes Component
 * 
 * Displays formatted release notes with markdown support
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Skeleton } from 'primereact/skeleton';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import './ReleaseNotes.css';

interface ReleaseNote {
  version: string;
  releaseDate: string;
  notes: string;
  channel?: string;
}

interface ReleaseNotesProps {
  version?: string;
  onFetchNotes?: (version: string) => Promise<ReleaseNote>;
}

export const ReleaseNotes: React.FC<ReleaseNotesProps> = ({
  version,
  onFetchNotes
}) => {
  const [releaseNote, setReleaseNote] = useState<ReleaseNote | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (version && onFetchNotes) {
      loadReleaseNotes();
    }
  }, [version]);

  const loadReleaseNotes = async () => {
    if (!version || !onFetchNotes) return;

    setLoading(true);
    setError(null);

    try {
      const notes = await onFetchNotes(version);
      setReleaseNote(notes);
    } catch (err) {
      setError('Failed to load release notes');
      console.error('Error loading release notes:', err);
    } finally {
      setLoading(false);
    }
  };

  const getChannelSeverity = (channel?: string) => {
    switch (channel) {
      case 'alpha':
        return 'danger';
      case 'beta':
        return 'warning';
      default:
        return 'success';
    }
  };

  const formatMarkdown = (markdown: string): string => {
    // Simple markdown to HTML conversion
    let html = markdown;

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Code
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');

    // Links
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');

    // Lists
    html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // Line breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>' + html + '</p>';

    return html;
  };

  if (loading) {
    return (
      <Card className="release-notes-card">
        <div className="release-notes-skeleton">
          <Skeleton width="200px" height="2rem" className="mb-3" />
          <Skeleton width="100%" height="1rem" className="mb-2" />
          <Skeleton width="100%" height="1rem" className="mb-2" />
          <Skeleton width="80%" height="1rem" className="mb-3" />
          <Skeleton width="100%" height="1rem" className="mb-2" />
          <Skeleton width="90%" height="1rem" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="release-notes-card">
        <div className="release-notes-error">
          <i className="pi pi-exclamation-triangle" />
          <p>{error}</p>
          <Button
            label="Retry"
            icon="pi pi-refresh"
            onClick={loadReleaseNotes}
            className="p-button-sm"
          />
        </div>
      </Card>
    );
  }

  if (!releaseNote) {
    return (
      <Card className="release-notes-card">
        <div className="release-notes-empty">
          <i className="pi pi-file" />
          <p>No release notes available</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="release-notes-card">
      <div className="release-notes-header">
        <div className="release-notes-title">
          <h2>Version {releaseNote.version}</h2>
          {releaseNote.channel && releaseNote.channel !== 'latest' && (
            <Tag
              value={releaseNote.channel.toUpperCase()}
              severity={getChannelSeverity(releaseNote.channel)}
            />
          )}
        </div>
        <div className="release-notes-date">
          <i className="pi pi-calendar mr-2" />
          {new Date(releaseNote.releaseDate).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </div>
      </div>

      <div
        className="release-notes-content"
        dangerouslySetInnerHTML={{ __html: formatMarkdown(releaseNote.notes) }}
      />
    </Card>
  );
};
