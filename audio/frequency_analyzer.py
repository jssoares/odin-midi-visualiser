import numpy as np
from config import ELEMENT_REGISTRY

class FrequencyAnalyzer:
    def __init__(self):
        self.frequency_bands = ELEMENT_REGISTRY.get_frequency_bands()
        self.element_frequency_levels = {name: 0.0 for name in self.frequency_bands.keys()}
        
    def analyze_frequency_levels(self, audio_data, current_time):
        """Extract frequency levels for each element at current time"""
        if not audio_data or current_time is None:
            return
            
        stft_left = audio_data['stft_left']
        stft_right = audio_data['stft_right']
        time_frames = audio_data['time_frames']
        frequency_bins = audio_data['frequency_bins']
        
        # Find closest time frame
        time_idx = np.searchsorted(time_frames, current_time)
        time_idx = min(time_idx, len(time_frames) - 1)
        
        if time_idx >= stft_left.shape[1]:
            return
            
        # Get frequency spectrum for both channels
        magnitude_left = stft_left[:, time_idx]
        magnitude_right = stft_right[:, time_idx]
        
        # Analyze each element's frequency band
        for element_name, (freq_min, freq_max) in self.frequency_bands.items():
            freq_mask = (frequency_bins >= freq_min) & (frequency_bins <= freq_max)
            
            if np.any(freq_mask):
                # Sum amplitudes in frequency range
                left_amp = np.sum(magnitude_left[freq_mask])
                right_amp = np.sum(magnitude_right[freq_mask])
                total_amp = left_amp + right_amp
                
                # Normalize amplitude
                band_width = freq_max - freq_min
                normalized_amp = np.log1p(total_amp / band_width) / 10.0
                normalized_amp = min(1.0, normalized_amp)
                
                # Smooth the frequency level
                self.element_frequency_levels[element_name] += (
                    normalized_amp - self.element_frequency_levels[element_name]
                ) * 0.15
            else:
                # Decay if no frequency content
                self.element_frequency_levels[element_name] *= 0.85
    
    def get_frequency_levels(self):
        """Get current frequency levels for all elements"""
        return self.element_frequency_levels.copy()
