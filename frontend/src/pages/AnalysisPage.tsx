/**
 * AnalysisPage Component
 * Dashboard for displaying sleep analysis charts
 * Uses Recharts with retro pixel styling and pastel palette
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    AreaChart, Area, ScatterChart, Scatter,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    Legend, BarChart, Bar,
} from 'recharts';
import { DashboardLayout } from '../components/layout';
import { PixelCard } from '../components/ui';
import { getAnalysis } from '../services/api';
import type { AnalysisData } from '../types';


const TooltipUI = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="bg-dream-indigo-800 border-4 border-dream-purple-500 p-3 shadow-lg">
            <p className="font-pixel text-[8px] text-dream-yellow-500 mb-1">{label}</p>
            {payload.map((entry: any, i: number) => (
                <p key={i} className="font-body text-xs" style={{ color: entry.color }}>
                    {entry.name}: {entry.value}
                </p>
            ))}
        </div>
    );
};

const AxisTick = ({ x, y, payload }: any) => (
    <g transform={`translate(${x},${y})`}>
        <text x={0} y={0} dy={16} textAnchor="middle" fill="#9a72b3" className="font-body text-[10px]">
            {payload.value}
        </text>
    </g>
);

const Loader = () => (
    <div className="flex items-center justify-center h-64">
        <div className="text-center">
            <div className="w-16 h-16 border-4 border-dream-purple-500 border-t-dream-yellow-500 rounded-full animate-spin mx-auto mb-4" />
            <p className="font-pixel text-dream-purple-300">LOADING...</p>
        </div>
    </div>
);

// --- Main Component ---

export const AnalysisPage = ({ onLogout }: { onLogout?: () => void }) => {
    const { sessionId: id } = useParams<{ sessionId: string }>();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<AnalysisData | null>(null);

    // Static background clusters for visualization context
    // In a real app, these might come from the backend relative to the patient
    const bgPoints = [
        { x: 2.5, y: 4.0, cluster: 1, id: 'Type A', isPatient: false },
        { x: 5.3, y: 2.2, cluster: 2, id: 'Type B', isPatient: false },
        { x: 7.8, y: 6.0, cluster: 3, id: 'Type C', isPatient: false },
        // Add some noise around them
        { x: 2.3, y: 4.1, cluster: 1, isPatient: false }, { x: 2.8, y: 3.9, cluster: 1, isPatient: false },
        { x: 5.5, y: 2.4, cluster: 2, isPatient: false }, { x: 5.1, y: 1.8, cluster: 2, isPatient: false },
        { x: 8.1, y: 5.9, cluster: 3, isPatient: false }, { x: 7.5, y: 6.5, cluster: 3, isPatient: false },
    ];

    useEffect(() => {
        if (!id) {
            navigate('/dashboard');
            return;
        }

        getAnalysis(id)
            .then(res => {
                setData(res);
                setLoading(false);
            })
            .catch(err => {
                console.error("fetch err:", err);
                navigate('/dashboard');
            });
    }, [id, navigate]);

    if (loading || !data) {
        return (
            <DashboardLayout title="The Alchemist's Tower" userName="Wanderer" onLogout={onLogout}>
                <Loader />
            </DashboardLayout>
        );
    }

    // Process Data for Charts - Defensive Checks
    const stages = data.sleepStages || [];
    const spectralAnalysis = data.spectralAnalysis || [];
    const clusterAssignment = data.clusterAssignment || { x: 0, y: 0, cluster: 0 };
    const summary = data.summary || { totalSleepTime: 0, sleepEfficiency: 0, remLatency: 0 };
    const phenotype = data.phenotype || { type: 'Unknown', confidence: 0, characteristics: [] };

    // Calculate Stage Distribution from stages array
    const counts = stages.reduce((acc, curr) => {
        const l = curr.label || 'Unknown';
        acc[l] = (acc[l] || 0) + 1;
        return acc;
    }, {} as Record<string, number>);

    const total = stages.length || 1;
    const metrics = [
        { name: 'Wake', value: Math.round(((counts['Wake'] || 0) / total) * 100), fill: '#4a3070' },
        { name: 'N1', value: Math.round(((counts['N1'] || 0) / total) * 100), fill: '#7a5299' },
        { name: 'N2', value: Math.round(((counts['N2'] || 0) / total) * 100), fill: '#9a72b3' },
        { name: 'N3', value: Math.round(((counts['N3'] || 0) / total) * 100), fill: '#5c3d87' },
        { name: 'REM', value: Math.round(((counts['REM'] || 0) / total) * 100), fill: '#f5e6a3' },
    ].filter(s => s.value > 0);


    const userPoint = {
        x: clusterAssignment?.x || 0,
        y: clusterAssignment?.y || 0,
        cluster: clusterAssignment?.cluster || 0,
        id: 'YOU',
        isPatient: true
    };

    const points = [...bgPoints, userPoint];

    const spectral = spectralAnalysis.map(d => ({
        name: d.frequency === 1 ? 'Delta' :
            d.frequency === 6 ? 'Theta' :
                d.frequency === 10 ? 'Alpha' :
                    d.frequency === 20 ? 'Beta' :
                        d.frequency === 35 ? 'Gamma' : `${d.frequency}Hz`,
        power: d.power || 0,
        fill: '#9a72b3'
    }));



    const format = (m: number) => `${Math.floor(m / 60)}h ${m % 60}m`;

    const typeLabel = phenotype.type ? phenotype.type.split(':')[0] : 'Unknown';

    return (
        <DashboardLayout title="Quest Results" userName="Wanderer" onLogout={onLogout}>
            <div className="space-y-6">
                {/* Header Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <PixelCard>
                        <div className="text-center">
                            <p className="font-pixel text-[8px] text-dream-purple-400 mb-1">TOTAL SLEEP</p>
                            <p className="font-pixel text-xl text-dream-yellow-500">
                                {format(summary.totalSleepTime)}
                            </p>
                        </div>
                    </PixelCard>
                    <PixelCard>
                        <div className="text-center">
                            <p className="font-pixel text-[8px] text-dream-purple-400 mb-1">EFFICIENCY</p>
                            <p className="font-pixel text-xl text-dream-yellow-500">
                                {summary.sleepEfficiency}%
                            </p>
                        </div>
                    </PixelCard>
                    <PixelCard>
                        <div className="text-center">
                            <p className="font-pixel text-[8px] text-dream-purple-400 mb-1">REM LATENCY</p>
                            <p className="font-pixel text-xl text-dream-yellow-500">
                                {summary.remLatency}m
                            </p>
                        </div>
                    </PixelCard>
                    <PixelCard variant="highlight">
                        <div className="text-center">
                            <p className="font-pixel text-[8px] text-dream-purple-400 mb-1">YOUR LINEAGE</p>
                            <p className="font-pixel text-lg text-dream-yellow-500">
                                {typeLabel}
                            </p>
                        </div>
                    </PixelCard>
                </div>

                {/* Hypnogram - Sleep Stage Chart */}
                <PixelCard title="THE HYPNOGRAM SCROLL">
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={stages}>
                                <defs>
                                    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#f5e6a3" stopOpacity={0.4} />
                                        <stop offset="95%" stopColor="#5c3d87" stopOpacity={0.1} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="4 4" stroke="#3d2660" strokeWidth={2} />
                                <XAxis
                                    dataKey="time"
                                    tick={<AxisTick />}
                                    axisLine={{ stroke: '#5c3d87', strokeWidth: 3 }}
                                />
                                <YAxis
                                    domain={[0, 4]}
                                    ticks={[0, 1, 2, 3, 4]}
                                    tickFormatter={(value) => ['Wake', 'N1', 'N2', 'N3', 'REM'][value] || ''}
                                    tick={{ fill: '#9a72b3', fontSize: 10 }}
                                    axisLine={{ stroke: '#5c3d87', strokeWidth: 3 }}
                                />
                                <Tooltip content={<TooltipUI />} />
                                <Area
                                    type="stepAfter"
                                    dataKey="stage"
                                    stroke="#f5e6a3"
                                    strokeWidth={4}
                                    fill="url(#g)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </PixelCard>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Spectral Power */}
                    <PixelCard title="MAGICAL RESONANCE (SPECTRAL)">
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={spectral}>
                                    <CartesianGrid strokeDasharray="4 4" stroke="#3d2660" strokeWidth={2} />
                                    <XAxis
                                        dataKey="name"
                                        tick={{ fill: '#9a72b3', fontSize: 10 }}
                                    />
                                    <YAxis
                                        tick={{ fill: '#9a72b3', fontSize: 10 }}
                                    />
                                    <Tooltip content={<TooltipUI />} />
                                    <Bar dataKey="power" fill="#9a72b3" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </PixelCard>

                    {/* Sleep Stage Distribution */}
                    <PixelCard title="REALM DISTRIBUTION">
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={metrics} layout="vertical">
                                    <CartesianGrid strokeDasharray="4 4" stroke="#3d2660" strokeWidth={2} horizontal={false} />
                                    <XAxis type="number" tick={{ fill: '#9a72b3', fontSize: 10 }} unit="%" />
                                    <YAxis type="category" dataKey="name" tick={{ fill: '#9a72b3', fontSize: 10 }} width={50} />
                                    <Tooltip content={<TooltipUI />} />
                                    <Bar dataKey="value" radius={[0, 4, 4, 0]} fill="#7a5299">
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </PixelCard>
                </div>

                {/* Cluster Visualization */}
                <PixelCard title="THE GUILD MAP">
                    <div className="h-96">
                        <ResponsiveContainer width="100%" height="100%">
                            <ScatterChart margin={{ top: 20, right: 30, bottom: 40, left: 20 }}>
                                <CartesianGrid strokeDasharray="4 4" stroke="#3d2660" strokeWidth={2} />
                                <XAxis
                                    type="number"
                                    dataKey="x"
                                    name="PC1"
                                    tick={{ fill: '#9a72b3', fontSize: 10 }}
                                    axisLine={{ stroke: '#5c3d87', strokeWidth: 3 }}
                                    domain={[-5, 10]}
                                />
                                <YAxis
                                    type="number"
                                    dataKey="y"
                                    name="PC2"
                                    tick={{ fill: '#9a72b3', fontSize: 10 }}
                                    axisLine={{ stroke: '#5c3d87', strokeWidth: 3 }}
                                    domain={[-5, 10]}
                                />
                                <Tooltip content={<TooltipUI />} cursor={{ strokeDasharray: '3 3' }} />
                                <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: 10 }} />

                                {/* Background Clusters */}
                                <Scatter
                                    name="Known Factions"
                                    data={points.filter(d => !d.isPatient)}
                                    fill="#7a5299"
                                    shape="circle"
                                />

                                {/* Current Patient */}
                                <Scatter
                                    name="You"
                                    data={points.filter(d => d.isPatient)}
                                    fill="#f5e6a3"
                                    shape="star"
                                    r={40} // Make it big
                                />
                            </ScatterChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Legend text */}
                    <div className="mt-4 flex justify-center">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-dream-purple-700 border-4 border-dream-yellow-500 animate-pulse">
                            <div className="w-3 h-3 bg-dream-yellow-500" />
                            <span className="font-pixel text-[8px] text-dream-yellow-500">
                                WANDERER LOCATION: {phenotype.type}
                            </span>
                        </div>
                    </div>
                </PixelCard>

                {/* Analysis Summary */}
                <PixelCard title="THE ALCHEMIST'S LOG" variant="highlight">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h4 className="font-pixel text-[10px] text-dream-yellow-500 mb-3">
                                QUEST DISCOVERIES
                            </h4>
                            <ul className="space-y-2">
                                <li className="flex items-start gap-2">
                                    <span className="text-dream-yellow-500">▸</span>
                                    <span className="font-body text-sm text-pixel-white">
                                        Type: {phenotype.type}
                                    </span>
                                </li>
                                {phenotype.characteristics.map((char, i) => (
                                    <li key={i} className="flex items-start gap-2">
                                        <span className="text-dream-yellow-500">▸</span>
                                        <span className="font-body text-sm text-pixel-white">
                                            {char}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-pixel text-[10px] text-dream-yellow-500 mb-3">
                                METRICS
                            </h4>
                            <div className="bg-dream-purple-800 border-4 border-dream-purple-600 p-4">
                                <p className="font-body text-sm text-dream-purple-300">
                                    Confidence: {(phenotype.confidence * 100).toFixed(1)}%
                                </p>
                            </div>
                        </div>
                    </div>
                </PixelCard>
            </div>
        </DashboardLayout>
    );
};

export default AnalysisPage;
