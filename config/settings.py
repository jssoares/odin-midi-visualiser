import os

class Settings:
    # Window settings
    WINDOW_WIDTH  = 1400
    WINDOW_HEIGHT = 900
    WINDOW_TITLE  = "ODIN & Elements - MIDI Visualizer"
    
    # Visual settings
    GRID_COLOR   = (20, 30, 40)
    GRID_SPACING = 50
    
    # Network settings
    SATELLITE_DISTANCE = 250
    
    # Element configuration
    ELEMENT_DEFINITIONS = [
        # (offset_x, offset_y, channel, name, color)
        (0, 1, 0, "EARTH", [139, 69, 19]),       # Bottom (center_y + distance)
        (1, 0, 1, "WIND", [135, 206, 235]),      # Right (center_x + distance)  
        (0, -1, 2, "FIRE", [220, 20, 20]),       # Top (center_y - distance)
        (-1, 0, 3, "WATER", [0, 191, 255])       # Left (center_x - distance)
    ]

    # Background pattern settings
    BACKGROUND_PATTERN_ENABLED = True
    BACKGROUND_PATTERN_OPACITY = 60  # Very subtle
    BACKGROUND_PATTERN_SIZE = 30     # Size of pattern elements
    BACKGROUND_PATTERN_SPACING = 40 # Distance between pattern elements
    BACKGROUND_PATTERN_PULSE_INTENSITY = 0.3  # How much it pulses (0.0 to 1.0)

    # Audio settings
    DEFAULT_SAMPLE_RATE = 44100
    FFT_WINDOW_SIZE = 2048
    FFT_HOP_LENGTH = 512
    
    # Recording settings
    DEFAULT_TARGET_FPS = 25
    
    # UI settings
    INFO_LABEL_COUNT = 20
    EVENT_LABEL_COUNT = 15
    FONT_SIZE_INFO = 12
    FONT_SIZE_EVENT = 10
    LABEL_COLOR = (200, 200, 200, 255)

    # File paths
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
    AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
    MIDI_DIR = os.path.join(ASSETS_DIR, "midi")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
    OUTPUT_VIDEOS_DIR = os.path.join(OUTPUT_DIR, "videos")

    # Default filenames (can be overridden)
    DEFAULT_MIDI_FILE = "Odin.mid"
    DEFAULT_AUDIO_FILE = "Odin.mp3"
