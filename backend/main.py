from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time
import shutil
from typing import Dict, Optional
import mne
import tempfile
import os
from supabase import create_client, Client
from analysis import analyze_session

app = FastAPI()

URL = os.environ.get("VITE_SUPABASE_URL")
KEY = os.environ.get("VITE_SUPABASE_ANON_KEY")
supabase: Optional[Client] = None

if URL and KEY:
    try:
        supabase = create_client(URL, KEY)
        print("Supabase connected")
    except Exception as e:
        print(f"Supabase fail: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache: Dict[str, dict] = {}

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    if not file.filename.lower().endswith('.edf'):
        raise HTTPException(status_code=400, detail="EDF required")

    sid = str(uuid.uuid4())
    print(f"Starting: {file.filename}")

    fd, path = tempfile.mkstemp(suffix=".edf")
    try:
        with os.fdopen(fd, 'wb') as tmp:
            shutil.copyfileobj(file.file, tmp)
        
        # Validate
        try:
            mne.io.read_raw_edf(path, preload=False, verbose=False)
        except Exception as e:
            print(f"Invalid EDF: {e}")
            raise HTTPException(status_code=400, detail="Invalid EDF format")

        # Analyze
        res = analyze_session(path)
        res.update({
            "sessionId": sid,
            "patientId": f"P-{sid[:8]}",
            "date": time.strftime("%Y-%m-%d")
        })

        # DB Sync
        if supabase and authorization:
            try:
                token = authorization.replace("Bearer ", "")
                u = supabase.auth.get_user(token)
                uid = u.user.id
                if uid:
                    supabase.table("analyses").insert({
                        "user_id": uid,
                        "session_id": sid,
                        "result": res
                    }).execute()
            except Exception as e:
                print(f"DB error: {e}")

        cache[sid] = res
        print(f"Done: {sid}")
        return {"sessionId": sid}

    except Exception as e:
        print(f"Error: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(path):
            os.remove(path)

@app.get("/results/{sid}")
async def get_results(sid: str):
    if sid in cache:
        return cache[sid]
    
    if supabase:
        try:
            r = supabase.table("analyses").select("result").eq("session_id", sid).single().execute()
            if r.data: return r.data["result"]
        except: pass
            
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)