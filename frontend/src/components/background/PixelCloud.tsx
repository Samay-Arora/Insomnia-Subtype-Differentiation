/**
 * PixelCloud Component
 * Floating pixelated cloud decoration
 * Adds dreamy atmosphere to backgrounds
 */

import React from 'react';

interface PixelCloudProps {
    variant?: 'sm' | 'md' | 'lg';
    className?: string;
    opacity?: number;
}

export const PixelCloud: React.FC<PixelCloudProps> = ({
    variant = 'md',
    className = '',
    opacity = 0.15,
}) => {
    const sizes = {
        sm: { width: 60, height: 30 },
        md: { width: 100, height: 50 },
        lg: { width: 150, height: 75 },
    };

    const { width, height } = sizes[variant];

    return (
        <div
            className={`pointer-events-none ${className}`}
            style={{ width, height, opacity }}
        >
            <svg viewBox="0 0 100 50" width={width} height={height}>
                {/* Pixelated cloud shape using rectangles */}
                <g fill="#9a72b3">
                    {/* Bottom row */}
                    <rect x="10" y="35" width="10" height="10" />
                    <rect x="20" y="35" width="10" height="10" />
                    <rect x="30" y="35" width="10" height="10" />
                    <rect x="40" y="35" width="10" height="10" />
                    <rect x="50" y="35" width="10" height="10" />
                    <rect x="60" y="35" width="10" height="10" />
                    <rect x="70" y="35" width="10" height="10" />
                    <rect x="80" y="35" width="10" height="10" />

                    {/* Middle rows */}
                    <rect x="5" y="25" width="10" height="10" />
                    <rect x="15" y="25" width="10" height="10" />
                    <rect x="25" y="25" width="10" height="10" />
                    <rect x="35" y="25" width="10" height="10" />
                    <rect x="45" y="25" width="10" height="10" />
                    <rect x="55" y="25" width="10" height="10" />
                    <rect x="65" y="25" width="10" height="10" />
                    <rect x="75" y="25" width="10" height="10" />
                    <rect x="85" y="25" width="10" height="10" />

                    {/* Top bumps */}
                    <rect x="15" y="15" width="10" height="10" />
                    <rect x="25" y="15" width="10" height="10" />
                    <rect x="35" y="15" width="10" height="10" />
                    <rect x="55" y="15" width="10" height="10" />
                    <rect x="65" y="15" width="10" height="10" />
                    <rect x="75" y="15" width="10" height="10" />

                    <rect x="20" y="5" width="10" height="10" />
                    <rect x="30" y="5" width="10" height="10" />
                    <rect x="60" y="5" width="10" height="10" />
                    <rect x="70" y="5" width="10" height="10" />
                </g>
            </svg>
        </div>
    );
};

export default PixelCloud;
