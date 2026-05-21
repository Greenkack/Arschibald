/**
 * Update Notification Dialog (Modern - shadcn/ui)
 * 
 * Displays when a new update is available with version info and release notes
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Info, Download, X, ArrowRight, Calendar, ExternalLink } from 'lucide-react';

interface UpdateInfo {
  version: string;
  releaseDate: string;
  releaseNotes?: string;
  releaseNotesUrl?: string;
  currentVersion: string;
  updateChannel?: string;
}

interface UpdateNotificationProps {
  visible: boolean;
  updateInfo: UpdateInfo | null;
  onDownload: () => void;
  onSkipVersion: () => void;
  onRemindLater: () => void;
  onClose: () => void;
}

export const UpdateNotificationModern: React.FC<UpdateNotificationProps> = ({
  visible,
  updateInfo,
  onDownload,
  onSkipVersion,
  onRemindLater,
  onClose
}) => {
  const [skipThisVersion, setSkipThisVersion] = useState(false);

  useEffect(() => {
    if (!visible) {
      setSkipThisVersion(false);
    }
  }, [visible]);

  if (!updateInfo) return null;

  const handleSkip = () => {
    if (skipThisVersion) {
      onSkipVersion();
    } else {
      onRemindLater();
    }
    onClose();
  };

  const handleDownload = () => {
    onDownload();
    onClose();
  };

  const getChannelVariant = (channel?: string): 'default' | 'destructive' | 'outline' | 'secondary' => {
    switch (channel) {
      case 'alpha':
        return 'destructive';
      case 'beta':
        return 'secondary';
      default:
        return 'default';
    }
  };

  return (
    <Dialog open={visible} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            Update Available
            {updateInfo.updateChannel && updateInfo.updateChannel !== 'latest' && (
              <Badge variant={getChannelVariant(updateInfo.updateChannel)}>
                {updateInfo.updateChannel.toUpperCase()}
              </Badge>
            )}
          </DialogTitle>
          <DialogDescription>
            A new version of the application is ready to download
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Version Comparison */}
          <div className="flex items-center justify-center gap-4 p-4 rounded-lg bg-muted/30">
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-1">Current Version</p>
              <p className="text-xl font-semibold">{updateInfo.currentVersion}</p>
            </div>
            <ArrowRight className="h-5 w-5 text-muted-foreground" />
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-1">New Version</p>
              <p className="text-xl font-semibold text-green-600 dark:text-green-400">
                {updateInfo.version}
              </p>
            </div>
          </div>

          {/* Release Date */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            Released: {new Date(updateInfo.releaseDate).toLocaleDateString()}
          </div>

          {/* Release Notes */}
          {updateInfo.releaseNotes && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold">What's New</h4>
              <ScrollArea className="h-[200px] w-full rounded-md border p-4">
                <div
                  className="prose prose-sm dark:prose-invert max-w-none"
                  dangerouslySetInnerHTML={{ __html: updateInfo.releaseNotes }}
                />
              </ScrollArea>
            </div>
          )}

          {/* Release Notes Link */}
          {updateInfo.releaseNotesUrl && (
            <Button
              variant="link"
              className="gap-2 px-0"
              onClick={() => window.open(updateInfo.releaseNotesUrl, '_blank')}
            >
              View Full Release Notes
              <ExternalLink className="h-4 w-4" />
            </Button>
          )}

          <Separator />

          {/* Info Message */}
          <div className="flex gap-2 p-3 rounded-lg bg-blue-50 dark:bg-blue-950/20 text-sm">
            <Info className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-blue-700 dark:text-blue-300">
              The update will be downloaded in the background. You can continue working
              and install it when ready.
            </p>
          </div>

          {/* Skip Version Checkbox */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id="skip-version"
              checked={skipThisVersion}
              onCheckedChange={(checked) => setSkipThisVersion(checked as boolean)}
            />
            <Label htmlFor="skip-version" className="cursor-pointer">
              Skip this version
            </Label>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="ghost"
            onClick={handleSkip}
            className="gap-2"
          >
            <X className="h-4 w-4" />
            {skipThisVersion ? 'Skip Version' : 'Remind Me Later'}
          </Button>
          <Button
            onClick={handleDownload}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            Download Update
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
