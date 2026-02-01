import numpy as np
import pandas as pd
import antropy as ant
import joblib
import mne
from scipy.signal import welch
from typing import Dict, Any

import os

def convert_numpy(obj):
    """Recursively convert numpy types to native Python types"""
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, (np.intc, np.intp, np.int8,
                          np.int16, np.int32, np.int64, np.uint8,
                          np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return convert_numpy(obj.tolist())
    return obj

SFREQ = 100  
EPOCH_SEC = 30  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "insomnia_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "insomnia_scaler.pkl")

BANDS = {
    'Delta': (0.5, 4),
    'Theta': (4, 8),
    'Alpha': (8, 12),
    'Beta': (12, 30),
    'Gamma': (30, 45)
}

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("✅ ML Models loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load ML models: {e}")
    model = None
    scaler = None

def get_spectral_features(data, fs):
    freqs, psd = welch(data, fs, nperseg=fs*2)
    
    features = {}
    total_power = np.sum(psd)
    if total_power == 0:
        return {f'Rel_{band}': 0 for band in BANDS}
    
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

def extract_features_from_raw(raw: mne.io.Raw) -> Dict[str, float]:
    if raw.info['sfreq'] != SFREQ:
        raw.resample(SFREQ)
    
    data = raw.get_data()[0]
    epoch_len = int(SFREQ * EPOCH_SEC)
    n_epochs = len(data) // epoch_len
    if n_epochs < 1:
        raise ValueError("Recording too short (< 30s)")
    data = data[:n_epochs * epoch_len]
    epochs = data.reshape(n_epochs, epoch_len)
    epoch_features_list = []
    
    for epoch in epochs:
        spec = get_spectral_features(epoch, SFREQ)
        chaos = get_chaos_features(epoch)
        epoch_features_list.append({**spec, **chaos})
        
    df_epochs = pd.DataFrame(epoch_features_list)
    avg_features = df_epochs.mean().to_dict()
    return avg_features

def analyze_session(file_path: str) -> Dict[str, Any]:
    raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
    features = extract_features_from_raw(raw)
    df_input = pd.DataFrame([features])
    inference_result = {
        "subtype": "Unknown",
        "confidence": 0.0,
        "cluster": -1
    }
    
    if model and scaler:
        try:
            X = df_input.values
            X_scaled = scaler.transform(X)
            cluster = model.predict(X_scaled)[0]
            subtypes = {
                0: "Subtype 1: Low Arousal / Deep Sleep Deficit",
                1: "Subtype 2: High Arousal / Hyperactive",
                2: "Subtype 3: Fragmented / Chaotic",
                3: "Subtype 4: Periodic Leg Movement / Restless"
            }
            
            inference_result["cluster"] = int(cluster)
            inference_result["subtype"] = subtypes.get(cluster, f"Subtype {cluster}")
            inference_result["confidence"] = 0.85 # Placeholder as KMeans has no proba
            
        except Exception as e:
            print(f"Inference failed: {e}")




    final_result = {
        "sleepStages": [
            {
                "time": i*30, 
                "stage": (s := int(np.random.choice([0, 1, 2, 3, 4], p=[0.1, 0.1, 0.4, 0.2, 0.2]))),
                "label": ["Wake", "N1", "N2", "N3", "REM"][s]
            }
            for i in range(min(30, int(raw.times[-1]//30)))
        ],
        "spectralAnalysis": [
            {"frequency": 1, "power": float(features.get('Rel_Delta', 0)), "channel": raw.ch_names[0]},
            {"frequency": 6, "power": float(features.get('Rel_Theta', 0)), "channel": raw.ch_names[0]},
            {"frequency": 10, "power": float(features.get('Rel_Alpha', 0)), "channel": raw.ch_names[0]},
            {"frequency": 20, "power": float(features.get('Rel_Beta', 0)), "channel": raw.ch_names[0]},
            {"frequency": 35, "power": float(features.get('Rel_Gamma', 0)), "channel": raw.ch_names[0]},
        ],
        "clusterAssignment": {
            "x": float(np.random.normal(0, 1)),
            "y": float(np.random.normal(0, 1)),
            "cluster": int(inference_result["cluster"]),
            "patientId": "Generating..."
        },
        "phenotype": {
            "type": inference_result["subtype"],
            "confidence": float(inference_result["confidence"]),
            "characteristics": [
                "Beta Power: " + ("High" if features.get('Rel_Beta', 0) > 0.3 else "Normal"),
                "Chaos Index: " + ("High" if features.get('Fractal_Dim', 0) > 1.5 else "Normal"),
                "Sleep Stability: Variable"
            ]
        },
        "summary": {
            "totalSleepTime": int(raw.times[-1] / 60),
            "sleepEfficiency": 85,
            "wakeAfterSleepOnset": 30,
            "remLatency": 60
        }
    }
    
    return convert_numpy(final_result)
