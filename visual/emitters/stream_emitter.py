import random
import math
from .base_emitter    import BaseEmitter
from visual.particles import WaterParticle

class StreamEmitter(BaseEmitter):
    def __init__(self, element_node, batch, stream_interval=0.06):
        super().__init__(element_node, batch)
        self.stream_interval = stream_interval
        self.cluster_sizes = [4, 5, 6]
        self.angle_spread_range = (-25, 25)
        self.distance_range = (1, 12)
        
    def get_emission_probability(self, freq_level, midi_activity):
        # Water uses time-based emission instead of probability
        return 1.0
    
    def emit_particles(self, odin_pos, particles_list, element_pan=0.0):
        if not self.can_emit():
            return
            
        element_pos = self.get_element_position_with_jitter()
        
        # Create water droplet cluster
        cluster_size = random.choice(self.cluster_sizes)
        
        for i in range(cluster_size):
            droplet_pos = self._calculate_droplet_position(element_pos, odin_pos)
            
            water_particle = WaterParticle(
                droplet_pos, odin_pos, self.element_node.color,
                self.batch, None, (0, 0)
            )
            
            # Configure stream properties
            water_particle.curve_intensity = random.uniform(0.2, 0.4)
            water_particle.curve_start_time = random.uniform(0.8, 1.4)
            water_particle.speed = random.uniform(55, 80)
            water_particle.stream_alignment_strength = random.uniform(0.4, 0.8)
            
            particles_list.append(water_particle)
        
        # Reset cooldown for next emission
        self.emission_cooldown = random.uniform(0.04, 0.08)
    
    def _calculate_droplet_position(self, element_pos, odin_pos):
        """Calculate organic droplet position with angular variation"""
        angle_spread = random.uniform(*self.angle_spread_range)
        distance = random.uniform(*self.distance_range)
        
        base_angle = math.atan2(
            odin_pos[1] - self.element_node.original_y,
            odin_pos[0] - self.element_node.original_x
        )
        varied_angle = base_angle + math.radians(angle_spread)
        
        return (
            self.element_node.original_x + math.cos(varied_angle) * distance,
            self.element_node.original_y + math.sin(varied_angle) * distance
        )
