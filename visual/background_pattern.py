import math
import time
from pyglet          import shapes
from config.settings import Settings

class BackgroundPattern:
    def __init__(self, window_width, window_height, batch):
        self.window_width = window_width
        self.window_height = window_height
        self.batch = batch
        
        # Pattern state
        self.audio_intensity = 0.0
        self.target_audio_intensity = 0.0
        self.pattern_elements = []
        
        # Create pattern elements if enabled
        if Settings.BACKGROUND_PATTERN_ENABLED:
            self.create_pattern()
    
    def create_pattern(self):
        """Create a lattice/grid of lines that can undulate"""
        spacing = Settings.BACKGROUND_PATTERN_SPACING
        
        # Create vertical lines
        for x in range(0, self.window_width, spacing):
            line = shapes.Line(x, 0, x, self.window_height, color=(40, 50, 60), batch=self.batch)
            line.opacity = Settings.BACKGROUND_PATTERN_OPACITY
            line.base_x1 = x
            line.base_x2 = x
            line.direction = 'vertical'
            self.pattern_elements.append(line)
        
        # Create horizontal lines  
        for y in range(0, self.window_height, spacing):
            line = shapes.Line(0, y, self.window_width, y, color=(40, 50, 60), batch=self.batch)
            line.opacity = Settings.BACKGROUND_PATTERN_OPACITY
            line.base_y1 = y
            line.base_y2 = y
            line.direction = 'horizontal'
            self.pattern_elements.append(line)
        
    def update(self, dt, total_audio_activity=0.0):
        """Update lattice with undulating waves"""
        if not Settings.BACKGROUND_PATTERN_ENABLED or not self.pattern_elements:
            return
        
        # Smooth audio intensity
        self.target_audio_intensity = min(1.0, total_audio_activity)
        self.audio_intensity += (self.target_audio_intensity - self.audio_intensity) * dt * 4
        
        current_time = time.time()

        wave_speed     = 1.5 + self.audio_intensity * 2  # Faster waves with more audio
        wave_amplitude = 15 * self.audio_intensity       # Bigger waves with more audio

        for line in self.pattern_elements:
            if line.direction == 'vertical':
                # Vertical lines undulate horizontally
                wave_phase = current_time * wave_speed + line.base_x1 * 0.002
                offset     = math.sin(wave_phase) * wave_amplitude
                line.x     = int(line.base_x1 + offset)
                line.x2    = int(line.base_x2 + offset)
            else:
                # Horizontal lines undulate vertically  
                wave_phase = current_time * wave_speed + line.base_y1 * 0.002
                offset     = math.sin(wave_phase) * wave_amplitude
                line.y     = int(line.base_y1 + offset)
                line.y2    = int(line.base_y2 + offset)