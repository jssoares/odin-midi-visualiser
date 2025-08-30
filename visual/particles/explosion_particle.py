import random
from pyglet import shapes

class ExplosionParticle:
    def __init__(self, start_pos, direction, color, batch, depth_factor=1.0, element_type=None):
        self.x, self.y = start_pos
        self.vx = direction[0] * random.uniform(100, 300)
        self.vy = direction[1] * random.uniform(100, 300)
        self.color = color
        self.element_type = element_type or "GENERIC"

        # 3D depth properties
        self.depth_factor = depth_factor  # 1.0 = normal, >1.0 = closer to camera
        self.base_radius = 2
        self.current_radius = int(self.base_radius * depth_factor)
        self.max_alpha = min(255, int(255 / depth_factor))  # Closer = more transparent

        # Create element-specific shape
        self.shape_elements = self.create_element_shape(color, batch)
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
        
        # Update shapes based on element type
        self.update_shapes()
        
        # Fade based on life and depth
        life_alpha = self.life * 255
        final_alpha = min(life_alpha, self.max_alpha)
        
        # Set opacity for all shape elements
        for shape in self.shape_elements:
            shape.opacity = max(0, int(final_alpha))

    def update_shapes(self):
        """Update all shape elements based on current position"""
        if self.element_type == "FIRE":
            # Update chevron lines
            if len(self.shape_elements) >= 2:
                left_line, right_line = self.shape_elements[0], self.shape_elements[1]
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
            if self.shape_elements:
                square = self.shape_elements[0]
                square.x, square.y = int(self.x-1), int(self.y-1)
                if self.depth_factor > 1.0:
                    square.width = square.height = max(1, self.current_radius * 2)

        elif self.element_type == "WATER":
            # Update triangle - all vertices move together
            if self.shape_elements:
                tri = self.shape_elements[0]
                # All vertices relative to current position
                tri.x1, tri.y1 = int(self.x + 3), int(self.y)      # tip
                tri.x2, tri.y2 = int(self.x - 2), int(self.y - 2)  # bottom back
                tri.x3, tri.y3 = int(self.x - 2), int(self.y + 2)  # top back

        else:
            # Update circle (generic fallback)
            if self.shape_elements:
                circle = self.shape_elements[0]
                circle.x, circle.y = int(self.x), int(self.y)
                if self.depth_factor > 1.0:
                    circle.radius = max(1, self.current_radius)

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
            # For explosion particles, all vertices move together immediately
            if self.shape_elements:
                tri = self.shape_elements[0]
                # All vertices relative to current position
                tip_x, tip_y = int(self.x + 3), int(self.y)
                base_left_x, base_left_y = int(self.x - 2), int(self.y - 2)
                base_right_x, base_right_y = int(self.x - 2), int(self.y + 2)
                
                tri.x1, tri.y1 = tip_x, tip_y
                tri.x2, tri.y2 = base_left_x, base_left_y
                tri.x3, tri.y3 = base_right_x, base_right_y
        
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
        