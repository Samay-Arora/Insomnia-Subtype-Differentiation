from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time
from typing import Dict, Optional
import mne
import tempfile
import os
from supabase import create_client, Client

app = FastAPI()

# Supabase Setup
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")
supabase: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase successfully connected")
    except Exception as e:
        print(f"⚠️ Supabase connection failed: {e}")
else:
    print("⚠️ Warning: Supabase credentials not found. Persistence disabled.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

results_cache: Dict[str, dict] = {}

@app.post("/analyze")
async def analyze_eeg(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    if not file.filename.lower().endswith('.edf'):
        raise HTTPException(status_code=400, detail="Only .edf files are supported")

    max_size = 500 * 1024 * 1024
    content = await file.read()
    print(f"📁 Received file: {file.filename}, Size: {len(content) / (1024*1024):.2f} MB")
    
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail=f"File too large ({len(content)/(1024*1024):.1f}MB). Max is 500MB")
        
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        with tempfile.NamedTemporaryFile(suffix=".edf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            raw = mne.io.read_raw_edf(tmp_path, preload=False, verbose=False)
            if len(raw.ch_names) == 0:
                 raise ValueError("No EEG channels found")
        except Exception as e:
            print(f"Validation Error: {e}")
            raise HTTPException(status_code=400, detail="Invalid or corrupted EDF file")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Server error during validation: {str(e)}")

    session_id = str(uuid.uuid4())
    
    from analysis import analyze_session
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".edf", delete=False) as session_tmp:
            session_tmp.write(content)
            session_path = session_tmp.name
            
        try:
            analysis_results = analyze_session(session_path)
            
            analysis_results["sessionId"] = session_id
            analysis_results["patientId"] = f"PATIENT-{session_id[:8].upper()}"
            analysis_results["recordingDate"] = time.strftime("%Y-%m-%d")
            
            # --- PERSISTENCE LAYER ---
            if supabase and authorization:
                try:
                    # 1. Verify User
                    token = authorization.replace("Bearer ", "")
                    # We still use the main supabase client to verify the token
                    user_data = supabase.auth.get_user(token)
                    user_id = user_data.user.id
                    
                    if user_id:
                        print(f"💾 Saving results for user: {user_id}")
                        
                        # Use a scoped client for DB operations to satisfy RLS
                        # This ensures auth.uid() inside Supabase matches user_id
                        # We pass the token in the request headers via the client
                        from postgrest import SyncPostgrestClient
                        db = create_client(SUPABASE_URL, SUPABASE_KEY)
                        db.postgrest.auth(token)
                        
                        # 2. Save Analysis
                        db.table("analyses").insert({
                            "user_id": user_id,
                            "session_id": session_id,
                            "result": analysis_results
                        }).execute()
                        
                        # 3. Update Profile (Upload Count)
                        try:
                            # Use the same scoped client for profile update
                            current = db.table("profiles").select("upload_count").eq("id", user_id).execute()
                            count = 0
                            if current.data:
                                count = current.data[0].get("upload_count", 0)
                            
                            db.table("profiles").update({
                                "upload_count": count + 1,
                                "last_file_name": file.filename,
                                "updated_at": "now()"
                            }).eq("id", user_id).execute()
                            
                        except Exception as p_err:
                            print(f"⚠️ Profile update error: {p_err}")
                            
                except Exception as db_err:
                    print(f"⚠️ Persistence failed (continuing anyway): {db_err}")
            # -------------------------

            results_cache[session_id] = analysis_results
            return {"sessionId": session_id}
            
        finally:
            if os.path.exists(session_path):
                os.remove(session_path)
    except Exception as e:
        print(f"Analysis Failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/results/{session_id}")
async def get_results(session_id: str):
    if session_id in results_cache:
        return results_cache[session_id]
    if supabase:
        try:
            db_res = supabase.table("analyses").select("result").eq("session_id", session_id).single().execute()
            if db_res.data:
                return db_res.data["result"]
        except:
            pass
            
    raise HTTPException(status_code=404, detail="Analysis results not found or expired")

if __name__ == "__main__":
    import uvicorn
    # In production, these should be set in environment variables
    # For local dev, we rely on them being set before running script
    uvicorn.run(app, host="0.0.0.0", port=8000)