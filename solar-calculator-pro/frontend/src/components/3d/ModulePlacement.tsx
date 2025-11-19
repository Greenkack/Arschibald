import React, { useState } from 'react';
import { SolarModule } from './SolarModule';

interface ModulePosition {
  id: string;
  position: [number, number, number];
  rotation: [number, number, number];
}

interface ModulePlacementProps {
  roofWidth: number;
  roofLength: number;
  roofHeight: number;
  roofAngle: number;
  moduleCount: number;
  moduleWidth?: number;
  moduleHeight?: number;
  spacing?: number;
}

export const ModulePlacement: React.FC<ModulePlacementProps> = ({
  roofWidth,
  roofLength,
  roofHeight,
  roofAngle,
  moduleCount,
  moduleWidth = 1.7,
  moduleHeight = 1.0,
  spacing = 0.05
}) => {
  const [selectedModule, setSelectedModule] = useState<string | null>(null);

  // Calculate optimal module placement
  const calculateModulePositions = (): ModulePosition[] => {
    const positions: ModulePosition[] = [];
    
    // Calculate how many modules fit in each direction
    const modulesPerRow = Math.floor(roofWidth / (moduleWidth + spacing));
    const modulesPerColumn = Math.floor(roofLength / (moduleHeight + spacing));
    const maxModules = Math.min(moduleCount, modulesPerRow * modulesPerColumn);
    
    // Calculate starting position to center the array
    const startX = -(modulesPerRow * (moduleWidth + spacing)) / 2 + moduleWidth / 2;
    const startZ = -(modulesPerColumn * (moduleHeight + spacing)) / 2 + moduleHeight / 2;
    
    let placedModules = 0;
    
    for (let row = 0; row < modulesPerColumn && placedModules < maxModules; row++) {
      for (let col = 0; col < modulesPerRow && placedModules < maxModules; col++) {
        const x = startX + col * (moduleWidth + spacing);
        const z = startZ + row * (moduleHeight + spacing);
        const y = roofHeight + 0.15; // Slightly above roof
        
        positions.push({
          id: `module-${placedModules}`,
          position: [x, y, z],
          rotation: [-(roofAngle * Math.PI) / 180, 0, 0] // Match roof angle
        });
        
        placedModules++;
      }
    }
    
    return positions;
  };

  const modulePositions = calculateModulePositions();

  return (
    <group>
      {modulePositions.map((module) => (
        <SolarModule
          key={module.id}
          position={module.position}
          rotation={module.rotation}
          width={moduleWidth}
          height={moduleHeight}
          selected={selectedModule === module.id}
          onClick={() => setSelectedModule(module.id)}
        />
      ))}
    </group>
  );
};
