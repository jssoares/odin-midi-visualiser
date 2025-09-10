from abc import ABC, abstractmethod

class BaseParticle(ABC):
    def __init__(self, start_pos, color, batch, element_type=None):
        self.x, self.y = start_pos
        self.color = color
        self.batch = batch
        self.element_type = element_type or "GENERIC"
        self.alive = True
        self.elapsed_time = 0.0
        
        # Create the visual representation
        self.shape_elements = self.create_shape(color, batch)
    
    @abstractmethod
    def create_shape(self, color, batch):
        """Create the visual shape elements for this particle"""
        pass
    
    @abstractmethod
    def update_movement(self, dt):
        """Update particle position and movement logic"""
        pass
    
    @abstractmethod 
    def update_visual_properties(self, dt):
        """Update visual properties like opacity, size, etc."""
        pass
    
    def update(self, dt, **kwargs):
        """Main update method - calls movement and visual updates"""
        self.elapsed_time += dt
        
        if not self.alive:
            return
            
        self.update_movement(dt)
        self.update_visual_properties(dt)
        self.update_shapes()
    
    def update_shapes(self):
        """Update shape positions - can be overridden for complex shapes"""
        if hasattr(self, 'shape_elements') and self.shape_elements:
            if len(self.shape_elements) == 1:  # Single shape
                shape = self.shape_elements[0]
                if hasattr(shape, 'x'):
                    shape.x, shape.y = int(self.x), int(self.y)
