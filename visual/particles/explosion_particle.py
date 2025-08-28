import random
from pyglet import shapes

class ExplosionParticle:
    def __init__(self, start_pos, direction, color, batch, depth_factor=1.0):
        self.x, self.y = start_pos
        self.vx = direction[0] * random.uniform(100, 300)
        self.vy = direction[1] * random.uniform(100, 300)
        self.color = color

        # 3D depth properties
        self.depth_factor = depth_factor  # 1.0 = normal, >1.0 = closer to camera
        self.base_radius = 2
        self.current_radius = int(self.base_radius * depth_factor)
        self.max_alpha = min(255, int(255 / depth_factor))  # Closer = more transparent

        self.circle = shapes.Circle(self.x, self.y, radius=3, color=tuple(color), batch=batch)
        self.life = 10.0
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt * 2.5  # Fade out over 4.0 seconds
        
        if self.life <= 0:
            self.alive = False
            return
        # Scale grows over time for "closer" particles
        if self.depth_factor > 1.0:
            growth_rate = (self.depth_factor - 1.0) * 2  # Faster growth for closer particles
            self.current_radius = int(self.base_radius * self.depth_factor * (1 + growth_rate * (1 - self.life/10.0)))
            self.circle.radius = max(1, self.current_radius)
         
        self.circle.x = int(self.x)
        self.circle.y = int(self.y)
        self.circle.opacity = int(self.life * 255)

        # Fade based on life and depth
        life_alpha = self.life * 255
        final_alpha = min(life_alpha, self.max_alpha)
        self.circle.opacity = max(0, int(final_alpha))