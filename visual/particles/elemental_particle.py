import random
import math
from pyglet import shapes

class ElementalParticle:
    def __init__(self, start_pos, initial_target, color, batch, odin_node=None, pan_offset=(0, 0), emission_direction=None):
        self.x, self.y = start_pos
        self.target_x, self.target_y = initial_target
        self.odin_node = odin_node
        self.color = color
        self.circle = shapes.Circle(self.x, self.y, radius=2, color=tuple(color), batch=batch)
        self.speed = random.uniform(40, 100)
        self.alive = True
        
        # Store the pan offset for initial trajectory
        self.pan_offset_x, self.pan_offset_y = pan_offset
        
        # NEW: Handle directional emission
        self.emission_direction = emission_direction
        self.emission_phase_duration = random.uniform(0.3, 0.8)  # How long to maintain emission direction
        self.elapsed_time = 0.0
        self.emission_phase = True if emission_direction else False
        
        # Curve properties
        self.curve_start_time = random.uniform(0.2, 1.3) if not emission_direction else self.emission_phase_duration
        self.curve_intensity = random.uniform(0.3, 1.0)
        self.curve_direction = random.choice([-1, 1])
        self.is_curving = False
        self.curve_transition = 0.0
        
        # Store original straight-line trajectory for reference
        self.original_target = initial_target

    def update(self, dt):
        self.elapsed_time += dt
        
        # Handle emission phase (initial directional movement)
        if self.emission_phase and self.elapsed_time < self.emission_phase_duration:
            # Move in emission direction
            if self.emission_direction:
                self.x += self.emission_direction[0] * self.speed * dt
                self.y += self.emission_direction[1] * self.speed * dt
            
            self.circle.x = int(self.x)
            self.circle.y = int(self.y)
            return
        
        # End emission phase, start targeting Odin
        if self.emission_phase:
            self.emission_phase = False
        
        # Start curving after emission phase
        if not self.is_curving and self.elapsed_time > self.curve_start_time:
            self.is_curving = True
        
        # Rest of the original update logic stays the same...
        if self.odin_node:
            odin_pos = self.odin_node.get_current_position()
            
            if self.is_curving:
                self.curve_transition += dt * 1.5
                self.curve_transition = min(1.0, self.curve_transition)
                
                pan_target_x = odin_pos[0] + self.pan_offset_x
                pan_target_y = odin_pos[1] + self.pan_offset_y
                
                self.target_x = pan_target_x + (odin_pos[0] - pan_target_x) * self.curve_transition
                self.target_y = pan_target_y + (odin_pos[1] - pan_target_y) * self.curve_transition
            else:
                self.target_x = odin_pos[0] + self.pan_offset_x
                self.target_y = odin_pos[1] + self.pan_offset_y
        
        # Move toward target with curve effect
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 5:
            self.alive = False
            return
            
        if dist > 0:
            direction_x = dx / dist
            direction_y = dy / dist
            
            if self.is_curving:
                perp_x = -direction_y * self.curve_direction
                perp_y = direction_x * self.curve_direction
                curve_strength = min(1.0, dist / 100) * self.curve_intensity * 30
                
                direction_x += perp_x * curve_strength * dt
                direction_y += perp_y * curve_strength * dt
                
                new_mag = math.hypot(direction_x, direction_y)
                if new_mag > 0:
                    direction_x /= new_mag
                    direction_y /= new_mag
            
            self.x += direction_x * self.speed * dt
            self.y += direction_y * self.speed * dt
            
        self.circle.x = int(self.x)
        self.circle.y = int(self.y)