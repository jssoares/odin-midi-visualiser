
import time
from config.settings import Settings
from pyglet          import shapes, text

class UIManager:
    def __init__(self, window_width, window_height, ui_batch, grid_batch):
        # UI
        self.info_labels = []
        self.event_labels = []
        self.show_logs = True
        self.ui_batch = ui_batch
        self.grid_batch = grid_batch
        self.window_width = window_width
        self.window_height = window_height

    def create_grid(self):
        grid_color   = Settings.GRID_COLOR
        grid_spacing = Settings.GRID_SPACING

        for x in range(0, self.window_width, grid_spacing):
            shapes.Line(x, 0, x, self.window_height, color=grid_color, batch=self.grid_batch)
        for y in range(0, self.window_height, grid_spacing):
            shapes.Line(0, y, self.window_width, y, color=grid_color, batch=self.grid_batch)
    
    def create_ui(self):
        for i in range(Settings.INFO_LABEL_COUNT):
            label = text.Label(
                '', font_size=Settings.FONT_SIZE_INFO, color=Settings.LABEL_COLOR,
                x=10, y=self.window_height - 30 - i * 20, batch=self.ui_batch
            )
            self.info_labels.append(label)
        
        for i in range(Settings.EVENT_LABEL_COUNT):
            label = text.Label(
                '', font_size=Settings.FONT_SIZE_EVENT, color=Settings.LABEL_COLOR,
                x=10, y=self.window_height - 200 - i * 16, batch=self.ui_batch
            )
            self.event_labels.append(label)

    def update_ui(self, audio_time, start_time, playing, midi_processor, video_recorder, network_manager, audio_analyzer):
        system_time = (time.time() - start_time) if (start_time and playing) else 0
        info_text = [
            f"Audio Time: {audio_time:.1f}s",
            f"System Time: {system_time:.1f}s",
            f"Events: {midi_processor.current_event_index}/{len(midi_processor.midi_events)}",
            f"Playing: {'Yes' if playing else 'No'}",
            f"Recording: {'🔴 REC' if video_recorder.recording else 'No'}",
            f"Frames: {video_recorder.frames_recorded}" if video_recorder.recording else "Press V to record",
            f"Target FPS: {video_recorder.target_fps}",
            f"Active Elements: {len([c for c, a in midi_processor.channel_activity.items() if a > 0.1 and c < 4])}",
            f"Particles in Odin: {len(network_manager.odin_node.particle_sink) if network_manager.odin_node else 0}/{network_manager.odin_node.max_sink_capacity if network_manager.odin_node else 0}",
            f"EARTH: {audio_analyzer.element_frequency_levels['EARTH']:.4f}",
            f"WATER: {audio_analyzer.element_frequency_levels['WATER']:.4f}",
            f"FIRE: {audio_analyzer.element_frequency_levels['FIRE']:.4f}",
            f"WIND: {audio_analyzer.element_frequency_levels['WIND']:.4f}",
            f"EARTH Pan: {audio_analyzer.element_panning.get('EARTH', 0.0):.2f}",
            f"WATER Pan: {audio_analyzer.element_panning.get('WATER', 0.0):.2f}",
            f"FIRE Pan: {audio_analyzer.element_panning.get('FIRE', 0.0):.2f}",
            f"WIND Pan: {audio_analyzer.element_panning.get('WIND', 0.0):.2f}",
        ]
        
        for i, (label, text) in enumerate(zip(self.info_labels, info_text)):
            if label:
                label.text = text
        
        # Event log
        if self.show_logs:
            recent_events_list = list(midi_processor.recent_events)[-8:]
            for i, label in enumerate(self.event_labels):
                if i < len(recent_events_list) and label:
                    label.text = recent_events_list[-(i+1)]
                    alpha = max(50, 255 - i * 25)
                    label.color = (alpha, alpha, alpha, 255)
                elif label:
                    label.text = ""
        else:
            for label in self.event_labels:
                label.text = ""

    def toggle_logs(self):
        """Toggle the display of event logs"""
        self.show_logs = not self.show_logs
        return self.show_logs  # Return new state for feedback

    def get_show_logs(self):
        """Get current log display state"""
        return self.show_logs