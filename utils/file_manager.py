import os
import glob
from config.settings import Settings

class FileManager:
    @staticmethod
    def ensure_directories():
        """Create necessary directories if they don't exist"""
        directories = [
            Settings.ASSETS_DIR,
            Settings.AUDIO_DIR,
            Settings.MIDI_DIR,
            Settings.OUTPUT_DIR,
            Settings.OUTPUT_VIDEOS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        print("✅ Directory structure verified")
    
    @staticmethod
    def find_midi_file(filename=None):
        """Find MIDI file in assets/midi directory"""
        if filename:
            path = os.path.join(Settings.MIDI_DIR, filename)
            if os.path.exists(path):
                return path
        
        # Try default filename
        default_path = os.path.join(Settings.MIDI_DIR, Settings.DEFAULT_MIDI_FILE)
        if os.path.exists(default_path):
            return default_path
        
        # Find any MIDI file
        midi_files = glob.glob(os.path.join(Settings.MIDI_DIR, "*.mid")) + \
                    glob.glob(os.path.join(Settings.MIDI_DIR, "*.midi"))
        
        if midi_files:
            return midi_files[0]  # Return first found
        
        return None
    
    @staticmethod
    def find_audio_file(filename=None):
        """Find audio file in assets/audio directory"""
        if filename:
            path = os.path.join(Settings.AUDIO_DIR, filename)
            if os.path.exists(path):
                return path
        
        # Try default filename
        default_path = os.path.join(Settings.AUDIO_DIR, Settings.DEFAULT_AUDIO_FILE)
        if os.path.exists(default_path):
            return default_path
        
        # Find any audio file
        audio_files = glob.glob(os.path.join(Settings.AUDIO_DIR, "*.mp3")) + \
                     glob.glob(os.path.join(Settings.AUDIO_DIR, "*.wav")) + \
                     glob.glob(os.path.join(Settings.AUDIO_DIR, "*.flac"))
        
        if audio_files:
            return audio_files[0]  # Return first found
        
        return None
    
    @staticmethod
    def get_output_video_path(filename):
        """Get full path for output video"""
        return os.path.join(Settings.OUTPUT_VIDEOS_DIR, filename)
    
    @staticmethod
    def list_available_files():
        """List all available MIDI and audio files"""
        midi_files = glob.glob(os.path.join(Settings.MIDI_DIR, "*.mid")) + \
                    glob.glob(os.path.join(Settings.MIDI_DIR, "*.midi"))
        audio_files = glob.glob(os.path.join(Settings.AUDIO_DIR, "*.mp3")) + \
                     glob.glob(os.path.join(Settings.AUDIO_DIR, "*.wav")) + \
                     glob.glob(os.path.join(Settings.AUDIO_DIR, "*.flac"))
        
        print("📁 Available files:")
        print("  MIDI files:")
        for f in midi_files:
            print(f"    - {os.path.basename(f)}")
        print("  Audio files:")
        for f in audio_files:
            print(f"    - {os.path.basename(f)}")
        
        return midi_files, audio_files