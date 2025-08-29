import math
import random
from pyglet import shapes

class ExplosionParticle3D:
    def __init__(self, start_pos, direction, color, batch, particle_type="screen_plane", element_type=None):
        self.x, self.y = start_pos
        self.start_x, self.start_y = start_pos  # Store starting position
        self.particle_type = particle_type  # Store the particle type
        self.element_type = element_type or "GENERIC"

        if particle_type == "toward_viewer":
            # 5% - Coming toward viewer
            self.vx = direction[0] * random.uniform(20, 60)
            self.vy = direction[1] * random.uniform(20, 60)  
            self.vz = random.uniform(50, 150)  # Positive Z = toward viewer
        elif particle_type == "away_from_viewer":
            # 5% - Going away from viewer
            self.vx = direction[0] * random.uniform(30, 80)
            self.vy = direction[1] * random.uniform(30, 80)
            self.vz = random.uniform(-150, -50)  # Negative Z = away from viewer
        else:  # screen_plane
            # 90% - Stay in screen plane (normal explosion)
            self.vx = direction[0] * random.uniform(50, 150)
            self.vy = direction[1] * random.uniform(50, 150)
            self.vz = 0  # Exactly zero Z = stay in screen plane (no drift)
        
        # Rest stays the same...
        self.color = color
        self.z = 0.0
        self.focal_length = 2000
        self.base_radius = 2
        self.shape_elements = self.create_element_shape(color, batch)
        self.life = 20.0
        self.max_life = 20.0
        self.alive = True

    def update(self, dt):
        # Update 3D position
        self.x += self.vx * dt
        self.y += self.vy * dt  
        self.z += self.vz * dt
        
        # Kill away_from_viewer particles when they're far enough from START position
        if self.particle_type == "away_from_viewer":
            distance_from_start = math.sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2 + self.z**2)
            if distance_from_start > 2:  # Reasonable threshold
                self.alive = False
                return
        
        # Add acceleration for toward_viewer particles to get to you faster
        if self.particle_type == "toward_viewer":
            # Simple acceleration - they speed up over time
            self.vz += 50 * dt  # Constant acceleration toward viewer
        elif self.particle_type == "away_from_viewer":
            # Accelerate away from viewer - they speed up going away
            self.vz -= 100000 * dt  # Double the acceleration away from viewer
        
        # Adjust fade rate based on particle type
        if self.particle_type == "away_from_viewer":
            self.life -= dt * 100.0  # 10x faster fade than normal
        else:
            self.life -= dt * 0.5  # Normal fade rate
        
        if self.life <= 0:
            self.alive = False
            return
        
        # Single perspective projection calculation
        if self.z > -self.focal_length:
            perspective_scale = self.focal_length / (self.focal_length - self.z)
            perspective_scale = max(0.1, perspective_scale)
            
            projected_radius = int(self.base_radius * perspective_scale)
            projected_radius = max(1, projected_radius)
            
            if perspective_scale > 3.0:
                opacity_factor = max(0.2, 3.0 / perspective_scale)
            else:
                opacity_factor = 1.0
            
            opacity = int((self.life / self.max_life) * 255 * opacity_factor)

            if self.element_type == "FIRE":
                left_line, right_line = self.shape_elements
                size = int(3 * perspective_scale)
                left_line.x, left_line.y = int(self.x - size), int(self.y - size//2)
                left_line.x2, left_line.y2 = int(self.x), int(self.y + size//2)
                right_line.x, right_line.y = int(self.x), int(self.y + size//2)
                right_line.x2, right_line.y2 = int(self.x + size), int(self.y - size//2)
                left_line.opacity = opacity
                right_line.opacity = opacity
                left_line.width = max(1, int(2 * perspective_scale))
                right_line.width = max(1, int(2 * perspective_scale))
            elif self.element_type == "WIND":
                line = self.shape_elements[0]
                size = int(3 * perspective_scale)
                line.x, line.y = int(self.x-size), int(self.y)
                line.x2, line.y2 = int(self.x+size), int(self.y)
                line.opacity = opacity
                line.width = max(1, int(2 * perspective_scale))
            elif self.element_type == "EARTH":
                square = self.shape_elements[0]
                size = max(1, int(2 * perspective_scale))
                square.x, square.y = int(self.x-size//2), int(self.y-size//2)
                square.width, square.height = size, size
                square.opacity = opacity
            else:
                circle = self.shape_elements[0]
                circle.radius = projected_radius
                circle.opacity = opacity
                circle.x, circle.y = int(self.x), int(self.y)
        else:
            self.alive = False
            return

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
            # Small teardrop (circle)
            return [shapes.Circle(self.x, self.y, radius=2, color=tuple(color), batch=batch)]
        
        elif self.element_type == "WIND":
            # Small horizontal line (dash)
            return [shapes.Line(int(self.x-3), int(self.y), int(self.x+3), int(self.y), 
                            thickness=2, color=tuple(color), batch=batch)]
        
        elif self.element_type == "EARTH":
            # Small square
            return [shapes.Rectangle(int(self.x-1), int(self.y-1), 2, 2, color=tuple(color), batch=batch)]
        
        else:
            # Default circle
            return [shapes.Circle(self.x, self.y, radius=2, color=tuple(color), batch=batch)]