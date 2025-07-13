from .background_pattern import BackgroundPattern

class VisualManager:
    def __init__(self, window_width, window_height, grid_batch):
        self.window_width = window_width
        self.window_height = window_height
        
        # Initialize visual effects
        self.background_pattern = BackgroundPattern(window_width, window_height, grid_batch)
    
    def update_effects(self, dt, total_audio_activity=0.0):
        """Update all visual effects"""
        self.background_pattern.update(dt, total_audio_activity)