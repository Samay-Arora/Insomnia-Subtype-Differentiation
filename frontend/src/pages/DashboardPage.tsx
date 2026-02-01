/**
 * DashboardPage Component
 * Main dashboard with file upload portal
 * Features drag-and-drop zone styled as pixelated inventory slot
 */

import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '../components/layout';
import { PixelCard } from '../components/ui';

interface DashboardPageProps {
    onLogout?: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onLogout }) => {
    const navigate = useNavigate();
    const [isDragging, setIsDragging] = useState(false);
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [uploadProgress, setUploadProgress] = useState(0);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleUpload = async (file: File) => {
        try {
            // Reset Progress
            setUploadProgress(10);

            // Import API call
            const { uploadEEG } = await import('../services/api');
            setUploadProgress(30);

            // Perform Upload
            console.log('🚀 Starting upload and analysis (this may take ~30s)...');
            const response = await uploadEEG(file);
            setUploadProgress(90);

            if (response.success && response.sessionId) {
                setUploadProgress(100);
                setTimeout(() => {
                    navigate(`/analysis/${response.sessionId}`);
                }, 500);
            } else {
                alert(`Upload failed: ${response.error}`);
                setUploadProgress(0);
                setUploadedFile(null);
            }
        } catch (error) {
            console.error(error);
            alert('An unexpected error occurred during upload.');
            setUploadProgress(0);
            setUploadedFile(null);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            const file = files[0];
            setUploadedFile(file);
            handleUpload(file);
        }
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.name.toLowerCase().endsWith('.edf')) {
                setUploadedFile(file);
                handleUpload(file);
            } else {
                alert('Please upload an .EDF file');
            }
        }
    }, [navigate]);

    return (
        <DashboardLayout title="Upload Portal" userName="Traveler" onLogout={onLogout}>
            <div className="max-w-4xl mx-auto">
                {/* Welcome Message */}
                <div className="mb-8">
                    <h1 className="font-pixel text-lg text-pixel-white mb-2">
                        WELCOME, TRAVELER
                    </h1>
                    <p className="font-body text-dream-purple-300">
                        Upload your EEG recording to begin the sleep analysis journey.
                    </p>
                </div>

                {/* Upload Portal */}
                <PixelCard title="⬆ EEG DATA PORTAL" variant="highlight">
                    <div
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        className={`
              relative min-h-[300px] 
              border-4 border-dashed
              flex flex-col items-center justify-center
              transition-all duration-200 cursor-pointer
              ${isDragging
                                ? 'border-dream-yellow-500 bg-dream-purple-700/50 scale-[1.02]'
                                : 'border-dream-purple-500 bg-dream-indigo-800/50 hover:border-dream-purple-400'
                            }
            `}
                    >
                        {/* Portal Animation */}
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <div className={`
                w-32 h-32 rounded-full border-4 border-dream-purple-500
                ${isDragging ? 'animate-ping opacity-50' : 'opacity-20'}
              `} />
                        </div>

                        {!uploadedFile ? (
                            <>
                                {/* Upload Icon - Pixel Style */}
                                <div className="relative z-10 mb-6">
                                    <div className="w-20 h-20 bg-dream-purple-700 border-4 border-dream-purple-500 flex items-center justify-center">
                                        <span className="text-4xl">📁</span>
                                    </div>
                                </div>

                                <p className="font-pixel text-[10px] text-dream-yellow-500 text-center mb-2 relative z-10">
                                    DROP .EDF FILE HERE
                                </p>
                                <p className="font-body text-sm text-dream-purple-400 text-center mb-6 relative z-10">
                                    or click to select from your computer
                                </p>

                                <input
                                    type="file"
                                    accept=".edf,.EDF"
                                    onChange={handleFileSelect}
                                    className="absolute inset-0 opacity-0 cursor-pointer"
                                />

                                {/* File type hint */}
                                <div className="flex gap-2 relative z-10">
                                    <span className="px-3 py-1 bg-dream-purple-700 border-2 border-dream-purple-500 font-pixel text-[8px] text-dream-purple-300">
                                        .EDF
                                    </span>
                                </div>
                            </>
                        ) : (
                            <>
                                {/* Uploaded File Display */}
                                <div className="relative z-10 text-center">
                                    <div className="w-16 h-16 bg-dream-yellow-500/20 border-4 border-dream-yellow-500 flex items-center justify-center mx-auto mb-4">
                                        <span className="text-3xl">✨</span>
                                    </div>

                                    <p className="font-pixel text-[10px] text-dream-yellow-500 mb-2">
                                        FILE RECEIVED
                                    </p>
                                    <p className="font-body text-sm text-pixel-white mb-4">
                                        {uploadedFile.name}
                                    </p>

                                    {/* Progress Bar */}
                                    <div className="w-64 mx-auto mb-6">
                                        <div className="h-4 bg-dream-indigo-800 border-4 border-dream-purple-600">
                                            <div
                                                className="h-full bg-dream-yellow-500 transition-all duration-200"
                                                style={{ width: `${uploadProgress}%` }}
                                            />
                                        </div>
                                        <p className="font-pixel text-[8px] text-dream-purple-400 mt-2">
                                            {uploadProgress < 30 ? `UPLOADING... ${uploadProgress}%` :
                                                uploadProgress < 100 ? `ANALYZING DREAMSCAPE... ${uploadProgress}%` :
                                                    'READY FOR ANALYSIS'}
                                        </p>
                                    </div>

                                    {uploadProgress >= 100 && (
                                        <div className="text-center font-pixel text-[8px] text-dream-yellow-500 animate-pulse">
                                            REDIRECTING TO DREAMSCAPE...
                                        </div>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                </PixelCard>
            </div>
        </DashboardLayout>
    );
};

export default DashboardPage;
