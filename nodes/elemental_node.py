import time
import math
from pyglet        import text
from visual.shapes import ElementalShape
from config        import ELEMENT_REGISTRY

class ElementalNode:
    """Enhanced node class for elements with audio-reactive shapes"""
    def __init__(self, x, y, node_id, batch, instrument_channel=None, element_type="", element_color=None):
        self.x = int(x)
        self.y = int(y)
        self.original_x = int(x)  # Store original position
        self.original_y = int(y)
        self.id = node_id
        self.instrument_channel = instrument_channel
        self.element_type = element_type
        self.base_size = 55
        self.size = self.base_size
        self.target_size = self.base_size
        self.color = [int(c) for c in element_color] if element_color else [100, 150, 200]
        self.target_color = self.color.copy()
        self.base_color = self.color.copy()
        self.activity = 0
        self.label = element_type
        self.active_notes = set()
        
        # Audio reactivity
        self.audio_intensity = 0.0
        self.audio_smoothed = 0.0
        
        # Jitter properties
        self.jitter_x = 0.0
        self.jitter_y = 0.0
        self.jitter_intensity = 0.0
        
        # MIDI note-based color gradient tracking
        self.current_gradient_color = self.base_color.copy()
        self.note_colors = {}  # Track colors for each active note
        
        # Create elemental shape
        self.elemental_shape = ElementalShape(x, y, self.base_size, batch, element_type, self.color)
        
        # Labels (kept in code but hidden)
        self.label_text = text.Label(
            self.label, font_size=12, color=(220, 220, 220, 0),  # Invisible
            x=x, y=y - self.base_size - 25, anchor_x='center', batch=batch
        )
        self.notes_text = text.Label(
            '', font_size=10, color=(180, 255, 180, 0),  # Invisible
            x=x, y=y - self.base_size - 40, anchor_x='center', batch=batch
        )
        
    def get_note_color_for_element(self, note):
        """Generate element-specific color gradients based on MIDI note"""
        element_config = ELEMENT_REGISTRY.get_element(self.element_type)
        if element_config:
            return element_config.get_note_color(note)
        return self.base_color
    
    def update_gradient_color(self):
        """Update the gradient color based on active MIDI notes"""
        if not self.active_notes:
            # No notes active - return to base color
            self.current_gradient_color = self.base_color.copy()
            return
        
        # Blend colors from all active notes
        blended_color = [0, 0, 0]
        for note in self.active_notes:
            note_color = self.get_note_color_for_element(note)
            for i in range(3):
                blended_color[i] += note_color[i]
        
        # Average the colors
        num_notes = len(self.active_notes)
        self.current_gradient_color = [int(c / num_notes) for c in blended_color]
        
    def update(self, dt):
        # Override audio intensity with frequency-based reactivity
        if hasattr(self, 'visualizer_ref') and self.visualizer_ref:
            freq_level = self.visualizer_ref.audio_analyzer.element_frequency_levels.get(self.element_type, 0.0)
            # Blend MIDI activity with frequency analysis
            self.audio_intensity = max(self.activity, freq_level * 1.5)  # Boost frequency response
        else:
            self.audio_intensity = self.activity

        self.audio_smoothed += (self.audio_intensity - self.audio_smoothed) * dt * 6
        
        # Update gradient color based on active MIDI notes
        self.update_gradient_color()
        
        # Update jitter based on activity
        self.jitter_intensity = self.activity * 1.2  # Reduced from 2.5
        
        # Generate different jitter patterns for each element
        time_factor = time.time() * (12 + self.id)  # Different speed per element
        self.jitter_x = math.sin(time_factor) * self.jitter_intensity
        self.jitter_y = math.cos(time_factor * 1.2) * self.jitter_intensity
        
        # Smooth size transitions
        self.size += (self.target_size - self.size) * dt * 8
        self.size = max(15, min(60, self.size))
        
        # Use gradient color instead of target color
        self.color = self.current_gradient_color.copy()
        
        # Activity decay
        self.activity = max(0, min(1, self.activity * 0.92))
        
        if self.active_notes:
            self.activity = min(1.0, len(self.active_notes) * 0.3)
        
        # Current position with jitter
        current_x = int(self.x + self.jitter_x)
        current_y = int(self.y + self.jitter_y)
        
        # Update elemental shape with gradient color AND both intensities
        self.elemental_shape.set_position_and_size(current_x, current_y, int(self.size))
        self.elemental_shape.update(dt, self.color, self.audio_smoothed, self.activity)
        
        # Update labels (hidden but kept for compatibility)
        new_size = int(self.size)
        self.label_text.x = current_x
        self.label_text.y = current_y - new_size - 25
        self.notes_text.x = current_x
        self.notes_text.y = current_y - new_size - 40
        # Labels are invisible so no text updates needed
    
    def get_current_position(self):
        """Get current position including jitter"""
        return (int(self.x + self.jitter_x), int(self.y + self.jitter_y))
    
    def note_on(self, note, velocity):
        """MIDI note on - this preserves the MIDI reactiveness"""
        self.active_notes.add(note)
        intensity = min(1.0, velocity / 127.0)
        
        self.target_size = self.base_size + intensity * 25
        self.activity = min(1.0, self.activity + intensity * 0.8)
        
        # Gradient color will be updated in update() method
    
    def note_off(self, note):
        """MIDI note off - this preserves the MIDI reactiveness"""
        self.active_notes.discard(note)
        if not self.active_notes:
            self.target_size = self.base_size