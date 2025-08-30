import random
import math
from pyglet import shapes

class ElementalParticle:
    def __init__(self, start_pos, initial_target, color, batch, odin_node=None, pan_offset=(0, 0), emission_direction=None, element_type = None):
        self.x, self.y = start_pos
        self.target_x, self.target_y = initial_target
        self.odin_node = odin_node
        self.color = color
        self.speed = random.uniform(40, 100)
        self.alive = True
        

        # Water-specific anchor properties
        self.water_anchor_release_time = random.uniform(0.5, 1.2)  # When to release the anchor
        self.water_anchor_released = False
        self.water_anchor_original_x, self.water_anchor_original_y = start_pos

        # Stream cohesion properties for water
        self.stream_cohesion = 0.8 if element_type == "WATER" else 0.0
        self.stream_neighbor_distance = 25 if element_type == "WATER" else 15  # How close particles need to be to affect each other
        self.stream_alignment_strength = 0.3  # How much particles align with neighbors
        self.velocity_x = 0.0  # Track velocity for stream behavior
        self.velocity_y = 0.0

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

        self.color = color
        
        # Use passed element type or detect from color as fallback
        self.element_type = element_type
        
        # Create element-specific shape
        self.shape_elements = self.create_element_shape(color, batch)

    def update(self, dt, all_particles=None):
        self.elapsed_time += dt
        
        # Handle emission phase (initial directional movement)
        if self.emission_phase and self.elapsed_time < self.emission_phase_duration:
            # Move in emission direction
            if self.emission_direction:
                self.x += self.emission_direction[0] * self.speed * dt
                self.y += self.emission_direction[1] * self.speed * dt

            # Update visual position during emission phase
            self.update_shapes()
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

        # Water stream behavior - particles influence each other
        if self.element_type == "WATER" and self.stream_cohesion > 0 and all_particles:
            # Find nearby water particles for cohesion
            neighbor_vx = 0.0
            neighbor_vy = 0.0
            neighbor_count = 0
            
            for other_particle in all_particles:
                if (other_particle != self and 
                    other_particle.element_type == "WATER" and 
                    other_particle.alive):
                    
                    dist_to_neighbor = math.hypot(other_particle.x - self.x, other_particle.y - self.y)
                    if dist_to_neighbor < self.stream_neighbor_distance:
                        neighbor_vx += other_particle.velocity_x
                        neighbor_vy += other_particle.velocity_y
                        neighbor_count += 1
            
            # Calculate movement with neighbor influence
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist < 5:
                self.alive = False
                return
                
            if dist > 0:
                direction_x = dx / dist
                direction_y = dy / dist
                
                # Blend with neighbor velocities for stream cohesion
                if neighbor_count > 0:
                    avg_neighbor_vx = neighbor_vx / neighbor_count
                    avg_neighbor_vy = neighbor_vy / neighbor_count
                    
                    # Blend individual direction with stream flow
                    blend_factor = self.stream_alignment_strength
                    direction_x = direction_x * (1 - blend_factor) + (avg_neighbor_vx / self.speed) * blend_factor
                    direction_y = direction_y * (1 - blend_factor) + (avg_neighbor_vy / self.speed) * blend_factor
                    
                    # Renormalize
                    new_mag = math.hypot(direction_x, direction_y)
                    if new_mag > 0:
                        direction_x /= new_mag
                        direction_y /= new_mag
                
                # Minimal curving for water
                if self.is_curving:
                    perp_x = -direction_y * self.curve_direction
                    perp_y = direction_x * self.curve_direction
                    curve_strength = min(1.0, dist / 100) * self.curve_intensity * 3
                    
                    direction_x += perp_x * curve_strength * dt * 0.1
                    direction_y += perp_y * curve_strength * dt * 0.1
                
                self.velocity_x = direction_x * self.speed
                self.velocity_y = direction_y * self.speed
                self.x += self.velocity_x * dt
                self.y += self.velocity_y * dt
        
        else:
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
            
        # Update the visual shapes
        self.update_shapes()

    def update_shapes(self):
        """Update all shape elements based on current position"""
        if self.element_type == "FIRE":
            # Update chevron lines
            left_line, right_line = self.shape_elements
            size = 3
            left_line.x, left_line.y = int(self.x - size), int(self.y - size//2)
            left_line.x2, left_line.y2 = int(self.x), int(self.y + size//2)
            right_line.x, right_line.y = int(self.x), int(self.y + size//2)
            right_line.x2, right_line.y2 = int(self.x + size), int(self.y - size//2)

        elif self.element_type == "WIND":
            # Update 3 segments of the enhanced S-curve
            if len(self.shape_elements) >= 3:
                line1, line2, line3 = self.shape_elements[0], self.shape_elements[1], self.shape_elements[2]
                # first segment: left curve
                line1.x, line1.y = int(self.x - 4), int(self.y - 2)
                line1.x2, line1.y2 = int(self.x - 1), int(self.y)
                # middle segment: straight center
                line2.x, line2.y = int(self.x - 1), int(self.y)
                line2.x2, line2.y2 = int(self.x + 1), int(self.y)
                # third segment: right curve
                line3.x, line3.y = int(self.x + 1), int(self.y)
                line3.x2, line3.y2 = int(self.x + 4), int(self.y - 2)

        elif self.element_type == "EARTH":
            # Update square
            square = self.shape_elements[0]
            square.x, square.y = int(self.x-1), int(self.y-1)

        elif self.element_type == "WATER":
            # Update triangle with anchor release logic
            tri = self.shape_elements[0]
            
            # Release anchor after shorter time for more fluid behavior
            if not self.water_anchor_released and self.elapsed_time > 0.6:
                self.water_anchor_released = True
            
            if not self.water_anchor_released:
                # Anchor phase: tip stays at original position
                tip_x, tip_y = int(self.water_anchor_original_x), int(self.water_anchor_original_y)
                base_left_x, base_left_y = int(self.x - 1.5), int(self.y - 1)
                base_right_x, base_right_y = int(self.x - 1.5), int(self.y + 1)
            else:
                # Released phase: compact droplet
                tip_x, tip_y = int(self.x + 1.5), int(self.y)
                base_left_x, base_left_y = int(self.x - 1.5), int(self.y - 1)
                base_right_x, base_right_y = int(self.x - 1.5), int(self.y + 1)
            
            # Update triangle vertices
            tri.x1, tri.y1 = tip_x, tip_y
            tri.x2, tri.y2 = base_left_x, base_left_y
            tri.x3, tri.y3 = base_right_x, base_right_y

        else:
            # Update circle (generic fallback)
            circle = self.shape_elements[0]
            circle.x, circle.y = int(self.x), int(self.y)

    def create_element_shape(self, color, batch):
        """Create element-specific particle shape"""
        if self.element_type == "FIRE":
            # Small chevron
            size = 3
            left_line = shapes.Line(
                int(self.x - size), int(self.y - size//2),
                int(self.x), int(self.y + size//2),
                thickness=2, color=tuple(color), batch=batch
            )
            right_line = shapes.Line(
                int(self.x), int(self.y + size//2), 
                int(self.x + size), int(self.y - size//2),
                thickness=2, color=tuple(color), batch=batch
            )
            return [left_line, right_line]
        
        elif self.element_type == "WATER":
            # Small water droplet - more circular than triangular
            return [shapes.Triangle(
                int(self.x + 1.5), int(self.y),      # Shorter point
                int(self.x - 1.5), int(self.y - 1),  # Rounder back
                int(self.x - 1.5), int(self.y + 1),  # Rounder back
                color=tuple(color), batch=batch
            )]
        
        elif self.element_type == "WIND":
            # Enhanced 3-segment S-curve for wind flow
            line1 = shapes.Line(
                int(self.x - 4), int(self.y - 2),
                int(self.x - 1), int(self.y),
                thickness=2, color=tuple(color), batch=batch
            )
            line2 = shapes.Line(
                int(self.x - 1), int(self.y),
                int(self.x + 1), int(self.y),
                thickness=2, color=tuple(color), batch=batch
            )
            line3 = shapes.Line(
                int(self.x + 1), int(self.y),
                int(self.x + 4), int(self.y - 2),
                thickness=2, color=tuple(color), batch=batch
            )
            return [line1, line2, line3]
        
        elif self.element_type == "EARTH":
            # Small square
            return [shapes.Rectangle(int(self.x-1), int(self.y-1), 3, 3, color=tuple(color), batch=batch)]
        
        else:
            # Default circle
            return [shapes.Circle(self.x, self.y, radius=2, color=tuple(color), batch=batch)]
