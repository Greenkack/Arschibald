/**
 * Notification Center Component (Modern - shadcn/ui)
 * 
 * Displays in-app notifications with filtering, actions, and real-time updates.
 */

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Bell, 
  Check, 
  Settings, 
  X, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Calculator, 
  FileText, 
  Folder, 
  Info,
  Inbox
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Notification {
  id: number;
  type: string;
  priority: string;
  title: string;
  message: string;
  category?: string;
  action_url?: string;
  action_label?: string;
  icon?: string;
  is_read: boolean;
  created_at: string;
  actions?: NotificationAction[];
}

interface NotificationAction {
  id: number;
  action_type: string;
  label: string;
  url?: string;
  is_executed: boolean;
}

interface NotificationCenterProps {
  onNotificationClick?: (notification: Notification) => void;
}

export const NotificationCenterModern: React.FC<NotificationCenterProps> = ({
  onNotificationClick
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const categoryFilter: string | null = null;
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(() => {
      loadUnreadCount();
      if (isOpen) {
        loadNotifications();
      }
    }, 30000);
    
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter, categoryFilter, isOpen]);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: '50',
        unread_only: filter === 'unread' ? 'true' : 'false'
      });
      
      if (categoryFilter) {
        params.append('category', categoryFilter);
      }
      
      const response = await fetch(`/api/v1/notifications?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications);
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await fetch('/api/v1/notifications/unread-count', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Error loading unread count:', error);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      const response = await fetch(`/api/v1/notifications/${notificationId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ is_read: true })
      });
      
      if (response.ok) {
        loadNotifications();
        loadUnreadCount();
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const response = await fetch('/api/v1/notifications/mark-all-read', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        loadNotifications();
        loadUnreadCount();
      }
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const deleteNotification = async (notificationId: number) => {
    try {
      const response = await fetch(`/api/v1/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        loadNotifications();
        loadUnreadCount();
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      markAsRead(notification.id);
    }
    
    if (onNotificationClick) {
      onNotificationClick(notification);
    }
    
    if (notification.action_url) {
      window.location.href = notification.action_url;
    }
  };

  const getNotificationIcon = (notification: Notification) => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'calculation_complete':
        return <Calculator className="h-5 w-5 text-blue-600" />;
      case 'pdf_generated':
        return <FileText className="h-5 w-5 text-purple-600" />;
      case 'project_updated':
        return <Folder className="h-5 w-5 text-orange-600" />;
      default:
        return <Info className="h-5 w-5 text-blue-600" />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      
      <PopoverContent className="w-[400px] p-0" align="end">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold text-lg">Notifications</h3>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={markAllAsRead}
              disabled={unreadCount === 0}
              title="Mark all as read"
            >
              <Check className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => window.location.href = '/settings/notifications'}
              title="Notification settings"
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Filter */}
        <div className="p-4 border-b">
          <Select value={filter} onValueChange={(value: 'all' | 'unread') => setFilter(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Notifications</SelectItem>
              <SelectItem value="unread">Unread Only</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        {/* Notifications List */}
        <ScrollArea className="h-[400px]">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8">
              <Inbox className="h-12 w-12 mb-2" />
              <p className="text-sm">No notifications</p>
            </div>
          ) : (
            <div className="divide-y">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={cn(
                    'flex gap-3 p-4 cursor-pointer transition-colors hover:bg-muted/50',
                    !notification.is_read && 'bg-blue-50 dark:bg-blue-950/20'
                  )}
                  onClick={() => handleNotificationClick(notification)}
                >
                  {/* Icon */}
                  <div className="flex-shrink-0 mt-1">
                    {getNotificationIcon(notification)}
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <h4 className={cn(
                        'text-sm font-medium line-clamp-1',
                        !notification.is_read && 'font-semibold'
                      )}>
                        {notification.title}
                      </h4>
                      {!notification.is_read && (
                        <div className="h-2 w-2 rounded-full bg-blue-600 flex-shrink-0 mt-1" />
                      )}
                    </div>
                    
                    <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                      {notification.message}
                    </p>
                    
                    <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                      <span>{formatTimestamp(notification.created_at)}</span>
                      {notification.category && (
                        <>
                          <span>•</span>
                          <span className="capitalize">{notification.category}</span>
                        </>
                      )}
                    </div>
                    
                    {/* Actions */}
                    {notification.actions && notification.actions.length > 0 && (
                      <div className="flex gap-2 mt-3">
                        {notification.actions.map((action) => (
                          <Button
                            key={action.id}
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (action.url) {
                                window.location.href = action.url;
                              }
                            }}
                            disabled={action.is_executed}
                          >
                            {action.label}
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Delete Button */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="flex-shrink-0 h-8 w-8"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteNotification(notification.id);
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
        
        <Separator />
        
        {/* Footer */}
        <div className="p-3">
          <Button
            variant="ghost"
            className="w-full"
            onClick={() => window.location.href = '/notifications'}
          >
            View All
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
};
