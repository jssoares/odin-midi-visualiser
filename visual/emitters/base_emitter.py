import abc
import random

class BaseEmitter(abc.ABC):
    def __init__(self, element_node, batch):
        self.element_node = element_node
        self.batch = batch
        self.emission_cooldown = 0.0
        self.last_emission_time = 0.0
        
    @abc.abstractmethod
    def get_emission_probability(self, freq_level, midi_activity):
        """Calculate base emission probability"""
        pass
    
    @abc.abstractmethod
    def emit_particles(self, odin_pos, particles_list, element_pan=0.0):
        """Emit particles toward Odin"""
        pass
    
    def update_cooldown(self, dt):
        """Update emission cooldown timer"""
        self.emission_cooldown -= dt
        
    def can_emit(self):
        """Check if cooldown allows emission"""
        return self.emission_cooldown <= 0
    
    def get_element_position_with_jitter(self):
        """Get element position with subtle random movement"""
        pos = self.element_node.get_current_position()
        jitter_x = random.uniform(-8, 8)
        jitter_y = random.uniform(-8, 8)
        return (pos[0] + jitter_x, pos[1] + jitter_y)
