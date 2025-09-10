class ElementConfig:
    def __init__(self, name, channel, base_color, position_offset, frequency_range):
        self.name = name
        self.channel = channel
        self.base_color = base_color
        self.position_offset = position_offset  # (offset_x, offset_y)
        self.frequency_range = frequency_range  # (min_hz, max_hz)
        
        # Generate MIDI note color gradients
        self.note_gradients = self._generate_note_gradients()
        
        # Element-specific properties
        self.emitter_config = self._get_emitter_config()
        
    def _generate_note_gradients(self):
        """Generate 12-note color gradients for this element"""
        if self.name == "EARTH":
            return [
                [139, 69, 19], [150, 75, 20], [160, 80, 25], [170, 85, 30],
                [180, 90, 35], [190, 85, 25], [200, 80, 15], [210, 75, 10],
                [220, 70, 5], [200, 65, 15], [180, 60, 25], [160, 55, 35]
            ]
        elif self.name == "WIND":
            return [
                [135, 206, 235], [120, 200, 230], [105, 195, 225], [90, 190, 220],
                [75, 185, 215], [85, 180, 210], [95, 175, 205], [105, 170, 200],
                [115, 165, 195], [125, 160, 190], [135, 155, 185], [145, 150, 180]
            ]
        elif self.name == "FIRE":
            return [
                [180, 0, 0], [200, 10, 0], [220, 20, 0], [240, 30, 0],
                [255, 40, 0], [255, 60, 0], [255, 80, 0], [255, 100, 0],
                [255, 120, 0], [255, 140, 10], [255, 160, 20], [255, 180, 30]
            ]
        elif self.name == "WATER":
            return [
                [0, 191, 255], [10, 185, 250], [20, 180, 245], [30, 175, 240],
                [40, 170, 235], [35, 165, 230], [30, 160, 225], [25, 155, 220],
                [20, 150, 215], [15, 145, 210], [10, 140, 205], [5, 135, 200]
            ]
        else:
            return [self.base_color] * 12
    
    def _get_emitter_config(self):
        """Get emitter-specific configuration"""
        if self.name in ["FIRE", "EARTH"]:
            return {
                "type": "directional",
                "emitter_separation": 60,
                "emission_directions": [(-1, 0), (1, 0)]  # Left, Right
            }
        elif self.name == "WIND":
            return {
                "type": "radial", 
                "emitter_offset": 20,
                "emission_positions": [(0, 1), (0, -1)]  # Top, Bottom
            }
        elif self.name == "WATER":
            return {
                "type": "stream",
                "stream_interval": 0.06,
                "cluster_sizes": [4, 5, 6],
                "angle_spread": (-25, 25),
                "distance_range": (1, 12)
            }
    
    def get_note_color(self, midi_note):
        """Get color for specific MIDI note"""
        note_in_octave = midi_note % 12
        return self.note_gradients[note_in_octave]
    
    def get_world_position(self, center_x, center_y, satellite_distance):
        """Calculate world position from center"""
        offset_x, offset_y = self.position_offset
        return (
            center_x + (offset_x * satellite_distance),
            center_y + (offset_y * satellite_distance)
        )
