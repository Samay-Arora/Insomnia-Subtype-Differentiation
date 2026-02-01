/**
 * Sidebar Component
 * Pixel-aesthetic navigation sidebar for the dashboard
 * Features retro styling with pixel borders and icons
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface SidebarProps {
    onLogout?: () => void;
}

interface NavItem {
    label: string;
    path: string;
    icon: string;
}

const navItems: NavItem[] = [
    { label: 'Dashboard', path: '/dashboard', icon: '🏠' },
    { label: 'Analysis', path: '/analysis', icon: '📊' },
];

export const Sidebar: React.FC<SidebarProps> = ({ onLogout }) => {
    const location = useLocation();

    return (
        <aside className="w-64 min-h-screen bg-dream-indigo-800 border-r-4 border-dream-purple-600 flex flex-col">
            {/* Logo Section */}
            <div className="p-4 border-b-4 border-dream-purple-600">
                <Link to="/dashboard" className="block">
                    <h1 className="font-pixel text-[10px] text-dream-yellow-500 leading-relaxed">
                        SLEEP<br />RESEARCH
                    </h1>
                    <p className="font-body text-xs text-dream-purple-300 mt-1">
                        Insomnia Phenotyping
                    </p>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-3">
                <ul className="space-y-2">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <li key={item.path}>
                                <Link
                                    to={item.path}
                                    className={`
                    flex items-center gap-3 px-4 py-3
                    font-pixel text-[8px] uppercase tracking-wider
                    border-4 transition-all duration-100
                    ${isActive
                                            ? 'bg-dream-purple-700 border-dream-yellow-500 text-dream-yellow-500 shadow-[inset_-3px_-3px_0px_0px_rgba(0,0,0,0.3),3px_3px_0px_0px_rgba(0,0,0,0.4)]'
                                            : 'bg-dream-purple-800 border-dream-purple-600 text-pixel-white hover:bg-dream-purple-700 hover:border-dream-purple-500'
                                        }
                  `}
                                >
                                    <span className="text-base">{item.icon}</span>
                                    <span>{item.label}</span>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* Logout Section */}
            <div className="p-3 border-t-4 border-dream-purple-600">
                <button
                    onClick={onLogout}
                    className="
            w-full flex items-center justify-center gap-2 px-4 py-3
            font-pixel text-[8px] uppercase tracking-wider
            bg-dream-purple-800 text-dream-purple-300
            border-4 border-dream-purple-600
            hover:bg-dream-purple-700 hover:text-pixel-white
            transition-all duration-100
          "
                >
                    <span>🚪</span>
                    <span>Logout</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
