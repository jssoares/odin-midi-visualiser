import random
from .base_particle import BaseParticle
from .element_shape_factory import ElementShapeFactory

class ExplosionParticle(BaseParticle):
    def __init__(self, start_pos, direction, color, batch, depth_factor=1.0, element_type=None):
        self.vx = direction[0] * random.uniform(100, 300)
        self.vy = direction[1] * random.uniform(100, 300)
        
        # 3D depth properties
        self.depth_factor = depth_factor
        self.base_radius = 2
        self.current_radius = int(self.base_radius * depth_factor)
        self.max_alpha = min(255, int(255 / depth_factor))
        
        # Life properties
        self.life = 10.0
        
        super().__init__(start_pos, color, batch, element_type)
    
    def create_shape(self, color, batch):
        return ElementShapeFactory.create_shape_for_element(
            self.element_type, self.x, self.y, color, batch
        )
    
    def update_movement(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
    
    def update_visual_properties(self, dt):
        self.life -= dt * 2.5
        
        if self.life <= 0:
            self.alive = False
            return
            
        # Scale grows over time for "closer" particles
        if self.depth_factor > 1.0:
            growth_rate = (self.depth_factor - 1.0) * 2
            self.current_radius = int(self.base_radius * self.depth_factor * (1 + growth_rate * (1 - self.life/10.0)))
        
        # Calculate opacity
        life_alpha = self.life * 255
        final_alpha = min(life_alpha, self.max_alpha)
        
        # Set opacity for all shape elements
        for shape in self.shape_elements:
            shape.opacity = max(0, int(final_alpha))
    
    def update_shapes(self):
        # Use factory for most elements, but handle depth scaling
        if self.element_type in ["FIRE", "WIND"]:
            ElementShapeFactory.update_shape_for_element(
                self.element_type, self.shape_elements, self.x, self.y
            )
        elif self.element_type == "EARTH":
            self._update_earth_with_scaling()
        elif self.element_type == "WATER":
            self._update_water_explosion()
        else:
            self._update_circle_with_scaling()
    
    def _update_earth_with_scaling(self):
        if self.shape_elements:
            square = self.shape_elements[0]
            square.x, square.y = int(self.x-1), int(self.y-1)
            if self.depth_factor > 1.0:
                square.width = square.height = max(1, self.current_radius * 2)
    
    def _update_water_explosion(self):
        if self.shape_elements:
            tri = self.shape_elements[0]
            tri.x1, tri.y1 = int(self.x + 3), int(self.y)
            tri.x2, tri.y2 = int(self.x - 2), int(self.y - 2)
            tri.x3, tri.y3 = int(self.x - 2), int(self.y + 2)
    
    def _update_circle_with_scaling(self):
        if self.shape_elements:
            circle = self.shape_elements[0]
            circle.x, circle.y = int(self.x), int(self.y)
            if self.depth_factor > 1.0:
                circle.radius = max(1, self.current_radius)