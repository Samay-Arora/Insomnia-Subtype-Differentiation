import os
import numpy as np
import pandas as pd
import antropy as ant
from scipy.signal import welch
from tqdm import tqdm

# --- CONFIGURATION ---
INPUT_DIR = "processed_data"
OUTPUT_FILE = "features_with_chaos.csv"
SFREQ = 100  
EPOCH_SEC = 30  

BANDS = {
    'Delta': (0.5, 4),
    'Theta': (4, 8),
    'Alpha': (8, 12),
    'Beta': (12, 30),
    'Gamma': (30, 45)
}

def get_spectral_features(data, fs):
    freqs, psd = welch(data, fs, nperseg=fs*2)
    
    features = {}
    total_power = np.sum(psd)
    
    for band, (low, high) in BANDS.items():
        idx = np.logical_and(freqs >= low, freqs <= high)
        band_power = np.sum(psd[idx])
        features[f'Rel_{band}'] = band_power / total_power
        
    return features

def get_chaos_features(data):
    features = {}
    try:
        features['Perm_Entropy'] = ant.perm_entropy(data, normalize=True)
    except:
        features['Perm_Entropy'] = 0
    try:
        features['Fractal_Dim'] = ant.petrosian_fd(data)
    except:
        features['Fractal_Dim'] = 0
    try:
        _, features['Hjorth_Complexity'] = ant.hjorth_params(data)
    except:
        features['Hjorth_Complexity'] = 0
        
    return features

def process_subject(file_path):
    try:
        data = np.load(file_path)
    except:
        return None
    epoch_len = int(SFREQ * EPOCH_SEC)
    n_epochs = len(data) // epoch_len
    
    if n_epochs < 10: 
        return None
    
    data = data[:n_epochs * epoch_len]
    epochs = data.reshape(n_epochs, epoch_len)
    epoch_features = []
    for epoch in epochs:
        spec = get_spectral_features(epoch, SFREQ)
        chaos = get_chaos_features(epoch)
        epoch_features.append({**spec, **chaos})
    df_epochs = pd.DataFrame(epoch_features)
    avg_features = df_epochs.mean().to_dict()
    
    return avg_features

if __name__ == "__main__":
    print("Feature Extraction...")
    
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".npy")]
    all_subject_data = []
    
    for filename in tqdm(files):
        file_path = os.path.join(INPUT_DIR, filename)
        parts = filename.replace('.npy', '').split('_')
        dataset = parts[0]
        subject_id = "_".join(parts[1:])
        feats = process_subject(file_path)
        
        if feats:
            feats['Subject_ID'] = subject_id
            feats['Dataset'] = dataset
            all_subject_data.append(feats)
            
    df_final = pd.DataFrame(all_subject_data)
    cols = ['Subject_ID', 'Dataset'] + [c for c in df_final.columns if c not in ['Subject_ID', 'Dataset']]
    df_final = df_final[cols]
    
    df_final.to_csv(OUTPUT_FILE, index=False)
    print(f"\n Extraction Complete. Features saved to '{OUTPUT_FILE}'")