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
        import math
        
        R = self.size  # Circle radius
        
        """Arc of influence"""
        self.circumference = shapes.Arc(
            self.x, self.y,  # Circle center
            R,               # Radius
            angle=360,       # Full circle outline
            thickness=1,     # Line width
            color=(100, 100, 100),
            batch=self.batch
        )
        self.circumference.opacity = 60
        
        """Earth: Downward pointing triangle"""
        # Triangle vertices (120° apart, starting at 270°)
        vertex1_x = self.x
        vertex1_y = self.y - R                                    # Bottom point (270°)
        
        vertex2_x = self.x - R * math.cos(math.radians(30))      # Top-left (150°)
        vertex2_y = self.y + R * math.sin(math.radians(30))
        
        vertex3_x = self.x + R * math.cos(math.radians(30))      # Top-right (30°)
        vertex3_y = self.y + R * math.sin(math.radians(30))
        
        self.base_rect = shapes.Triangle(
            vertex1_x, vertex1_y,  # Bottom
            vertex2_x, vertex2_y,  # Top-left
            vertex3_x, vertex3_y,  # Top-right
            color=tuple(self.base_color), batch=self.batch
        )
        self.base_rect.opacity = 160

        """Horizontal dividing line"""
        self.line = shapes.Line(
            self.x - R * math.cos(math.radians(30)), self.y,  # Start at left edge of triangle
            self.x + R * math.cos(math.radians(30)), self.y,  # End at right edge of triangle
            thickness=3,
            color=tuple(self.base_color),
            batch=self.batch
        )
        self.line.opacity = 160
        
        # Crystal spikes that emerge with audio (small rectangles at corners/edges)
        self.crystals = []
        for i in range(8):
            angle = math.radians(i * 45)  # 45° intervals for octagon vertices
            
            # Octagon vertex position ON the circumference
            vertex_x = self.x + R * math.cos(angle)
            vertex_y = self.y + R * math.sin(angle)
            
            # Small square crystal AT the vertex point
            crystal = shapes.Rectangle(
                int(vertex_x - 2), int(vertex_y - 2),  # Center 4x4 square on vertex
                4, 4,  # Small square
                color=tuple(self.base_color), batch=self.batch
            )
            crystal.opacity = 0
            self.crystals.append(crystal)
    
    def create_wind_shape(self):
        R = self.size  # Circle radius
        
        """Arc of influence"""
        self.circumference = shapes.Arc(
            self.x, self.y,  # Circle center
            R,               # Radius
            angle=360,       # Full circle outline
            thickness=1,     # Line width
            color=(100, 100, 100),
            batch=self.batch
        )
        self.circumference.opacity = 60
        
        """Wind: Upward pointing triangle"""
        # Triangle vertices (120° apart, starting at 90°)
        vertex1_x = self.x
        vertex1_y = self.y + R                                    # Top point (90°)
        
        vertex2_x = self.x - R * math.cos(math.radians(30))      # Bottom-left (210°)
        vertex2_y = self.y - R * math.sin(math.radians(30))
        
        vertex3_x = self.x + R * math.cos(math.radians(30))      # Bottom-right (330°)
        vertex3_y = self.y - R * math.sin(math.radians(30))
        
        self.base_rect = shapes.Triangle(
            vertex1_x, vertex1_y,  # Top
            vertex2_x, vertex2_y,  # Bottom-left
            vertex3_x, vertex3_y,  # Bottom-right
            color=tuple(self.base_color), batch=self.batch
        )
        self.base_rect.opacity = 160

        """Horizontal dividing line"""
        self.line = shapes.Line(
            self.x - R * math.cos(math.radians(30)), self.y,  # Start at left edge of triangle
            self.x + R * math.cos(math.radians(30)), self.y,  # End at right edge of triangle
            thickness=3,
            color=tuple(self.base_color),
            batch=self.batch
        )
        self.line.opacity = 160
        
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
        R = self.size  # Circle radius
        
        """Arc of influence"""
        self.circumference = shapes.Arc(
            self.x, self.y,  # Circle center
            R,               # Radius
            angle=360,       # Full circle outline
            thickness=1,     # Line width
            color=(100, 100, 100),
            batch=self.batch
        )
        self.circumference.opacity = 60
        
        """Fire: Upward pointing triangle"""
        # Triangle vertices (120° apart, starting at 90°)
        vertex1_x = self.x
        vertex1_y = self.y + R                                    # Top point (90°)
        
        vertex2_x = self.x - R * math.cos(math.radians(30))      # Bottom-left (210°)
        vertex2_y = self.y - R * math.sin(math.radians(30))
        
        vertex3_x = self.x + R * math.cos(math.radians(30))      # Bottom-right (330°)
        vertex3_y = self.y - R * math.sin(math.radians(30))
        
        self.base_rect = shapes.Triangle(
            vertex1_x, vertex1_y,  # Top
            vertex2_x, vertex2_y,  # Bottom-left
            vertex3_x, vertex3_y,  # Bottom-right
            color=tuple(self.base_color), batch=self.batch
        )
        self.base_rect.opacity = 160
        
        # Flame chevrons (3 V-shaped lines stacked vertically with diminishing sizes)
        self.flame_chevrons = []

        # Three chevrons stacked vertically, getting smaller as they go up
        chevron_configs = [
            (0, self.size * 0.3, 12),    # Bottom chevron - largest
            (0, self.size * 0.6, 8),     # Middle chevron - medium  
            (0, self.size * 0.9, 4),     # Top chevron - smallest
        ]

        for dx, dy, chevron_size in chevron_configs:
            chevron_x = self.x + dx
            chevron_y = self.y + dy
            
            # Create two lines forming a V shape (chevron pointing up)
            left_line = shapes.Line(
                int(chevron_x - chevron_size), int(chevron_y - chevron_size//2),
                int(chevron_x), int(chevron_y + chevron_size//2),
                thickness=2,
                color=tuple(self.base_color), batch=self.batch
            )
            left_line.opacity = 0
            
            right_line = shapes.Line(
                int(chevron_x), int(chevron_y + chevron_size//2),
                int(chevron_x + chevron_size), int(chevron_y - chevron_size//2),
                thickness=2,
                color=tuple(self.base_color), batch=self.batch
            )
            right_line.opacity = 0
            
            self.flame_chevrons.append((left_line, right_line))
    
    def create_water_shape(self):
        R = self.size  # Circle radius
        
        """Arc of influence"""
        self.circumference = shapes.Arc(
            self.x, self.y,  # Circle center
            R,               # Radius
            angle=360,       # Full circle outline
            thickness=1,     # Line width
            color=(100, 100, 100),
            batch=self.batch
        )
        self.circumference.opacity = 60
        
        """Water: Downward pointing triangle"""
        # Triangle vertices (120° apart, starting at 270°)
        vertex1_x = self.x
        vertex1_y = self.y - R                                    # Bottom point (270°)
        
        vertex2_x = self.x - R * math.cos(math.radians(30))      # Top-left (150°)
        vertex2_y = self.y + R * math.sin(math.radians(30))
        
        vertex3_x = self.x + R * math.cos(math.radians(30))      # Top-right (30°)
        vertex3_y = self.y + R * math.sin(math.radians(30))
        
        self.base_rect = shapes.Triangle(
            vertex1_x, vertex1_y,  # Bottom
            vertex2_x, vertex2_y,  # Top-left
            vertex3_x, vertex3_y,  # Top-right
            color=tuple(self.base_color), batch=self.batch
        )
        self.base_rect.opacity = 160
        
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
            self.base_rect.opacity = 20  # Always there # during MIDI activity
        else:
            self.base_rect.opacity = 160  # Visible when no MIDI
        self.base_rect.color = tuple(color)

        self.circumference.color = (120, 120, 120)  # Slightly lighter gray
        circumference_opacity = 60 + int(self.audio_intensity * 30)  # Subtle pulse with audio
        self.circumference.opacity = circumference_opacity

        if hasattr(self, 'line'):
            self.line.color = tuple(color)
            if self.midi_activity > 0.17:
                self.line.opacity = 20  # Hidden during MIDI activity
            else:
                self.line.opacity = 140  # Visible when no MIDI

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
            self.base_rect.opacity = 130  # Visible when no MIDI
        self.base_rect.color = tuple(color)

        self.circumference.color = (120, 120, 120)  # Slightly lighter gray
        circumference_opacity = 60 + int(self.audio_intensity * 30)  # Subtle pulse with audio
        self.circumference.opacity = circumference_opacity

        if hasattr(self, 'line'):
            self.line.color = tuple(color)
            if self.midi_activity > 0.07:
                self.line.opacity = 0  # Hidden during MIDI activity
            else:
                self.line.opacity = 160  # Visible when no MIDI

        stream_opacity = int(min(255, max(0, self.audio_intensity * 200)))  # Quicker fade-in
        for i, stream in enumerate(self.wind_streams):
            stream.color = tuple(color)
            stream.opacity = stream_opacity
            # Streams extend with audio
            stream.width = int((self.size * 2) + self.audio_intensity * 30)
    
    def update_fire(self, color):
        """Fire tips flicker with audio"""
        # Square completely disappears when flames are active, reappears when inactive
        if self.midi_activity > 0.05:
            self.base_rect.opacity = 30  # Hidden during MIDI activity
        else:
            self.base_rect.opacity = 120  # Visible when no MIDI
        self.base_rect.color = tuple(color)

        self.circumference.color = (120, 120, 120)  # Slightly lighter gray
        circumference_opacity = 60 + int(self.audio_intensity * 30)  # Subtle pulse with audio
        self.circumference.opacity = circumference_opacity

        # Only show fire chevrons when there's audio activity
        for i, (left_line, right_line) in enumerate(self.flame_chevrons):
            if self.audio_intensity > 0.02:
                # Flicker effect - different chevrons react differently, bottom chevron most responsive
                flicker_intensity = self.audio_intensity + math.sin(time.time() * (5 + i)) * 0.2
                # Bottom chevron (i=0) gets full intensity, top chevrons get progressively less
                intensity_multiplier = 1.0 - (i * 0.2)  # 1.0, 0.8, 0.6
                chevron_opacity = int(max(0, min(255, flicker_intensity * 240 * intensity_multiplier)))
                
                brighter_color = [min(255, int(c * 1.3)) for c in color]
                
                left_line.color = tuple(brighter_color)
                right_line.color = tuple(brighter_color)
                left_line.opacity = chevron_opacity
                right_line.opacity = chevron_opacity
                
                # Make chevrons grow with audio by increasing thickness
                new_thickness = int(2 + self.audio_intensity * 3 * intensity_multiplier)
                left_line.width = new_thickness
                right_line.width = new_thickness
            else:
                left_line.opacity = 0
                right_line.opacity = 0
    
    def update_water(self, color):
        """Water ripples pulse with audio"""
        # Square completely disappears when ripples are active, reappears when inactive
        if self.midi_activity > 0.02:
            self.base_rect.opacity = 10  # Hidden during MIDI activity
        else:
            self.base_rect.opacity = 120  # Visible when no MIDI
        self.base_rect.color = tuple(color)

        self.circumference.color = (120, 120, 120)  # Slightly lighter gray
        circumference_opacity = 60 + int(self.audio_intensity * 30)  # Subtle pulse with audio
        self.circumference.opacity = circumference_opacity

        for i, ripple in enumerate(self.ripples):
            if self.audio_intensity > 0.02:
                # Ripples fade from center outward
                ripple_opacity = int(max(0, self.audio_intensity * 150 - i * 30))
                ripple.color = tuple(color)
                ripple.opacity = ripple_opacity
                # Make first ripple smaller than the square
                if i == 0:
                    base_radius = self.size * 0.8  # 80% of square size
                else:
                    base_radius = self.size + i * 10  # Subsequent ripples grow outward
                
                # Ensure radius is always positive
                calculated_radius = int(base_radius + self.audio_intensity * 15)
                ripple.radius = max(1, calculated_radius)
            else:
                # Ensure they're completely hidden when no audio
                ripple.opacity = 0
                ripple.radius = 1  # Set to 1 instead of 0 to avoid GL error
    
    def set_position_and_size(self, x, y, size):
        """Update position and size"""
        x, y, size = int(x), int(y), int(size)
        if abs(self.x - x) > 1 or abs(self.y - y) > 1 or abs(self.size - size) > 1:
            self.x = x
            self.y = y
            self.size = size
            # Recreate the shape with new parameters
            self.create_elemental_shape()