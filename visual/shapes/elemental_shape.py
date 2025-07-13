from pyglet import shapes
import math
import time

class ElementalShape:
    """Base class for elemental shapes with audio reactivity"""
    def __init__(self, x, y, size, batch, element_type, color):
        self.x = int(x)
        self.y = int(y)
        self.size = int(size)
        self.batch = batch
        self.element_type = element_type
        self.base_color = [int(c) for c in color]
        self.audio_intensity = 0.0
        self.target_audio_intensity = 0.0
        
        # Create shapes based on element type
        self.create_elemental_shape()
    
    def create_elemental_shape(self):
        """Create shapes specific to each element"""
        if self.element_type == "EARTH":
            self.create_earth_shape()
        elif self.element_type == "WIND":
            self.create_wind_shape()
        elif self.element_type == "FIRE":
            self.create_fire_shape()
        elif self.element_type == "WATER":
            self.create_water_shape()
    
    def create_earth_shape(self):
        """Earth: Solid square that grows crystals/spikes with audio"""
        # Base solid square
        self.base_rect = shapes.Rectangle(
            self.x - self.size, self.y - self.size, 
            self.size * 2, self.size * 2, 
            color=tuple(self.base_color), batch=self.batch
        )
        self.base_rect.opacity = 160
        
        # Crystal spikes that emerge with audio (small rectangles at corners/edges)
        self.crystals = []
        spike_positions = [
            (self.size * 1.2, 0),           # Right
            (-self.size * 1.2, 0),          # Left  
            (0, self.size * 1.2),           # Top
            (0, -self.size * 1.2),          # Bottom
            (self.size * 0.8, self.size * 0.8),   # Top-right
            (-self.size * 0.8, self.size * 0.8),  # Top-left
            (self.size * 0.8, -self.size * 0.8),  # Bottom-right
            (-self.size * 0.8, -self.size * 0.8)  # Bottom-left
        ]
        
        for dx, dy in spike_positions:
            crystal = shapes.Rectangle(
                int(self.x + dx - 3), int(self.y + dy - 8), 6, 16,
                color=tuple(self.base_color), batch=self.batch
            )
            crystal.opacity = 0
            self.crystals.append(crystal)
    
    def create_wind_shape(self):
        """Wind: Flowing lines/curves that ripple with audio"""
        # Base square (like other elements)
        self.base_rect = shapes.Rectangle(
            self.x - self.size, self.y - self.size, 
            self.size * 2, self.size * 2, 
            color=tuple(self.base_color), batch=self.batch
        )
        self.base_rect.opacity = 100
        
        # Wind streams (horizontal lines that shift with audio)
        self.wind_streams = []
        for i in range(6):
            y_offset = (i - 2.5) * 8
            stream = shapes.Rectangle(
                self.x - self.size, int(self.y + y_offset - 1), 
                self.size * 2, 2, color=tuple(self.base_color), batch=self.batch
            )
            stream.opacity = 0
            self.wind_streams.append(stream)
    
    def create_fire_shape(self):
        """Fire: Triangular flames that dance with audio"""
        # Base square (like other elements)
        self.base_rect = shapes.Rectangle(
            self.x - self.size, self.y - self.size, 
            self.size * 2, self.size * 2, 
            color=tuple(self.base_color), batch=self.batch
        )
        self.base_rect.opacity = 140
        
        # Flame tips (small circles that flicker with audio)
        self.flame_tips = []
        flame_positions = [
            (0, self.size),                    # Main tip
            (-self.size * 0.4, self.size * 0.7),    # Left tip
            (self.size * 0.4, self.size * 0.7),     # Right tip
            (-self.size * 0.2, self.size * 1.2),    # Left high
            (self.size * 0.2, self.size * 1.2),     # Right high
        ]
        
        for dx, dy in flame_positions:
            tip = shapes.Circle(
                int(self.x + dx), int(self.y + dy), 2,  # Changed from 4 to 2
                color=tuple(self.base_color), batch=self.batch
            )
            tip.opacity = 0
            self.flame_tips.append(tip)
    
    def create_water_shape(self):
        """Water: Flowing drops/waves that pulse with audio"""
        # Base square (like other elements)
        self.base_rect = shapes.Rectangle(
            self.x - self.size, self.y - self.size, 
            self.size * 2, self.size * 2, 
            color=tuple(self.base_color), batch=self.batch
        )
        self.base_rect.opacity = 120
        
        # Water ripples (concentric circles that expand with audio)
        self.ripples = []
        for i in range(4):
            ripple_size = self.size + (i + 1) * 5
            ripple = shapes.Circle(
                self.x, self.y, ripple_size, 
                color=tuple(self.base_color), batch=self.batch
            )
            ripple.opacity = 0
            self.ripples.append(ripple)
    
    def update(self, dt, color, audio_intensity=0.0, midi_activity=0.0):
        """Update the elemental shape based on audio and MIDI"""
        # Ensure color is integers
        color = [int(c) for c in color]
    
        # Smooth audio intensity (for elemental effects)
        self.target_audio_intensity = audio_intensity
        self.audio_intensity += (self.target_audio_intensity - self.audio_intensity) * dt * 8
        
        # Store MIDI activity (for fade animation)
        self.midi_activity = midi_activity
    
        # Update based on element type
        if self.element_type == "EARTH":
            self.update_earth(color)
        elif self.element_type == "WIND":
            self.update_wind(color)
        elif self.element_type == "FIRE":
            self.update_fire(color)
        elif self.element_type == "WATER":
            self.update_water(color)
    
    def update_earth(self, color):
        """Earth crystals grow with audio"""
        # Use MIDI activity for square fade (not audio_intensity)
        if self.midi_activity > 0.02:
            self.base_rect.opacity = 0  # Hidden during MIDI activity
        else:
            self.base_rect.opacity = 160  # Visible when no MIDI
        self.base_rect.color = tuple(color)
        
        # Use audio_intensity for crystal effects
        crystal_opacity = int(min(255, max(0, self.audio_intensity * 220)))
        for i, crystal in enumerate(self.crystals):
            # Much more saturated crystals - boost all color channels significantly
            brighter_color = [min(255, int(c * 2.0)) for c in color]  # Increased from 1.2 to 2.0
            crystal.color = tuple(brighter_color)
            crystal.opacity = crystal_opacity
            # Make crystals grow with audio
            crystal.height = int(16 + self.audio_intensity * 12)
    
    def update_wind(self, color):
        """Wind streams flow with audio"""
        # Square completely disappears when streams are active, reappears when inactive
        if self.midi_activity > 0.02:
            self.base_rect.opacity = 0  # Hidden during MIDI activity
        else:
            self.base_rect.opacity = 160  # Visible when no MIDI
        self.base_rect.color = tuple(color)
        
        stream_opacity = int(min(255, max(0, self.audio_intensity * 200)))  # Quicker fade-in
        for i, stream in enumerate(self.wind_streams):
            stream.color = tuple(color)
            stream.opacity = stream_opacity
            # Streams extend with audio
            stream.width = int((self.size * 2) + self.audio_intensity * 30)
    
    def update_fire(self, color):
        """Fire tips flicker with audio"""
        # Square completely disappears when flames are active, reappears when inactive
        if self.midi_activity > 0.02:
            self.base_rect.opacity = 0  # Hidden during MIDI activity
        else:
            self.base_rect.opacity = 160  # Visible when no MIDI
        self.base_rect.color = tuple(color)
        
        # Only show fire tips when there's audio activity
        for i, tip in enumerate(self.flame_tips):
            if self.audio_intensity > 0.02:  # Lower threshold for quicker response
                # Flicker effect - different tips react differently
                flicker_intensity = self.audio_intensity + math.sin(time.time() * (5 + i)) * 0.2
                tip_opacity = int(max(0, min(255, flicker_intensity * 240)))  # Quicker fade-in
                brighter_color = [min(255, int(c * 1.3)) for c in color]
                tip.color = tuple(brighter_color)
                tip.opacity = tip_opacity
                # Tips grow with audio - BIGGER FIRE ANIMATION
                tip.radius = int(3 + self.audio_intensity * 5)
            else:
                tip.opacity = 0  # Hide when inactive
    
    def update_water(self, color):
        """Water ripples pulse with audio"""
        # Square completely disappears when ripples are active, reappears when inactive
        if self.midi_activity > 0.02:
            self.base_rect.opacity = 0  # Hidden during MIDI activity
        else:
            self.base_rect.opacity = 160  # Visible when no MIDI
        self.base_rect.color = tuple(color)
        
        for i, ripple in enumerate(self.ripples):
            # Ripples fade from center outward
            ripple_opacity = int(max(0, self.audio_intensity * 150 - i * 30))  # Quicker fade-in
            ripple.color = tuple(color)
            ripple.opacity = ripple_opacity
            # Ripples expand with audio
            base_radius = self.size + (i + 1) * 10
            ripple.radius = int(base_radius + self.audio_intensity * 15)
    
    def set_position_and_size(self, x, y, size):
        """Update position and size"""
        x, y, size = int(x), int(y), int(size)
        if abs(self.x - x) > 1 or abs(self.y - y) > 1 or abs(self.size - size) > 1:
            self.x = x
            self.y = y
            self.size = size
            # Recreate the shape with new parameters
            self.create_elemental_shape()