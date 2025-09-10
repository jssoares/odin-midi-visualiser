import pyglet
import time
import os
import librosa

from config.settings          import Settings
from audio                    import AudioAnalyzer, AudioPlayer
from midi.midi_processor      import MIDIProcessor
from recording.video_recorder import VideoRecorder
from network.network_manager  import NetworkManager
from ui.ui_manager            import UIManager
from visual.visual_manager    import VisualManager
from utils.file_manager       import FileManager

from video.video_effects_manager import VideoEffectsManager


class MIDIVisualizer(pyglet.window.Window):
    def __init__(self):
        super().__init__(
            width=Settings.WINDOW_WIDTH, 
            height=Settings.WINDOW_HEIGHT, 
            caption=Settings.WINDOW_TITLE,
        )

        pyglet.gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Rendering batches
        self.batch = pyglet.graphics.Batch()
        self.ui_batch = pyglet.graphics.Batch()
        self.grid_batch = pyglet.graphics.Batch()
        self.video_batch = pyglet.graphics.Batch()
        
        # Instantitate the audio analyzer class
        self.audio_analyzer = AudioAnalyzer()

        # Instantiate the audio player class
        self.audio_player = AudioPlayer()

        # Instantiate the midi processor class
        self.midi_processor = MIDIProcessor()

        # Instantitate the video recorder class
        self.video_recorder = VideoRecorder()

        # Instantiate the ui manager class
        self.ui_manager = UIManager(self.width, self.height, self.ui_batch, self.grid_batch)

        # Instantiate the network manager class
        self.network_manager = NetworkManager(self.width, self.height, self.batch, self)

        # Instantiate the visual manager class
        self.visual_manager = VisualManager(self.width, self.height, self.grid_batch)        

        # Instantiate the video effects manager class
        self.video_effects_manager = VideoEffectsManager(self.width, self.height, self.video_batch)

        self.start_time = None
        self.playing = False
        
        # Visual state
        self.background_intensity = 0
        
        # UI
        self.ui_manager.create_ui()
        self.ui_manager.create_grid()
        
        # Update loop
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        
        self.total_audio_duration = None

        print("🌟 Odin & Elements MIDI Visualizer initialized")
    
    def update(self, dt):
        """Main update loop"""
        try:
            audio_time = self.audio_player.get_current_time()
            # Process MIDI if playing
            if self.playing:    
                if self.playing and self.audio_analyzer.audio_data is not None:
                    self.audio_analyzer.get_element_frequency_levels_and_panning(audio_time)
                
                self.midi_processor.process_midi_events(audio_time, self.network_manager.channel_nodes, self.network_manager.connections)
            
            # Update visuals
            total_activity = sum(self.midi_processor.channel_activity.values())
            self.background_intensity = min(0.3, max(0, total_activity * 0.1))
            
            # Update all nodes (with audio level for Odin)
            audio_level = self.audio_analyzer.get_audio_level(self.midi_processor.channel_activity, self.playing)

            # Update network components
            self.network_manager.update_nodes_and_connections(dt, audio_level)
            self.network_manager.update_particles(dt)
            self.network_manager.update_odin_from_elements(self.midi_processor, self.audio_analyzer, dt)

            # Update visual effects (background patterns, etc.)
            self.visual_manager.update_effects(dt, total_activity)
            
            # Update video effects (fades, transitions, etc.)
            elapsed_time = audio_time if self.playing else 0.0
            self.video_effects_manager.update_effects(elapsed_time)

            # Update UI
            self.ui_manager.update_ui(
                audio_time,
                self.start_time,
                self.playing,
                self.midi_processor,
                self.video_recorder,
                self.network_manager,
                self.audio_analyzer,
            )
            
            # Capture frame if recording
            if self.video_recorder.recording and self.playing:
                self.video_recorder.capture_frame(dt, self.width, self.height)
                
        except Exception as e:
            import traceback
            print(f"❌ Update error: {e}")
            traceback.print_exc()
    
    def on_draw(self):
        self.clear()
        
        # Background with activity-based intensity
        bg_intensity = 0.98 + max(0, min(0.08, self.background_intensity * 0.15))
        pyglet.gl.glClearColor(bg_intensity, bg_intensity, bg_intensity, 1.0)
        
        # Draw everything in proper layer order
        self.grid_batch.draw()      # Background grid
        self.batch.draw()           # Main content (nodes, particles)
        self.ui_batch.draw()        # UI panels
        self.video_batch.draw()     # Video effects (fades, overlays) - LAST
    
    def on_key_press(self, symbol, _modifiers):
        try:
            if symbol == pyglet.window.key.SPACE:
                if self.midi_processor.midi_events:
                    if self.playing:
                        self.playing = False
                        self.audio_player.pause()
                        print("⏸️  Paused")
                    else:
                        self.playing = True
                        self.start_time = time.time()
                        self.audio_player.play()
                        print("▶️  Playing")
            
            elif symbol == pyglet.window.key.R:
                if self.midi_processor.midi_events:
                    # Restart everything
                    self.midi_processor.current_event_index = 0
                    self.start_time = time.time()
                    self.playing = True
                    self.midi_processor.channel_activity.clear()
                    self.midi_processor.recent_events.clear()
                    
                    # Reset nodes
                    for node in self.network_manager.nodes:
                        node.active_notes.clear()
                        node.target_size = node.base_size
                        node.target_color = node.base_color.copy()
                    
                    # Reset Odin tracking
                    self.midi_processor.active_channels.clear()
                    self.midi_processor.channel_note_counts.clear()

                    # Restart audio
                    self.audio_player.restart()
                    
                    print("🔄 Restarted")
            
            elif symbol == pyglet.window.key.V:
                if not self.video_recorder.recording:
                    if not self.playing:
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"odin_elements_{timestamp}.mp4"
                        output_path = FileManager.get_output_video_path(filename)
                        if self.video_recorder.start_recording(output_path, self.width, self.height):
                            print(f"✅ Recording setup complete: {filename}")
                            print("🎬 Press SPACE to start music and begin recording")
                    else:
                        print("⚠️  Stop playback first (R to restart, then V, then SPACE)")
                else:
                    self.video_recorder.stop_recording()
            elif symbol == pyglet.window.key.F:
                # Toggle fade effects
                current_state = self.video_effects_manager.fade_controller.fade_enabled
                self.video_effects_manager.enable_fade(not current_state)
                print(f"{'✅' if not current_state else '🚫'} Fade effects {'enabled' if not current_state else 'disabled'}")
            elif symbol == pyglet.window.key.ESCAPE:
                self.close()
            elif symbol == pyglet.window.key.L:
                new_state = self.ui_manager.toggle_logs()
                print(f"{'✅' if new_state else '🚫'} Logs {'enabled' if new_state else 'disabled'}")

                
        except Exception as e:
            print(f"❌ Key press error: {e}")
    
    def on_close(self):
        try:
            if self.video_recorder.recording:
                self.video_recorder.stop_recording()
                self.audio_player.cleanup()
        except:
            pass
        super().on_close()
    
    def run_visualization(self, midi_file=None, audio_file=None):
        # Ensure directories exist
        FileManager.ensure_directories()
        
        # Find files
        midi_path = FileManager.find_midi_file(midi_file)
        audio_path = FileManager.find_audio_file(audio_file)
        
        if midi_path:
            if not self.midi_processor.load_midi(midi_path):
                print("❌ Failed to load MIDI file")
            else:
                print(f"✅ Loaded MIDI: {os.path.basename(midi_path)}")
        else:
            print("❌ No MIDI file found")
            FileManager.list_available_files()
            return
        
        if audio_path:
            if not self.audio_player.load_audio(audio_path):
                print("❌ Failed to load audio file")
            else:
                print(f"✅ Loaded audio: {os.path.basename(audio_path)}")
                # Get audio duration and set for video effects
                try:
                    y, sr = librosa.load(audio_path, sr=None)
                    duration = librosa.get_duration(y=y, sr=sr)
                    self.total_audio_duration = duration
                    self.video_effects_manager.set_total_duration(duration)
                    print(f"✅ Audio duration: {duration:.1f}s (video effects timing set)")
                except Exception as e:
                    print(f"⚠️  Could not get audio duration: {e}")

                # Setup audio analyzer with the loaded audio
                if self.audio_analyzer.setup_audio_capture(self.audio_player.get_audio_source()):
                    print(f"✅ Audio capture enabled: {self.audio_analyzer.sample_rate}Hz, {self.audio_analyzer.channels} channels")

                if self.audio_analyzer.analyze_audio_frequencies(audio_path):
                    print("✅ Frequency analysis ready")

                self.video_recorder.set_original_audio_file(audio_path)
        else:
            print("❌ No audio file found")
            FileManager.list_available_files()
            return
        
        print("\n⚡ ODIN & ELEMENTS - MIDI Visualizer ⚡")
        print("🎬 Complete video+audio recording with elemental magic!")
        print("\nElements:")
        print("  🏔️  EARTH (CH0) - Brown squares with crystal spikes")
        print("  💨 WIND (CH1) - Sky blue circles with flowing streams")
        print("  🔥 FIRE (CH2) - Red-orange flames with dancing tips")
        print("  💧 WATER (CH3) - Deep blue drops with rippling waves")
        print("  ⚡ ODIN (Center) - Purple, grows with elemental power!")
        print("\nControls:")
        print("  SPACE - Play/Pause")
        print("  R - Restart")
        print("  V - Start/Stop video recording")
        print("  F - Toggle fade effects")
        print("  ESC - Exit")
        print("\nWorkflow:")
        print("  1. Press V (start recording)")
        print("  2. Press SPACE (start music)")
        print("  3. Watch Odin grow with elemental power!")
        print("  4. Press V (stop recording)")
        print("  5. Get final video with audio - ready for upload!")
        
        pyglet.app.run()

if __name__ == "__main__":
    visualizer = MIDIVisualizer()
    visualizer.run_visualization(midi_file="Odin.mid", audio_file="Odin.mp3")