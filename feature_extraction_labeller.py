"""
EEG Feature Extraction - OSA Classification Version (v7)
- Uses robust file loading & spectral features.
- CLASSIFICATION CHANGE:
- High SOL -> Sleep Onset Insomnia
- High WASO -> Sleep Maintenance Insomnia
- Low Efficiency -> OSA (Obstructive Sleep Apnea)
- Normal -> Good Sleeper
- Uses "Grading on a Curve" (Percentiles) to handle the data offset issues.
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
        
        # Frequency bands
        self.frequency_bands = {
            'delta': (0.5, 4), 'theta': (4, 8), 'alpha': (8, 13),
            'beta': (13, 30), 'sigma': (11, 16)
        }

    # ==================== HYPNOGRAM LOADING ====================
    def load_hypnogram(self, filepath):
        try:
            annotations = mne.read_annotations(filepath)
            if len(annotations) == 0: return None
            
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

    # ==================== METRICS CALCULATION (RAW) ====================
    def calculate_sleep_metrics(self, sleep_stages):
        if sleep_stages is None or len(sleep_stages) == 0:
            return None

        # 1. SOL (Raw - Relative to start of recording)
        nrem_stages = {1, 2, 3, 4}
        first_nrem = None
        for i, stage in enumerate(sleep_stages):
            if stage in nrem_stages:
                first_nrem = i
                break
        
        if first_nrem is None:
            SOL = len(sleep_stages) * 0.5
            sleep_start_idx = len(sleep_stages)
        else:
            SOL = first_nrem * 0.5
            sleep_start_idx = first_nrem

        # 2. Find Sleep End
        last_sleep_idx = None
        for i, stage in enumerate(sleep_stages):
            if stage > 0 and stage != 9:
                last_sleep_idx = i
        
        # 3. WASO & Awakenings (Between Sleep Start and End)
        WASO = 0.0
        num_awakenings = 0
        
        if first_nrem is not None and last_sleep_idx is not None:
            sleep_period = sleep_stages[first_nrem : last_sleep_idx + 1]
            
            WASO = np.sum(sleep_period == 0) * 0.5
            
            in_wake = False
            for stage in sleep_period:
                if stage == 0:
                    if not in_wake:
                        num_awakenings += 1
                        in_wake = True
                elif stage != 9:
                    in_wake = False

        # 4. Early Wake
        early_wake_val = 0.0
        if last_sleep_idx is not None:
            valid_tail = sleep_stages[last_sleep_idx:]
            valid_tail = valid_tail[valid_tail != 9]
            early_wake_val = max(0, (len(valid_tail) - 1) * 0.5)

        # 5. Sleep Efficiency (Classic definition using full recording)
        valid_stages = sleep_stages[sleep_stages != 9]
        time_in_bed = len(valid_stages) * 0.5
        total_sleep_time = np.sum(valid_stages > 0) * 0.5

        sleep_efficiency = 0
        if time_in_bed > 0:
            sleep_efficiency = (total_sleep_time / time_in_bed) * 100

        return {
            'SOL_minutes': SOL,
            'WASO_minutes': WASO,
            'num_awakenings': num_awakenings,
            'early_morning_awakening_mins': early_wake_val,
            'sleep_efficiency_percent': sleep_efficiency,
            'total_sleep_time_minutes': total_sleep_time
        }

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
            raw = mne.io.read_raw_edf(psg_file, preload=True, verbose=False)
            eeg_channels = [ch for ch in raw.ch_names if 'EEG' in ch]
            if not eeg_channels: return None, "No EEG channels found"
            
            selected_channel = eeg_channels[0]
            for ch in eeg_channels:
                if 'Fpz-Cz' in ch:
                    selected_channel = ch
                    break
            
            raw.pick_channels([selected_channel])
            eeg_data = raw.get_data()[0]
            fs = raw.info['sfreq']

            sleep_stages = self.load_hypnogram(hypnogram_file)
            if sleep_stages is None: return None, "Hypnogram read failure"

            metrics = self.calculate_sleep_metrics(sleep_stages)
            if metrics is None: return None, "Invalid metrics"

            spectral = self.calculate_spectral_features(eeg_data, fs)
            
            stats_dict = {
                'mean_amplitude': np.mean(eeg_data),
                'std_amplitude': np.std(eeg_data),
                'skewness': stats.skew(eeg_data),
                'kurtosis': stats.kurtosis(eeg_data)
            }

            feature_dict = {'eeg_channel': selected_channel}
            feature_dict.update(spectral)
            feature_dict.update(stats_dict)
            feature_dict.update(metrics)

            return feature_dict, None

        except Exception as e:
            return None, f"Exception: {e}"

    # ==================== PERCENTILE CLASSIFIER (OSA UPDATE) ====================
    def apply_percentile_classification(self, df):
        """
        Classify subjects based on the distribution of the data (The Curve).
        Top 25% (Worst) in each category get the flag.
        """
        print("\n--- Applying Percentile-Based Classification ---")
        
        # Calculate Thresholds (Worst 25%)
        sol_thresh = df['SOL_minutes'].quantile(0.75)
        waso_thresh = df['WASO_minutes'].quantile(0.75)
        # Efficiency: Lower is worse, so use 25th percentile
        eff_thresh = df['sleep_efficiency_percent'].quantile(0.25)
        
        print(f"Thresholds (Worst Quartile):")
        print(f"  SOL (Onset)  : > {sol_thresh:.2f} min")
        print(f"  WASO (Maint) : > {waso_thresh:.2f} min")
        print(f"  Eff (OSA)    : < {eff_thresh:.2f} %")

        labels = []
        for idx, row in df.iterrows():
            has_onset = row['SOL_minutes'] > sol_thresh
            has_maint = row['WASO_minutes'] > waso_thresh
            has_eff = row['sleep_efficiency_percent'] < eff_thresh
            
            if has_onset and has_maint:
                labels.append("Mixed_Insomnia")
            elif has_onset:
                labels.append("Sleep_Onset_Insomnia")
            elif has_maint:
                labels.append("Sleep_Maintenance_Insomnia")
            elif has_eff:
                # REPLACED "Poor_Sleeper" with "OSA"
                labels.append("OSA")
            else:
                labels.append("Good_Sleeper")
                
        df['insomnia_subtype'] = labels
        return df

    def process_all_files(self):
        print("Starting processing...")
        data_path = Path(self.input_dir)
        if not data_path.is_dir():
            print(f"CRITICAL ERROR: Directory '{self.input_dir}' not found.")
            return

        psg_files = sorted(list(data_path.glob("**/*-PSG.edf")))
        print(f"Found {len(psg_files)} PSG files.")

        if len(psg_files) == 0:
            print("No *-PSG.edf files found.")
            return

        records = []
        failed_files = []

        for psg_file in tqdm(psg_files, desc="Extraction"):
            try:
                base_stem = psg_file.name.split('-')[0]
                subject_id = base_stem[:6]
                
                hypno_files = list(psg_file.parent.glob(f"{subject_id}*-Hypnogram.edf"))
                if len(hypno_files) == 0:
                    hypno_files = list(data_path.glob(f"**/{subject_id}*-Hypnogram.edf"))

                if len(hypno_files) == 0:
                    failed_files.append((psg_file.name, "No matching hypnogram"))
                    continue
                
                hypno_path = hypno_files[0]

                features, error = self.extract_features(psg_file, hypno_path)
                if error or features is None:
                    failed_files.append((psg_file.name, error))
                    continue

                features['subject_id'] = subject_id
                records.append(features)

            except Exception as e:
                failed_files.append((psg_file.name, traceback.format_exc()))
                continue

        if len(records) > 0:
            df = pd.DataFrame(records)
            
            # Apply the OSA classification logic
            df = self.apply_percentile_classification(df)
            
            print("\nFinal Class Distribution:")
            print(df['insomnia_subtype'].value_counts())
            
            Path(self.output_file).parent.mkdir(exist_ok=True)
            df.to_csv(self.output_file, index=False)
            print(f"\nSaved output to: {self.output_file}")
        else:
            print("No records processed.")
            
        if len(failed_files) > 0:
            print(f"\nFailed files ({len(failed_files)}):")
            for name, err in failed_files[:5]:
                print(f"  {name}: {err}")


if __name__ == "__main__":
    DATA_DIR = "sleep_edf_data" 
    OUTPUT_FILE = "processed_data/ml_ready_dataset.csv"
    
    processor = SleepDataProcessor(
        input_dir=DATA_DIR,
        output_file=OUTPUT_FILE
    )
    processor.process_all_files()