from .fade_controller import FadeController

class VideoEffectsManager:
    def __init__(self, window_width, window_height, video_batch):
        self.window_width = window_width
        self.window_height = window_height
        
        # Initialize video effects
        self.fade_controller = FadeController(window_width, window_height, video_batch)
        
    def update_effects(self, elapsed_time):
        """Update all video effects"""
        self.fade_controller.update(elapsed_time)
        
    def set_total_duration(self, duration):
        """Set total duration for time-based effects"""
        self.fade_controller.set_total_duration(duration)
        
    def enable_fade(self, enabled=True):
        """Enable/disable fade effects"""
        self.fade_controller.enable_fade(enabled)
        
    def set_fade_durations(self, fade_in=2.0, fade_out=2.0):
        """Configure fade timing"""
        self.fade_controller.set_fade_durations(fade_in, fade_out)
