import os
import mido
from collections import deque, defaultdict

class MIDIProcessor:
    def __init__(self):
        # MIDI data
        self.midi_file = None
        self.midi_events = []
        self.current_event_index = 0
        self.tempo = 500000

        # Channel tracking
        self.channel_activity = defaultdict(float)
        self.recent_events = deque(maxlen=50)

        # Enhanced tracking for Odin's sustained growth
        self.active_channels = set()  # Channels with notes currently held
        self.channel_note_counts = defaultdict(int)  # Number of notes held per channel

    def load_midi(self, filename):
        try:
            print(f"Loading MIDI file: {filename}")
            if not os.path.exists(filename):
                print(f"❌ Error: MIDI file '{filename}' not found!")
                return False
            
            self.midi_file = mido.MidiFile(filename)
            self.midi_events = []
            
            for track_num, track in enumerate(self.midi_file.tracks):
                track_time = 0
                for msg in track:
                    track_time += msg.time
                    if msg.type in ['note_on', 'note_off']:
                        time_seconds = mido.tick2second(track_time, self.midi_file.ticks_per_beat, self.tempo)
                        self.midi_events.append({
                            'time': time_seconds,
                            'type': msg.type,
                            'channel': msg.channel,
                            'note': msg.note,
                            'velocity': getattr(msg, 'velocity', 0)
                        })
                    elif msg.type == 'set_tempo':
                        self.tempo = msg.tempo
            
            self.midi_events.sort(key=lambda x: x['time'])
            print(f"✅ Loaded {len(self.midi_events)} MIDI events")
            return len(self.midi_events) > 0
        
        except Exception as e:
            print(f"❌ Error loading MIDI: {e}")
            return False
        
    def process_midi_events(self, current_time, channel_nodes, connections):
        """Process MIDI events"""
        events_processed = 0
        
        while (self.current_event_index < len(self.midi_events) and 
               self.midi_events[self.current_event_index]['time'] <= current_time):
            
            event = self.midi_events[self.current_event_index]
            channel = min(15, max(0, event['channel']))
            
            if event['type'] == 'note_on' and event['velocity'] > 0:
                intensity = min(1.0, max(0, event['velocity'] / 127.0))
                self.channel_activity[channel] = min(1.0, self.channel_activity[channel] + intensity)
                
                # Track active channels and note counts for Odin
                self.active_channels.add(channel)
                self.channel_note_counts[channel] += 1
                
                # THIS IS THE MIDI REACTIVENESS - it calls note_on on the element nodes
                if channel in channel_nodes:
                    channel_nodes[channel].note_on(event['note'], event['velocity'])
                
                for connection in connections:
                    if (connection.node1.instrument_channel == channel or 
                        connection.node2.instrument_channel == channel):
                        connection.note_trigger(intensity)
                
                self.recent_events.append(f"CH{channel}: Note {event['note']} ON (vel:{event['velocity']})")
                
            elif event['type'] == 'note_off' or (event['type'] == 'note_on' and event['velocity'] == 0):
                # Track note releases for Odin
                self.channel_note_counts[channel] = max(0, self.channel_note_counts[channel] - 1)
                if self.channel_note_counts[channel] == 0:
                    self.active_channels.discard(channel)
                
                # THIS IS THE MIDI REACTIVENESS - it calls note_off on the element nodes
                if channel in channel_nodes:
                    channel_nodes[channel].note_off(event['note'])
                
                self.recent_events.append(f"CH{channel}: Note {event['note']} OFF")
            
            self.current_event_index += 1
            events_processed += 1
        
        # Decay channel activities only if no notes are held
        for channel in self.channel_activity:
            if channel not in self.active_channels:
                self.channel_activity[channel] = max(0, self.channel_activity[channel] * 0.95)
        
        return events_processed