import os

class Settings:
    # Window settings
    WINDOW_WIDTH  = 1920
    WINDOW_HEIGHT = 1080
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
    BACKGROUND_PATTERN_ENABLED         = True
    BACKGROUND_PATTERN_OPACITY         = 20  # Very subtle
    BACKGROUND_PATTERN_SIZE            = 30     # Size of pattern elements
    BACKGROUND_PATTERN_SPACING         = 40 # Distance between pattern elements
    BACKGROUND_PATTERN_PULSE_INTENSITY = 0.3  # How much it pulses (0.0 to 1.0)
    # BACKGROUND_PATTERN_COLOR           = (40, 50, 60) # Light lattice
    BACKGROUND_PATTERN_COLOR           = (120, 120, 120) # Dark Lattice

    # Audio settings
    DEFAULT_SAMPLE_RATE = 44100
    FFT_WINDOW_SIZE     = 2048
    FFT_HOP_LENGTH      = 512
    
    # Recording settings
    DEFAULT_TARGET_FPS = 25
    
    # UI settings
    INFO_LABEL_COUNT  = 20
    EVENT_LABEL_COUNT = 15
    FONT_SIZE_INFO    = 12
    FONT_SIZE_EVENT   = 10
    LABEL_COLOR       = (200, 200, 200, 255)

    # UI Panel Layout (clean, geometric spacing)
    PANEL_MARGIN       = 30     # Distance from screen edges
    PANEL_SPACING      = 20     # Space between panels
    PANEL_WIDTH        = 280    # Fixed width for consistency
    PANEL_HEIGHT       = 180    # Fixed height for clean rectangles
    PANEL_PADDING      = 15     # Internal padding inside panels
    PANEL_TITLE_HEIGHT = 25     # Height reserved for panel titles

    # Panel Positions (calculated from margins)
    PANEL_TOP_Y    = WINDOW_HEIGHT - PANEL_MARGIN - PANEL_HEIGHT
    PANEL_BOTTOM_Y = PANEL_MARGIN + 30
    PANEL_LEFT_X   = PANEL_MARGIN  
    PANEL_RIGHT_X  = WINDOW_WIDTH - PANEL_MARGIN - PANEL_WIDTH

    # Clean Color Palette (muted, professional)
    PANEL_BACKGROUND  = (5, 8, 12, 100)        # Darker background
    PANEL_BORDER      = (120, 160, 200, 220)   # Brighter borders
    PANEL_GLOW        = (80, 120, 160, 60)     # Subtle blue glow
    PANEL_TITLE_COLOR = (255, 255, 255, 255)   # Pure white titles
    PANEL_TEXT_COLOR  = (240, 250, 255, 255)   # Higher contrast text
    PANEL_ACCENT      = (100, 150, 200, 255)   # Blue accent for highlights

    # Monospace Font Settings (2001 computer aesthetic)
    UI_FONT_FAMILY   = "Consolas"     # Primary choice
    UI_FONT_FALLBACK = "Courier New"  # Fallback monospace
    UI_TITLE_SIZE    = 11             # Panel titles
    UI_DATA_SIZE     = 9              # Data text
    UI_SMALL_SIZE    = 8              # Secondary info

    # Border and Glow Settings (minimal, clean)
    PANEL_BORDER_WIDTH  = 1  # Ultra-thin borders
    PANEL_GLOW_WIDTH    = 3  # Subtle glow effect
    PANEL_CORNER_RADIUS = 0  # Sharp, geometric corners

    # Panel Content Layout
    LINES_PER_PANEL     = 6   # Max lines per panel
    LINE_HEIGHT         = 14  # Spacing between lines
    TITLE_BOTTOM_MARGIN = 8   # Space below panel titles

    # File paths
    PROJECT_ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSETS_DIR        = os.path.join(PROJECT_ROOT, "assets")
    AUDIO_DIR         = os.path.join(ASSETS_DIR, "audio")
    MIDI_DIR          = os.path.join(ASSETS_DIR, "midi")
    OUTPUT_DIR        = os.path.join(PROJECT_ROOT, "output")
    OUTPUT_VIDEOS_DIR = os.path.join(OUTPUT_DIR, "videos")

    # Default filenames (can be overridden)
    DEFAULT_MIDI_FILE  = "Odin.mid"
    DEFAULT_AUDIO_FILE = "Odin.mp3"
