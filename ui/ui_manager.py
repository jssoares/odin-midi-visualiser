
import time
from config.settings import Settings
from pyglet          import shapes, text

class UIManager:
    def __init__(self, window_width, window_height, ui_batch, grid_batch):
        # UI
        self.info_labels   = []
        self.event_labels  = []
        self.show_logs     = True
        self.ui_batch      = ui_batch
        self.grid_batch    = grid_batch
        self.window_width  = window_width
        self.window_height = window_height
        self.panels        = {}             # Store panel background shapes
        self.panel_labels  = {}             # Store labels organized by panel
        self.clean_font    = None           # Store working font name

        # Animation state for holographic effects
        self.pulse_timer       = 0.0
        self.last_data_update  = {}  # Track when each panel's data changed
        self.panel_fade_states = {}  # Track fade animations per panel

    def create_grid(self):
        grid_color   = Settings.GRID_COLOR
        grid_spacing = Settings.GRID_SPACING

        for x in range(0, self.window_width, grid_spacing):
            shapes.Line(x, 0, x, self.window_height, color=grid_color, batch=self.grid_batch)
        for y in range(0, self.window_height, grid_spacing):
            shapes.Line(0, y, self.window_width, y, color=grid_color, batch=self.grid_batch)
    
    def create_ui(self):
        # Setup font first
        self.setup_clean_font()
        
        # Create panels
        # Top-left: System Status
        self.panels['system'] = self.create_clean_panel(
            Settings.PANEL_LEFT_X, Settings.PANEL_TOP_Y, 
            Settings.PANEL_WIDTH, Settings.PANEL_HEIGHT, "SYSTEM"
        )

        # Calculate the offset to align bottoms of both panels
        audio_panel_y_offset = Settings.PANEL_HEIGHT_AUDIO - Settings.PANEL_HEIGHT

        # Top-right: Audio Analysis
        # Audio panel is taller
        self.panels['audio'] = self.create_clean_panel(
            Settings.PANEL_RIGHT_X, Settings.PANEL_TOP_Y - audio_panel_y_offset,
            Settings.PANEL_WIDTH, Settings.PANEL_HEIGHT_AUDIO, "AUDIO"
        )
        
        # Bottom-left: MIDI Data
        self.panels['midi'] = self.create_clean_panel(
            Settings.PANEL_LEFT_X, Settings.PANEL_BOTTOM_Y,
            Settings.PANEL_WIDTH, Settings.PANEL_HEIGHT, "MIDI"
        )
        
        # Bottom-right: Particle System
        self.panels['particles'] = self.create_clean_panel(
            Settings.PANEL_RIGHT_X, Settings.PANEL_BOTTOM_Y,
            Settings.PANEL_WIDTH, Settings.PANEL_HEIGHT, "PARTICLES"
        )
        
        # Create labels for each panel
        self.panel_labels['system'] = self.create_panel_labels(
            Settings.PANEL_LEFT_X, Settings.PANEL_TOP_Y, "SYSTEM", 6, Settings.PANEL_HEIGHT
        )
        
        self.panel_labels['audio'] = self.create_panel_labels(
            Settings.PANEL_RIGHT_X, Settings.PANEL_TOP_Y - audio_panel_y_offset, "AUDIO", 11, Settings.PANEL_HEIGHT_AUDIO
        )
        
        self.panel_labels['midi'] = self.create_panel_labels(
            Settings.PANEL_LEFT_X, Settings.PANEL_BOTTOM_Y, "MIDI", 8, Settings.PANEL_HEIGHT
        )
        
        self.panel_labels['particles'] = self.create_panel_labels(
            Settings.PANEL_RIGHT_X, Settings.PANEL_BOTTOM_Y, "PARTICLES", 6, Settings.PANEL_HEIGHT
        )

    def update_ui(self, audio_time, start_time, playing, midi_processor, video_recorder, network_manager, audio_analyzer):
        """Update all 4 panels with organized data"""
        self.update_system_panel(audio_time, start_time, playing, video_recorder)
        self.update_audio_panel(audio_analyzer)
        self.update_midi_panel(midi_processor)
        self.update_particles_panel(network_manager, midi_processor)

        # Apply subtle holographic animations
        self.update_panel_animations(1/60.0)  # Assume 60fps
        self.update_fade_effects()

    def update_system_panel(self, audio_time, start_time, playing, video_recorder):
        """Update top-left panel with core system status"""
        system_time = (time.time() - start_time) if (start_time and playing) else 0
        
        system_data = [
            f"AUDIO: {audio_time:.1f}s",
            f"SYSTEM: {system_time:.1f}s", 
            f"STATUS: {'PLAYING' if playing else 'STOPPED'}",
            f"RECORD: {'●REC' if video_recorder.recording else 'READY'}",
            f"FRAMES: {video_recorder.frames_recorded}",
            f"FPS: {video_recorder.target_fps}"
        ]
        
        for i, label in enumerate(self.panel_labels['system']):
            if i < len(system_data):
                label.text = system_data[i]
            else:
                label.text = ""

    def update_audio_panel(self, audio_analyzer):
        """Update top-right panel with complete audio frequency and panning data"""
        audio_data = [
            f"[FREQUENCY]",
            f"EARTH :  {audio_analyzer.element_frequency_levels['EARTH']:.4f}",
            f"WIND  :  {audio_analyzer.element_frequency_levels['WIND']:.4f}",
            f"FIRE  :  {audio_analyzer.element_frequency_levels['FIRE']:.4f}",
            f"WATER :  {audio_analyzer.element_frequency_levels['WATER']:.4f}",
            f"",
            f"[PANNING]",
            f"EARTH : {audio_analyzer.element_panning.get('EARTH', 0.0):+.4f}",
            f"WIND  : {audio_analyzer.element_panning.get('WIND', 0.0):+.4f}",
            f"FIRE  : {audio_analyzer.element_panning.get('FIRE', 0.0):+.4f}",
            f"WATER : {audio_analyzer.element_panning.get('WATER', 0.0):+.4f}",
        ]
        
        for i, label in enumerate(self.panel_labels['audio']):
            if i < len(audio_data):
                label.text = audio_data[i]
            else:
                label.text = ""

    def update_midi_panel(self, midi_processor):
        """Update bottom-left panel with MIDI event data"""
        active_elements = len([c for c, a in midi_processor.channel_activity.items() 
                            if a > 0.1 and c < 4])
        
        midi_data = [
            f"EVENTS: {midi_processor.current_event_index}/{len(midi_processor.midi_events)}",
            f"ACTIVE: {active_elements} ELEMENTS",
            f"CHANNELS: {len(midi_processor.active_channels)}",
            f"EARTH: {midi_processor.channel_activity.get(0, 0.0):.4f}",
            f"WIND:  {midi_processor.channel_activity.get(1, 0.0):.4f}",
            f"FIRE:  {midi_processor.channel_activity.get(2, 0.0):.4f}",
            f"WATER: {midi_processor.channel_activity.get(3, 0.0):.4f}",
        ]
        
        for i, label in enumerate(self.panel_labels['midi']):
            if i < len(midi_data):
                label.text = midi_data[i]
            else:
                label.text = ""

    def update_particles_panel(self, network_manager, midi_processor):
        """Update bottom-right panel with particle system and events"""
        odin_particles = len(network_manager.odin_node.particle_sink) if network_manager.odin_node else 0
        max_capacity = network_manager.odin_node.max_sink_capacity if network_manager.odin_node else 0
        
        # Show recent events if logs enabled, otherwise show more particle data
        if self.show_logs:
            recent_events = list(midi_processor.recent_events)[-4:]  # Only last 4 events
            particles_data = [
                f"ODIN: {odin_particles}/{max_capacity}",
                f"RECENT EVENTS:",
            ] + [event for event in recent_events]
        else:
            particles_data = [
                f"ODIN: {odin_particles}/{max_capacity}",
                f"CAPACITY: {(odin_particles/max_capacity*100):.1f}%" if max_capacity > 0 else "CAPACITY: 0%",
                f"PARTICLES: {len(network_manager.particles)}",
                f"EXPLOSIONS: {len(network_manager.explosion_particles)}",
                "",
                f"LOGS DISABLED"
            ]
        
        for i, label in enumerate(self.panel_labels['particles']):
            if i < len(particles_data):
                label.text = particles_data[i]
            else:
                label.text = ""

    def toggle_logs(self):
        """Toggle the display of event logs"""
        self.show_logs = not self.show_logs
        return self.show_logs  # Return new state for feedback

    def get_show_logs(self):
        """Get current log display state"""
        return self.show_logs
    
    def create_clean_panel(self, x, y, width, height, title):
        """Create a 2001/Minority Report style panel"""
        panel_info = {}
        
        # Subtle glow effect (behind everything, larger and transparent)
        glow = shapes.Rectangle(
            x - Settings.PANEL_GLOW_WIDTH, 
            y - Settings.PANEL_GLOW_WIDTH,
            width + (Settings.PANEL_GLOW_WIDTH * 2), 
            height + (Settings.PANEL_GLOW_WIDTH * 2),
            color=Settings.PANEL_GLOW[:3], 
            batch=self.ui_batch
        )
        glow.opacity = Settings.PANEL_GLOW[3]
        
        # Main panel background
        panel_bg = shapes.Rectangle(
            x, y, width, height, 
            color=Settings.PANEL_BACKGROUND[:3], 
            batch=self.ui_batch
        )
        panel_bg.opacity = Settings.PANEL_BACKGROUND[3]
        
        # Border (4 thin lines forming a rectangle outline)
        # Top border
        border_top = shapes.Rectangle(
            x, y + height - Settings.PANEL_BORDER_WIDTH, 
            width, Settings.PANEL_BORDER_WIDTH,
            color=Settings.PANEL_BORDER[:3], batch=self.ui_batch
        )
        border_top.opacity = Settings.PANEL_BORDER[3]

        # Bottom border
        border_bottom = shapes.Rectangle(
            x, y, 
            width, Settings.PANEL_BORDER_WIDTH,
            color=Settings.PANEL_BORDER[:3], batch=self.ui_batch
        )
        border_bottom.opacity = Settings.PANEL_BORDER[3]

        # Left border
        border_left = shapes.Rectangle(
            x, y, 
            Settings.PANEL_BORDER_WIDTH, height,
            color=Settings.PANEL_BORDER[:3], batch=self.ui_batch
        )
        border_left.opacity = Settings.PANEL_BORDER[3]

        # Right border
        border_right = shapes.Rectangle(
            x + width - Settings.PANEL_BORDER_WIDTH, y, 
            Settings.PANEL_BORDER_WIDTH, height,
            color=Settings.PANEL_BORDER[:3], batch=self.ui_batch
        )
        border_right.opacity = Settings.PANEL_BORDER[3]
        
        # Title label
        title_label = text.Label(
            title, font_name=self.clean_font, font_size=Settings.UI_TITLE_SIZE,
            color=Settings.PANEL_TITLE_COLOR,
            x=x + Settings.PANEL_PADDING, 
            y=y + height - Settings.PANEL_PADDING - 5,
            batch=self.ui_batch
        )
        
        panel_info['background'] = panel_bg
        panel_info['borders'] = [border_top, border_bottom, border_left, border_right]
        panel_info['glow'] = glow
        panel_info['title'] = title_label
        
        return panel_info

    def setup_clean_font(self):
        """Try to use clean monospace font with fallback"""
        # Pyglet will automatically fall back to system default if font doesn't exist
        # So we can just set our preferred font directly
        self.clean_font = Settings.UI_FONT_FAMILY
        print(f"✅ Using font: {Settings.UI_FONT_FAMILY} (with system fallback)")

    def create_panel_labels(self, panel_x, panel_y, panel_title, label_count, panel_height=None):
        """Create labels positioned within a clean panel"""
        labels = []
        
        # Use provided height or default
        if panel_height is None:
            panel_height = Settings.PANEL_HEIGHT
        
        for i in range(label_count):
            # Calculate Y position using the actual panel height
            label_y = (panel_y + panel_height - Settings.PANEL_PADDING - 
                    Settings.TITLE_BOTTOM_MARGIN - Settings.PANEL_TITLE_HEIGHT - 
                    (i * Settings.LINE_HEIGHT))
            
            label = text.Label(
                '', 
                font_name=self.clean_font, 
                font_size=Settings.UI_DATA_SIZE,
                color=Settings.PANEL_TEXT_COLOR,
                x=panel_x + Settings.PANEL_PADDING,
                y=label_y,
                batch=self.ui_batch
            )
            labels.append(label)
        
        return labels
    
    def update_panel_animations(self, dt):
        """Apply subtle 2001/Minority Report style animations"""
        if not Settings.PANEL_PULSE_ENABLED:
            return
        
        import math
        self.pulse_timer += dt
        
        # Calculate breathing pulse (sine wave)
        pulse_factor = math.sin(self.pulse_timer * Settings.PANEL_PULSE_SPEED * 2 * math.pi)
        pulse_opacity_modifier = 1.0 + (pulse_factor * Settings.PANEL_PULSE_INTENSITY)
        
        # Apply to all panel backgrounds
        for panel_name, panel_info in self.panels.items():
            if 'background' in panel_info:
                base_opacity = Settings.PANEL_BACKGROUND[3]
                new_opacity = int(base_opacity * pulse_opacity_modifier)
                panel_info['background'].opacity = max(20, min(255, new_opacity))

    def detect_data_changes(self, panel_name, new_data):
        """Detect when panel data changes for fade effects"""
        if panel_name not in self.last_data_update:
            self.last_data_update[panel_name] = new_data
            return False
        
        if self.last_data_update[panel_name] != new_data:
            self.last_data_update[panel_name] = new_data
            self.trigger_panel_highlight(panel_name)
            return True
        return False

    def trigger_panel_highlight(self, panel_name):
        """Subtle highlight when data changes (Minority Report style)"""
        if panel_name in self.panels and 'borders' in self.panels[panel_name]:
            # Briefly brighten the border
            for border in self.panels[panel_name]['borders']:
                # Store original opacity and boost it temporarily
                if not hasattr(border, 'original_opacity'):
                    border.original_opacity = border.opacity
                border.opacity = min(255, border.opacity + 60)
            
            # Schedule fade back to normal
            self.panel_fade_states[panel_name] = time.time()

    def update_fade_effects(self):
        """Handle fade-back animations for highlighted panels"""
        current_time = time.time()
        
        for panel_name, trigger_time in list(self.panel_fade_states.items()):
            if current_time - trigger_time > 0.5:  # Fade duration
                # Restore original border opacity
                if panel_name in self.panels and 'borders' in self.panels[panel_name]:
                    for border in self.panels[panel_name]['borders']:
                        if hasattr(border, 'original_opacity'):
                            border.opacity = border.original_opacity
                
                # Remove from fade tracking
                del self.panel_fade_states[panel_name]