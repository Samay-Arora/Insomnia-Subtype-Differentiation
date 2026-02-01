import mne
import sys
import os

file_path = "/Users/Samay/Desktop/Repos/Insomnia-Subtype-Differentiation/sleep_edf_data/SC4201E0-PSG.edf"
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)

try:
    raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)
    print("✅ Header read successfully")
    print(f"Channels: {raw.ch_names}")
    print(f"Duration: {raw.times[-1]}s")
except Exception as e:
    print(f"❌ Failed to read EDF: {e}")
