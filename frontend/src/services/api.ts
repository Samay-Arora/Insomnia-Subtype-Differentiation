/**
 * API Service for Sleep Research Platform
 * Integrated with Supabase for Auth and Data
 */

import { createClient } from '@supabase/supabase-js';
import type {
    LoginCredentials,
    SignupCredentials,
    AuthResponse,
    UploadResponse,
    AnalysisData
} from '../types';

// Initialize Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';
export const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * Register a new user account
 */
export async function signup(credentials: SignupCredentials): Promise<AuthResponse> {
    const { data, error } = await supabase.auth.signUp({
        email: credentials.email,
        password: credentials.password,
    });

    if (error) {
        return { success: false, error: error.message };
    }

    return { success: true };
}

/**
 * Authenticate user with email and password
 */
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
    const { data, error } = await supabase.auth.signInWithPassword({
        email: credentials.email,
        password: credentials.password,
    });

    if (error) {
        return { success: false, error: error.message };
    }

    return { success: true };
}

// FastAPI backend URL (no file storage for privacy)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Upload and analyze an EEG/EDF file
 * File is processed in-memory and NOT stored (HIPAA-friendly)
 * @param file - The .EDF file to analyze
 */
export async function uploadEEG(file: File): Promise<UploadResponse> {
    try {
        const formData = new FormData();
        formData.append('file', file);

        // Get current auth session to send token
        const { data: { session } } = await supabase.auth.getSession();

        const headers: HeadersInit = {};
        if (session?.access_token) {
            headers['Authorization'] = `Bearer ${session.access_token}`;
        }

        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData,
            headers: headers
        });

        if (!response.ok) {
            const error = await response.json();
            return { success: false, error: error.detail || 'Analysis failed' };
        }

        const result = await response.json();
        return {
            success: true,
            sessionId: result.sessionId,
            filename: file.name,
        };
    } catch (error) {
        console.error('Upload/analysis error:', error);
        return { success: false, error: 'Failed to connect to analysis server' };
    }
}

/**
 * Retrieve cached analysis results for a session
 * Results are temporarily cached in FastAPI (auto-expires)
 */
export async function getAnalysis(sessionId: string): Promise<AnalysisData> {
    const response = await fetch(`${API_BASE_URL}/results/${sessionId}`);

    if (!response.ok) {
        throw new Error('Analysis not found or expired');
    }

    return response.json();
}
