

import { createClient } from '@supabase/supabase-js';
import type {
    LoginCredentials,
    SignupCredentials,
    AnalysisData
} from '../types';

const url = import.meta.env.VITE_SUPABASE_URL || '';
const key = import.meta.env.VITE_SUPABASE_ANON_KEY || '';
export const supabase = createClient(url, key);

export async function signup(creds: SignupCredentials) {
    const { error } = await supabase.auth.signUp({
        email: creds.email,
        password: creds.password,
    });

    if (error) return { success: false, error: error.message };
    return { success: true };
}

export async function login(creds: LoginCredentials) {
    const { error } = await supabase.auth.signInWithPassword({
        email: creds.email,
        password: creds.password,
    });

    if (error) return { success: false, error: error.message };
    return { success: true };
}

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function upload(file: File) {
    try {
        const fd = new FormData();
        fd.append('file', file);

        const { data: { session } } = await supabase.auth.getSession();
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
                return { success: false, error: `server error ${res.status}` };
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
        console.error('upload catch:', e);
        return { success: false, error: e.message || 'connection failed' };
    }
}

export async function getAnalysis(sid: string) {
    console.log(`fetch analysis: ${sid}`);
    const res = await fetch(`${BASE}/results/${sid}`);

    if (!res.ok) {
        console.error(`fetch failed: ${res.status}`);
        throw new Error('not found');
    }

    const data = await res.json();
    console.log('data received');
    return data as AnalysisData;
}
