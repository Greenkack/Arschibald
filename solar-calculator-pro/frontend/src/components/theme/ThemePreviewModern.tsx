/**
 * Theme Preview Component (Modern - shadcn/ui)
 * Shows a live preview of the current theme with sample UI elements
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2, Info, AlertTriangle, AlertCircle } from 'lucide-react';
import { useThemeStore } from '../../store/themeStore';

export const ThemePreviewModern: React.FC = () => {
  const { theme } = useThemeStore();

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-1">Live Preview</h3>
        <p className="text-sm text-muted-foreground">
          See how your theme looks with actual UI components
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Buttons Section */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Buttons</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Button variant="default">Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="destructive">Danger</Button>
            <Button variant="link">Link</Button>
          </CardContent>
        </Card>

        {/* Inputs Section */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Inputs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input placeholder="Text Input" />
            <Input placeholder="Disabled Input" disabled />
          </CardContent>
        </Card>

        {/* Messages Section */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Alerts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Alert className="border-green-500 bg-green-50 dark:bg-green-950">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700 dark:text-green-300">
                Success message - Operation completed successfully
              </AlertDescription>
            </Alert>

            <Alert className="border-blue-500 bg-blue-50 dark:bg-blue-950">
              <Info className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-700 dark:text-blue-300">
                Info message - Here's some useful information
              </AlertDescription>
            </Alert>

            <Alert className="border-yellow-500 bg-yellow-50 dark:bg-yellow-950">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <AlertDescription className="text-yellow-700 dark:text-yellow-300">
                Warning message - Please pay attention to this
              </AlertDescription>
            </Alert>

            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Error message - Something went wrong
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {/* Typography Section */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Typography</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <h1 className="text-4xl font-bold">Heading 1</h1>
            <h2 className="text-3xl font-semibold">Heading 2</h2>
            <h3 className="text-2xl font-medium">Heading 3</h3>
            <p className="text-base">
              This is a paragraph with normal text. It demonstrates how the theme's typography settings
              affect regular content.
            </p>
            <p className="text-base">
              <strong>Bold text</strong> and <em>italic text</em> are also styled according to the theme.
            </p>
          </CardContent>
        </Card>

        {/* Colors Section */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Color Palette</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="space-y-2">
                <div
                  className="h-16 rounded-lg border shadow-sm"
                  style={{ backgroundColor: theme.colors.primary }}
                />
                <p className="text-sm text-center font-medium">Primary</p>
              </div>
              <div className="space-y-2">
                <div
                  className="h-16 rounded-lg border shadow-sm"
                  style={{ backgroundColor: theme.colors.secondary }}
                />
                <p className="text-sm text-center font-medium">Secondary</p>
              </div>
              <div className="space-y-2">
                <div
                  className="h-16 rounded-lg border shadow-sm"
                  style={{ backgroundColor: theme.colors.accent }}
                />
                <p className="text-sm text-center font-medium">Accent</p>
              </div>
              <div className="space-y-2">
                <div
                  className="h-16 rounded-lg border shadow-sm"
                  style={{ backgroundColor: theme.colors.success }}
                />
                <p className="text-sm text-center font-medium">Success</p>
              </div>
              <div className="space-y-2">
                <div
                  className="h-16 rounded-lg border shadow-sm"
                  style={{ backgroundColor: theme.colors.warning }}
                />
                <p className="text-sm text-center font-medium">Warning</p>
              </div>
              <div className="space-y-2">
                <div
                  className="h-16 rounded-lg border shadow-sm"
                  style={{ backgroundColor: theme.colors.error }}
                />
                <p className="text-sm text-center font-medium">Error</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Surface Section */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Surfaces</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div
                className="h-24 rounded-lg border p-4 flex items-center justify-center"
                style={{ backgroundColor: theme.colors.background }}
              >
                <span style={{ color: theme.colors.text }} className="font-medium">
                  Background
                </span>
              </div>
              <div
                className="h-24 rounded-lg border p-4 flex items-center justify-center"
                style={{ backgroundColor: theme.colors.surface }}
              >
                <span style={{ color: theme.colors.text }} className="font-medium">
                  Surface
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
