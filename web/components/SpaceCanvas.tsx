'use client';

import { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

function StarField() {
  const ref = useRef<THREE.Points>(null!);
  
  // Generate random 3D coordinates for stars
  const [sphere] = useState(() => {
    const p = new Float32Array(5000 * 3);
    for (let i = 0; i < 5000; i++) {
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      const r = 1.2 * Math.cbrt(Math.random());
      const sinTheta = Math.sin(theta);
      const cosTheta = Math.cos(theta);
      const sinPhi = Math.sin(phi);
      const cosPhi = Math.cos(phi);
      
      p[i * 3] = r * sinPhi * cosTheta * 5;     // x
      p[i * 3 + 1] = r * sinPhi * sinTheta * 5; // y
      p[i * 3 + 2] = r * cosPhi * 5;            // z
    }
    return p;
  });

  useFrame((state, delta) => {
    ref.current.rotation.x -= delta / 15;
    ref.current.rotation.y -= delta / 20;
  });

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <points ref={ref} frustumCulled={false}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[sphere, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          transparent
          color="#06b6d4"
          size={0.015}
          sizeAttenuation={true}
          depthWrite={false}
        />
      </points>
    </group>
  );
}

export default function SpaceCanvas() {
  return (
    <div className="fixed inset-0 pointer-events-none z-0">
      <Canvas camera={{ position: [0, 0, 1] }}>
        <StarField />
      </Canvas>
    </div>
  );
}