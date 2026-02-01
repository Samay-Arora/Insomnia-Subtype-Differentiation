/**
 * Header Component
 * Top navigation bar for the dashboard with pixel aesthetic
 * Shows current page title and user info
 */

import React from 'react';

interface HeaderProps {
    title?: string;
    userName?: string;
}

export const Header: React.FC<HeaderProps> = ({
    title = 'Dashboard',
    userName = 'Traveler',
}) => {
    return (
        <header className="h-16 bg-dream-purple-800 border-b-4 border-dream-purple-600 flex items-center justify-between px-6">
            {/* Page Title */}
            <div className="flex items-center gap-4">
                <h2 className="font-pixel text-[12px] text-pixel-white uppercase tracking-wider">
                    {title}
                </h2>
                <div className="flex gap-1">
                    {[...Array(3)].map((_, i) => (
                        <div
                            key={i}
                            className="w-2 h-2 bg-dream-yellow-500 animate-pulse"
                            style={{ animationDelay: `${i * 0.2}s` }}
                        />
                    ))}
                </div>
            </div>

            {/* User Info */}
            <div className="flex items-center gap-4">
                <div className="text-right">
                    <p className="font-pixel text-[7px] text-dream-purple-300 uppercase">
                        Logged in as
                    </p>
                    <p className="font-body text-sm text-dream-yellow-500">
                        {userName}
                    </p>
                </div>

                {/* Avatar Placeholder - Pixel Style */}
                <div className="w-10 h-10 bg-dream-purple-600 border-4 border-dream-purple-400 flex items-center justify-center">
                    <span className="font-pixel text-[8px] text-pixel-white">
                        {userName.charAt(0).toUpperCase()}
                    </span>
                </div>
            </div>
        </header>
    );
};

export default Header;
