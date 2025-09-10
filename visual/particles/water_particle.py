import math
from .elemental_particle import ElementalParticle

class WaterParticle(ElementalParticle):
    def __init__(self, start_pos, initial_target, color, batch, odin_node=None, pan_offset=(0, 0)):
        super().__init__(start_pos, initial_target, color, batch, odin_node, pan_offset, None, "WATER")
        
        # Water-specific properties
        self.water_anchor_released = False
        self.water_anchor_original_x, self.water_anchor_original_y = start_pos
        
        # Stream cohesion properties
        self.stream_neighbor_distance = 25
        self.stream_alignment_strength = 0.3
        self.velocity_x = 0.0
        self.velocity_y = 0.0
    
    def update_visual_properties(self, dt):
        # Water anchor release logic
        if not self.water_anchor_released and self.elapsed_time > 0.6:
            self.water_anchor_released = True
    
    def update(self, dt, all_particles=None):
        """Override to handle stream cohesion"""
        self.elapsed_time += dt
        
        if not self.alive:
            return
        
        # Handle emission phase first
        if self.emission_phase and self.elapsed_time < self.emission_phase_duration:
            if self.emission_direction:
                self.x += self.emission_direction[0] * self.speed * dt
                self.y += self.emission_direction[1] * self.speed * dt
            self.update_visual_properties(dt)
            self.update_shapes()
            return
        
        # End emission phase
        if self.emission_phase:
            self.emission_phase = False
        
        # Start curving
        if not self.is_curving and self.elapsed_time > self.curve_start_time:
            self.is_curving = True
        
        # Update target
        self._update_target()
        
        # Use stream movement if other particles provided
        if all_particles:
            self._update_stream_movement(dt, all_particles)
        else:
            self._move_toward_target(dt)
        
        self.update_visual_properties(dt)
        self.update_shapes()
    
    def _update_stream_movement(self, dt, all_particles):
        """Handle water stream cohesion"""
        # Find nearby water particles
        neighbor_vx = 0.0
        neighbor_vy = 0.0
        neighbor_count = 0
        
        for other_particle in all_particles:
            if (other_particle != self and 
                getattr(other_particle, 'element_type', None) == "WATER" and 
                other_particle.alive):
                
                dist = math.hypot(other_particle.x - self.x, other_particle.y - self.y)
                if dist < self.stream_neighbor_distance:
                    neighbor_vx += getattr(other_particle, 'velocity_x', 0)
                    neighbor_vy += getattr(other_particle, 'velocity_y', 0)
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
            
            # Blend with neighbor velocities
            if neighbor_count > 0:
                avg_neighbor_vx = neighbor_vx / neighbor_count
                avg_neighbor_vy = neighbor_vy / neighbor_count
                
                blend_factor = self.stream_alignment_strength
                direction_x = direction_x * (1 - blend_factor) + (avg_neighbor_vx / self.speed) * blend_factor
                direction_y = direction_y * (1 - blend_factor) + (avg_neighbor_vy / self.speed) * blend_factor
                
                # Renormalize
                new_mag = math.hypot(direction_x, direction_y)
                if new_mag > 0:
                    direction_x /= new_mag
                    direction_y /= new_mag
            
            # Apply minimal curve effect for water
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
    
    def update_shapes(self):
        """Override to handle water anchor logic"""
        if self.shape_elements:
            tri = self.shape_elements[0]
            
            if not self.water_anchor_released:
                # Anchor phase: tip stays at original position
                tip_x, tip_y = int(self.water_anchor_original_x), int(self.water_anchor_original_y)
                base_left_x, base_left_y = int(self.x - 1.5), int(self.y - 1)
                base_right_x, base_right_y = int(self.x - 1.5), int(self.y + 1)
            else:
                # Released phase: all vertices move together
                tip_x, tip_y = int(self.x + 1.5), int(self.y)
                base_left_x, base_left_y = int(self.x - 1.5), int(self.y - 1)
                base_right_x, base_right_y = int(self.x - 1.5), int(self.y + 1)
            
            tri.x1, tri.y1 = tip_x, tip_y
            tri.x2, tri.y2 = base_left_x, base_left_y
            tri.x3, tri.y3 = base_right_x, base_right_y
