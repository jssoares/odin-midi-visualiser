from pyglet import shapes

class FadeController:
    def __init__(self, window_width, window_height, batch):
        self.window_width = window_width
        self.window_height = window_height
        self.batch = batch
        
        # Fade timing settings
        self.fade_in_duration = 2.0   # seconds
        self.fade_out_duration = 2.0  # seconds
        self.current_fade_alpha = 0.0 # 0.0 = black, 1.0 = normal
        
        # Track total duration for fade out timing
        self.total_duration = None
        self.fade_enabled = True
        
        # Create black overlay rectangle
        self.fade_overlay = shapes.Rectangle(
            0, 0, window_width, window_height,
            color=(0, 0, 0), batch=batch
        )
        self.fade_overlay.opacity = 255  # Start fully black
        
    def set_total_duration(self, duration):
        """Set the total duration for calculating fade out timing"""
        self.total_duration = duration
        
    def update(self, elapsed_time):
        """Update fade alpha based on elapsed time"""
        if not self.fade_enabled:
            self.current_fade_alpha = 1.0
            self.fade_overlay.opacity = 0
            return
            
        if elapsed_time < self.fade_in_duration:
            # Fade in from black (0.0 to 1.0)
            self.current_fade_alpha = elapsed_time / self.fade_in_duration
        elif self.total_duration and elapsed_time > (self.total_duration - self.fade_out_duration):
            # Fade out to black (1.0 to 0.0)
            remaining = self.total_duration - elapsed_time
            self.current_fade_alpha = max(0.0, remaining / self.fade_out_duration)
        else:
            # Normal playback
            self.current_fade_alpha = 1.0
            
        # Update overlay opacity (inverse of fade alpha)
        overlay_alpha = int((1.0 - self.current_fade_alpha) * 255)
        self.fade_overlay.opacity = max(0, min(255, overlay_alpha))
        
    def enable_fade(self, enabled=True):
        """Enable or disable fade effects"""
        self.fade_enabled = enabled
        if not enabled:
            self.fade_overlay.opacity = 0
            
    def set_fade_durations(self, fade_in=2.0, fade_out=2.0):
        """Configure fade timing"""
        self.fade_in_duration = fade_in
        self.fade_out_duration = fade_out