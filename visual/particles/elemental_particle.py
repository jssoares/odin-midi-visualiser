import random
import math
from .base_particle import BaseParticle
from .element_shape_factory import ElementShapeFactory

class ElementalParticle(BaseParticle):
    def __init__(self, start_pos, initial_target, color, batch, odin_node=None, 
                 pan_offset=(0, 0), emission_direction=None, element_type=None):
        
        # Core movement properties
        self.target_x, self.target_y = initial_target
        self.odin_node = odin_node
        self.speed = random.uniform(40, 100)
        self.pan_offset_x, self.pan_offset_y = pan_offset
        
        # Emission behavior
        self.emission_direction = emission_direction
        self.emission_phase_duration = random.uniform(0.3, 0.8)
        self.emission_phase = True if emission_direction else False
        
        # Curve behavior
        self.curve_start_time = random.uniform(0.2, 1.3) if not emission_direction else self.emission_phase_duration
        self.curve_intensity = random.uniform(0.3, 1.0)
        self.curve_direction = random.choice([-1, 1])
        self.is_curving = False
        self.curve_transition = 0.0
        
        super().__init__(start_pos, color, batch, element_type)
    
    def create_shape(self, color, batch):
        return ElementShapeFactory.create_shape_for_element(
            self.element_type, self.x, self.y, color, batch
        )
    
    def update_movement(self, dt):
        # Handle emission phase
        if self.emission_phase and self.elapsed_time < self.emission_phase_duration:
            if self.emission_direction:
                self.x += self.emission_direction[0] * self.speed * dt
                self.y += self.emission_direction[1] * self.speed * dt
            return
        
        # End emission phase, start normal movement
        if self.emission_phase:
            self.emission_phase = False
        
        # Start curving
        if not self.is_curving and self.elapsed_time > self.curve_start_time:
            self.is_curving = True
        
        # Update target position based on Odin
        self._update_target()
        
        # Move toward target
        self._move_toward_target(dt)
    
    def update_visual_properties(self, dt):
        # Base implementation - subclasses can override
        pass
    
    def _update_target(self):
        if not self.odin_node:
            return
            
        odin_pos = self.odin_node.get_current_position()
        
        if self.is_curving:
            self.curve_transition += 0.025  # dt * 1.5 approximation
            self.curve_transition = min(1.0, self.curve_transition)
            
            pan_target_x = odin_pos[0] + self.pan_offset_x
            pan_target_y = odin_pos[1] + self.pan_offset_y
            
            self.target_x = pan_target_x + (odin_pos[0] - pan_target_x) * self.curve_transition
            self.target_y = pan_target_y + (odin_pos[1] - pan_target_y) * self.curve_transition
        else:
            self.target_x = odin_pos[0] + self.pan_offset_x
            self.target_y = odin_pos[1] + self.pan_offset_y
    
    def _move_toward_target(self, dt):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 5:
            self.alive = False
            return
            
        if dist > 0:
            direction_x = dx / dist
            direction_y = dy / dist
            
            # Apply curve effect
            if self.is_curving:
                perp_x = -direction_y * self.curve_direction
                perp_y = direction_x * self.curve_direction
                curve_strength = min(1.0, dist / 100) * self.curve_intensity * 30
                
                direction_x += perp_x * curve_strength * dt
                direction_y += perp_y * curve_strength * dt
                
                # Renormalize
                new_mag = math.hypot(direction_x, direction_y)
                if new_mag > 0:
                    direction_x /= new_mag
                    direction_y /= new_mag
            
            self.x += direction_x * self.speed * dt
            self.y += direction_y * self.speed * dt
    
    def update_shapes(self):
        # Use factory's shape update methods
        ElementShapeFactory.update_shape_for_element(
            self.element_type, self.shape_elements, self.x, self.y
        )
