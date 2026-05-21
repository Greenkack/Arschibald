/**
 * Modern 3D Visualization Page with shadcn/ui
 * 
 * Configure your solar installation and view it in 3D
 */

import React, { useState } from 'react';
import { Settings2, Zap, Box } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Viewer3D } from '../components/3d';

export const Visualization3DModern: React.FC = () => {
  const [roofType, setRoofType] = useState<'flat' | 'gable' | 'hip'>('gable');
  const [roofWidth, setRoofWidth] = useState(10);
  const [roofLength, setRoofLength] = useState(12);
  const [roofHeight, setRoofHeight] = useState(3);
  const [roofAngle, setRoofAngle] = useState(30);
  const [moduleCount, setModuleCount] = useState(24);

  const applyPreset = (preset: 'small' | 'medium' | 'large') => {
    switch (preset) {
      case 'small':
        setRoofType('flat');
        setRoofWidth(8);
        setRoofLength(10);
        setRoofAngle(0);
        setModuleCount(16);
        break;
      case 'medium':
        setRoofType('gable');
        setRoofWidth(12);
        setRoofLength(15);
        setRoofAngle(35);
        setModuleCount(36);
        break;
      case 'large':
        setRoofType('hip');
        setRoofWidth(15);
        setRoofLength(18);
        setRoofAngle(25);
        setModuleCount(48);
        break;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg">
              <Box className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">3D Solar Installation Visualization</h1>
              <p className="text-muted-foreground">
                Configure your solar installation and view it in 3D
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 lg:grid-cols-[400px_1fr]">
          {/* Configuration Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings2 className="h-5 w-5" />
                  Roof Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="roofType">Roof Type</Label>
                  <Select value={roofType} onValueChange={(value) => setRoofType(value as 'flat' | 'gable' | 'hip')}>
                    <SelectTrigger id="roofType">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="flat">Flat Roof</SelectItem>
                      <SelectItem value="gable">Gable Roof</SelectItem>
                      <SelectItem value="hip">Hip Roof</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="roofWidth">Width (m)</Label>
                    <Input
                      id="roofWidth"
                      type="number"
                      value={roofWidth}
                      onChange={(e) => setRoofWidth(parseFloat(e.target.value) || 10)}
                      min={5}
                      max={30}
                      step={0.5}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="roofLength">Length (m)</Label>
                    <Input
                      id="roofLength"
                      type="number"
                      value={roofLength}
                      onChange={(e) => setRoofLength(parseFloat(e.target.value) || 12)}
                      min={5}
                      max={30}
                      step={0.5}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="roofHeight">Building Height (m)</Label>
                  <Input
                    id="roofHeight"
                    type="number"
                    value={roofHeight}
                    onChange={(e) => setRoofHeight(parseFloat(e.target.value) || 3)}
                    min={2}
                    max={10}
                    step={0.5}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="roofAngle">Roof Angle: {roofAngle}°</Label>
                  <Slider
                    id="roofAngle"
                    value={[roofAngle]}
                    onValueChange={(value) => setRoofAngle(value[0])}
                    min={0}
                    max={60}
                    step={5}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Solar Modules
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="moduleCount">Number of Modules</Label>
                  <Input
                    id="moduleCount"
                    type="number"
                    value={moduleCount}
                    onChange={(e) => setModuleCount(parseInt(e.target.value) || 24)}
                    min={1}
                    max={100}
                    step={1}
                  />
                </div>

                <div className="rounded-lg bg-muted p-4 space-y-2">
                  <p className="font-semibold text-sm">Module Specifications</p>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• Size: 1.7m × 1.0m</li>
                    <li>• Power: 400W per module</li>
                    <li>• Total Power: <span className="font-bold text-foreground">{(moduleCount * 400 / 1000).toFixed(2)} kWp</span></li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Presets</CardTitle>
                <CardDescription>Apply common configurations</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-2">
                <Button variant="outline" onClick={() => applyPreset('small')}>
                  Small Flat Roof
                </Button>
                <Button variant="outline" onClick={() => applyPreset('medium')}>
                  Medium Gable Roof
                </Button>
                <Button variant="outline" onClick={() => applyPreset('large')}>
                  Large Hip Roof
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* 3D Viewer */}
          <Card className="overflow-hidden">
            <CardContent className="p-0">
              <div className="aspect-video bg-slate-100 dark:bg-slate-900">
                <Viewer3D
                  roofType={roofType}
                  roofWidth={roofWidth}
                  roofLength={roofLength}
                  roofHeight={roofHeight}
                  roofAngle={roofAngle}
                  moduleCount={moduleCount}
                />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
