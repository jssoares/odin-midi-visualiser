import time
import math
import random
from pyglet import shapes, text
from visual.shapes import CurvedOdinShape
from visual.particles import ExplosionParticle
from visual.particles import ExplosionParticle3D

class OdinNode:
    """Special node class for Odin with audio-reactive morphing"""
    def __init__(self, x, y, node_id, batch, instrument_channel=None):
        self.x = int(x)
        self.y = int(y)
        self.original_x = int(x)  # Store original center position
        self.original_y = int(y)
        self.id = node_id
        self.instrument_channel = instrument_channel
        self.base_size = 45
        self.size = self.base_size
        self.target_size = self.base_size
        self.color = [120, 80, 180]  # Purple
        self.target_color = [120, 80, 180]
        self.base_color = [120, 80, 180]
        self.activity = 0
        self.label = "ODIN"
        self.active_notes = set()
        
        # Audio reactivity
        self.audio_intensity = 0.0
        self.audio_smoothed = 0.0
        
        # Jitter properties
        self.jitter_x = 0.0
        self.jitter_y = 0.0
        self.jitter_intensity = 0.0
        
        # Create custom curved shape instead of regular rectangle
        self.curved_shape = CurvedOdinShape(x, y, self.base_size, batch)
        
        # Border effect (keep as rectangle for simplicity)
        self.border = shapes.Rectangle(
            x - self.base_size, y - self.base_size,
            self.base_size * 2, self.base_size * 2,
            color=(150, 200, 255), batch=batch
        )
        self.border.opacity = 0
        
        # Labels (kept in code but hidden)
        self.label_text = text.Label(
            self.label, font_size=14, color=(220, 220, 220, 0),  # Invisible
            x=x, y=y - self.base_size - 25, anchor_x='center', batch=batch
        )
        self.notes_text = text.Label(
            '', font_size=10, color=(180, 255, 180, 0),  # Invisible
            x=x, y=y - self.base_size - 45, anchor_x='center', batch=batch
        )

        # Particle sink properties
        self.particle_sink = []  # Store particles that reach Odin
        self.max_sink_capacity = 500  # Maximum particles Odin can hold
        self.was_large = False  # Track if Odin was previously large to detect contraction
        
    def update(self, dt, audio_level=0.0):
        # Smooth audio level for reactivity
        self.audio_intensity = audio_level
        self.audio_smoothed += (audio_level - self.audio_smoothed) * dt * 8
        
        # Update jitter based on audio
        self.jitter_intensity = self.audio_smoothed * 1.5  # Reduced from 3.0
        
        # Generate audio-reactive jitter
        time_factor = time.time() * 15  # Jitter speed
        self.jitter_x = math.sin(time_factor) * self.jitter_intensity
        self.jitter_y = math.cos(time_factor * 1.3) * self.jitter_intensity
        
        # Smooth size transitions
        self.size += (self.target_size - self.size) * dt * 8
        self.size = max(20, min(120, self.size))  # Larger max size for Odin

        # Check for contraction (was large, now becoming small) - ADD THIS AFTER SIZE UPDATE
        current_is_large = self.size > self.base_size * 1.5
        if self.was_large and not current_is_large and self.particle_sink:
            # Odin is contracting and has particles in sink - EXPLODE!
            return True  # Signal explosion needed
        self.was_large = current_is_large

        # Smooth color transitions
        for i in range(3):
            self.color[i] += (self.target_color[i] - self.color[i]) * dt * 5
            self.color[i] = max(0, min(255, self.color[i]))
        
        # Activity decay
        self.activity = max(0, min(1, self.activity * 0.92))
        
        # Current position with jitter
        current_x = int(self.x + self.jitter_x)
        current_y = int(self.y + self.jitter_y)
        
        # Update curved shape with audio reactivity
        self.curved_shape.set_position_and_size(current_x, current_y, int(self.size))
        self.curved_shape.update(dt, self.color, self.audio_smoothed, int(self.size))
        
        # Update border for active nodes
        if self.activity > 0.2:
            new_size = int(self.size)
            self.border.x = current_x - new_size - 3
            self.border.y = current_y - new_size - 3
            self.border.width = new_size * 2 + 6
            self.border.height = new_size * 2 + 6
            self.border.opacity = int(self.activity * 200)
        else:
            self.border.opacity = 0
        
        # Update labels (hidden but kept for compatibility)
        new_size = int(self.size)
        self.label_text.x = current_x
        self.label_text.y = current_y - new_size - 25
        self.notes_text.x = current_x
        self.notes_text.y = current_y - new_size - 45
        # Labels are invisible so no text updates needed

        return False  # No explosion
    
    def get_current_position(self):
        """Get current position including jitter"""
        return (int(self.x + self.jitter_x), int(self.y + self.jitter_y))
    
    def set_position(self, x, y):
        """Set Odin's base position (can be moved by elemental forces)"""
        self.x = int(x)
        self.y = int(y)
    
    def note_on(self, note, velocity):
        # Odin doesn't directly receive MIDI notes, but we keep this for compatibility
        pass
    
    def note_off(self, note):
        # Odin doesn't directly receive MIDI notes, but we keep this for compatibility
        pass

    def add_particle_to_sink(self, particle):
        """Add a particle to Odin's internal sink"""
        if len(self.particle_sink) < self.max_sink_capacity:
            self.particle_sink.append({
                'color': particle.color,
                'added_time': time.time()
            })
            return True
        return False

    def explode_particles(self, explosion_particles_list, batch):
        """Release all particles from sink in 3D explosion pattern"""
        if not self.particle_sink:
            return
            
        current_pos = self.get_current_position()
        
        for particle_data in self.particle_sink:
            # Generate random 3D direction (sphere distribution)
            # This naturally creates particles going in all directions including toward viewer
            phi = random.uniform(0, 2 * math.pi)  # Horizontal angle
            theta = random.uniform(0, math.pi)     # Vertical angle (0 to π for full sphere)
            
            # Convert spherical to cartesian coordinates
            direction = (
                math.sin(theta) * math.cos(phi),  # X component
                math.sin(theta) * math.sin(phi),  # Y component  
            )
            
            explosion_particle = ExplosionParticle3D(
                current_pos, direction, particle_data['color'], batch
            )
            explosion_particles_list.append(explosion_particle)
        
        # Clear the sink
        self.particle_sink.clear()