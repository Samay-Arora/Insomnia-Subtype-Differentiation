import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: './frontend/.env' });

const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY;

console.log(`URL: ${supabaseUrl}`);
console.log(`Key: ${supabaseKey?.substring(0, 10)}...`);

if (!supabaseUrl || !supabaseKey) {
    console.error("Missing credentials");
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function test() {
    const { data, error } = await supabase.from('profiles').select('*').limit(1);
    if (error) {
        console.error("❌ Supabase Error:", error.message);
    } else {
        console.log("✅ Supabase Connection Successful");
        console.log("Data:", data);
    }
}

test();
