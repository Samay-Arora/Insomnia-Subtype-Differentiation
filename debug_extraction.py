"""
EEG Feature Extraction from Sleep-EDF PSG Files
Extracts clinically-relevant features AND generates insomnia labels.

THIS IS THE ALL-IN-ONE SCRIPT.

*** FINAL v5.2: "CRITICAL FIX" Version ***
- Fixes CRITICAL indentation bug causing WASO=0.0.
- Fixes CRITICAL sleep_efficiency logic bug (TIB).
- Retains all other fixes from v5 (SOL, classification, crash-proofing)
"""

import numpy as np
import pandas as pd
import mne
from pathlib import Path
from scipy import signal, stats
from scipy.signal import welch, find_peaks, hilbert
from tqdm import tqdm
import warnings
import traceback # For better error logging

warnings.filterwarnings('ignore')
mne.set_log_level('WARNING')


class EEGFeatureExtractor:
    
    def __init__(self, data_dir='sleep_edf_data'):
        # All files (PSG and Hypnogram) MUST be in this directory
        self.data_dir = data_dir
        
        # Clinical thresholds
        self.SOL_threshold = 30  # minutes
        self.WASO_threshold = 30  # minutes
        self.awakening_threshold = 3  # count
        self.sleep_efficiency_threshold = 85  # percentage
        self.early_wake_threshold = 60  # minutes
        
        # EEG channel priorities
        self.eeg_channel_priority = [
            'EEG Fpz-Cz', 'EEG Pz-Oz', # Sleep-EDF standards
            'C3-A2', 'C4-A1', 'Fpz-Cz', 'Pz-Oz' # Fallbacks
        ]
        
        # Frequency bands
        self.frequency_bands = {
            'delta': (0.5, 4), 'theta': (4, 8), 'alpha': (8, 13),
            'beta': (13, 30), 'sigma': (11, 16)
        }
    
    # ==================== LOAD HYPNOGRAM & GENERATE LABELS ====================
    
    def load_hypnogram(self, filepath):
        """
        Load sleep stage annotations from hypnogram file
        (Vulnerability: end_time logic is weak)
        """
        try:
            annotations = mne.read_annotations(filepath)
            end_time = annotations.onset[-1] + annotations.duration[-1]
            n_epochs = int(np.ceil(end_time / 30.0))
            sleep_stages = np.full(n_epochs, 9, dtype=int) # 9 = Unknown

            for annot in annotations:
                desc = annot['description']
                onset = annot['onset']
                duration = annot['duration']

                # --- Robust Parsing Logic (v5) ---
                if desc is None:
                    stage_code = 9
                else:
                    d = desc.strip()
                    d_lower = d.lower()

                    if 'wake' in d_lower or d_lower == 'w':
                        stage_code = 0
                    elif 'stage 1' in d_lower or 'n1' in d_lower or d_lower == '1':
                        stage_code = 1
                    elif 'stage 2' in d_lower or 'n2' in d_lower or d_lower == '2':
                        stage_code = 2
                    elif 'stage 3' in d_lower or 'n3' in d_lower or d_lower == '3':
                        stage_code = 3
                    elif 'stage 4' in d_lower or d_lower == '4':
                        stage_code = 4
                    elif 'rem' in d_lower or 'stage r' in d_lower or d_lower == 'r':
                        stage_code = 5
                    elif '?' in d or 'movement' in d_lower:
                        stage_code = 9
                    else:
                        stage_code = 9 # Default to Unknown
                # --- End Robust Parsing ---

                start_epoch = int(np.floor(onset / 30.0))
                end_epoch = int(np.ceil((onset + duration) / 30.0))
                
                start_epoch = max(start_epoch, 0)
                end_epoch = min(end_epoch, n_epochs)
                    
                sleep_stages[start_epoch:end_epoch] = stage_code
            
            return sleep_stages
        
        except Exception as e:
            print(f"Error loading hypnogram {filepath.name}: {e}")
            return None
    
    def calculate_sleep_metrics_from_hypnogram(self, sleep_stages):
        """
        Calculate sleep metrics from hypnogram annotations
        *** v5.2: CRITICAL FIX for WASO (indentation) & Sleep Efficiency (TIB) ***
        """
        if sleep_stages is None or len(sleep_stages) == 0:
            return None
        
        # Define Time in Bed (TIB) as the total duration of the recording
        # This is the FIX for Sleep Efficiency
        time_in_bed = len(sleep_stages) * 0.5
        if time_in_bed == 0:
            # Cannot process an empty recording
            return {
                'SOL_minutes': 0, 'WASO_minutes': 0, 'num_awakenings': 0,
                'early_morning_awakening': False, 'sleep_efficiency_percent': 0,
                'total_sleep_time_minutes': 0
            }

        # Valid NREM sleep stages for SOL
        nrem_sleep_stages = {1, 2, 3, 4}

        # SOL: Sleep Onset Latency
        SOL = 0.0 
        for i, stage in enumerate(sleep_stages):
            if stage in nrem_sleep_stages: # Must be NREM
                SOL = i * 0.5
                break
        else: 
            SOL = time_in_bed # If no NREM sleep, SOL is entire night

        # WASO: Wake After Sleep Onset
        first_sleep = None
        last_sleep = None
        for i, stage in enumerate(sleep_stages):
            if stage > 0 and stage != 9: # Any sleep (incl. REM)
                if first_sleep is None:
                    first_sleep = i
                last_sleep = i # <-- CORRECTED. Now updates on *every* sleep epoch.
        
        WASO = 0
        if first_sleep is not None:
            # Sleep period is from first sleep to last sleep
            sleep_period = sleep_stages[first_sleep:last_sleep+1]
            wake_epochs = np.sum(sleep_period == 0)
            WASO = wake_epochs * 0.5
        
        # Number of awakenings
        num_awakenings = 0
        if first_sleep is not None:
            in_wake = False
            # Check for wakes *within* the sleep period
            for stage in sleep_stages[first_sleep:last_sleep+1]:
                if stage == 0:
                    if not in_wake:
                        num_awakenings += 1
                        in_wake = True
                elif stage != 9:
                    in_wake = False
        
        # Early morning awakening (now uses correct last_sleep)
        last_sleep_index = last_sleep
        
        early_wake = False
        if last_sleep_index is not None:
            final_wake_duration = (len(sleep_stages) - last_sleep_index - 1) * 0.5
            early_wake = final_wake_duration > self.early_wake_threshold
        
        # Sleep efficiency
        valid_stages = sleep_stages[sleep_stages != 9] # Stages that are not 'Unknown'
        if len(valid_stages) == 0:
            total_sleep_time = 0.0
        else:
            total_sleep_epochs = np.sum(valid_stages > 0) # Total epochs of any sleep
            total_sleep_time = total_sleep_epochs * 0.5
        
        # Use correct TIB
        sleep_efficiency = (total_sleep_time / time_in_bed) * 100
        
        return {
            'SOL_minutes': SOL,
            'WASO_minutes': WASO,
            'num_awakenings': num_awakenings,
            'early_morning_awakening': early_wake,
            'sleep_efficiency_percent': sleep_efficiency,
            'total_sleep_time_minutes': total_sleep_time
        }
    
    def classify_insomnia_subtype(self, metrics):
        """
        Classify into insomnia subtype based on clinical criteria
        (v5 logic - robust)
        """
        if metrics is None: return "Unknown"
        
        SOL = metrics['SOL_minutes']
        WASO = metrics['WASO_minutes']
        num_awakenings = metrics['num_awakenings']
        early_wake = metrics['early_morning_awakening']
        sleep_efficiency = metrics['sleep_efficiency_percent']
        
        # --- Check for problems ---
        has_sol_problem = SOL >= self.SOL_threshold
        has_maint_problem = (WASO >= self.WASO_threshold) or (num_awakenings > self.awakening_threshold)
        has_early_wake_problem = early_wake
        has_efficiency_problem = sleep_efficiency <= self.sleep_efficiency_threshold

        # --- Good Sleeper ---
        if not (has_sol_problem or has_maint_problem or has_early_wake_problem or has_efficiency_problem):
            return "Good_Sleeper"

        # --- Mixed Insomnia (Most severe) ---
        if has_sol_problem and (has_maint_problem or has_early_wake_problem):
            return "Mixed_Insomnia"

        # --- Sleep Onset Insomnia ---
        if has_sol_problem:
            return "Sleep_Onset_Insomnia"
            
        # --- Sleep Maintenance Insomnia ---
        if has_maint_problem:
            return "Sleep_Maintenance_Insomnia"
            
        # --- Early Morning Awakening ---
        if has_early_wake_problem:
            return "Early_Morning_Awakening"

        # --- Poor Sleeper (unspecified) ---
        if has_efficiency_problem:
            return "Poor_Sleeper_Unspecified"

        # Fallback (should be unreachable)
        return "Good_Sleeper"
    
    # ==================== LOAD PSG DATA ====================
    
    def load_psg_file(self, filepath):
        """
        Load PSG file and extract EEG channel (v5 logic - robust)
        """
        try:
            raw = mne.io.read_raw_edf(filepath, preload=True, verbose=False)
            available_channels = raw.ch_names
            selected_channel = None
            
            for channel in ['EEG Fpz-Cz', 'EEG Pz-Oz']:
                if channel in available_channels:
                    selected_channel = channel
                    break
            
            if selected_channel is None:
                for channel in self.eeg_channel_priority:
                    if channel in available_channels:
                        selected_channel = channel
                        break

            if selected_channel is None:
                eeg_channels = [ch for ch in available_channels if 'EEG' in ch.upper()]
                if eeg_channels:
                    selected_channel = eeg_channels[0]
                else:
                    return None, None, None
            
            raw.pick_channels([selected_channel])
            eeg_data = raw.get_data()[0]
            sampling_rate = raw.info['sfreq']
            
            return eeg_data, sampling_rate, selected_channel
            
        except Exception as e:
            print(f"Error loading {filepath.name}: {e}")
            return None, None, None
    
    # ==================== FEATURE CALCULATION FUNCTIONS ====================
    
    def calculate_band_power(self, eeg_data, fs, band_range):
        nperseg = min(int(fs * 4), len(eeg_data))
        freqs, psd = welch(eeg_data, fs=fs, nperseg=nperseg)
        idx_band = np.logical_and(freqs >= band_range[0], freqs <= band_range[1])
        band_power = np.mean(psd[idx_band])
        return band_power
    
    def calculate_relative_band_power(self, eeg_data, fs):
        features = {}
        band_powers = {}
        for band_name, band_range in self.frequency_bands.items():
            power = self.calculate_band_power(eeg_data, fs, band_range)
            band_powers[band_name] = power
            features[f'{band_name}_power'] = power
        
        total_power = sum(band_powers.values())
        if total_power < 1e-10: total_power = 1e-10
        
        for band_name, power in band_powers.items():
            features[f'{band_name}_relative'] = (power / total_power * 100)
        
        features['theta_alpha_ratio'] = (band_powers['theta'] / (band_powers['alpha'] + 1e-10))
        features['delta_beta_ratio'] = (band_powers['delta'] / (band_powers['beta'] + 1e-10))
        
        return features
    
    def detect_sleep_spindles(self, eeg_data, fs):
        # (Vulnerability: This is a "toy" detector)
        nyquist = fs / 2
        low = 11 / nyquist
        high = 16 / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        spindle_signal = signal.filtfilt(b, a, eeg_data)
        analytic_signal = hilbert(spindle_signal)
        amplitude_envelope = np.abs(analytic_signal)
        window_size = int(0.1 * fs)
        envelope_smooth = np.convolve(amplitude_envelope, 
                                    np.ones(window_size)/window_size, 
                                    mode='same')
        
        threshold = np.mean(envelope_smooth) + 1.5 * np.std(envelope_smooth)
        peaks, properties = find_peaks(envelope_smooth, 
                                    height=threshold,
                                    distance=int(0.5 * fs))
        duration_minutes = len(eeg_data) / fs / 60
        spindle_density = len(peaks) / duration_minutes if duration_minutes > 0 else 0
        avg_spindle_amplitude = np.mean(properties['peak_heights']) if len(peaks) > 0 else 0
        
        return {
            'spindle_count': len(peaks),
            'spindle_density': spindle_density,
            'avg_spindle_amplitude': avg_spindle_amplitude
        }
    
    def calculate_statistical_features(self, eeg_data):
        return {
            'mean_amplitude': np.mean(eeg_data),
            'std_amplitude': np.std(eeg_data),
            'variance': np.var(eeg_data),
            'skewness': stats.skew(eeg_data),
            'kurtosis': stats.kurtosis(eeg_data),
            'peak_to_peak': np.ptp(eeg_data),
            'rms': np.sqrt(np.mean(eeg_data**2)),
            'zero_crossings': len(np.where(np.diff(np.sign(eeg_data)))[0])
        }
    
    def calculate_epoch_features(self, eeg_data, fs, epoch_length=30):
        epoch_samples = int(epoch_length * fs)
        n_epochs = len(eeg_data) // epoch_samples
        if n_epochs == 0: return {}
        
        delta_powers, theta_powers, alpha_powers, beta_powers = [], [], [], []
        
        for i in range(n_epochs):
            start_idx = i * epoch_samples
            end_idx = start_idx + epoch_samples
            epoch_data = eeg_data[start_idx:end_idx]
            
            delta_powers.append(self.calculate_band_power(epoch_data, fs, self.frequency_bands['delta']))
            theta_powers.append(self.calculate_band_power(epoch_data, fs, self.frequency_bands['theta']))
            alpha_powers.append(self.calculate_band_power(epoch_data, fs, self.frequency_bands['alpha']))
            beta_powers.append(self.calculate_band_power(epoch_data, fs, self.frequency_bands['beta']))
        
        return {
            'delta_power_mean': np.mean(delta_powers), 'delta_power_std': np.std(delta_powers),
            'theta_power_mean': np.mean(theta_powers), 'theta_power_std': np.std(theta_powers),
            'alpha_power_mean': np.mean(alpha_powers), 'alpha_power_std': np.std(alpha_powers),
            'beta_power_mean': np.mean(beta_powers), 'beta_power_std': np.std(beta_powers),
            'power_variability': np.std([np.mean(delta_powers), np.mean(theta_powers), 
                                        np.mean(alpha_powers), np.mean(beta_powers)])
        }
    
    # ==================== EXTRACT ALL FEATURES ====================
    
    def extract_features_from_file(self, psg_filepath):
        eeg_data, fs, channel_name = self.load_psg_file(psg_filepath)
        if eeg_data is None: return None
        
        subject_id = psg_filepath.stem.split('-')[0]
        features = {'subject_id': subject_id, 'eeg_channel': channel_name}
        
        features.update(self.calculate_relative_band_power(eeg_data, fs))
        features.update(self.detect_sleep_spindles(eeg_data, fs))
        features.update(self.calculate_statistical_features(eeg_data))
        features.update(self.calculate_epoch_features(eeg_data, fs))
        
        return features
    
    # ==================== PROCESS ALL FILES (v5 - BEST OF BOTH) ====================
    
    def process_all_files(self, output_file='processed_data/ml_ready_dataset.csv'):
        print()
        print("=" * 80)
        print("EEG FEATURE EXTRACTION & LABEL GENERATION (v5.2 - Final)")
        print("=" * 80)
        print()
        
        data_path = Path(self.data_dir)
        if not data_path.is_dir():
            print(f"❌ ERROR: Data directory not found: {self.data_dir}")
            return None

        psg_files = sorted(list(data_path.glob('*-PSG.edf')))
        
        if len(psg_files) == 0:
            print(f"❌ ERROR: No PSG files found in {self.data_dir}/")
            return None
        
        print(f"Found {len(psg_files)} PSG files")
        print("Processing files... (this may take 10-20 minutes)")
        print()
        
        all_data = []
        failed_files = []
        
        for psg_file in tqdm(psg_files, desc="Processing", unit="file"):
            try:
                # --- 1. Extract EEG Features ---
                features = self.extract_features_from_file(psg_file)
                if features is None:
                    failed_files.append((psg_file.name, "EEG data read error"))
                    continue
                
                # --- 2. Find Matching Hypnogram (ROBUST LOGIC) ---
                base_stem = psg_file.stem.split('-')[0]
                hypno_files = list(data_path.glob(f"{base_stem}-*Hypnogram.edf")) + \
                              list(data_path.glob(f"{base_stem}*-Hypnogram.edf")) + \
                              list(data_path.glob(f"{base_stem}*Hypnogram.edf"))
                if len(hypno_files) == 0:
                    subject_prefix = ''.join([c for c in base_stem if c.isalnum()][:6])
                    hypno_files = list(data_path.glob(f"{subject_prefix}*-Hypnogram.edf"))
                hypno_files = sorted(set(hypno_files))

                if len(hypno_files) == 0:
                    failed_files.append((psg_file.name, f"No matching hypnogram for {base_stem}*"))
                    continue
                if len(hypno_files) > 1:
                    failed_files.append((psg_file.name, f"Multiple hypnograms for {base_stem}*"))
                    continue

                hypno_path = hypno_files[0] 
                sleep_stages = self.load_hypnogram(hypno_path)
                if sleep_stages is None:
                    failed_files.append((psg_file.name, "Hypnogram load error"))
                    continue
                
                # --- 3. Calculate Real Sleep Metrics ---
                metrics = self.calculate_sleep_metrics_from_hypnogram(sleep_stages)
                if metrics is None: # CRASH FIX
                    failed_files.append((psg_file.name, "Metrics calculation error"))
                    continue
                    
                # --- 4. Classify Insomnia Subtype ---
                subtype = self.classify_insomnia_subtype(metrics)
                
                # --- 5. Combine All Data ---
                features.update(metrics)
                features['insomnia_subtype'] = subtype
                
                all_data.append(features)
                    
            except Exception as e:
                print(f"\nError processing {psg_file.name}: {traceback.format_exc()}")
                failed_files.append((psg_file.name, str(e)))
                continue
        
        # Create DataFrame
        df_final = pd.DataFrame(all_data)
        
        print()
        print("=" * 80)
        print("PROCESSING SUMMARY")
        print("=" * 80)
        
        if len(df_final) == 0:
            print("❌ No data was processed successfully.")
        else:
            print(f"✓ Successfully processed: {len(df_final)} subjects")
            
        print(f"✗ Failed: {len(failed_files)} files")
        if len(failed_files) > 0 and len(failed_files) < 20:
            print("\n--- Failed files (up to 20) ---")
            for name, err in failed_files:
                print(f"  - {name}: {err}")
        print("=" * 80)

        if len(df_final) > 0:
            print("Insomnia Subtype Distribution:")
            print(df_final['insomnia_subtype'].value_counts().to_string())
            print()
            
            print("Sleep Metrics Summary:")
            print(df_final[['SOL_minutes', 'WASO_minutes', 'sleep_efficiency_percent']].describe().to_string())
            print()
            
            output_dir = Path(output_file).parent
            output_dir.mkdir(exist_ok=True)
            df_final.to_csv(output_file, index=False)
            
            print(f"ML-ready dataset saved to: {output_file}")
            print("=" * 80)
        
        return df_final

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    import sys
    
    print()
    print("🧠 EEG Feature Extraction & Labeling Pipeline (All-in-One, v5.2)")
    print("=" * 80)
    
    DATA_FOLDER = 'sleep_edf_data'
    
    extractor = EEGFeatureExtractor(data_dir=DATA_FOLDER)
    
    df_final = extractor.process_all_files(output_file='processed_data/ml_ready_dataset.csv')
    
    if df_final is not None and len(df_final) > 0:
        print()
        print("✅ SUCCESS! Your dataset is ready for machine learning.")
        print()
        print("Next steps:")
        print("  1. Review: processed_data/ml_ready_dataset.csv")
        print("  2. Proceed to ML training")
    else:
        print("\n❌ Pipeline failed.")
        print(f"   Please ensure all files are in '{DATA_FOLDER}'.")