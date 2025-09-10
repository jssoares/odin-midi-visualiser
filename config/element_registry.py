from .element_config import ElementConfig

class ElementRegistry:
    def __init__(self):
        self.elements = {}
        self.channel_to_element = {}
        self._setup_elements()
    
    def _setup_elements(self):
        """Initialize all element configurations"""
        element_definitions = [
            ("EARTH", 0, [139, 69, 19], (0, 1), (20, 250)),
            ("WIND", 1, [135, 206, 235], (1, 0), (250, 1000)),
            ("FIRE", 2, [220, 20, 20], (0, -1), (1000, 4000)),
            ("WATER", 3, [0, 191, 255], (-1, 0), (4000, 22050))
        ]
        
        for name, channel, color, position, freq_range in element_definitions:
            element_config = ElementConfig(name, channel, color, position, freq_range)
            self.elements[name] = element_config
            self.channel_to_element[channel] = element_config
    
    def get_element(self, name):
        """Get element config by name"""
        return self.elements.get(name)
    
    def get_element_by_channel(self, channel):
        """Get element config by MIDI channel"""
        return self.channel_to_element.get(channel)
    
    def get_all_elements(self):
        """Get all element configurations"""
        return list(self.elements.values())
    
    def get_frequency_bands(self):
        """Get frequency band mapping for audio analysis"""
        return {name: config.frequency_range for name, config in self.elements.items()}

# Global registry instance
ELEMENT_REGISTRY = ElementRegistry()
