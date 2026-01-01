import pandas as pd
import mne
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# 1. Setup
data_dir = Path('sleep_edf_data')
csv_path = 'processed_data/ml_ready_dataset.csv'

# Load your labeled dataset
df = pd.read_csv(csv_path)

# 2. Pick one representative patient for each Class
# We sort by 'subject_id' to get consistent results
classes = df['insomnia_subtype'].unique()
selected_subjects = {}

print("Selecting patients...")
for subtype in classes:
    # Get the first subject for this subtype
    subject = df[df['insomnia_subtype'] == subtype]['Subject Id'].iloc[0]
    selected_subjects[subtype] = subject
    print(f"  {subtype}: {subject}")

# 3. Setup the Plot
fig, axes = plt.subplots(len(classes), 1, figsize=(12, 10), sharex=True)
plt.subplots_adjust(hspace=0.4)
colors = sns.color_palette("viridis", len(classes))

print("\nLoading and plotting EEG signals...")

# 4. Loop through and plot each one
for i, (subtype, subject_id) in enumerate(selected_subjects.items()):
    ax = axes[i]
    
    # Find the file
    psg_files = list(data_dir.glob(f"{subject_id}*-PSG.edf"))
    
    if len(psg_files) == 0:
        print(f"  ⚠️ Could not find file for {subject_id}")
        continue
        
    psg_path = psg_files[0]
    
    # Load Data
    raw = mne.io.read_raw_edf(psg_path, preload=False, verbose=False)
    eeg_channels = [ch for ch in raw.ch_names if 'EEG' in ch]
    channel = eeg_channels[0] 
    
    start_time = 2000 
    duration = 10 
    data, times = raw.get_data(picks=channel, tmin=start_time, tmax=start_time+duration, return_times=True)
    
    # Scale to uV
    data = data[0] * 1e6 
    
    # --- FIX STARTS HERE ---
    # Actually draw the data on the axis
    ax.plot(times, data, color=colors[i])
    
    # Add labels so you know which is which
    ax.set_title(f"Subtype: {subtype} (Subject {subject_id})")
    ax.set_ylabel("uV")

# Move plt.show() OUTSIDE the loop so it shows all plots at once
plt.xlabel("Time (seconds)")
plt.tight_layout()
plt.show()