import os
import pyglet

class AudioPlayer:
    def __init__(self):
        # Audio player state
        self.audio_source = None
        self.audio_player = None
        self.audio_loaded = False
        self.original_audio_file = None
    
    def load_audio(self, filename):
        """Load an audio file for playback"""
        try:
            print(f"Loading audio file: {filename}")
            if not os.path.exists(filename):
                print(f"❌ Error: Audio file '{filename}' not found!")
                return False
            
            self.audio_source = pyglet.media.load(filename)
            self.audio_player = pyglet.media.Player()
            self.audio_loaded = True
            self.original_audio_file = filename
            print(f"✅ Audio loaded: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Could not load audio: {e}")
            self.audio_loaded = False
            return False

    def get_audio_source(self):
        """Get the loaded audio source for analysis"""
        return self.audio_source

    def play(self):
        """Start or resume audio playback"""
        if self.audio_player and self.audio_loaded:
            self.audio_player.queue(self.audio_source)
            self.audio_player.play()
            return True
        return False
    
    def pause(self):
        """Pause audio playback"""
        if self.audio_player and self.audio_loaded:
            self.audio_player.pause()
            return True
        return False
    
    def restart(self):
        """Restart audio from the beginning"""
        if self.audio_player and self.audio_loaded:
            self.audio_player.delete()
            self.audio_player = pyglet.media.Player()
            self.audio_player.queue(self.audio_source)
            self.audio_player.play()
            return True
        return False
    
    def get_current_time(self):
        """Get current audio playback time"""
        if (self.audio_player and self.audio_loaded and 
            hasattr(self.audio_player, 'time') and self.audio_player.playing):
            try:
                return self.audio_player.time or 0
            except:
                return 0
        return 0
    
    def is_loaded(self):
        """Check if audio is loaded"""
        return self.audio_loaded
    
    def is_playing(self):
        """Check if audio is currently playing"""
        if self.audio_player and self.audio_loaded:
            return self.audio_player.playing
        return False
    
    def get_original_file(self):
        """Get the original audio filename"""
        return self.original_audio_file
    
    def cleanup(self):
        """Clean up audio resources"""
        try:
            if self.audio_player:
                self.audio_player.delete()
                self.audio_player = None
            self.audio_source = None
            self.audio_loaded = False
            self.original_audio_file = None
        except:
            pass