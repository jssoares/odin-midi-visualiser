import random
import time
import math
from pyglet import shapes

class Connection:
    def __init__(self, node1, node2, batch):
        self.node1, self.node2 = node1, node2
        self.strength, self.target_strength, self.pulse_strength = 0.3, 0.3, 0
        self.harmonic_sensitivity = random.uniform(0.4, 1.0)
        
        # Store original positions for dynamic movement
        self.node1_original_pos = (node1.x, node1.y)
        self.node2_original_pos = (node2.x, node2.y)
        
        # Dynamic connection properties
        self.connection_pull = 0.0  # How much the connection "pulls" nodes
        self.target_connection_pull = 0.0
        
        # Jitter properties for connections
        self.jitter_x1 = 0.0
        self.jitter_y1 = 0.0
        self.jitter_x2 = 0.0
        self.jitter_y2 = 0.0
        self.jitter_intensity = 0.0
        
        self.batch = batch
        self.line = shapes.Line(
            node1.x, node1.y, node2.x, node2.y, 
            color=(120, 160, 220), batch=batch
        )
        self.line.opacity = 0  # Make connections invisible
        
    def update(self, dt):
        self.strength += (self.target_strength - self.strength) * dt * 4
        self.pulse_strength = max(0, self.pulse_strength * 0.88)
        
        # Update connection pull smoothly
        self.connection_pull += (self.target_connection_pull - self.connection_pull) * dt * 6
        
        # React to connected nodes' activity
        combined_activity = (self.node1.activity + self.node2.activity) / 2
        if combined_activity > 0.1:
            self.pulse_strength = min(1.0, self.pulse_strength + combined_activity * 0.6)
            self.target_strength = min(1.0, 0.3 + combined_activity * 0.7)
        
        # Update jitter based on combined activity
        self.jitter_intensity = combined_activity * 0.8  # Reduced from 1.5
        
        # Generate jitter for connection endpoints
        time_factor = time.time() * 18
        self.jitter_x1 = math.sin(time_factor) * self.jitter_intensity
        self.jitter_y1 = math.cos(time_factor * 1.1) * self.jitter_intensity
        self.jitter_x2 = math.sin(time_factor * 1.3) * self.jitter_intensity
        self.jitter_y2 = math.cos(time_factor * 0.9) * self.jitter_intensity
        
        # Apply dynamic positioning based on connection pull
        self.apply_dynamic_positioning()
        
        # Update visual properties
        width = max(2, min(12, int(self.strength * 3 + self.pulse_strength * 4)))
        color_variance = int(min(80, self.pulse_strength * 80))
        color = (
            min(255, 120 + color_variance), 
            min(255, 160 + color_variance//2), 
            min(255, 220 + color_variance//3)
        )
        
        self.line.width = width
        self.line.color = color
        self.line.opacity = 0  # Keep connections invisible
        
        # Update line endpoints to current node positions with jitter
        node1_pos = self.node1.get_current_position()
        node2_pos = self.node2.get_current_position()
        
        self.line.x = int(node1_pos[0] + self.jitter_x1)
        self.line.y = int(node1_pos[1] + self.jitter_y1)
        self.line.x2 = int(node2_pos[0] + self.jitter_x2)
        self.line.y2 = int(node2_pos[1] + self.jitter_y2)
    
    def apply_dynamic_positioning(self):
        """Apply dynamic positioning to nodes based on connection strength"""
        if self.connection_pull <= 0:
            return
        
        # Calculate direction vector from node2 to node1 (element to Odin)
        dx = self.node1_original_pos[0] - self.node2_original_pos[0]
        dy = self.node1_original_pos[1] - self.node2_original_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize direction
            nx = dx / distance
            ny = dy / distance
            
            # Apply pull effect - move element node toward Odin
            pull_amount = self.connection_pull * 15  # Maximum 15 pixels of movement
            
            # Update node2 (elemental node) position
            self.node2.x = int(self.node2_original_pos[0] + nx * pull_amount)
            self.node2.y = int(self.node2_original_pos[1] + ny * pull_amount)
    
    def note_trigger(self, intensity):
        intensity = min(1.0, intensity)
        self.pulse_strength = min(1.0, self.pulse_strength + intensity * self.harmonic_sensitivity)
        self.target_strength = min(1.0, 0.4 + intensity * 0.6)
    
    def set_connection_pull(self, pull_strength):
        """Set the connection pull strength (0.0 to 1.0)"""
        self.target_connection_pull = min(1.0, max(0.0, pull_strength))# Update labels to follow the node
        if hasattr(self.node2, 'label_text'):
            self.node2.label_text.x = self.node2.x
            self.node2.label_text.y = self.node2.y - int(self.node2.size) - 25
        if hasattr(self.node2, 'notes_text'):
            self.node2.notes_text.x = self.node2.x
            self.node2.notes_text.y = self.node2.y - int(self.node2.size) - 40
        
    def note_trigger(self, intensity):
        intensity = min(1.0, intensity)
        self.pulse_strength = min(1.0, self.pulse_strength + intensity * self.harmonic_sensitivity)
        self.target_strength = min(1.0, 0.4 + intensity * 0.6)
    
    def set_connection_pull(self, pull_strength):
        """Set the connection pull strength (0.0 to 1.0)"""
        self.target_connection_pull = min(1.0, max(0.0, pull_strength))