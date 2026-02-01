/**
 * PixelCard Component
 * Container with pixel-art borders for content sections
 * Provides the signature retro look for dashboard panels
 */

import React from 'react';

interface PixelCardProps {
    children: React.ReactNode;
    title?: string;
    className?: string;
    variant?: 'default' | 'highlight' | 'dark';
    noPadding?: boolean;
}

export const PixelCard: React.FC<PixelCardProps> = ({
    children,
    title,
    className = '',
    variant = 'default',
    noPadding = false,
}) => {
    const variantStyles = {
        default: `
      bg-dream-purple-800 border-dream-purple-500
      shadow-[inset_-4px_-4px_0px_0px_rgba(0,0,0,0.3),inset_4px_4px_0px_0px_rgba(255,255,255,0.05),6px_6px_0px_0px_rgba(0,0,0,0.4)]
    `,
        highlight: `
      bg-dream-purple-700 border-dream-yellow-500
      shadow-[inset_-4px_-4px_0px_0px_rgba(0,0,0,0.2),inset_4px_4px_0px_0px_rgba(255,255,255,0.1),6px_6px_0px_0px_rgba(0,0,0,0.4)]
    `,
        dark: `
      bg-dream-indigo-800 border-dream-purple-600
      shadow-[inset_-4px_-4px_0px_0px_rgba(0,0,0,0.4),inset_4px_4px_0px_0px_rgba(255,255,255,0.03),6px_6px_0px_0px_rgba(0,0,0,0.5)]
    `,
    };

    return (
        <div
            className={`
        border-4 border-solid
        ${variantStyles[variant]}
        ${className}
      `}
        >
            {title && (
                <div className="border-b-4 border-dream-purple-600 bg-dream-purple-900/50 px-4 py-3">
                    <h3 className="font-pixel text-[10px] text-dream-yellow-500 uppercase tracking-wider">
                        {title}
                    </h3>
                </div>
            )}
            <div className={noPadding ? '' : 'p-5'}>
                {children}
            </div>
        </div>
    );
};

export default PixelCard;
