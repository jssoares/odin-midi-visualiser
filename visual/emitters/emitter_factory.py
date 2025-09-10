from .directional_emitter import DirectionalEmitter
from .radial_emitter      import RadialEmitter
from .stream_emitter      import StreamEmitter

class EmitterFactory:
    @staticmethod
    def create_emitter(element_type, element_node, batch):
        """Create appropriate emitter for element type"""
        if element_type in ["FIRE", "EARTH"]:
            return DirectionalEmitter(element_node, batch)
        elif element_type == "WIND":
            return RadialEmitter(element_node, batch)
        elif element_type == "WATER":
            return StreamEmitter(element_node, batch)
        else:
            raise ValueError(f"Unknown element type: {element_type}")
