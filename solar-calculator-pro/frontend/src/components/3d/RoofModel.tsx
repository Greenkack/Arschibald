import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Mesh, BoxGeometry, MeshStandardMaterial } from 'three';

interface RoofModelProps {
  roofType: 'flat' | 'gable' | 'hip';
  width: number;
  length: number;
  height: number;
  angle: number;
  color?: string;
}

export const RoofModel: React.FC<RoofModelProps> = ({
  roofType,
  width,
  length,
  height,
  angle,
  color = '#8B4513'
}) => {
  const meshRef = useRef<Mesh>(null);

  // Render different roof types
  const renderRoof = () => {
    switch (roofType) {
      case 'flat':
        return (
          <mesh ref={meshRef} position={[0, height / 2, 0]}>
            <boxGeometry args={[width, 0.2, length]} />
            <meshStandardMaterial color={color} />
          </mesh>
        );
      
      case 'gable':
        return (
          <group>
            {/* Base */}
            <mesh position={[0, height / 2, 0]}>
              <boxGeometry args={[width, height, length]} />
              <meshStandardMaterial color="#D3D3D3" />
            </mesh>
            {/* Roof planes */}
            <mesh 
              position={[0, height + 0.5, 0]} 
              rotation={[0, 0, (angle * Math.PI) / 180]}
            >
              <boxGeometry args={[width, 0.2, length / Math.cos((angle * Math.PI) / 180)]} />
              <meshStandardMaterial color={color} />
            </mesh>
            <mesh 
              position={[0, height + 0.5, 0]} 
              rotation={[0, 0, -(angle * Math.PI) / 180]}
            >
              <boxGeometry args={[width, 0.2, length / Math.cos((angle * Math.PI) / 180)]} />
              <meshStandardMaterial color={color} />
            </mesh>
          </group>
        );
      
      case 'hip':
        return (
          <group>
            {/* Base */}
            <mesh position={[0, height / 2, 0]}>
              <boxGeometry args={[width, height, length]} />
              <meshStandardMaterial color="#D3D3D3" />
            </mesh>
            {/* Hip roof - simplified as pyramid */}
            <mesh position={[0, height + 1, 0]}>
              <coneGeometry args={[Math.max(width, length) / 2, 2, 4]} />
              <meshStandardMaterial color={color} />
            </mesh>
          </group>
        );
      
      default:
        return null;
    }
  };

  return <>{renderRoof()}</>;
};
