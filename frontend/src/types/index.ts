/**
 * Type definitions for the Sleep Research Platform
 * API request/response types and shared interfaces
 */

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface SignupCredentials {
    email: string;
    password: string;
    name: string;
}

export interface AuthResponse {
    success: boolean;
    token?: string;
    user?: {
        id: string;
        email: string;
        name: string;
    };
    error?: string;
}

export interface UploadResponse {
    success: boolean;
    sessionId?: string;
    filename?: string;
    error?: string;
}

export interface SleepStageData {
    time: number;
    stage: number;
    label: string;
}

export interface SpectralData {
    frequency: number;
    power: number;
    channel: string;
}

export interface ClusterData {
    x: number;
    y: number;
    cluster: number;
    patientId: string;
}

export interface AnalysisData {
    sessionId: string;
    patientId: string;
    recordingDate: string;
    sleepStages: SleepStageData[];
    spectralAnalysis: SpectralData[];
    clusterAssignment: ClusterData;
    phenotype: {
        type: string;
        confidence: number;
        characteristics: string[];
    };
    summary: {
        totalSleepTime: number;
        sleepEfficiency: number;
        wakeAfterSleepOnset: number;
        remLatency: number;
    };
}

export interface NavItem {
    label: string;
    path: string;
    icon?: string;
}
