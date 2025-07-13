import random
from pyglet import shapes

class ExplosionParticle:
    def __init__(self, start_pos, direction, color, batch):
        self.x, self.y = start_pos
        self.vx = direction[0] * random.uniform(100, 300)
        self.vy = direction[1] * random.uniform(100, 300)
        self.color = color
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
            
        self.circle.x = int(self.x)
        self.circle.y = int(self.y)
        self.circle.opacity = int(self.life * 255)