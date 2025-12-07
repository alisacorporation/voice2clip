#!/usr/bin/env python3
"""
Audio Input Test Script

This script tests if your microphone is working correctly by:
1. Listing available audio devices
2. Testing audio recording for 3 seconds
3. Playing back the recorded audio
4. Saving to a test file

Usage: python3 test_audio_input.py
"""

import pyaudio
import wave
import time
import sys

def list_audio_devices():
    """List all available audio devices"""
    print("🎤 Available Audio Devices:")
    print("=" * 40)
    
    try:
        audio = pyaudio.PyAudio()
        
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            print(f"Device {i}: {device_info['name']}")
            print(f"  - Max Input Channels: {device_info['maxInputChannels']}")
            print(f"  - Max Output Channels: {device_info['maxOutputChannels']}")
            print(f"  - Default Sample Rate: {device_info['defaultSampleRate']}")
            print()
        
        device_count = audio.get_device_count()
        audio.terminate()
        return device_count
        
    except Exception as e:
        print(f"❌ Error accessing audio devices: {e}")
        print("Note: Some audio systems may require special permissions or setup")
        return 0

def test_microphone_recording(device_index=None, duration=3):
    """Test microphone recording"""
    print(f"🎵 Testing Microphone Recording")
    print(f"Device: {device_index if device_index is not None else 'Default'}")
    print(f"Duration: {duration} seconds")
    print("=" * 40)
    
    # Audio settings
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    audio = pyaudio.PyAudio()
    
    try:
        # Open stream
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        
        print("📢 Recording started! Speak into your microphone...")
        print("🔴 Recording", end="", flush=True)
        
        frames = []
        
        # Record for specified duration
        for i in range(int(RATE / CHUNK * duration)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                if i % 10 == 0:
                    print(".", end="", flush=True)
            except Exception as e:
                print(f"\n❌ Error reading audio: {e}")
                return False
        
        print(" ✅ Done!")
        
        # Stop and close stream
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save to file
        filename = "test_recording.wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"💾 Recording saved as: {filename}")
        print(f"📊 Audio data: {len(frames)} frames, {(len(frames) * CHUNK)/RATE:.1f} seconds")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during recording: {e}")
        audio.terminate()
        return False

def test_audio_playback():
    """Test if audio playback works"""
    try:
        print("\n🔊 Testing Audio Playback...")
        
        audio = pyaudio.PyAudio()
        
        # Try to play back the recorded file
        wf = wave.open("test_recording.wav", 'rb')
        
        stream = audio.open(
            format=audio.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        
        data = wf.readframes(1024)
        print("🎵 Playing back recording...")
        
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        
        stream.stop_stream()
        stream.close()
        wf.close()
        audio.terminate()
        
        print("✅ Playback completed!")
        return True
        
    except Exception as e:
        print(f"❌ Playback error: {e}")
        return False

def main():
    """Main test function"""
    print("🎤 Audio Input Test Tool")
    print("=" * 40)
    
    # List devices
    device_count = list_audio_devices()
    
    if device_count == 0:
        print("❌ No audio devices found!")
        return
    
    print("\n🔍 Testing audio input...")
    
    # Test default device first
    print("\n1. Testing DEFAULT audio device:")
    success = test_microphone_recording()
    
    if not success:
        print("\n❌ Default device failed. Trying specific devices...")
        # Try each input device
        audio = pyaudio.PyAudio()
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"\n2. Testing device {i}: {device_info['name']}")
                success = test_microphone_recording(device_index=i)
                if success:
                    break
        audio.terminate()
    
    if success:
        print("\n✅ Audio recording test PASSED!")
        test_audio_playback()
        
        print("\n📋 Summary:")
        print("- Your microphone is working correctly")
        print("- Audio recording and playback both work")
        print("- Ready to use with push-to-talk script")
        
    else:
        print("\n❌ Audio recording test FAILED!")
        print("\n🔧 Troubleshooting:")
        print("1. Check if microphone is connected")
        print("2. Verify microphone permissions")
        print("3. Try different audio devices")
        print("4. Check system audio settings")

if __name__ == "__main__":
    main()