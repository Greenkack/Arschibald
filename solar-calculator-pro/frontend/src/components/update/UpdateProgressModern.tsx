/**
 * Update Progress Dialog (Modern - shadcn/ui)
 * 
 * Shows download progress with percentage, speed, and size information
 */

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Download, X, Zap, Clock, Info } from 'lucide-react';

interface ProgressInfo {
  percent: number;
  bytesPerSecond: number;
  transferred: number;
  total: number;
}

interface UpdateProgressProps {
  visible: boolean;
  progress: ProgressInfo | null;
  version: string;
  onCancel: () => void;
}

export const UpdateProgressModern: React.FC<UpdateProgressProps> = ({
  visible,
  progress,
  version,
  onCancel
}) => {
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  const formatSpeed = (bytesPerSecond: number): string => {
    return `${formatBytes(bytesPerSecond)}/s`;
  };

  const formatTime = (seconds: number): string => {
    if (!isFinite(seconds) || seconds < 0) return 'Calculating...';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getEstimatedTime = (): string => {
    if (!progress || progress.bytesPerSecond === 0) {
      return 'Calculating...';
    }
    const remaining = progress.total - progress.transferred;
    const seconds = remaining / progress.bytesPerSecond;
    return formatTime(seconds);
  };

  return (
    <Dialog open={visible} onOpenChange={onCancel}>
      <DialogContent className="sm:max-w-[500px]" onInteractOutside={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Downloading Update
          </DialogTitle>
          <DialogDescription>
            Version: {version}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Progress Info */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-2xl font-bold">
                {progress ? `${Math.round(progress.percent)}%` : '0%'}
              </span>
              <span className="text-muted-foreground">
                {progress
                  ? `${formatBytes(progress.transferred)} / ${formatBytes(progress.total)}`
                  : 'Preparing...'}
              </span>
            </div>

            <Progress value={progress?.percent || 0} className="h-2" />
          </div>

          {/* Details */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
              <Zap className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-xs text-muted-foreground">Speed</p>
                <p className="text-sm font-semibold">
                  {progress ? formatSpeed(progress.bytesPerSecond) : 'N/A'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
              <Clock className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-xs text-muted-foreground">Time Remaining</p>
                <p className="text-sm font-semibold">{getEstimatedTime()}</p>
              </div>
            </div>
          </div>

          {/* Info Message */}
          <div className="flex gap-2 p-3 rounded-lg bg-blue-50 dark:bg-blue-950/20 text-sm">
            <Info className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-blue-700 dark:text-blue-300">
              You can continue working while the update downloads. The installation
              will begin when you close the application.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="destructive"
            onClick={onCancel}
            className="gap-2"
          >
            <X className="h-4 w-4" />
            Cancel Download
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
