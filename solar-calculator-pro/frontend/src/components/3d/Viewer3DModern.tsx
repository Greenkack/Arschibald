/**
 * Viewer3DModern Component
 * 
 * 3D Visualization component for solar panel configurations.
 * Migrated from PrimeReact to shadcn/ui.
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import { Slider } from '../ui/slider';
import { Label } from '../ui/label';
import { RotateCw, Grid3x3, Cloud } from 'lucide-react';
import { Scene3D } from './Scene3D';
import { ExportControls } from './ExportControls';
import { cn } from '@/lib/utils';

interface Viewer3DModernProps {
  roofType: 'flat' | 'gable' | 'hip';
  roofWidth: number;
  roofLength: number;
  roofHeight?: number;
  roofAngle: number;
  moduleCount: number;
  className?: string;
}

export const Viewer3DModern: React.FC<Viewer3DModernProps> = ({
  roofType,
  roofWidth,
  roofLength,
  roofHeight = 3,
  roofAngle,
  moduleCount,
  className
}) => {
  const [showGrid, setShowGrid] = useState(true);
  const [showSky, setShowSky] = useState(true);
  const [autoRotate, setAutoRotate] = useState(false);
  const [cameraDistance, setCameraDistance] = useState(15);

  const cameraPosition: [number, number, number] = [
    cameraDistance,
    cameraDistance * 0.7,
    cameraDistance
  ];

  const resetView = () => {
    setCameraDistance(15);
    setAutoRotate(false);
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>3D Visualisierung</span>
          <Button
            variant="outline"
            size="sm"
            onClick={resetView}
            className="gap-2"
          >
            <RotateCw className="h-4 w-4" />
            Ansicht zurücksetzen
          </Button>
        </CardTitle>
        <CardDescription>
          Interaktive 3D-Darstellung Ihrer Solaranlage
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Controls */}
        <div className="flex flex-wrap gap-6">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="grid"
              checked={showGrid}
              onCheckedChange={(checked) => setShowGrid(checked as boolean)}
            />
            <Label htmlFor="grid" className="flex items-center gap-2 cursor-pointer">
              <Grid3x3 className="h-4 w-4" />
              Raster anzeigen
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="sky"
              checked={showSky}
              onCheckedChange={(checked) => setShowSky(checked as boolean)}
            />
            <Label htmlFor="sky" className="flex items-center gap-2 cursor-pointer">
              <Cloud className="h-4 w-4" />
              Himmel anzeigen
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="rotate"
              checked={autoRotate}
              onCheckedChange={(checked) => setAutoRotate(checked as boolean)}
            />
            <Label htmlFor="rotate" className="flex items-center gap-2 cursor-pointer">
              <RotateCw className="h-4 w-4" />
              Auto-Rotation
            </Label>
          </div>
        </div>

        {/* Camera Distance Slider */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="camera-distance">Kamera-Distanz</Label>
            <span className="text-sm text-muted-foreground">{cameraDistance}m</span>
          </div>
          <Slider
            id="camera-distance"
            value={[cameraDistance]}
            onValueChange={(vals) => setCameraDistance(vals[0])}
            min={5}
            max={50}
            step={1}
            className="w-full"
          />
        </div>

        {/* 3D Scene */}
        <div className="rounded-lg border bg-muted/50 overflow-hidden">
          <Scene3D
            roofType={roofType}
            roofWidth={roofWidth}
            roofLength={roofLength}
            roofHeight={roofHeight}
            roofAngle={roofAngle}
            moduleCount={moduleCount}
            showGrid={showGrid}
            showSky={showSky}
            autoRotate={autoRotate}
            cameraPosition={cameraPosition}
          />
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-lg bg-muted/30">
          <div>
            <p className="text-sm font-medium text-muted-foreground">Dachtyp</p>
            <p className="text-lg font-semibold capitalize">{roofType}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Abmessungen</p>
            <p className="text-lg font-semibold">{roofWidth}m × {roofLength}m</p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Dachneigung</p>
            <p className="text-lg font-semibold">{roofAngle}°</p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Module</p>
            <p className="text-lg font-semibold">{moduleCount}</p>
          </div>
        </div>

        {/* Export Controls */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold">3D-Modell exportieren</h4>
          <ExportControls filename={`solar-${roofType}-${moduleCount}modules`} />
        </div>

        {/* Instructions */}
        <div className="rounded-lg border p-4 space-y-2">
          <h4 className="text-sm font-semibold">Steuerung:</h4>
          <ul className="text-sm space-y-1 text-muted-foreground">
            <li><strong>Drehen:</strong> Linke Maustaste + Ziehen</li>
            <li><strong>Zoom:</strong> Mausrad oder Pinch</li>
            <li><strong>Verschieben:</strong> Rechte Maustaste + Ziehen</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default Viewer3DModern;
