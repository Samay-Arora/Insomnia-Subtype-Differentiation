import os
import numpy as np
import mne
from tqdm import tqdm
import warnings

# --- CONFIGURATION ---
TARGET_RATE = 100 
OUTPUT_DIR = "processed_data"

DATA_SOURCES = {
    "Sleep-EDF": "sleep_edf_data",
    "CAP": "cap_data"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Suppress the annoyingly verbose warnings from MNE
mne.set_log_level('ERROR')
warnings.filterwarnings("ignore", category=RuntimeWarning) 

def find_best_channel(raw, dataset_name):
    ch_names = raw.ch_names
    
    if dataset_name == "Sleep-EDF":
        targets = ['EEG Fpz-Cz', 'EEG FPZ-CZ', 'Fpz-Cz']
    elif dataset_name == "CAP":
        targets = [ 'F4-C4', 'F4A1', 'F3A2', 'F3-A2', 'F4-A1', 'C4-A1', 'EEG C4-A1', 'C4A1', 'C3-A2', 'EEG C3-A2', 'C3A2']
    else:
        targets = []

    for t in targets:
        for ch in ch_names:
            if t.lower() in ch.lower(): 
                return ch
                
    for ch in ch_names:
        if "EEG" in ch.upper():
            return ch
            
    return None

def process_file(file_path, subject_id, dataset_name):
    try:
        # 1. Load Header ONLY (preload=False) - This is the speed hack
        raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)
        
        # 2. Pick Channel BEFORE loading data
        ch_name = find_best_channel(raw, dataset_name)
        if ch_name is None:
            return f"Skipped {subject_id}: No EEG channel found"
        
        # 3. Load only the specific channel (The "New" way)
        raw.pick([ch_name]) 
        raw.load_data()
        
        # 4. Resample to 100Hz
        if raw.info['sfreq'] != TARGET_RATE:
            raw.resample(TARGET_RATE)
            
        # 5. Normalize (Z-Score)
        data = raw.get_data()[0] * 1e6 # Convert to uV
        data = (data - np.mean(data)) / np.std(data)
        
        # 6. Save
        save_name = f"{dataset_name}_{subject_id}.npy"
        np.save(os.path.join(OUTPUT_DIR, save_name), data)
        
        return None
        
    except Exception as e:
        return f"Error {subject_id}: {str(e)}"

# --- MAIN EXECUTION ---
print("🚀 Starting Optimized Harmonization...")

all_tasks = []

# Gather Sleep-EDF
for root, dirs, files in os.walk(DATA_SOURCES["Sleep-EDF"]):
    for file in files:
        if file.endswith("PSG.edf"):
            full_path = os.path.join(root, file)
            sid = file.split('-')[0]
            all_tasks.append((full_path, sid, "Sleep-EDF"))

# Gather CAP
if os.path.exists(DATA_SOURCES["CAP"]):
    for root, dirs, files in os.walk(DATA_SOURCES["CAP"]):
        for file in files:
            if file.endswith(".edf") and (file.startswith("ins") or file.startswith("n")):
                full_path = os.path.join(root, file)
                sid = file.replace(".edf", "")
                all_tasks.append((full_path, sid, "CAP"))

print(f"Found {len(all_tasks)} total subjects.")

# Process
errors = []
for file_path, sid, dataset in tqdm(all_tasks):
    err = process_file(file_path, sid, dataset)
    if err:
        errors.append(err)

print("\n✅ Harmonization Complete!")
print(f"Success: {len(all_tasks) - len(errors)}")
print(f"Failed:  {len(errors)}")