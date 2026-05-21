import React from 'react';
import { Mesh } from 'three';

interface SolarModuleProps {
  position: [number, number, number];
  rotation?: [number, number, number];
  width?: number;
  height?: number;
  thickness?: number;
  color?: string;
  selected?: boolean;
  onClick?: () => void;
}

export const SolarModule: React.FC<SolarModuleProps> = ({
  position,
  rotation = [0, 0, 0],
  width = 1.7,
  height = 1.0,
  thickness = 0.04,
  color = '#1a1a2e',
  selected = false,
  onClick
}) => {
  return (
    <group position={position} rotation={rotation}>
      {/* Module frame */}
      <mesh onClick={onClick}>
        <boxGeometry args={[width, thickness, height]} />
        <meshStandardMaterial 
          color={selected ? '#FFD700' : color}
          metalness={0.5}
          roughness={0.3}
        />
      </mesh>
      
      {/* Solar cells grid */}
      <mesh position={[0, thickness / 2 + 0.001, 0]}>
        <planeGeometry args={[width * 0.95, height * 0.95]} />
        <meshStandardMaterial 
          color="#0f3460"
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>
      
      {/* Selection indicator */}
      {selected && (
        <mesh position={[0, thickness / 2 + 0.01, 0]}>
          <boxGeometry args={[width + 0.1, 0.01, height + 0.1]} />
          <meshBasicMaterial color="#FFD700" transparent opacity={0.3} />
        </mesh>
      )}
    </group>
  );
};
