#!/usr/bin/env python3
"""
Audio Quality Diagnostics

This script helps diagnose audio quality issues that might be causing
poor transcription results.
"""

import pyaudio
import wave
import numpy as np
import time
import sys

def calculate_audio_levels(audio_data):
    """Calculate audio levels and RMS"""
    try:
        # Convert to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate RMS (Root Mean Square) - measure of audio amplitude
        rms = np.sqrt(np.mean(audio_array**2))
        
        # Calculate peak level
        peak = np.max(np.abs(audio_array))
        
        # Calculate dB level (relative to full scale)
        if rms > 0:
            db_level = 20 * np.log10(rms / 32768.0)
        else:
            db_level = -100  # Very quiet
            
        return {
            'rms': rms,
            'peak': peak,
            'db_level': db_level,
            'max_possible': 32768
        }
    except Exception as e:
        return {'error': str(e)}

def test_audio_quality(device_index=None, duration=3):
    """Test audio quality with detailed metrics"""
    print(f"🔍 Testing Audio Quality")
    print(f"Device: {device_index if device_index is not None else 'Default'}")
    print(f"Duration: {duration} seconds")
    print("=" * 50)
    
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
        
        print("📢 Recording for quality analysis...")
        print("🔴 Speak normally into your microphone...")
        
        all_levels = []
        total_frames = 0
        
        # Record and analyze
        for i in range(int(RATE / CHUNK * duration)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                levels = calculate_audio_levels(data)
                
                if 'error' not in levels:
                    all_levels.append(levels)
                    total_frames += 1
                    
                    # Show progress and current levels
                    if i % 5 == 0:
                        print(f"Frame {i+1}: RMS={levels['rms']:.1f}, dB={levels['db_level']:.1f}, Peak={levels['peak']}")
                        
            except Exception as e:
                print(f"❌ Error reading audio: {e}")
                return False
        
        print("✅ Recording completed!")
        
        # Analyze results
        if all_levels:
            print("\n📊 AUDIO QUALITY ANALYSIS:")
            print("=" * 40)
            
            # Calculate statistics
            rms_values = [l['rms'] for l in all_levels]
            db_values = [l['db_level'] for l in all_levels]
            peak_values = [l['peak'] for l in all_levels]
            
            print(f"Audio Level Statistics:")
            print(f"  Average RMS: {np.mean(rms_values):.1f}")
            print(f"  Average dB: {np.mean(db_values):.1f}")
            print(f"  Average Peak: {np.mean(peak_values):.1f}")
            print(f"  Max Peak: {np.max(peak_values)}")
            print(f"  Min Peak: {np.min(peak_values)}")
            
            # Quality assessment
            avg_db = np.mean(db_values)
            max_peak = np.max(peak_values)
            
            print(f"\n🎯 QUALITY ASSESSMENT:")
            if avg_db < -40:
                print("  ❌ AUDIO TOO QUIET - Whisper may not detect speech properly")
                print("  💡 Try: Speaking closer to microphone, increasing mic volume")
            elif avg_db > -10:
                print("  ⚠️  AUDIO TOO LOUD - May cause distortion")
                print("  💡 Try: Speaking farther from microphone, reducing mic volume")
            else:
                print("  ✅ Audio level is good")
                
            if max_peak < 1000:
                print("  ❌ PEAK LEVEL TOO LOW - Weak signal")
                print("  💡 Try: Checking microphone connection, enabling mic boost")
            elif max_peak > 30000:
                print("  ⚠️  PEAK LEVEL TOO HIGH - Possible distortion")
                print("  💡 Try: Reducing microphone gain")
            else:
                print("  ✅ Peak levels are good")
                
            # Whisper-specific recommendations
            print(f"\n🎤 WHISPER RECOMMENDATIONS:")
            if avg_db < -30:
                print("  - Audio is too quiet for reliable transcription")
                print("  - Try increasing microphone volume in system settings")
                print("  - Consider using a better quality microphone")
            elif avg_db > -15:
                print("  - Audio might be too loud")
                print("  - Try speaking slightly farther from microphone")
            else:
                print("  - Audio levels should work well with whisper.cpp")
                
            # Check for background noise
            rms_silence = min(rms_values) if rms_values else 0
            rms_speech = max(rms_values) if rms_values else 0
            signal_ratio = rms_speech / max(rms_silence, 1)
            
            print(f"  - Signal-to-noise ratio: {signal_ratio:.1f}")
            if signal_ratio < 5:
                print("  ⚠️  Low signal-to-noise ratio detected")
                print("  💡 Try: Recording in quieter environment")
            else:
                print("  ✅ Good signal-to-noise ratio")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        try:
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except:
            pass

def list_audio_devices_with_quality():
    """List devices and test quality of each input device"""
    print("🎤 Audio Device Quality Test")
    print("=" * 40)
    
    audio = pyaudio.PyAudio()
    
    input_devices = []
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_devices.append((i, device_info['name']))
    
    if not input_devices:
        print("❌ No input devices found!")
        return
    
    print(f"Found {len(input_devices)} input devices:")
    for idx, name in input_devices:
        print(f"  {idx}: {name}")
    
    audio.terminate()
    
    # Test each device briefly
    for idx, name in input_devices:
        print(f"\n{'='*20}")
        print(f"Testing Device {idx}: {name}")
        test_audio_quality(device_index=idx, duration=2)
        print()

def main():
    """Main diagnostic function"""
    print("🔧 Audio Quality Diagnostics for Push-to-Talk")
    print("This tool helps identify why whisper.cpp returns 'you' instead of actual speech")
    print()
    
    # Test default device first
    print("1. Testing DEFAULT audio device:")
    test_audio_quality(duration=3)
    
    # Ask if user wants to test all devices
    print("\n2. Testing all input devices:")
    list_audio_devices_with_quality()
    
    print("\n💡 COMMON ISSUES & SOLUTIONS:")
    print("=" * 40)
    print("If whisper.cpp only returns 'you' or similar:")
    print("1. 🔊 Audio too quiet → Increase microphone volume")
    print("2. 📏 Too far from mic → Speak closer (2-6 inches)")
    print("3. 🔌 Bad connection → Check microphone cable/USB")
    print("4. 🎚️ Wrong device → Use --audio-device to select correct mic")
    print("5. 🌫️ Background noise → Record in quieter environment")
    print("6. ⚙️ System settings → Check microphone permissions")

if __name__ == "__main__":
    main()