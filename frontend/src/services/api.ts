

import { createClient } from '@supabase/supabase-js';
import type {
    LoginCredentials,
    SignupCredentials,
    AnalysisData
} from '../types';

const url = import.meta.env.VITE_SUPABASE_URL || 'https://placeholder.supabase.co';
const key = import.meta.env.VITE_SUPABASE_ANON_KEY || 'placeholder-key';
export const supabase = createClient(url, key);

export async function signup(creds: SignupCredentials) {
    try {
        const { error } = await supabase.auth.signUp({
            email: creds.email,
            password: creds.password,
        });

        if (error) {
            console.warn('Signup error:', error.message);
            if (error.message.toLowerCase().includes('fetch') || error.message.includes('502') || error.message.includes('503') || error.message.includes('Database')) {
                localStorage.setItem('offline_mode', 'true');
                return { success: true };
            }
            return { success: false, error: error.message };
        }
        return { success: true };
    } catch (e: any) {
        console.warn('Signup exception:', e);
        localStorage.setItem('offline_mode', 'true');
        return { success: true };
    }
}

export async function login(creds: LoginCredentials) {
    try {
        const { error } = await supabase.auth.signInWithPassword({
            email: creds.email,
            password: creds.password,
        });

        if (error) {
            console.warn('Login error:', error.message);
            if (error.message.toLowerCase().includes('fetch') || error.message.includes('502') || error.message.includes('503') || error.message.includes('Database')) {
                localStorage.setItem('offline_mode', 'true');
                return { success: true };
            }
            return { success: false, error: error.message };
        }
        return { success: true };
    } catch (e: any) {
        console.warn('Login exception:', e);
        localStorage.setItem('offline_mode', 'true');
        return { success: true };
    }
}

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function upload(file: File) {
    try {
        const fd = new FormData();
        fd.append('file', file);

        let session = null;
        try {
            const res = await supabase.auth.getSession();
            if (res.data && res.data.session) {
                session = res.data.session;
            }
        } catch (err) {
            console.warn("Could not get session for upload:", err);
        }

        const headers: HeadersInit = {};
        if (session?.access_token) {
            headers['Authorization'] = `Bearer ${session.access_token}`;
        }

        console.log(`uploading to ${BASE}/analyze...`);
        const res = await fetch(`${BASE}/analyze`, {
            method: 'POST',
            body: fd,
            headers
        });

        if (!res.ok) {
            const txt = await res.text();
            console.error('server err:', res.status, txt);
            try {
                const err = JSON.parse(txt);
                return { success: false, error: err.detail || `server error ${res.status}` };
            } catch {
                return { success: false, error: `server error ${res.status}: ${txt}` };
            }
        }

        const data = await res.json();
        console.log('upload success:', data);
        return {
            success: true,
            sessionId: data.sessionId,
            filename: file.name,
        };
    } catch (e: any) {
        console.error('Backend unreachable:', e);
        return {
            success: false,
            error: 'Cannot reach analysis server. Please ensure the backend is running.',
        };
    }
}

export async function getAnalysis(sid: string) {
    console.log(`fetch analysis: ${sid}`);
    try {
        const res = await fetch(`${BASE}/results/${sid}`);

        if (!res.ok) {
            const txt = await res.text();
            console.error(`fetch failed: ${res.status}`, txt);
            try {
                const err = JSON.parse(txt);
                throw new Error(err.detail || `server error ${res.status}`);
            } catch {
                throw new Error(`server error ${res.status}`);
            }
        }

        const data = await res.json();
        console.log('data received');
        return data as AnalysisData;
    } catch (e: any) {
        console.error('Failed to fetch analysis results:', e);
        throw e;
    }
}
