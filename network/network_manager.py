import math
import random
from config.settings  import Settings
from visual.particles import ElementalParticle
from nodes            import OdinNode, ElementalNode, Connection

class NetworkManager:
    def __init__(self, window_width, window_height, batch, visualizer_ref):
        self.batch = batch
        self.channel_nodes = {}

        self.window_width = window_width
        self.window_height = window_height

        self.visualizer_ref = visualizer_ref

        # Network
        self.nodes = []
        self.connections = []
        self.odin_node = None
        
        # Particles
        self.particles = []
        self.explosion_particles = []  # New list for explosion particles

        # Create the network immediately
        self.create_network()

    def create_network(self):
        center_x, center_y = self.window_width // 2, self.window_height // 2
        
        # Odin - Central node with audio-reactive morphing
        self.odin_node = OdinNode(center_x, center_y, 0, self.batch, instrument_channel=None)
        self.nodes.append(self.odin_node)

        for i, (offset_x, offset_y, channel, name, color) in enumerate(Settings.ELEMENT_DEFINITIONS):
            x = center_x + (offset_x * Settings.SATELLITE_DISTANCE)
            y = center_y + (offset_y * Settings.SATELLITE_DISTANCE)
            
            element_node = ElementalNode(
                x, y, i + 1, self.batch, instrument_channel=channel, 
                element_type=name, element_color=color
            )
            element_node.visualizer_ref = self.visualizer_ref
            self.nodes.append(element_node)
            self.channel_nodes[channel] = element_node
        
        # Connections - each element connects to Odin
        for i in range(1, 5):
            connection = Connection(self.nodes[0], self.nodes[i], self.batch)
            self.connections.append(connection)
        
        print("🌟 Created Odin & Elements network:")
        print("   🏔️  EARTH (CH0) - Brown squares with crystal spikes")
        print("   💨 WIND (CH1) - Sky blue circles with flowing streams") 
        print("   🔥 FIRE (CH2) - Red-orange flames with dancing tips")
        print("   💧 WATER (CH3) - Deep blue drops with rippling waves")
        print("   ⚡ ODIN (Central) - Audio-reactive morphing square→circle")

    def update_odin_from_elements(self, midi_processor, audio_analyzer):
        """Update Odin based on elemental activity - elements can push/pull Odin around"""
        if not self.odin_node:
            return
        
        # Count active channels (instruments with notes currently held)
        active_element_channels = [ch for ch in midi_processor.active_channels if ch < 4]  # Only elements (0-3)
        num_active_instruments = len(active_element_channels)
        
        # Calculate sustained activity from held notes
        sustained_activity = 0
        elemental_colors = []
        
        # Calculate forces that will push/pull Odin
        odin_force_x = 0.0
        odin_force_y = 0.0
        
        for channel in active_element_channels:
            if channel in midi_processor.channel_activity and channel in self.channel_nodes:
                activity = midi_processor.channel_activity[channel]
                sustained_activity += activity

                element_node = self.channel_nodes[channel]
                elemental_colors.append([c * activity for c in element_node.base_color])
                
                # Get element type to determine how pan affects emission
                element_type = element_node.element_type

                # NEW: Base emission on frequency activity
                element_freq_level = audio_analyzer.element_frequency_levels.get(element_type, 0.0)
                emission_probability = 0.1 + (element_freq_level * 0.4)  # 0.1 to 0.5 range
                if random.random() < emission_probability:
                    element_pos = element_node.get_current_position()
                    odin_pos = self.odin_node.get_current_position()
                    
                    # Get this element's individual panning
                    element_pan = 0.0
                    if element_type in audio_analyzer.element_panning:
                        element_pan = audio_analyzer.element_panning[element_type]
                    
                    # Add subtle random movement to emitters
                    subtle_offset_x = random.uniform(-8, 8)  # ±8 pixels random movement
                    subtle_offset_y = random.uniform(-8, 8)  # ±8 pixels random movement
                    
                    if element_type == "FIRE" or element_type == "EARTH":  # North/South elements
                        # Get this element's individual panning
                        element_pan = 0.0
                        if element_type in audio_analyzer.element_panning:
                            element_pan = audio_analyzer.element_panning[element_type]
                        
                        # Calculate LEFT and RIGHT emitter positions with subtle movement
                        left_emitter_pos = (element_pos[0] - 30 + subtle_offset_x, element_pos[1] + subtle_offset_y)
                        right_emitter_pos = (element_pos[0] + 30 + subtle_offset_x, element_pos[1] + subtle_offset_y)
                        
                        # Calculate emission probabilities based on stereo panning
                        # Pan ranges from -1.0 (left) to +1.0 (right)
                        if element_pan < -0.1:  # Panned left
                            left_probability = 0.9   # High chance from left
                            right_probability = 0.1  # Low chance from right
                        elif element_pan > 0.1:  # Panned right
                            left_probability = 0.1   # Low chance from left
                            right_probability = 0.9  # High chance from right
                        else:  # Center or no panning
                            left_probability = 0.5   # Equal chance from both sides
                            right_probability = 0.5
                        
                            # LEFT EMITTER
                            if random.random() < left_probability:
                                left_particle = ElementalParticle(
                                    left_emitter_pos, odin_pos, element_node.color, 
                                    self.batch, self.odin_node, (0, 0), 
                                    emission_direction=(-1, 0)  # Emit westward
                                )
                                self.particles.append(left_particle)

                            # RIGHT EMITTER
                            if random.random() < right_probability:
                                right_particle = ElementalParticle(
                                    right_emitter_pos, odin_pos, element_node.color, 
                                    self.batch, self.odin_node, (0, 0),
                                    emission_direction=(1, 0)  # Emit eastward
                                )
                                self.particles.append(right_particle)
                            
                    elif element_type == "WIND" or element_type == "WATER":  # East/West elements
                        # Calculate TOP and BOTTOM emitter positions with subtle movement
                        top_emitter_pos = (element_pos[0] + subtle_offset_x, element_pos[1] + 23 + subtle_offset_y)
                        bottom_emitter_pos = (element_pos[0] + subtle_offset_x, element_pos[1] - 18 + subtle_offset_y)
                        
                        # Calculate emission probabilities
                        top_probability = max(0.2, 0.8 - element_pan)
                        bottom_probability = max(0.2, 0.8 + element_pan)
                        
                        # TOP EMITTER
                        if random.random() < top_probability:
                            top_particle = ElementalParticle(
                                top_emitter_pos, odin_pos, element_node.color, 
                                self.batch, self.odin_node, (0, 0)
                            )
                            self.particles.append(top_particle)
                        
                        # BOTTOM EMITTER
                        if random.random() < bottom_probability:
                            bottom_particle = ElementalParticle(
                                bottom_emitter_pos, odin_pos, element_node.color, 
                                self.batch, self.odin_node, (0, 0)
                            )
                            self.particles.append(bottom_particle)
                
                # Calculate force from this element on Odin
                # Each active element "pushes" Odin away from its original position
                dx = self.odin_node.original_x - element_node.original_x
                dy = self.odin_node.original_y - element_node.original_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    # Normalize direction (from element to Odin)
                    nx = dx / distance
                    ny = dy / distance
                    
                    # Force strength based on activity
                    force_strength = activity * 8.0  # Scale force
                    
                    # Apply force (elements push Odin away)
                    odin_force_x += nx * force_strength
                    odin_force_y += ny * force_strength
        
        # Update Odin based on sustained elemental activity
        if num_active_instruments > 0:
            # ENHANCED compound effect: grows based on number of active instruments
            base_multiplier = sustained_activity
            
            # Exponential scaling for multiple active instruments
            if num_active_instruments == 1:
                compound_factor = base_multiplier * 1.0        # Normal growth for single instrument
            elif num_active_instruments == 2:
                compound_factor = base_multiplier * 2.5        # 2.5x growth for dual instruments
            elif num_active_instruments == 3:
                compound_factor = base_multiplier * 4.0        # 4x growth for triple instruments
            elif num_active_instruments == 4:
                compound_factor = base_multiplier * 6.0        # 6x growth for all instruments (GODMODE!)
            else:
                compound_factor = base_multiplier
            
            # Odin maintains this size while notes are held, grows more when additional instruments join
            target_size = self.odin_node.base_size + compound_factor * 50
            
            # Only grow larger, don't shrink while any notes are held
            if target_size > self.odin_node.target_size:
                self.odin_node.target_size = target_size
            # If current target is already larger, maintain it
            
            self.odin_node.activity = min(1.0, compound_factor * 1.2)
            
            # Apply elemental forces to move Odin's position
            new_odin_x = self.odin_node.original_x + odin_force_x
            new_odin_y = self.odin_node.original_y + odin_force_y
            
            # Limit Odin's movement to prevent going off-screen
            max_displacement = 50
            new_odin_x = max(max_displacement, min(self.window_width - max_displacement, new_odin_x))
            new_odin_y = max(max_displacement, min(self.window_height - max_displacement, new_odin_y))

            
            self.odin_node.set_position(new_odin_x, new_odin_y)
            
            # Color mixing: blend elemental colors
            if elemental_colors:
                # Average the active elemental colors
                mixed_color = [0, 0, 0]
                for color in elemental_colors:
                    for i in range(3):
                        mixed_color[i] += color[i]
                
                # Normalize and blend with Odin's base color
                blend_ratio = min(0.6, num_active_instruments * 0.15)
                for i in range(3):
                    mixed_color[i] = mixed_color[i] / len(elemental_colors)
                    # Dynamic blending based on number of active instruments
                    self.odin_node.target_color[i] = min(255, 
                        self.odin_node.base_color[i] * (1 - blend_ratio) + mixed_color[i] * blend_ratio)
            
            # DYNAMIC CONNECTION PULL: Make connections pull elements toward Odin
            connection_pull_strength = min(1.0, compound_factor * 0.8)  # Scale with Odin's power
            for connection in self.connections:
                if connection.node1 == self.odin_node or connection.node2 == self.odin_node:
                    # Set connection pull based on Odin's power
                    connection.set_connection_pull(connection_pull_strength)
                    
                    # Enhanced pulsation effect through connections
                    pulse_intensity = compound_factor * (0.6 + num_active_instruments * 0.2)
                    connection.note_trigger(min(1.0, pulse_intensity))
                    
        else:
            # No notes held - Odin returns to base state and original position
            self.odin_node.target_size = self.odin_node.base_size
            self.odin_node.target_color = self.odin_node.base_color.copy()
            self.odin_node.activity *= 0.85  # Slow decay
            
            # Smoothly return Odin to center
            center_x, center_y = self.window_width // 2, self.window_height // 2
            self.odin_node.set_position(center_x, center_y)
            
            # Release connection pull
            for connection in self.connections:
                if connection.node1 == self.odin_node or connection.node2 == self.odin_node:
                    connection.set_connection_pull(0.0)

    def update_particles(self, dt):
        """Update particles and return if explosion is needed"""
        explosion_needed = False
        
        # Update particles and check for particles reaching Odin
        particles_to_remove = []
        for i, particle in enumerate(self.particles):
            particle.update(dt)
            if not particle.alive:
                particles_to_remove.append(i)
            else:
                # Check if particle reached Odin
                odin_pos = self.odin_node.get_current_position()
                dist_to_odin = math.hypot(particle.x - odin_pos[0], particle.y - odin_pos[1])
                if dist_to_odin < 20:  # Within Odin's radius
                    if self.odin_node.add_particle_to_sink(particle):
                        particles_to_remove.append(i)

        # Remove processed particles
        for i in reversed(particles_to_remove):
            self.particles.pop(i)

        # Update explosion particles
        explosion_particles_to_remove = []
        for i, explosion_particle in enumerate(self.explosion_particles):
            explosion_particle.update(dt)
            if not explosion_particle.alive:
                explosion_particles_to_remove.append(i)

        # Remove finished explosion particles
        for i in reversed(explosion_particles_to_remove):
            self.explosion_particles.pop(i)
        
        return explosion_needed

    def update_nodes_and_connections(self, dt, audio_level):
        """Update all nodes and connections"""
        explosion_needed = False
        
        # Update all nodes (with audio level for Odin)
        for node in self.nodes:
            if isinstance(node, OdinNode):
                if node.update(dt, audio_level):
                    explosion_needed = True
            else:
                node.update(dt)

        # Handle Odin explosion if needed
        if explosion_needed:
            self.odin_node.explode_particles(self.explosion_particles, self.batch)

        # Update all connections
        for connection in self.connections:
            connection.update(dt)
        
        return explosion_needed