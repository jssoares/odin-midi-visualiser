import random
from pyglet import shapes

class ExplosionParticle3D:
    def __init__(self, start_pos, direction, color, batch):
        self.x, self.y = start_pos
        
        # 3D velocity components - slower speeds for more gradual effect
        self.vx = direction[0] * random.uniform(50, 150)  # Reduced from 100-300
        self.vy = direction[1] * random.uniform(50, 150)  # Reduced from 100-300
        self.vz = random.uniform(-100, 200)  # Reduced from -200 to 400
        
        self.color = color
        self.z = 0.0  # Z position (0 = screen plane, positive = toward viewer)
        
        # Perspective projection settings
        self.focal_length = 2000  # Increased from 1000 - slower perspective growth
        
        self.base_radius = 2
        # Create circle with more segments for smoother appearance at large sizes
        self.circle = shapes.Circle(
            self.x, self.y, radius=2, 
            color=tuple(color), batch=batch,
            segments=32  # More segments = smoother circles at large sizes
        )
        self.life = 60.0  # Much longer life - 60 seconds!
        self.max_life = 60.0  # Store original life for opacity calculations
        self.alive = True

    def update(self, dt):
        # Update 3D position
        self.x += self.vx * dt
        self.y += self.vy * dt  
        self.z += self.vz * dt
        
        self.life -= dt * 0.5  # Even slower fade - 0.5 instead of 1.0
        
        if self.life <= 0:
            self.alive = False
            return
        
        # Perspective projection
        if self.z > -self.focal_length:
            # Calculate perspective scale - slower growth due to higher focal_length
            perspective_scale = self.focal_length / (self.focal_length - self.z)
            perspective_scale = max(0.1, perspective_scale)
            
            # No size limit - let them grow as big as they want!
            projected_radius = int(self.base_radius * perspective_scale)
            projected_radius = max(1, projected_radius)  # Removed max limit
            
            # Scale opacity (closer = more transparent due to "overexposure")
            if perspective_scale > 3.0:  # Adjusted threshold
                opacity_factor = max(0.2, 3.0 / perspective_scale)
            else:
                opacity_factor = 1.0
                
            self.circle.radius = projected_radius
            self.circle.opacity = int((self.life / self.max_life) * 255 * opacity_factor)
        else:
            # Too far behind camera
            self.alive = False
            return
        
        self.circle.x = int(self.x)
        self.circle.y = int(self.y)