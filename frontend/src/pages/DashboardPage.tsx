import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '../components/layout';
import { PixelCard } from '../components/ui';
import { upload } from '../services/api';

export const DashboardPage = ({ onLogout }: { onLogout?: () => void }) => {
    const navigate = useNavigate();
    const [dragging, setDragging] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [progress, setProgress] = useState(0);

    const onDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setDragging(true);
    }, []);

    const onLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setDragging(false);
    }, []);

    const processFile = async (f: File) => {
        try {
            setProgress(10);
            const res = await upload(f);
            setProgress(90);

            if (res.success && res.sessionId) {
                setProgress(100);
                setTimeout(() => navigate(`/analysis/${res.sessionId}`), 500);
            } else {
                alert(`Error: ${res.error}`);
                setProgress(0);
                setFile(null);
            }
        } catch (err) {
            console.error(err);
            alert('Upload failed');
            setProgress(0);
            setFile(null);
        }
    };

    const onSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0];
        if (selected) {
            setFile(selected);
            processFile(selected);
        }
    };

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setDragging(false);
        const dropped = e.dataTransfer.files[0];
        if (dropped?.name.toLowerCase().endsWith('.edf')) {
            setFile(dropped);
            processFile(dropped);
        } else {
            alert('EDF file required');
        }
    }, [navigate]);

    return (
        <DashboardLayout title="The Guild" userName="Wanderer" onLogout={onLogout}>
            <div className="max-w-4xl mx-auto">
                <div className="mb-8">
                    <h1 className="font-pixel text-lg text-pixel-white mb-2 flex items-center gap-3">
                        <span className="text-dream-yellow-500">⚔️</span> THE GUILD HALL
                    </h1>
                    <p className="font-body text-dream-purple-300 mb-4">Present your Sleep Scrolls (.EDF) to the Alchemists for decoding.</p>
                    
                    <div className="bg-dream-indigo-800/50 border border-dream-purple-500 p-4 mb-4">
                        <p className="font-body text-sm text-dream-purple-200">
                            <strong>The Council's Warning:</strong> This magical artifact is a research demonstration tool built on ancient lore (a 53-patient dataset). The prophecies should not be interpreted as actual clinical diagnoses. A sample scroll is provided for new adventurers.
                        </p>
                    </div>

                    <p className="font-body text-sm text-dream-purple-300">
                        Lack a scroll? <a href="/test_file.edf" download className="text-dream-yellow-500 hover:text-dream-yellow-400 underline">Claim a demonstration scroll</a>
                    </p>
                </div>

                <PixelCard title="THE ANVIL OF DREAMS" variant="highlight">
                    <div
                        onDragOver={onDrag}
                        onDragLeave={onLeave}
                        onDrop={onDrop}
                        className={`relative min-h-[300px] border-4 border-dashed flex flex-col items-center justify-center transition-all cursor-pointer ${dragging ? 'border-dream-yellow-500 bg-dream-purple-700/50' : 'border-dream-purple-500 bg-dream-indigo-800/50'
                            }`}
                    >
                        {!file ? (
                            <>
                                <div className="text-dream-purple-500 mb-6 font-pixel">
                                    <pre className="text-left text-[10px] leading-tight">
{`   .---.
  /   /|
 /---/ |
 |   | '
 |   |/
 '---'`}
                                    </pre>
                                </div>
                                <p className="font-pixel text-[10px] text-dream-yellow-500 mb-2">PLACE SCROLL HERE (.EDF)</p>
                                <input type="file" accept=".edf" onChange={onSelect} className="absolute inset-0 opacity-0 cursor-pointer" />
                            </>
                        ) : (
                            <div className="text-center">
                                <div className="w-16 h-16 bg-dream-yellow-500/20 border-4 border-dream-yellow-500 flex items-center justify-center mx-auto mb-4">
                                    <span className="text-3xl text-yellow-500">✨</span>
                                </div>
                                <p className="font-pixel text-[10px] text-dream-yellow-500 mb-2">SCROLL ACCEPTED</p>
                                <p className="font-body text-sm text-pixel-white mb-4">{file.name}</p>
                                <div className="w-64 mx-auto">
                                    <div className="h-4 bg-dream-indigo-800 border-4 border-dream-purple-600">
                                        <div className="h-full bg-dream-yellow-500 transition-all duration-300" style={{ width: `${progress}%` }} />
                                    </div>
                                    <p className="font-pixel text-[8px] text-dream-purple-400 mt-2">
                                        {progress < 100 ? `CASTING ALGORITHMS... ${progress}%` : 'MAGIC COMPLETE'}
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </PixelCard>
            </div>
        </DashboardLayout>
    );
};

export default DashboardPage;
