import random
from .base_emitter    import BaseEmitter
from visual.particles import ElementalParticle

class DirectionalEmitter(BaseEmitter):
    def __init__(self, element_node, batch, emitter_separation=60):
        super().__init__(element_node, batch)
        self.emitter_separation = emitter_separation
        
    def get_emission_probability(self, freq_level, midi_activity):
        return 0.1 + (freq_level * 0.4)
    
    def emit_particles(self, odin_pos, particles_list, element_pan=0.0):
        if not self.can_emit():
            return
            
        element_pos = self.get_element_position_with_jitter()
        
        # Calculate left/right emitter positions
        left_emitter = (element_pos[0] - self.emitter_separation//2, element_pos[1])
        right_emitter = (element_pos[0] + self.emitter_separation//2, element_pos[1])
        
        # Calculate emission probabilities based on panning
        left_prob, right_prob = self._calculate_pan_probabilities(element_pan)
        
        # Emit from left emitter
        if random.random() < left_prob:
            left_particle = ElementalParticle(
                left_emitter, odin_pos, self.element_node.color,
                self.batch, None, (0, 0),
                emission_direction=(-1, 0),
                element_type=self.element_node.element_type
            )
            particles_list.append(left_particle)
        
        # Emit from right emitter  
        if random.random() < right_prob:
            right_particle = ElementalParticle(
                right_emitter, odin_pos, self.element_node.color,
                self.batch, None, (0, 0),
                emission_direction=(1, 0),
                element_type=self.element_node.element_type
            )
            particles_list.append(right_particle)
    
    def _calculate_pan_probabilities(self, element_pan):
        """Calculate left/right emission probabilities from stereo panning"""
        if element_pan < -0.1:  # Panned left
            return 0.9, 0.1
        elif element_pan > 0.1:  # Panned right
            return 0.1, 0.9
        else:  # Center
            return 0.5, 0.5
