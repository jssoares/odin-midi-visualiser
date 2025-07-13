import random
import math
from pyglet import shapes

class ElementalParticle:
    def __init__(self, start_pos, initial_target, color, batch, odin_node=None, pan_offset=(0, 0)):
        self.x, self.y = start_pos
        self.target_x, self.target_y = initial_target
        self.odin_node = odin_node
        self.color = color
        self.circle = shapes.Circle(self.x, self.y, radius=2, color=tuple(color), batch=batch)
        self.speed = random.uniform(40, 100)
        self.alive = True
        
        # Store the pan offset for initial trajectory
        self.pan_offset_x, self.pan_offset_y = pan_offset
        
        # Curve properties
        self.curve_start_time = random.uniform(0.2, 1.3)  # When to start curving
        self.curve_intensity = random.uniform(0.3, 1.0)   # How much to curve
        self.curve_direction = random.choice([-1, 1])     # Curve left or right
        self.elapsed_time = 0.0
        self.is_curving = False
        self.curve_transition = 0.0  # 0.0 = pan target, 1.0 = odin center
        
        # Store original straight-line trajectory for reference
        self.original_target = initial_target

    def update(self, dt):
        self.elapsed_time += dt
        
        # Start curving after random delay
        if not self.is_curving and self.elapsed_time > self.curve_start_time:
            self.is_curving = True
        
        # Calculate target position with smooth transition
        if self.odin_node:
            odin_pos = self.odin_node.get_current_position()
            
            if self.is_curving:
                # Gradually transition from pan-deflected target to Odin's center
                self.curve_transition += dt * 1.5  # Transition speed
                self.curve_transition = min(1.0, self.curve_transition)
                
                # Interpolate between pan-deflected target and Odin's center
                pan_target_x = odin_pos[0] + self.pan_offset_x
                pan_target_y = odin_pos[1] + self.pan_offset_y
                
                # Smooth interpolation: start at pan target, end at Odin center
                self.target_x = pan_target_x + (odin_pos[0] - pan_target_x) * self.curve_transition
                self.target_y = pan_target_y + (odin_pos[1] - pan_target_y) * self.curve_transition
            else:
                # Before curving: head toward pan-deflected position
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
            
            # Add curve effect when curving
            if self.is_curving:
                # Calculate perpendicular direction for curve
                perp_x = -direction_y * self.curve_direction
                perp_y = direction_x * self.curve_direction
                
                # Apply curve based on distance to target (stronger when farther)
                curve_strength = min(1.0, dist / 100) * self.curve_intensity * 30
                
                direction_x += perp_x * curve_strength * dt
                direction_y += perp_y * curve_strength * dt
                
                # Normalize the direction
                new_mag = math.hypot(direction_x, direction_y)
                if new_mag > 0:
                    direction_x /= new_mag
                    direction_y /= new_mag
            
            self.x += direction_x * self.speed * dt
            self.y += direction_y * self.speed * dt
            
        self.circle.x = int(self.x)
        self.circle.y = int(self.y)