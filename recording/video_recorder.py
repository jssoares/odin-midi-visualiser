import os
import numpy as np
import time
import cv2
import pyglet
import PIL.Image
from config.settings import Settings

class VideoRecorder:
    def __init__(self, target_fps=Settings.DEFAULT_TARGET_FPS):
        # Recording
        self.recording = False
        self.video_writer = None
        self.output_filename = None
        self.frames_recorded = 0
        self.recording_start_time = None
        self.target_fps = target_fps
        self.frame_time_accumulator = 0.0
        self.original_audio_file = None

    def start_recording(self, filename, window_width, window_height):
        if self.recording:
            print("⚠️  Already recording!")
            return False
        
        print(f"Setting up recording: {filename}")
        
        for codec in ['H264', 'mp4v', 'MJPG', 'XVID']:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                test_writer = cv2.VideoWriter(filename, fourcc, self.target_fps, (window_width, window_height))
                
                if test_writer.isOpened():
                    print(f"✅ Video writer created with {codec}")
                    self.video_writer = test_writer
                    self.recording = True
                    self.output_filename = filename
                    self.frames_recorded = 0
                    self.recording_start_time = None
                    self.frame_time_accumulator = 0.0
                    return True
                else:
                    test_writer.release()
                    
            except Exception as e:
                print(f"❌ {codec} exception: {e}")
        
        print("❌ All codecs failed!")
        return False

    def stop_recording(self):
        if not self.recording:
            return False
        
        self.recording = False
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        print(f"✅ Recording stopped. Total frames: {self.frames_recorded}")
        
        if self.output_filename and os.path.exists(self.output_filename):
            file_size = os.path.getsize(self.output_filename) / (1024 * 1024)
            print(f"📁 Video file: {self.output_filename} ({file_size:.1f} MB)")
            
            # Automatically combine with audio
            if self.original_audio_file:
                self.combine_with_audio()
            else:
                print("🎬 Video-only file ready!")
        else:
            print("❌ Video file not found")
        
        return True
    
    def capture_frame(self, dt, window_width, window_height):
        """Frame capture for recording"""
        if not self.recording or not self.video_writer:
            return
        
        # Set recording start time on first frame
        if self.recording_start_time is None:
            self.recording_start_time = time.time()
            print(f"🎬 Recording started at {self.target_fps} FPS")
            return
        
        # Frame timing
        self.frame_time_accumulator += dt
        frame_interval = 1.0 / self.target_fps
        
        if self.frame_time_accumulator < frame_interval:
            return
        
        try:
            # Capture frame
            buffer = pyglet.image.get_buffer_manager().get_color_buffer()
            image_data = buffer.get_image_data()
            
            # Convert to OpenCV format
            if image_data.format == 'RGBA':
                rgba_data = image_data.get_data('RGBA', image_data.width * 4)
                pil_img = PIL.Image.frombytes('RGBA', (image_data.width, image_data.height), rgba_data)
                pil_img = pil_img.convert('RGB')
            else:
                rgb_data = image_data.get_data('RGB', image_data.width * 3)
                pil_img = PIL.Image.frombytes('RGB', (image_data.width, image_data.height), rgb_data)
            
            pil_img = pil_img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
            frame = np.array(pil_img, dtype=np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Write frame
            if self.video_writer.isOpened():
                result = self.video_writer.write(frame)
                if result is not False:
                    self.frames_recorded += 1
                    self.frame_time_accumulator -= frame_interval
                    
                    # Progress update
                    if self.frames_recorded % self.target_fps == 0:
                        elapsed_time = time.time() - self.recording_start_time
                        video_duration = self.frames_recorded / self.target_fps
                        actual_fps = self.frames_recorded / elapsed_time if elapsed_time > 0 else 0
                        efficiency = (actual_fps / self.target_fps) * 100
                        print(f"🎬 Real: {elapsed_time:.1f}s | Video: {video_duration:.1f}s | Frames: {self.frames_recorded} | FPS: {actual_fps:.1f} ({efficiency:.0f}%)")
                
        except Exception as e:
            print(f"❌ Frame capture error: {e}")

    def combine_with_audio(self):
        """Combine video with audio using ffmpeg"""
        if not self.original_audio_file or not self.output_filename:
            print("ℹ️  No audio to combine")
            return
        
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            base_name = self.output_filename.replace('.mp4', '')
            final_output = f"{base_name}_with_audio.mp4"
            
            print("🎵 Combining video with audio...")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', self.output_filename,
                '-i', self.original_audio_file,
                '-vf', 'scale=1920:1080', # Force scale to 1080p
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-shortest',
                final_output
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(final_output) / (1024 * 1024)
                print(f"🎉 Final video with audio: {final_output}")
                print(f"   File size: {file_size:.1f} MB")
                print(f"   Ready for YouTube upload!")
                
                try:
                    os.remove(self.output_filename)
                    print(f"   Cleaned up: {self.output_filename}")
                except:
                    pass
                    
            else:
                print(f"⚠️  ffmpeg failed: {result.stderr}")
                print(f"   Keeping video-only file: {self.output_filename}")
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ℹ️  ffmpeg not found - keeping video-only file")
            print("   Install ffmpeg to get video+audio output")

    def is_recording(self):
        return self.recording

    def get_frames_recorded(self):
        return self.frames_recorded

    def set_original_audio_file(self, filename):
        self.original_audio_file = filename