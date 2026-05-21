import React, { useRef } from 'react';
import { Button } from 'primereact/button';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter';
import { STLExporter } from 'three/examples/jsm/exporters/STLExporter';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter';

interface ExportControlsProps {
  filename?: string;
}

export const ExportControls: React.FC<ExportControlsProps> = ({
  filename = 'solar-installation'
}) => {
  const { scene, gl } = useThree();

  const downloadFile = (data: string | ArrayBuffer, filename: string, mimeType: string) => {
    const blob = new Blob([data], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportGLTF = () => {
    const exporter = new GLTFExporter();
    exporter.parse(
      scene,
      (gltf) => {
        const output = JSON.stringify(gltf, null, 2);
        downloadFile(output, `${filename}.gltf`, 'application/json');
      },
      (error) => {
        console.error('Error exporting GLTF:', error);
      },
      { binary: false }
    );
  };

  const exportGLB = () => {
    const exporter = new GLTFExporter();
    exporter.parse(
      scene,
      (gltf) => {
        downloadFile(gltf as ArrayBuffer, `${filename}.glb`, 'application/octet-stream');
      },
      (error) => {
        console.error('Error exporting GLB:', error);
      },
      { binary: true }
    );
  };

  const exportSTL = () => {
    const exporter = new STLExporter();
    const result = exporter.parse(scene);
    downloadFile(result, `${filename}.stl`, 'application/octet-stream');
  };

  const exportOBJ = () => {
    const exporter = new OBJExporter();
    const result = exporter.parse(scene);
    downloadFile(result, `${filename}.obj`, 'text/plain');
  };

  const exportPNG = () => {
    gl.render(scene, gl.camera);
    gl.domElement.toBlob((blob) => {
      if (blob) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${filename}.png`;
        link.click();
        URL.revokeObjectURL(url);
      }
    });
  };

  return (
    <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '10px' }}>
      <Button
        label="Export GLTF"
        icon="pi pi-download"
        onClick={exportGLTF}
        className="p-button-sm"
        tooltip="Export as GLTF (text format)"
      />
      <Button
        label="Export GLB"
        icon="pi pi-download"
        onClick={exportGLB}
        className="p-button-sm"
        tooltip="Export as GLB (binary format)"
      />
      <Button
        label="Export STL"
        icon="pi pi-download"
        onClick={exportSTL}
        className="p-button-sm"
        tooltip="Export as STL (3D printing)"
      />
      <Button
        label="Export OBJ"
        icon="pi pi-download"
        onClick={exportOBJ}
        className="p-button-sm"
        tooltip="Export as OBJ (Wavefront)"
      />
      <Button
        label="Export PNG"
        icon="pi pi-image"
        onClick={exportPNG}
        className="p-button-sm p-button-secondary"
        tooltip="Export as PNG image"
      />
    </div>
  );
};
