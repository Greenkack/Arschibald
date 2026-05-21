/**
 * Update Preferences Component (Modern - shadcn/ui)
 * 
 * Allows users to configure update settings
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { CheckCircle2, AlertCircle, RotateCw, Undo2, Info } from 'lucide-react';

interface UpdatePreferencesData {
  autoDownload: boolean;
  autoInstallOnAppQuit: boolean;
  checkOnStartup: boolean;
  checkInterval: number;
  updateChannel: string;
  skipVersion: string | null;
  notifyOnNoUpdate: boolean;
}

interface UpdatePreferencesProps {
  preferences: UpdatePreferencesData;
  currentVersion: string;
  onSave: (preferences: UpdatePreferencesData) => Promise<void>;
  onCheckNow: () => void;
  onClearSkipVersion: () => void;
}

export const UpdatePreferencesModern: React.FC<UpdatePreferencesProps> = ({
  preferences: initialPreferences,
  currentVersion,
  onSave,
  onCheckNow,
  onClearSkipVersion
}) => {
  const [preferences, setPreferences] = useState<UpdatePreferencesData>(initialPreferences);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setPreferences(initialPreferences);
  }, [initialPreferences]);

  useEffect(() => {
    const changed = JSON.stringify(preferences) !== JSON.stringify(initialPreferences);
    setHasChanges(changed);
    if (changed) {
      setSaved(false);
    }
  }, [preferences, initialPreferences]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(preferences);
      setSaved(true);
      setHasChanges(false);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setPreferences(initialPreferences);
  };

  const updateChannelOptions = [
    { value: 'latest', label: 'Stable (Recommended)', description: 'Production releases' },
    { value: 'beta', label: 'Beta', description: 'Pre-release versions' },
    { value: 'alpha', label: 'Alpha', description: 'Development builds' }
  ];

  const checkIntervalOptions = [
    { value: '900000', label: 'Every 15 minutes' },
    { value: '1800000', label: 'Every 30 minutes' },
    { value: '3600000', label: 'Every hour' },
    { value: '14400000', label: 'Every 4 hours' },
    { value: '43200000', label: 'Every 12 hours' },
    { value: '86400000', label: 'Once a day' }
  ];

  return (
    <Card className="max-w-3xl">
      <CardHeader>
        <CardTitle>Update Settings</CardTitle>
        <CardDescription>
          Configure how and when updates are downloaded and installed
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Auto Download */}
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="auto-download">Automatic Download</Label>
            <p className="text-sm text-muted-foreground">
              Automatically download updates when available
            </p>
          </div>
          <Switch
            id="auto-download"
            checked={preferences.autoDownload}
            onCheckedChange={(checked) => setPreferences({ ...preferences, autoDownload: checked })}
          />
        </div>

        <Separator />

        {/* Auto Install on Quit */}
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="auto-install">Install on Quit</Label>
            <p className="text-sm text-muted-foreground">
              Automatically install updates when closing the application
            </p>
          </div>
          <Switch
            id="auto-install"
            checked={preferences.autoInstallOnAppQuit}
            onCheckedChange={(checked) =>
              setPreferences({ ...preferences, autoInstallOnAppQuit: checked })
            }
          />
        </div>

        <Separator />

        {/* Check on Startup */}
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="check-startup">Check on Startup</Label>
            <p className="text-sm text-muted-foreground">
              Check for updates when the application starts
            </p>
          </div>
          <Switch
            id="check-startup"
            checked={preferences.checkOnStartup}
            onCheckedChange={(checked) => setPreferences({ ...preferences, checkOnStartup: checked })}
          />
        </div>

        <Separator />

        {/* Notify When No Update */}
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="notify-no-update">Notify When No Update</Label>
            <p className="text-sm text-muted-foreground">
              Show notification when no updates are available
            </p>
          </div>
          <Switch
            id="notify-no-update"
            checked={preferences.notifyOnNoUpdate}
            onCheckedChange={(checked) =>
              setPreferences({ ...preferences, notifyOnNoUpdate: checked })
            }
          />
        </div>

        <Separator />

        {/* Update Channel */}
        <div className="space-y-3">
          <Label htmlFor="update-channel">Update Channel</Label>
          <Select
            value={preferences.updateChannel}
            onValueChange={(value) => setPreferences({ ...preferences, updateChannel: value })}
          >
            <SelectTrigger id="update-channel">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {updateChannelOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div className="flex flex-col">
                    <span>{option.label}</span>
                    <span className="text-xs text-muted-foreground">{option.description}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-sm text-muted-foreground">
            Choose which type of updates you want to receive
          </p>
        </div>

        {/* Check Frequency */}
        <div className="space-y-3">
          <Label htmlFor="check-interval">Check Frequency</Label>
          <Select
            value={preferences.checkInterval.toString()}
            onValueChange={(value) => setPreferences({ ...preferences, checkInterval: parseInt(value) })}
          >
            <SelectTrigger id="check-interval">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {checkIntervalOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-sm text-muted-foreground">
            How often to check for new updates
          </p>
        </div>

        {/* Skipped Version */}
        {preferences.skipVersion && (
          <>
            <Separator />
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                You are skipping version {preferences.skipVersion}
              </AlertDescription>
            </Alert>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearSkipVersion}
              className="gap-2"
            >
              <AlertCircle className="h-4 w-4" />
              Clear Skipped Version
            </Button>
          </>
        )}

        <Separator />

        {/* Actions */}
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium">Current Version:</p>
            <p className="text-lg font-semibold">{currentVersion}</p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={onCheckNow}
              className="gap-2"
            >
              <RotateCw className="h-4 w-4" />
              Check for Updates
            </Button>
            {hasChanges && (
              <>
                <Button
                  variant="ghost"
                  onClick={handleReset}
                  className="gap-2"
                >
                  <Undo2 className="h-4 w-4" />
                  Reset
                </Button>
                <Button
                  onClick={handleSave}
                  disabled={saving}
                  className="gap-2"
                >
                  {saving ? (
                    <span className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <CheckCircle2 className="h-4 w-4" />
                  )}
                  Save Changes
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Success Message */}
        {saved && (
          <Alert className="border-green-500 bg-green-50 dark:bg-green-950">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-700 dark:text-green-300">
              Preferences saved successfully
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};
