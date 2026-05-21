/**
 * Update Ready Dialog (Modern - shadcn/ui)
 * 
 * Displays when update is downloaded and ready to install
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
import { CheckCircle2, Clock, RotateCw, Info } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface UpdateReadyProps {
  visible: boolean;
  version: string;
  onInstallNow: () => void;
  onInstallLater: () => void;
}

export const UpdateReadyModern: React.FC<UpdateReadyProps> = ({
  visible,
  version,
  onInstallNow,
  onInstallLater
}) => {
  return (
    <Dialog open={visible} onOpenChange={onInstallLater}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            Update Ready to Install
          </DialogTitle>
          <DialogDescription>
            Version {version} has been downloaded successfully
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Success Icon */}
          <div className="flex justify-center py-4">
            <div className="h-20 w-20 rounded-full bg-green-100 dark:bg-green-950 flex items-center justify-center">
              <CheckCircle2 className="h-12 w-12 text-green-600 dark:text-green-400" />
            </div>
          </div>

          {/* Message */}
          <div className="text-center space-y-2">
            <h3 className="text-lg font-semibold">
              Version {version} is ready to install
            </h3>
            <p className="text-sm text-muted-foreground">
              The update has been downloaded successfully and is ready to be installed.
            </p>
          </div>

          {/* Options */}
          <div className="grid gap-3">
            <Card className="border-2 hover:border-primary transition-colors cursor-pointer">
              <CardContent className="flex gap-4 p-4">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded-lg bg-green-100 dark:bg-green-950 flex items-center justify-center">
                    <RotateCw className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-1">Restart and Install Now</h4>
                  <p className="text-sm text-muted-foreground">
                    The application will close, install the update, and restart automatically.
                    Make sure to save your work first.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-primary transition-colors cursor-pointer">
              <CardContent className="flex gap-4 p-4">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded-lg bg-blue-100 dark:bg-blue-950 flex items-center justify-center">
                    <Clock className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-1">Install on Quit</h4>
                  <p className="text-sm text-muted-foreground">
                    Continue working and the update will be installed automatically
                    when you close the application.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Info Message */}
          <div className="flex gap-2 p-3 rounded-lg bg-blue-50 dark:bg-blue-950/20 text-sm">
            <Info className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-blue-700 dark:text-blue-300">
              Your settings and data will be preserved during the update.
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={onInstallLater}
            className="gap-2"
          >
            <Clock className="h-4 w-4" />
            Install on Quit
          </Button>
          <Button
            onClick={onInstallNow}
            className="gap-2"
          >
            <RotateCw className="h-4 w-4" />
            Restart and Install
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
