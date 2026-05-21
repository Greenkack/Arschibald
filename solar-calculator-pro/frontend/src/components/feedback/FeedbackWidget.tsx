/**
 * Feedback Widget
 * 
 * Floating feedback widget for beta testers
 */

import React, { useState, useEffect } from 'react';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { Badge } from 'primereact/badge';
import FeedbackForm from './FeedbackForm';
import './FeedbackWidget.css';

interface FeedbackWidgetProps {
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  showOnStartup?: boolean;
  reminderInterval?: number; // milliseconds
}

const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({
  position = 'bottom-right',
  showOnStartup = false,
  reminderInterval = 604800000, // 7 days
}) => {
  const [visible, setVisible] = useState(false);
  const [dialogVisible, setDialogVisible] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [lastReminderDate, setLastReminderDate] = useState<Date | null>(null);

  useEffect(() => {
    // Check if we should show startup reminder
    if (showOnStartup) {
      checkStartupReminder();
    }

    // Load last reminder date
    const savedDate = localStorage.getItem('feedback_last_reminder');
    if (savedDate) {
      setLastReminderDate(new Date(savedDate));
    }

    // Show widget after a delay
    const timer = setTimeout(() => {
      setVisible(true);
    }, 2000);

    return () => clearTimeout(timer);
  }, [showOnStartup]);

  const checkStartupReminder = () => {
    const lastReminder = localStorage.getItem('feedback_last_reminder');
    
    if (!lastReminder) {
      // First time - show reminder
      showReminder();
      return;
    }

    const lastDate = new Date(lastReminder);
    const now = new Date();
    const timeSinceLastReminder = now.getTime() - lastDate.getTime();

    if (timeSinceLastReminder >= reminderInterval) {
      showReminder();
    }
  };

  const showReminder = () => {
    // Show a subtle reminder
    setUnreadCount(1);
    
    // Save reminder date
    const now = new Date();
    localStorage.setItem('feedback_last_reminder', now.toISOString());
    setLastReminderDate(now);
  };

  const handleOpenDialog = () => {
    setDialogVisible(true);
    setUnreadCount(0);
  };

  const handleCloseDialog = () => {
    setDialogVisible(false);
  };

  const handleFeedbackSubmitted = () => {
    setDialogVisible(false);
    
    // Show success message
    // (This would typically be handled by a toast notification)
  };

  const getPositionClass = () => {
    return `feedback-widget-${position}`;
  };

  if (!visible) {
    return null;
  }

  return (
    <>
      {/* Floating Button */}
      <div className={`feedback-widget ${getPositionClass()}`}>
        <Button
          icon="pi pi-comment"
          rounded
          severity="info"
          aria-label="Send Feedback"
          onClick={handleOpenDialog}
          className="feedback-widget-button"
          tooltip="Send Feedback"
          tooltipOptions={{ position: 'left' }}
        >
          {unreadCount > 0 && (
            <Badge
              value={unreadCount}
              severity="danger"
              className="feedback-widget-badge"
            />
          )}
        </Button>
      </div>

      {/* Feedback Dialog */}
      <Dialog
        header="Send Feedback"
        visible={dialogVisible}
        style={{ width: '600px' }}
        onHide={handleCloseDialog}
        modal
        draggable={false}
        resizable={false}
      >
        <div className="feedback-dialog-content">
          <div className="feedback-dialog-intro">
            <p>
              Thank you for participating in our beta program! Your feedback
              helps us improve Solar Calculator Pro.
            </p>
            <p>
              Please share your thoughts, report bugs, or suggest new features.
            </p>
          </div>

          <FeedbackForm
            onSubmit={handleFeedbackSubmitted}
            onCancel={handleCloseDialog}
          />
        </div>
      </Dialog>
    </>
  );
};

export default FeedbackWidget;
