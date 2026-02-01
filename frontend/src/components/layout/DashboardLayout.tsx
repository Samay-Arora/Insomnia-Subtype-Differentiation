/**
 * DashboardLayout Component
 * Main layout wrapper for authenticated pages
 * Combines Sidebar and Header with content area
 */

import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface DashboardLayoutProps {
    children: React.ReactNode;
    title?: string;
    userName?: string;
    onLogout?: () => void;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
    children,
    title,
    userName,
    onLogout,
}) => {
    return (
        <div className="min-h-screen bg-dream-purple-900 flex">
            {/* Sidebar */}
            <Sidebar onLogout={onLogout} />

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col">
                <Header title={title} userName={userName} />

                <main className="flex-1 p-6 overflow-auto">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default DashboardLayout;
