import math
import random
from pyglet import shapes

class ExplosionParticle3D:
    def __init__(self, start_pos, direction, color, batch, particle_type="screen_plane"):
        self.x, self.y = start_pos
        self.start_x, self.start_y = start_pos  # Store starting position
        self.particle_type = particle_type  # Store the particle type
        
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
        self.circle = shapes.Circle(
            self.x, self.y, radius=2, 
            color=tuple(color), batch=batch,
            segments=32
        )
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
                
            self.circle.radius = projected_radius
            self.circle.opacity = int((self.life / self.max_life) * 255 * opacity_factor)
        else:
            self.alive = False
            return
        
        self.circle.x = int(self.x)
        self.circle.y = int(self.y)