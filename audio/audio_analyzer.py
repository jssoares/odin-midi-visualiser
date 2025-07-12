import librosa
import numpy as np
from collections import deque

from config.settings import Settings

class AudioAnalyzer:
    def __init__(self, sample_rate=Settings.DEFAULT_SAMPLE_RATE, fft_window_size=Settings.FFT_WINDOW_SIZE, fft_hop_length=Settings.FFT_HOP_LENGTH):

        # FFT Analysis properties
        self.fft_window_size = fft_window_size
        self.fft_hop_length = fft_hop_length
        self.sample_rate = sample_rate
        self.fft_update_rate = 60  # Hz
        self.last_fft_time = 0.0

        # Audio frequency band mapping for elemental reactivity
        self.frequency_bands = {
            'EARTH': (20, 250),      # Bass frequencies (extended range)
            'WATER': (250, 1000),    # Low-mid frequencies (wider range)
            'FIRE': (1000, 4000),    # Mid-high frequencies (wider range)
            'WIND': (4000, 22050)    # High frequencies (extended to Nyquist)
        }

        # Store current frequency amplitude levels from audio analysis
        self.element_frequency_levels = {
            'EARTH': 0.0,
            'WATER': 0.0, 
            'FIRE': 0.0,
            'WIND': 0.0
        }

        # Panning analysis
        self.current_pan = 0.0  # -1.0 (left) to 1.0 (right)
        self.pan_history = deque(maxlen=10)  # Smooth pan changes

        # Audio analysis for Odin's reactivity
        self.audio_samples = deque(maxlen=1024)  # Store recent audio samples
        self.audio_level = 0.0

        # Add new audio capture properties:
        self.audio_buffer = deque(maxlen=4096)  # Store raw audio samples
        self.audio_capture_active = False

        self.audio_stft_left = None
        self.audio_stft_right = None
        self.audio_times = None
        self.frequency_bins = None

        self.element_panning = {}

    def setup_audio_capture(self, audio_source):
        # Get audio format info
        if hasattr(audio_source, 'audio_format'):
            self.sample_rate = audio_source.audio_format.sample_rate
            self.channels = audio_source.audio_format.channels
        else:
            self.sample_rate = Settings.DEFAULT_SAMPLE_RATE
            self.channels = 2
        
        self.audio_capture_active = True
        return True
    
    def analyze_audio_frequencies(self, audio_file_path):
        """Pre-analyze the entire audio file for frequency content WITH STEREO"""
        if not audio_file_path:
            return False
        
        try:
            print("🎵 Analyzing audio frequencies...")
            
            # Load audio file with librosa - KEEP STEREO
            y, sr = librosa.load(audio_file_path, sr=self.sample_rate, mono=False)
            
            # Handle mono files
            if y.ndim == 1:
                y = np.stack([y, y])  # Convert mono to stereo
            
            # Compute STFT for LEFT and RIGHT channels separately
            self.audio_stft_left = np.abs(librosa.stft(y[0], n_fft=self.fft_window_size, hop_length=self.fft_hop_length))
            self.audio_stft_right = np.abs(librosa.stft(y[1], n_fft=self.fft_window_size, hop_length=self.fft_hop_length))
            
            # Create time and frequency arrays
            self.audio_times = librosa.frames_to_time(
                np.arange(self.audio_stft_left.shape[1]), 
                sr=sr, 
                hop_length=self.fft_hop_length
            )
            self.frequency_bins = librosa.fft_frequencies(sr=sr, n_fft=self.fft_window_size)
            
            print(f"✅ Stereo audio analysis complete: {len(self.audio_times)} time frames, {len(self.frequency_bins)} frequency bins")
            return True
            
        except Exception as e:
            print(f"❌ Audio analysis failed: {e}")
            return False

    def get_element_frequency_levels_and_panning(self, current_time):
        """Extract frequency levels AND panning for each element at current playback time"""
        if self.audio_stft_left is None or self.audio_times is None:
            return
        
        # Find closest time frame in pre-computed analysis
        time_idx = np.searchsorted(self.audio_times, current_time)
        time_idx = min(time_idx, len(self.audio_times) - 1)
        
        if time_idx >= self.audio_stft_left.shape[1]:
            return
        
        # Get frequency spectrum for both channels
        magnitude_spectrum_left = self.audio_stft_left[:, time_idx]
        magnitude_spectrum_right = self.audio_stft_right[:, time_idx]
        
        # Analyze each element's frequency band
        for element, (freq_min, freq_max) in self.frequency_bands.items():
            # Find frequency bin indices for this band
            freq_mask = (self.frequency_bins >= freq_min) & (self.frequency_bins <= freq_max)
            
            if np.any(freq_mask):
                # Sum amplitudes in this frequency range for each channel
                left_amplitude = np.sum(magnitude_spectrum_left[freq_mask])
                right_amplitude = np.sum(magnitude_spectrum_right[freq_mask])
                total_amplitude = left_amplitude + right_amplitude
                
                # Calculate element's frequency level (mono sum)
                band_width = freq_max - freq_min
                normalized_amplitude = np.log1p(total_amplitude / band_width) / 10.0
                normalized_amplitude = min(1.0, normalized_amplitude)
                
                # Apply smoothing for frequency level
                self.element_frequency_levels[element] += (normalized_amplitude - self.element_frequency_levels[element]) * 0.15
                
                # Calculate element's individual panning (-1.0 = left, 1.0 = right)
                if total_amplitude > 0.001:  # Only calculate pan if there's significant signal
                    element_pan = (right_amplitude - left_amplitude) / total_amplitude
                    element_pan = max(-1.0, min(1.0, element_pan))
                    
                    # Smooth the panning
                    if element in self.element_panning:
                        self.element_panning[element] += (element_pan - self.element_panning[element]) * 0.2
                    else:
                        self.element_panning[element] = element_pan
                else:
                    # Decay panning toward center if no signal
                    if element in self.element_panning:
                        self.element_panning[element] *= 0.9
            else:
                # Decay if no frequency content
                self.element_frequency_levels[element] *= 0.85
                if element in self.element_panning:
                    self.element_panning[element] *= 0.9

    def get_audio_level(self, channel_activity, is_playing):
        """Get current audio level for reactive morphing"""
        if is_playing:
            try:
                # Simple audio level estimation based on elemental activity
                # In a real implementation, you'd analyze actual audio data
                total_activity = sum(channel_activity.values())
                audio_level = min(1.0, total_activity * 0.8)
                
                # Smooth the audio level
                self.audio_level += (audio_level - self.audio_level) * 0.1
                return self.audio_level
            except:
                return 0.0
        return 0.0