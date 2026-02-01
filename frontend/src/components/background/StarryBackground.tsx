/**
 * StarryBackground Component
 * Animated pixelated stars for atmospheric backgrounds
 * Creates a dreamy night sky effect with twinkling stars
 */

import React, { useMemo } from 'react';

interface Star {
    id: number;
    x: number;
    y: number;
    size: number;
    delay: number;
    duration: number;
}

interface StarryBackgroundProps {
    starCount?: number;
    className?: string;
}

export const StarryBackground: React.FC<StarryBackgroundProps> = ({
    starCount = 50,
    className = '',
}) => {
    const stars: Star[] = useMemo(() => {
        return Array.from({ length: starCount }, (_, i) => ({
            id: i,
            x: Math.random() * 100,
            y: Math.random() * 100,
            size: Math.random() > 0.8 ? 4 : Math.random() > 0.5 ? 3 : 2,
            delay: Math.random() * 3,
            duration: 1.5 + Math.random() * 2,
        }));
    }, [starCount]);

    return (
        <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
            {stars.map((star) => (
                <div
                    key={star.id}
                    className="absolute bg-pixel-white"
                    style={{
                        left: `${star.x}%`,
                        top: `${star.y}%`,
                        width: `${star.size}px`,
                        height: `${star.size}px`,
                        animation: `star-twinkle ${star.duration}s ease-in-out infinite`,
                        animationDelay: `${star.delay}s`,
                        boxShadow: star.size > 3
                            ? '0 0 4px 1px rgba(255, 254, 245, 0.5)'
                            : 'none',
                    }}
                />
            ))}
        </div>
    );
};

export default StarryBackground;
