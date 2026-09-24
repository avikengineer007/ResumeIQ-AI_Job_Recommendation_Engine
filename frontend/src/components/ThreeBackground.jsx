import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function ThreeBackground() {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 80;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "low-power" });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    mount.appendChild(renderer.domElement);

    // Particle Constellation Geometry
    const particleCount = 75;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const velocities = [];

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 140;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 100;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 60;

      velocities.push({
        x: (Math.random() - 0.5) * 0.05,
        y: (Math.random() - 0.5) * 0.05,
        z: (Math.random() - 0.5) * 0.03,
      });
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    // Warm metallic gold particles
    const particleMaterial = new THREE.PointsMaterial({
      color: 0xd4af37,
      size: 1.8,
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending,
    });

    const particles = new THREE.Points(geometry, particleMaterial);
    scene.add(particles);

    // Connecting Lines Material
    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0xaa8830,
      transparent: true,
      opacity: 0.15,
      blending: THREE.AdditiveBlending,
    });

    const linesGeometry = new THREE.BufferGeometry();
    const linePositions = new Float32Array(particleCount * particleCount * 6);
    linesGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
    const linesMesh = new THREE.LineSegments(linesGeometry, lineMaterial);
    scene.add(linesMesh);

    // Mouse parallax tracking
    let mouseX = 0;
    let mouseY = 0;
    const handleMouseMove = (e) => {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 8;
      mouseY = (e.clientY / window.innerHeight - 0.5) * 8;
    };
    window.addEventListener('mousemove', handleMouseMove, { passive: true });

    // Animation Loop
    let animationFrameId;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      const pos = geometry.attributes.position.array;
      let lineVertexIndex = 0;

      // Update positions
      for (let i = 0; i < particleCount; i++) {
        pos[i * 3] += velocities[i].x;
        pos[i * 3 + 1] += velocities[i].y;
        pos[i * 3 + 2] += velocities[i].z;

        // Soft bounce boundaries
        if (Math.abs(pos[i * 3]) > 70) velocities[i].x *= -1;
        if (Math.abs(pos[i * 3 + 1]) > 50) velocities[i].y *= -1;
        if (Math.abs(pos[i * 3 + 2]) > 30) velocities[i].z *= -1;

        // Draw connections to nearby nodes
        for (let j = i + 1; j < particleCount; j++) {
          const dx = pos[i * 3] - pos[j * 3];
          const dy = pos[i * 3 + 1] - pos[j * 3 + 1];
          const dz = pos[i * 3 + 2] - pos[j * 3 + 2];
          const distSq = dx * dx + dy * dy + dz * dz;

          if (distSq < 550) {
            linePositions[lineVertexIndex++] = pos[i * 3];
            linePositions[lineVertexIndex++] = pos[i * 3 + 1];
            linePositions[lineVertexIndex++] = pos[i * 3 + 2];

            linePositions[lineVertexIndex++] = pos[j * 3];
            linePositions[lineVertexIndex++] = pos[j * 3 + 1];
            linePositions[lineVertexIndex++] = pos[j * 3 + 2];
          }
        }
      }

      geometry.attributes.position.needsUpdate = true;
      linesGeometry.setDrawRange(0, lineVertexIndex / 3);
      linesGeometry.attributes.position.needsUpdate = true;

      // Gentle camera parallax
      camera.position.x += (mouseX - camera.position.x) * 0.02;
      camera.position.y += (-mouseY - camera.position.y) * 0.02;
      camera.lookAt(scene.position);

      renderer.render(scene, camera);
    };

    animate();

    // Window Resize Handler
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      if (mount && renderer.domElement) {
        mount.removeChild(renderer.domElement);
      }
      geometry.dispose();
      particleMaterial.dispose();
      linesGeometry.dispose();
      lineMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="fixed inset-0 pointer-events-none z-0 overflow-hidden"
      style={{ opacity: 0.85 }}
    />
  );
}
