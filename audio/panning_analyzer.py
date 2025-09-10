import numpy as np
from collections import deque
from config      import ELEMENT_REGISTRY

class PanningAnalyzer:
    def __init__(self):
        self.frequency_bands = ELEMENT_REGISTRY.get_frequency_bands()
        self.element_panning = {name: 0.0 for name in self.frequency_bands.keys()}
        self.pan_history = deque(maxlen=10)
        
    def analyze_panning(self, audio_data, current_time):
        """Extract stereo panning for each element at current time"""
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
        
        # Analyze panning for each element
        for element_name, (freq_min, freq_max) in self.frequency_bands.items():
            freq_mask = (frequency_bins >= freq_min) & (frequency_bins <= freq_max)
            
            if np.any(freq_mask):
                left_amp = np.sum(magnitude_left[freq_mask])
                right_amp = np.sum(magnitude_right[freq_mask])
                total_amp = left_amp + right_amp
                
                # Calculate panning (-1.0 = left, 1.0 = right)
                if total_amp > 0.001:
                    element_pan = (right_amp - left_amp) / total_amp
                    element_pan = max(-1.0, min(1.0, element_pan))
                    
                    # Smooth the panning
                    if element_name in self.element_panning:
                        self.element_panning[element_name] += (
                            element_pan - self.element_panning[element_name]
                        ) * 0.2
                    else:
                        self.element_panning[element_name] = element_pan
                else:
                    # Decay toward center if no signal
                    if element_name in self.element_panning:
                        self.element_panning[element_name] *= 0.9
            else:
                # Decay if no frequency content
                if element_name in self.element_panning:
                    self.element_panning[element_name] *= 0.9
    
    def get_panning_levels(self):
        """Get current panning levels for all elements"""
        return self.element_panning.copy()
