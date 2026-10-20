"use client";

import React, { useEffect, useRef } from "react";
import { usePrefersReducedMotion } from "@/hooks/use-reduced-motion";

interface Particle {
  x: number;
  y: number;
  originX: number;
  originY: number;
  radius: number;
  color: string;
  angle: number;
  speed: number;
  orbitRadius: number;
  alpha: number;
}

export function ParticleFallback({ className = "" }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const prefersReducedMotion = usePrefersReducedMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || 800);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 600);

    const handleResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
    };

    window.addEventListener("resize", handleResize);

    // Generate Bloom Particles
    const colors = [
      "rgba(232, 184, 109, ",
      "rgba(255, 122, 89, ",
      "rgba(110, 200, 184, ",
      "rgba(251, 191, 36, ",
      "rgba(253, 186, 116, ",
    ];

    const particleCount = prefersReducedMotion ? 25 : 65;
    const particles: Particle[] = [];

    const centerX = width / 2;
    const centerY = height / 2;

    for (let i = 0; i < particleCount; i++) {
      const orbit = Math.random() * (Math.min(width, height) * 0.42);
      const angle = Math.random() * Math.PI * 2;
      particles.push({
        x: centerX + Math.cos(angle) * orbit,
        y: centerY + Math.sin(angle) * orbit,
        originX: centerX,
        originY: centerY,
        radius: Math.random() * 2.2 + 0.8,
        color: colors[Math.floor(Math.random() * colors.length)],
        angle,
        speed: (Math.random() * 0.003 + 0.001) * (Math.random() > 0.5 ? 1 : -1),
        orbitRadius: orbit,
        alpha: Math.random() * 0.7 + 0.3,
      });
    }

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Central core luminous glow
      const radial = ctx.createRadialGradient(
        width / 2,
        height / 2,
        10,
        width / 2,
        height / 2,
        Math.min(width, height) * 0.45
      );
      radial.addColorStop(0, "rgba(232, 184, 109, 0.2)");
      radial.addColorStop(0.3, "rgba(255, 122, 89, 0.08)");
      radial.addColorStop(1, "rgba(12, 10, 9, 0)");
      ctx.fillStyle = radial;
      ctx.fillRect(0, 0, width, height);

      // Draw and update bloom particles
      particles.forEach((p) => {
        if (!prefersReducedMotion) {
          p.angle += p.speed;
          p.x = p.originX + Math.cos(p.angle) * p.orbitRadius;
          p.y = p.originY + Math.sin(p.angle) * p.orbitRadius;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `${p.color}${p.alpha})`;
        ctx.shadowBlur = 12;
        ctx.shadowColor = p.color + "0.8)";
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      // Subtle interconnecting energy filaments between close particles
      if (!prefersReducedMotion) {
        ctx.lineWidth = 0.5;
        for (let i = 0; i < particles.length; i++) {
          for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 65) {
              ctx.strokeStyle = `rgba(232, 184, 109, ${0.14 * (1 - dist / 65)})`;
              ctx.beginPath();
              ctx.moveTo(particles[i].x, particles[i].y);
              ctx.lineTo(particles[j].x, particles[j].y);
              ctx.stroke();
            }
          }
        }
      }

      if (!prefersReducedMotion) {
        animationFrameId = requestAnimationFrame(render);
      }
    };

    render();

    return () => {
      window.removeEventListener("resize", handleResize);
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [prefersReducedMotion]);

  return (
    <canvas
      ref={canvasRef}
      className={`w-full h-full pointer-events-none ${className}`}
      aria-hidden="true"
    />
  );
}
