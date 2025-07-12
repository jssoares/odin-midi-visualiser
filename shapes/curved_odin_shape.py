from pyglet import shapes
import math

class CurvedOdinShape:
    """Custom shape for Odin that can morph from square to curved based on audio"""
    def __init__(self, x, y, size, batch):
        self.x = int(x)
        self.y = int(y)
        self.size = int(size)
        self.batch = batch
        self.curvature = 0.0  # 0 = square, 1 = fully curved
        self.target_curvature = 0.0
        
        # Use multiple overlapping circles/rectangles for morphing effect
        self.base_rect = shapes.Rectangle(
            x - size, y - size, size * 2, size * 2, 
            color=(120, 80, 180), batch=batch
        )
        self.base_rect.opacity = 128
        
        # Create overlapping circles for curved effect
        self.circles = []
        for i in range(8):  # 8 circles for smooth morphing
            angle = (2 * math.pi * i) / 8
            offset_x = math.cos(angle) * size * 0.3
            offset_y = math.sin(angle) * size * 0.3
            circle = shapes.Circle(
                int(x + offset_x), int(y + offset_y), int(size * 0.4), 
                color=(120, 80, 180), batch=batch
            )
            circle.opacity = 0  # Start invisible
            self.circles.append(circle)
    
    def update(self, dt, color, audio_intensity=0.0, current_size=45):
        """Update the shape with new curvature based on audio"""
        # Ensure color is integers
        color = [int(c) for c in color]
        
        # Update curvature towards target
        self.curvature += (self.target_curvature - self.curvature) * dt * 6
        
        # Set target curvature based on audio intensity
        self.target_curvature = min(1.0, audio_intensity * 1.5)
        
        # Calculate hollow effect based on size
        base_size = 45  # Base size from OdinNode
        
        # Hollow effect kicks in when size is > 1.8x base size
        hollow_threshold = base_size * 1.01
        if current_size > hollow_threshold:
            # Calculate hollow intensity (0.0 to 1.0)
            size_excess = current_size - hollow_threshold
            max_excess = (120 - hollow_threshold)  # Max size is 120
            hollow_intensity = min(0.7, size_excess / max_excess) if max_excess > 0 else 0.0
            
            # Make rectangle hollow by reducing its opacity significantly
            base_opacity = int(128 * (1 - self.curvature * 0.7) * (1 - hollow_intensity * 0.9))
        else:
            # Normal opacity when not large enough
            base_opacity = int(128 * (1 - self.curvature * 0.7))
        
        # Update base rectangle
        self.base_rect.color = tuple(color)
        self.base_rect.opacity = base_opacity
        
        # Update circles for curved effect
        circle_opacity = int(min(255, max(0, self.curvature * 80)))
        for circle in self.circles:
            circle.color = tuple(color)
            circle.opacity = circle_opacity
    
    def set_position_and_size(self, x, y, size):
        """Update position and size"""
        x, y, size = int(x), int(y), int(size)
        if abs(self.x - x) > 1 or abs(self.y - y) > 1 or abs(self.size - size) > 1:
            self.x = x
            self.y = y
            self.size = size
            
            # Update rectangle
            self.base_rect.x = x - size
            self.base_rect.y = y - size
            self.base_rect.width = size * 2
            self.base_rect.height = size * 2
            
            # Update circles
            for i, circle in enumerate(self.circles):
                angle = (2 * math.pi * i) / 8
                offset_x = math.cos(angle) * size * 0.3
                offset_y = math.sin(angle) * size * 0.3
                circle.x = int(x + offset_x)
                circle.y = int(y + offset_y)
                circle.radius = int(size * 0.4)
    
    def delete(self):
        """Clean up - not needed with batch rendering"""
        pass