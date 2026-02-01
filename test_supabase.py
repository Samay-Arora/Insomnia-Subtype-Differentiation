import os
from supabase import create_client, Client

url = "https://jtimabjchjsqijxyhura.supabase.co"
key = "sb_publishable_the7U0kVhAKR6Nw3BabkhQ_jZzxxarX"

print(f"Testing Supabase with URL: {url}")

try:
    supabase: Client = create_client(url, key)
    # Try a simple query
    res = supabase.table("profiles").select("*").limit(1).execute()
    print("✅ Supabase connection successful")
    print("Data:", res.data)
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
