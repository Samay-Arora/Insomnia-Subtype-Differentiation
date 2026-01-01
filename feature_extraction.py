"""
EEG Feature Extraction - PhysioNet Sleep-EDF Expanded Edition
- Robustly matches PSG and Hypnogram files using PhysioNet naming conventions.
- Matches files like 'SC4001E0-PSG.edf' with 'SC4001EC-Hypnogram.edf'
- Includes recursive search to find files in subfolders.
"""

import numpy as np
import pandas as pd
import mne
from pathlib import Path
from scipy import signal, stats
from scipy.signal import welch, find_peaks, hilbert
from tqdm import tqdm
import warnings
import traceback

warnings.filterwarnings('ignore')
mne.set_log_level('WARNING')

class SleepDataProcessor:
    def __init__(self, input_dir, output_file):
        self.input_dir = input_dir
        self.output_file = output_file
        
        # Clinical thresholds
        self.SOL_threshold = 30
        self.WASO_threshold = 30
        self.awakening_threshold = 3
        self.sleep_efficiency_threshold = 85
        self.early_wake_threshold = 60
        
        # Frequency bands
        self.frequency_bands = {
            'delta': (0.5, 4), 'theta': (4, 8), 'alpha': (8, 13),
            'beta': (13, 30), 'sigma': (11, 16)
        }

    # ==================== HYPNOGRAM LOADING ====================
    def load_hypnogram(self, filepath):
        try:
            # Using read_annotations is correct for PhysioNet Hypnograms
            annotations = mne.read_annotations(filepath)
            end_time = annotations.onset[-1] + annotations.duration[-1]
            n_epochs = int(np.ceil(end_time / 30.0))
            sleep_stages = np.full(n_epochs, 9, dtype=int)

            for onset, duration, desc in zip(
                annotations.onset, annotations.duration, annotations.description
            ):
                if desc is None:
                    stage_code = 9
                else:
                    d = desc.strip()
                    d_lower = d.lower()

                    if 'wake' in d_lower or d_lower in ('w', 'sleep stage w'):
                        stage_code = 0
                    elif 'stage 1' in d_lower or 'n1' in d_lower or d_lower == '1':
                        stage_code = 1
                    elif 'stage 2' in d_lower or 'n2' in d_lower or d_lower == '2':
                        stage_code = 2
                    elif 'stage 3' in d_lower or 'n3' in d_lower or d_lower == '3':
                        stage_code = 3
                    elif 'stage 4' in d_lower or d_lower == '4':
                        stage_code = 4
                    elif 'rem' in d_lower or d_lower == 'r' or 'stage r' in d_lower:
                        stage_code = 5
                    else:
                        stage_code = 9

                start_epoch = int(np.floor(onset / 30.0))
                end_epoch = int(np.ceil((onset + duration) / 30.0))
                start_epoch = max(start_epoch, 0)
                end_epoch = min(end_epoch, n_epochs)

                sleep_stages[start_epoch:end_epoch] = stage_code

            return sleep_stages

        except Exception as e:
            print(f"Error loading hypnogram {filepath.name}: {e}")
            return None

    # ==================== METRICS CALCULATION ====================
    def calculate_sleep_metrics(self, sleep_stages):
        if sleep_stages is None or len(sleep_stages) == 0:
            return None

        first_sleep = None
        last_sleep = None
        for i, stage in enumerate(sleep_stages):
            if stage > 0 and stage != 9:
                if first_sleep is None:
                    first_sleep = i
                last_sleep = i

        if first_sleep is None:
            SOL = len(sleep_stages) * 0.5
        else:
            SOL = first_sleep * 0.5

        WASO = 0.0
        if first_sleep is not None and last_sleep is not None and last_sleep >= first_sleep:
            sleep_period = sleep_stages[first_sleep:last_sleep + 1]
            WASO = np.sum(sleep_period == 0) * 0.5

        num_awakenings = 0
        if first_sleep is not None and last_sleep is not None and last_sleep >= first_sleep:
            in_wake = False
            for stage in sleep_stages[first_sleep:last_sleep + 1]:
                if stage == 0:
                    if not in_wake:
                        num_awakenings += 1
                        in_wake = True
                elif stage != 9:
                    in_wake = False

        last_sleep_index = last_sleep
        early_wake = False
        if last_sleep_index is not None:
            final_wake_duration = (len(sleep_stages) - last_sleep_index - 1) * 0.5
            early_wake = final_wake_duration > self.early_wake_threshold

        valid_mask = sleep_stages != 9
        valid_stages = sleep_stages[valid_mask]
        time_in_bed = len(valid_stages) * 0.5
        total_sleep_epochs = np.sum(valid_stages > 0)
        total_sleep_time = total_sleep_epochs * 0.5

        sleep_efficiency = 0
        if time_in_bed > 0:
            sleep_efficiency = total_sleep_time / time_in_bed * 100

        return {
            'SOL_minutes': SOL,
            'WASO_minutes': WASO,
            'num_awakenings': num_awakenings,
            'early_morning_awakening': early_wake,
            'sleep_efficiency_percent': sleep_efficiency,
            'total_sleep_time_minutes': total_sleep_time
        }

    # ==================== CLASSIFICATION LOGIC ====================
    def classify_insomnia_subtype(self, metrics):
        if metrics is None: return "Unknown"
        
        SOL = metrics['SOL_minutes']
        WASO = metrics['WASO_minutes']
        num_awakenings = metrics['num_awakenings']
        early_wake = metrics['early_morning_awakening']
        sleep_efficiency = metrics['sleep_efficiency_percent']
        
        has_sol = SOL >= self.SOL_threshold
        has_maint = (WASO >= self.WASO_threshold) or (num_awakenings > self.awakening_threshold)
        has_early = early_wake
        has_eff = sleep_efficiency <= self.sleep_efficiency_threshold

        if not (has_sol or has_maint or has_early or has_eff):
            return "Good_Sleeper"
        if has_sol and (has_maint or has_early):
            return "Mixed_Insomnia"
        if has_sol:
            return "Sleep_Onset_Insomnia"
        if has_maint:
            return "Sleep_Maintenance_Insomnia"
        if has_early:
            return "Early_Morning_Awakening"
        if has_eff:
            return "Poor_Sleeper_Unspecified"
            
        return "Good_Sleeper"

    # ==================== SPECTRAL FEATURES ====================
    def calculate_band_power(self, eeg_data, fs, band_range):
        nperseg = min(int(fs * 4), len(eeg_data))
        freqs, psd = welch(eeg_data, fs=fs, nperseg=nperseg)
        idx_band = np.logical_and(freqs >= band_range[0], freqs <= band_range[1])
        return np.mean(psd[idx_band])

    def calculate_spectral_features(self, eeg_data, fs):
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
            
        return features

    # ==================== MAIN PROCESSING ====================
    def extract_features(self, psg_file, hypnogram_file):
        try:
            # Load PSG
            raw = mne.io.read_raw_edf(psg_file, preload=True, verbose=False)
            
            # Find EEG channel
            eeg_channels = [ch for ch in raw.ch_names if 'EEG' in ch]
            if not eeg_channels:
                return None, "No EEG channels found"
            
            # Prefer Fpz-Cz as per Sleep-EDF standard
            selected_channel = eeg_channels[0]
            for ch in eeg_channels:
                if 'Fpz-Cz' in ch:
                    selected_channel = ch
                    break
            
            raw.pick_channels([selected_channel])
            eeg_data = raw.get_data()[0]
            fs = raw.info['sfreq']

            # Load Hypnogram
            sleep_stages = self.load_hypnogram(hypnogram_file)
            if sleep_stages is None:
                return None, "Hypnogram read failure"

            # Calculate Metrics
            metrics = self.calculate_sleep_metrics(sleep_stages)
            if metrics is None:
                return None, "Invalid metrics"

            # Calculate Spectral Features
            spectral = self.calculate_spectral_features(eeg_data, fs)
            
            # Calculate Statistical Features
            stats_dict = {
                'mean_amplitude': np.mean(eeg_data),
                'std_amplitude': np.std(eeg_data),
                'skewness': stats.skew(eeg_data),
                'kurtosis': stats.kurtosis(eeg_data)
            }

            # Assemble Feature Vector
            feature_dict = {'eeg_channel': selected_channel}
            feature_dict.update(spectral)
            feature_dict.update(stats_dict)
            feature_dict.update(metrics)

            return feature_dict, None

        except Exception as e:
            return None, f"Exception: {e}"

    def process_all_files(self):
        print("Starting processing...")
        data_path = Path(self.input_dir)
        
        if not data_path.is_dir():
            print(f"CRITICAL ERROR: Input directory '{self.input_dir}' does not exist.")
            print("Please check the path and try again.")
            return

        # RECURSIVE SEARCH for PSG files
        # This finds files even if they are in subfolders like 'sleep-cassette/'
        psg_files = sorted(list(data_path.glob("**/*-PSG.edf")))
        print(f"Found {len(psg_files)} PSG files in '{data_path}'.")

        if len(psg_files) == 0:
            print("No *-PSG.edf files found.")
            print("Make sure you downloaded the files and they are in the correct folder.")
            return

        records = []
        failed_files = []

        for psg_file in tqdm(psg_files, desc="Processing Files"):
            try:
                # Get the file stem (e.g., SC4001E0-PSG)
                base_stem = psg_file.name.split('-')[0] # SC4001E0
                
                # PHYSIONET MATCHING LOGIC
                # PSG: SC4001E0-PSG.edf
                # Hypno: SC4001EC-Hypnogram.edf
                # Common ID: SC4001 (First 6 characters)
                
                subject_id = base_stem[:6] # SC4001
                
                # Look for any Hypnogram file starting with the same Subject ID
                # We search in the SAME folder as the PSG file first
                hypno_files = list(psg_file.parent.glob(f"{subject_id}*-Hypnogram.edf"))
                
                # If not found, try searching the whole data directory recursively
                if len(hypno_files) == 0:
                    hypno_files = list(data_path.glob(f"**/{subject_id}*-Hypnogram.edf"))

                if len(hypno_files) == 0:
                    failed_files.append((psg_file.name, f"No matching hypnogram for ID {subject_id}"))
                    continue
                
                # Use the first match
                hypno_path = hypno_files[0]

                features, error = self.extract_features(psg_file, hypno_path)
                if error or features is None:
                    failed_files.append((psg_file.name, error))
                    continue

                # Classify
                label = self.classify_insomnia_subtype(features)
                features['insomnia_subtype'] = label
                features['subject_id'] = subject_id

                records.append(features)

            except Exception as e:
                failed_files.append((psg_file.name, traceback.format_exc()))
                continue

        # Save results
        if len(records) > 0:
            df = pd.DataFrame(records)
            
            print("\nInsomnia Subtype Distribution:")
            print(df['insomnia_subtype'].value_counts())
            
            print("\nSleep Metrics Summary:")
            print(df[['SOL_minutes', 'WASO_minutes', 'sleep_efficiency_percent']].describe())
            
            Path(self.output_file).parent.mkdir(exist_ok=True)
            df.to_csv(self.output_file, index=False)
            print(f"\nSaved output to: {self.output_file}")
        else:
            print("No records processed.")
            
        if len(failed_files) > 0:
            print(f"\nFailed files ({len(failed_files)}):")
            # Print first 10 failures to help debug
            for name, err in failed_files[:10]:
                print(f"  {name}: {err}")


if __name__ == "__main__":
    # CHANGE THIS PATH TO YOUR DATA FOLDER
    # Ensure this matches your actual folder name
    DATA_DIR = "sleep_edf_data" 
    OUTPUT_FILE = "processed_data/ml_ready_dataset.csv"
    
    processor = SleepDataProcessor(
        input_dir=DATA_DIR,
        output_file=OUTPUT_FILE
    )
    processor.process_all_files()