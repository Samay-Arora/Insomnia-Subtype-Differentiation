import time
from backend.analysis import analyze_session
import os

file_path = "sleep_edf_data/SC4201E0-PSG.edf"
if os.path.exists(file_path):
    start = time.time()
    print("Starting analysis...")
    try:
        results = analyze_session(file_path)
        end = time.time()
        print(f"✅ Analysis completed in {end - start:.2f}s")
        print(f"Result keys: {results.keys()}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
else:
    print("File not found.")
