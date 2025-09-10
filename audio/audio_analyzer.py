from config.settings import Settings
from .audio_file_processor import AudioFileProcessor
from .frequency_analyzer import FrequencyAnalyzer  
from .panning_analyzer import PanningAnalyzer

class AudioAnalyzer:
    def __init__(self, sample_rate=Settings.DEFAULT_SAMPLE_RATE, fft_window_size=Settings.FFT_WINDOW_SIZE, fft_hop_length=Settings.FFT_HOP_LENGTH):
       self.sample_rate = sample_rate
       self.channels = 2
       self.audio_capture_active = False
       self.audio_level = 0.0

       # Create specialized processors
       self.file_processor = AudioFileProcessor(sample_rate, fft_window_size, fft_hop_length)
       self.frequency_analyzer = FrequencyAnalyzer()
       self.panning_analyzer = PanningAnalyzer()
       
       # Store processed audio data
       self.audio_data = None
       
       # Legacy properties - initialize with proper keys
       from config import ELEMENT_REGISTRY
       element_names = list(ELEMENT_REGISTRY.get_frequency_bands().keys())
       self.element_frequency_levels = {name: 0.0 for name in element_names}
       self.element_panning = {name: 0.0 for name in element_names}

    def setup_audio_capture(self, audio_source):
        if hasattr(audio_source, 'audio_format'):
            self.sample_rate = audio_source.audio_format.sample_rate
            self.channels = audio_source.audio_format.channels
        else:
            self.sample_rate = Settings.DEFAULT_SAMPLE_RATE
            self.channels = 2
        
        self.audio_capture_active = True
        return True

    def analyze_audio_frequencies(self, audio_file_path):
        """Load and analyze audio file using file processor"""
        self.audio_data = self.file_processor.load_and_analyze(audio_file_path)
        return self.audio_data is not None

    def get_element_frequency_levels_and_panning(self, current_time):
        """Update frequency and panning analysis using specialized processors"""
        if not self.audio_data:
            return
            
        # Run the specialized analyzers
        self.frequency_analyzer.analyze_frequency_levels(self.audio_data, current_time)
        self.panning_analyzer.analyze_panning(self.audio_data, current_time)
        
        # Copy the results to maintain compatibility with existing code
        self.element_frequency_levels.update(self.frequency_analyzer.get_frequency_levels())
        self.element_panning.update(self.panning_analyzer.get_panning_levels())

    def get_audio_level(self, channel_activity, is_playing):
        if is_playing:
            try:
                total_activity = sum(channel_activity.values())
                audio_level = min(1.0, total_activity * 0.8)
                self.audio_level += (audio_level - self.audio_level) * 0.1
                return self.audio_level
            except:
                return 0.0
        return 0.0
