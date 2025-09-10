import librosa
import numpy as np
from config.settings import Settings

class AudioFileProcessor:
    def __init__(self, sample_rate=Settings.DEFAULT_SAMPLE_RATE, 
                 fft_window_size=Settings.FFT_WINDOW_SIZE, 
                 fft_hop_length=Settings.FFT_HOP_LENGTH):
        self.sample_rate = sample_rate
        self.fft_window_size = fft_window_size
        self.fft_hop_length = fft_hop_length
        
    def load_and_analyze(self, audio_file_path):
        """Load audio file and compute STFT for both channels"""
        if not audio_file_path:
            return None
            
        try:
            print("🎵 Loading audio file...")
            
            # Load audio with librosa - keep stereo
            y, sr = librosa.load(audio_file_path, sr=self.sample_rate, mono=False)
            
            # Handle mono files
            if y.ndim == 1:
                y = np.stack([y, y])  # Convert mono to stereo
            
            # Compute STFT for both channels
            stft_left = np.abs(librosa.stft(y[0], n_fft=self.fft_window_size, hop_length=self.fft_hop_length))
            stft_right = np.abs(librosa.stft(y[1], n_fft=self.fft_window_size, hop_length=self.fft_hop_length))
            
            # Create time and frequency arrays
            time_frames = librosa.frames_to_time(
                np.arange(stft_left.shape[1]), 
                sr=sr, 
                hop_length=self.fft_hop_length
            )
            frequency_bins = librosa.fft_frequencies(sr=sr, n_fft=self.fft_window_size)
            
            print(f"✅ Audio analysis complete: {len(time_frames)} time frames, {len(frequency_bins)} frequency bins")
            
            return {
                'stft_left': stft_left,
                'stft_right': stft_right,
                'time_frames': time_frames,
                'frequency_bins': frequency_bins,
                'sample_rate': sr
            }
            
        except Exception as e:
            print(f"❌ Audio analysis failed: {e}")
            return None
