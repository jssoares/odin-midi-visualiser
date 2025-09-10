import random
from .base_emitter    import BaseEmitter
from visual.particles import ElementalParticle

class RadialEmitter(BaseEmitter):
    def __init__(self, element_node, batch, emitter_offset=20):
        super().__init__(element_node, batch)
        self.emitter_offset = emitter_offset
        
    def get_emission_probability(self, freq_level, midi_activity):
        return 0.1 + (freq_level * 0.4)
    
    def emit_particles(self, odin_pos, particles_list, element_pan=0.0):
        if not self.can_emit():
            return
            
        element_pos = self.get_element_position_with_jitter()
        
        # Calculate top/bottom emitter positions
        top_emitter = (element_pos[0], element_pos[1] + self.emitter_offset)
        bottom_emitter = (element_pos[0], element_pos[1] - self.emitter_offset)
        
        # Calculate emission probabilities based on panning
        top_prob = max(0.2, 0.8 - element_pan)
        bottom_prob = max(0.2, 0.8 + element_pan)
        
        # Emit from top
        if random.random() < top_prob:
            top_particle = ElementalParticle(
                top_emitter, odin_pos, self.element_node.color,
                self.batch, None, (0, 0),
                element_type=self.element_node.element_type
            )
            particles_list.append(top_particle)
        
        # Emit from bottom
        if random.random() < bottom_prob:
            bottom_particle = ElementalParticle(
                bottom_emitter, odin_pos, self.element_node.color,
                self.batch, None, (0, 0),
                element_type=self.element_node.element_type
            )
            particles_list.append(bottom_particle)
