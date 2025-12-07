#!/usr/bin/env python3
"""
Push-to-Talk Script with whisper.cpp Integration

This script allows you to hold a key to record audio and automatically
transcribe it using whisper.cpp, then copy the result to your clipboard
and save it to disk with Linux desktop notifications.

Requirements:
- whisper.cpp installed and in PATH
- Python packages: pyaudio, pynput, pyperclip, plyer
"""

import os
import sys
import time
import signal
import threading
import subprocess
import tempfile
import wave
import json
import datetime
import shutil
from pathlib import Path
from typing import Optional

import pyaudio
import pynput
import pyperclip

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Warning: plyer not available for notifications")

# Check if notify-send is available for direct notification control
import shutil
NOTIFY_SEND_AVAILABLE = shutil.which("notify-send") is not None


class PushToTalk:
    def __init__(self, whisper_path="/home/amg/Desktop/local_voice_input/whisper.cpp/build/bin/whisper-cli", model_path="/home/amg/Desktop/local_voice_input/whisper.cpp/models/ggml-large-v3.bin", audio_device=None, transcription_dir=None):
        """
        Initialize Push-to-Talk functionality
        
        Args:
            whisper_path: Path to whisper.cpp CLI executable
            model_path: Path to whisper model (if None, will try to find in common locations)
            audio_device: Audio device index (if None, will use default)
            transcription_dir: Directory to save transcriptions (default: ./transcriptions)
        """
        self.whisper_path = whisper_path
        self.model_path = model_path or self._find_model_path()
        self.audio_device = audio_device
        
        # Transcription saving
        self.transcription_dir = Path(transcription_dir) if transcription_dir else Path.cwd() / "transcriptions"
        self.transcription_dir.mkdir(exist_ok=True)
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # Recording state
        self.is_recording = False
        self.audio_frames = []
        self.audio = pyaudio.PyAudio()
        
        # Key handling
        self.push_to_talk_key = pynput.keyboard.Key.alt_l  # Default to left alt
        
        # Find model if not provided
        if not self.model_path:
            print("Warning: No model path provided. You may need to specify one manually.")
            print("Common locations:")
            print("  - ~/.cache/whisper/")
            print("  - ./models/")
            
    def _find_model_path(self):
        """Try to find whisper model in common locations"""
        common_paths = [
            Path.home() / ".cache" / "whisper",
            Path.cwd() / "models",
            Path("/usr/local/share/whisper"),
            Path("/usr/share/whisper")
        ]
        
        for path in common_paths:
            if path.exists():
                # Look for .ggml files
                for ggml_file in path.glob("*.ggml*"):
                    if ggml_file.is_file():
                        return str(ggml_file)
        
        return None
        
    def _send_notification(self, title: str, message: str, timeout: int = 1, icon: str = None):
        """Send a desktop notification with 1-second timeout and aggressive clearing"""
        # Skip empty notifications
        if not title.strip() or not message.strip():
            return
            
        if NOTIFY_SEND_AVAILABLE:
            try:
                # Use notify-send with 1-second timeout
                cmd = ["notify-send", title, message, "-t", str(timeout * 1000)]
                if icon:
                    cmd.extend(["-i", icon])
                subprocess.run(cmd, capture_output=True, timeout=1)
                return
            except Exception as e:
                print(f"❌ Failed to send notify-send notification: {e}")
        
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=timeout,
                    app_icon=icon
                )
            except Exception as e:
                print(f"❌ Failed to send plyer notification: {e}")
        else:
            print(f"🔔 {title}: {message}")
    
    def _clear_notifications(self):
        """Clear any existing notifications immediately using aggressive methods"""
        # Method 1: Use dbus-send to close all notifications programmatically
        try:
            subprocess.run([
                "dbus-send", "--session", "--print-reply", 
                "--dest=org.freedesktop.Notifications", 
                "/org/freedesktop/Notifications",
                "org.freedesktop.Notifications.CloseNotification", "uint32:0"
            ], capture_output=True, timeout=0.3)
        except:
            pass
        
        # Method 2: Send empty notification with 0 timeout to clear
        try:
            subprocess.run(["notify-send", "", "", "-t", "0"], capture_output=True, timeout=0.3)
        except:
            pass
        
        # Method 3: Try dunstify close if available
        try:
            subprocess.run(["dunstify", "--close"], capture_output=True, timeout=0.3)
        except:
            pass
        
        # Method 4: Send multiple clearing attempts
        try:
            for _ in range(3):
                subprocess.run(["notify-send", " ", " ", "-t", "0"], capture_output=True, timeout=0.2)
                time.sleep(0.05)
        except:
            pass
            
    def _save_transcription(self, transcription: str, duration: float = None) -> Optional[Path]:
        """Save transcription to file with timestamp and metadata"""
        if not transcription:
            return None
            
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcription_{timestamp}.json"
            filepath = self.transcription_dir / filename
            
            metadata = {
                "timestamp": datetime.datetime.now().isoformat(),
                "transcription": transcription,
                "duration_seconds": duration,
                "audio_device": self.audio_device,
                "model_path": self.model_path
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            return filepath
        except Exception as e:
            print(f"❌ Failed to save transcription: {e}")
            return None
        
    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.audio_frames = []
        
        # Send recording started notification
        self._send_notification(
            "Start",
            "Recording...",
            timeout=1
        )
        
        try:
            # Open stream
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.audio_device,
                frames_per_buffer=self.CHUNK
            )
            
            print("🎤 Recording... (release key to transcribe)")
            
            # Record while recording flag is true
            frame_count = 0
            while self.is_recording:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                self.audio_frames.append(data)
                frame_count += 1
                if frame_count % 10 == 0:
                    print(f"🎤 Recording... ({frame_count} frames captured)")
                
            # Stop and close stream
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Error during recording: {e}")
            self.is_recording = False
            
    def stop_recording_and_transcribe(self):
        """Stop recording and transcribe the audio"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        print("⏹️  Processing...")
        
        # Send processing notification
        self._send_notification(
            "Processing",
            "Transcribing...",
            timeout=1
        )
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            # Save audio data
            wf = wave.open(temp_path, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()
            
            # Check audio duration
            audio_duration = (len(self.audio_frames) * self.CHUNK) / self.RATE
            print(f"🎵 Audio duration: {audio_duration:.2f} seconds ({len(self.audio_frames)} frames, chunk size: {self.CHUNK})")
            
            if len(self.audio_frames) == 0:
                print("❌ No audio frames recorded!")
                return None
                
            if audio_duration < 0.3:  # Less than 0.3 seconds
                print("⚠️  Audio too short, ignoring...")
                return None
            
            # Transcribe using whisper.cpp
            transcription = self._transcribe_audio(temp_path)
            
            if transcription:
                # Copy to clipboard
                pyperclip.copy(transcription)
                print(f"✅ Copied to clipboard: {transcription}")
                
                # Also print to console
                print(f"📝 Transcription: {transcription}")
                
                # Save transcription to file
                saved_path = self._save_transcription(transcription, audio_duration)
                if saved_path:
                    print(f"💾 Saved to: {saved_path}")
                    
                # Send completion notification
                self._send_notification(
                    "Completed",
                    "Transcribed",
                    timeout=1
                )
            else:
                # Don't send notification if no meaningful transcription
                pass
                
        except Exception as e:
            print(f"Error during transcription: {e}")
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
                
    def _transcribe_audio(self, audio_path):
        """Transcribe audio using whisper.cpp"""
        if not self.model_path or not os.path.exists(self.model_path):
            print("Error: Model path not found or doesn't exist")
            return None
            
        try:
            # Build command - use better parameters for accuracy
            cmd = [
                self.whisper_path,
                "-m", self.model_path,
                "-f", audio_path,
                #"-l", "ru",  # Language (Russian)
                "-t", "6",   # Threads
                "--split-on-word",
                "-np",       # No prints other than results
                "-nt",       # No timestamps
                "-wt", "0.01",  # Word timestamp threshold
                "-nth", "0.60", # No speech threshold
                "-bo", "3",     # Best candidates
                "-bs", "3"      # Beam size
            ]
            
            # Run whisper.cpp
            print(f"🔄 Running transcription...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # Reduced timeout to 30 seconds
            )
            
            if result.returncode == 0:
                # Clean and filter the output
                raw_output = result.stdout.strip()
                print(f"🔍 Raw output: '{raw_output}'")
                transcription = self._clean_transcription(raw_output)
                return transcription
            else:
                print(f"❌ Whisper error: {result.stderr}")
                if result.stdout:
                    print(f"🔍 Raw output: '{result.stdout}'")
                return None
                
        except subprocess.TimeoutExpired:
            print("Transcription timed out")
            self._send_notification(
                "⏰ Transcription Timeout",
                "Audio processing took too long",
                timeout=5
            )
            return None
        except Exception as e:
            print(f"Error running whisper.cpp: {e}")
            return None
            
    def _clean_transcription(self, text):
        """Clean and filter transcription output"""
        if not text:
            return None
            
        # Remove SRT-style timestamps [00:00:00.000 --> 00:00:02.000]
        import re
        text = re.sub(r'\[\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}\]', '', text)
        
        # Remove any remaining timestamp patterns
        text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}', '', text)
        text = re.sub(r'\d{2}:\d{2}:\d{2}', '', text)
        
        # Clean up extra whitespace and punctuation
        text = ' '.join(text.split())
        text = text.strip(' .,!?;-')
        
        if not text:
            return None
            
        # Filter out common false positives and meaningless results
        false_positives = [
            'um', 'uh', 'ah', 'eh', 'er',
            '', ' ', '  ', '...', '...'
        ]
        
        text_lower = text.lower().strip()
        
        # Check if the text is too short or a false positive
        if len(text_lower) < 2:
            return None
            
        if text_lower in false_positives:
            return None
            
        # Additional filtering for single words that are commonly false positives
        words = text_lower.split()
        if len(words) == 1 and words[0] in false_positives:
            return None
            
        # Allow single meaningful words
        meaningful_single_words = ['you', 'hello', 'yes', 'no', 'okay', 'ok', 'stop', 'go', 'up', 'down', 'left', 'right']
        if len(words) == 1 and words[0] in meaningful_single_words:
            print(f"✅ Accepting single meaningful word: '{text}'")
            return text
            
        # Filter out strings that are mostly punctuation or numbers
        if re.match(r'^[\d\s\.,!?;:]*$', text):
            return None
            
        return text
            
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            if key == self.push_to_talk_key:
                if not self.is_recording:
                    threading.Thread(target=self.start_recording, daemon=True).start()
        except AttributeError:
            pass
            
    def on_key_release(self, key):
        """Handle key release events"""
        try:
            if key == self.push_to_talk_key:
                if self.is_recording:
                    threading.Thread(target=self.stop_recording_and_transcribe, daemon=True).start()
        except AttributeError:
            pass
            
    def list_audio_devices(self):
        """List available audio devices"""
        print("Available audio devices:")
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            print(f"  {i}: {device_info['name']}")
            
    def run(self):
        """Start the push-to-talk application"""
        print("🎯 Push-to-Talk with whisper.cpp + Notifications")
        print("=" * 50)
        
        # Check if whisper.cpp is available
        if not self._check_whisper_availability():
            print("Error: whisper.cpp not found. Please install it and ensure it's in your PATH.")
            return
            
        # Check model
        if not self.model_path or not os.path.exists(self.model_path):
            print(f"Warning: Model not found at {self.model_path}")
            print("Please specify model path manually or download a model.")
            print("\nTo download a model, run:")
            print("  ./download-ggml-model.sh base")
            return
            
        print(f"Using model: {self.model_path}")
        print(f"Saving transcriptions to: {self.transcription_dir}")
        print("Hold LEFT ALT to record, release to transcribe")
        print("Press ESC to quit")
        print("")
        
        # Set up keyboard listener
        keyboard_listener = pynput.keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        # Handle SIGINT (Ctrl+C) gracefully
        def signal_handler(sig, frame):
            print("\n👋 Goodbye!")
            self._send_notification(
                "👋 Push-to-Talk Stopped",
                "Application has been closed",
                timeout=3
            )
            keyboard_listener.stop()
            self.audio.terminate()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            keyboard_listener.start()
            keyboard_listener.join()
        except KeyboardInterrupt:
            pass
        finally:
            self.audio.terminate()
            
    def _check_whisper_availability(self):
        """Check if whisper.cpp is available"""
        try:
            result = subprocess.run(
                [self.whisper_path, "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Push-to-Talk with whisper.cpp + Notifications")
    parser.add_argument("--whisper-path", default="whisper-cli", 
                       help="Path to whisper.cpp CLI executable")
    parser.add_argument("--model", 
                       help="Path to whisper model file")
    parser.add_argument("--audio-device", type=int, 
                       help="Audio device index")
    parser.add_argument("--transcription-dir", 
                       help="Directory to save transcriptions")
    parser.add_argument("--list-devices", action="store_true",
                       help="List available audio devices")
    
    args = parser.parse_args()
    
    # Create push-to-talk instance
    ptt = PushToTalk(
        whisper_path=args.whisper_path,
        model_path=args.model,
        audio_device=args.audio_device,
        transcription_dir=args.transcription_dir
    )
    
    if args.list_devices:
        ptt.list_audio_devices()
        return
        
    ptt.run()


if __name__ == "__main__":
    main()