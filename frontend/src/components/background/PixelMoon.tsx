/**
 * PixelMoon Component
 * Large pixel-art style pastel yellow moon
 * Central visual element for the landing page hero
 */

import React from 'react';

interface PixelMoonProps {
    size?: 'sm' | 'md' | 'lg' | 'xl';
    className?: string;
    animate?: boolean;
}

export const PixelMoon: React.FC<PixelMoonProps> = ({
    size = 'lg',
    className = '',
    animate = true,
}) => {
    const sizeMap = {
        sm: 80,
        md: 120,
        lg: 180,
        xl: 250,
    };

    const moonSize = sizeMap[size];

    return (
        <div
            className={`relative ${animate ? 'animate-[float_6s_ease-in-out_infinite]' : ''} ${className}`}
            style={{ width: moonSize, height: moonSize }}
        >
            {/* Moon base - circular pixel grid */}
            <svg
                viewBox="0 0 100 100"
                width={moonSize}
                height={moonSize}
                className="drop-shadow-[0_0_30px_rgba(245,230,163,0.4)]"
            >
                {/* Moon body */}
                <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="#F5E6A3"
                    className="drop-shadow-lg"
                />

                {/* Clean moon surface */}

                {/* Highlight for 3D pixel effect */}
                <ellipse
                    cx="40"
                    cy="40"
                    rx="30"
                    ry="25"
                    fill="url(#moonHighlight)"
                    opacity="0.3"
                />

                <defs>
                    <radialGradient id="moonHighlight" cx="30%" cy="30%">
                        <stop offset="0%" stopColor="#FFFAE0" />
                        <stop offset="100%" stopColor="#F5E6A3" stopOpacity="0" />
                    </radialGradient>
                </defs>
            </svg>

            {/* Glow effect */}
            <div
                className="absolute inset-0 rounded-full blur-xl opacity-30 -z-10"
                style={{
                    background: 'radial-gradient(circle, #F5E6A3 0%, transparent 70%)',
                    transform: 'scale(1.5)',
                }}
            />
        </div>
    );
};

export default PixelMoon;
