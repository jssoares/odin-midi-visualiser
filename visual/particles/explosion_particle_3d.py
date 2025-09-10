import math
import random
from .base_particle import BaseParticle
from .element_shape_factory import ElementShapeFactory

class ExplosionParticle3D(BaseParticle):
    def __init__(self, start_pos, direction, color, batch, particle_type="screen_plane", element_type=None):
        self.start_x, self.start_y = start_pos
        self.particle_type = particle_type
        
        # Set 3D velocity based on particle type
        self._setup_3d_velocity(direction, particle_type)
        
        # 3D properties
        self.z = 0.0
        self.focal_length = 2000
        self.base_radius = 2
        self.life = 20.0
        self.max_life = 20.0
        
        super().__init__(start_pos, color, batch, element_type)
    
    def _setup_3d_velocity(self, direction, particle_type):
        """Setup velocity based on 3D movement type"""
        if particle_type == "toward_viewer":
            self.vx = direction[0] * random.uniform(20, 60)
            self.vy = direction[1] * random.uniform(20, 60)  
            self.vz = random.uniform(50, 150)
        elif particle_type == "away_from_viewer":
            self.vx = direction[0] * random.uniform(30, 80)
            self.vy = direction[1] * random.uniform(30, 80)
            self.vz = random.uniform(-150, -50)
        else:  # screen_plane
            self.vx = direction[0] * random.uniform(50, 150)
            self.vy = direction[1] * random.uniform(50, 150)
            self.vz = 0
    
    def create_shape(self, color, batch):
        return ElementShapeFactory.create_shape_for_element(
            self.element_type, self.x, self.y, color, batch
        )
    
    def update_movement(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt  
        self.z += self.vz * dt
        
        # Kill particles that moved too far away
        if self.particle_type == "away_from_viewer":
            distance_from_start = math.sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2 + self.z**2)
            if distance_from_start > 2:
                self.alive = False
                return
        
        # Apply acceleration
        if self.particle_type == "toward_viewer":
            self.vz += 50 * dt
        elif self.particle_type == "away_from_viewer":
            self.vz -= 100000 * dt
    
    def update_visual_properties(self, dt):
        # Adjust fade rate based on particle type
        if self.particle_type == "away_from_viewer":
            self.life -= dt * 100.0
        else:
            self.life -= dt * 0.5
        
        if self.life <= 0:
            self.alive = False
            return
        
        # Calculate perspective and opacity
        if self.z > -self.focal_length:
            perspective_scale = self.focal_length / (self.focal_length - self.z)
            perspective_scale = max(0.1, perspective_scale)
            
            opacity_factor = max(0.2, 3.0 / perspective_scale) if perspective_scale > 3.0 else 1.0
            opacity = int((self.life / self.max_life) * 255 * opacity_factor)
            
            self._apply_perspective_scaling(perspective_scale, opacity)
        else:
            self.alive = False
    
    def _apply_perspective_scaling(self, perspective_scale, opacity):
        """Apply 3D perspective scaling to shapes"""
        if self.element_type == "FIRE":
            self._scale_fire_shape(perspective_scale, opacity)
        elif self.element_type == "WIND":
            self._scale_wind_shape(perspective_scale, opacity)
        elif self.element_type == "EARTH":
            self._scale_earth_shape(perspective_scale, opacity)
        elif self.element_type == "WATER":
            self._scale_water_shape(perspective_scale, opacity)
        else:
            self._scale_circle_shape(perspective_scale, opacity)
    
    def _scale_fire_shape(self, scale, opacity):
        if len(self.shape_elements) >= 2:
            left_line, right_line = self.shape_elements[0], self.shape_elements[1]
            size = int(3 * scale)
            left_line.x, left_line.y = int(self.x - size), int(self.y - size//2)
            left_line.x2, left_line.y2 = int(self.x), int(self.y + size//2)
            right_line.x, right_line.y = int(self.x), int(self.y + size//2)
            right_line.x2, right_line.y2 = int(self.x + size), int(self.y - size//2)
            left_line.opacity = right_line.opacity = opacity
            left_line.width = right_line.width = max(1, int(2 * scale))
    
    def _scale_wind_shape(self, scale, opacity):
        if len(self.shape_elements) >= 3:
            line1, line2, line3 = self.shape_elements[0], self.shape_elements[1], self.shape_elements[2]
            size = int(3 * scale)
            
            line1.x, line1.y = int(self.x - size*1.3), int(self.y - size*0.7)
            line1.x2, line1.y2 = int(self.x - size*0.3), int(self.y)
            line2.x, line2.y = int(self.x - size*0.3), int(self.y)
            line2.x2, line2.y2 = int(self.x + size*0.3), int(self.y)
            line3.x, line3.y = int(self.x + size*0.3), int(self.y)
            line3.x2, line3.y2 = int(self.x + size*1.3), int(self.y - size*0.7)
            
            for line in [line1, line2, line3]:
                line.opacity = opacity
                line.width = max(1, int(2 * scale))
    
    def _scale_earth_shape(self, scale, opacity):
        if self.shape_elements:
            square = self.shape_elements[0]
            size = max(1, int(2 * scale))
            square.x, square.y = int(self.x-size//2), int(self.y-size//2)
            square.width, square.height = size, size
            square.opacity = opacity
    
    def _scale_water_shape(self, scale, opacity):
        if self.shape_elements:
            tri = self.shape_elements[0]
            size = int(3 * scale)
            tri.x1, tri.y1 = int(self.x + size), int(self.y)
            tri.x2, tri.y2 = int(self.x - size*0.7), int(self.y - size*0.7)
            tri.x3, tri.y3 = int(self.x - size*0.7), int(self.y + size*0.7)
            tri.opacity = opacity
    
    def _scale_circle_shape(self, scale, opacity):
        if self.shape_elements:
            circle = self.shape_elements[0]
            circle.radius = max(1, int(self.base_radius * scale))
            circle.opacity = opacity
            circle.x, circle.y = int(self.x), int(self.y)
    
    def update_shapes(self):
        # Shapes are updated in update_visual_properties via perspective scaling
        pass
