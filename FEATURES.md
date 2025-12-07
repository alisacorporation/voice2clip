# Enhanced Push-to-Talk with Notifications

This enhanced version of the push-to-talk application includes Linux desktop notifications and automatic transcription saving features.

## 🎯 New Features

### 1. Linux Desktop Notifications
- **Recording Started**: Notifications when you begin recording
- **Processing**: Real-time updates during transcription
- **Success/Failure**: Clear feedback when transcription completes
- **Error Handling**: Informative error messages for troubleshooting

### 2. Automatic Transcription Saving
- **Timestamped Files**: Each transcription is saved with a timestamp
- **JSON Format**: Rich metadata including duration, device info, and model used
- **Organized Storage**: All transcriptions saved to `./transcriptions/` directory
- **Metadata**: Includes timestamp, audio duration, device, and model information

### 3. Enhanced User Experience
- **Real-time Feedback**: Immediate visual feedback through notifications
- **Error Prevention**: Clear error messages help troubleshoot issues
- **Progress Tracking**: Know exactly what's happening during recording/transcription
- **Persistent Storage**: Never lose important transcriptions

## 🚀 Usage

### Basic Usage
```bash
./run_push_to_talk.sh
```

### Custom Configuration
```bash
# Use custom transcription directory
python3 push_to_talk.py --transcription-dir "/path/to/transcriptions"

# List available audio devices
python3 push_to_talk.py --list-devices

# Use specific audio device
python3 push_to_talk.py --audio-device 1
```

## 📱 Notification Types

| Event | Notification | Timeout |
|-------|-------------|---------|
| Application Start | 🚀 Push-to-Talk Ready | 4 seconds |
| Recording Started | 🎤 Recording Started | 3 seconds |
| Processing | 🔄 Processing | 2 seconds |
| Transcription Complete | ✅ Transcription Complete | 4 seconds |
| Audio Too Short | ⚠️ Audio Too Short | 3 seconds |
| No Transcription | ⚠️ No Transcription | 3 seconds |
| Setup Error | ❌ Setup Error | 5 seconds |
| Model Missing | ⚠️ Model Missing | 5 seconds |
| Transcription Timeout | ⏰ Transcription Timeout | 5 seconds |
| Transcription Error | ❌ Transcription Error | 5 seconds |
| Application Closed | 👋 Push-to-Talk Stopped | 3 seconds |

## 💾 Transcription Files

Transcriptions are saved as JSON files with the following structure:

```json
{
  "timestamp": "2025-12-07T05:15:30.123456",
  "transcription": "Your transcribed text here",
  "duration_seconds": 2.5,
  "audio_device": null,
  "model_path": "/path/to/model.bin"
}
```

### File Naming Convention
- Format: `transcription_YYYYMMDD_HHMMSS.json`
- Example: `transcription_20251207_051530.json`

## 🔧 Dependencies

### Required Python Packages
```
pyaudio>=0.2.11      # Audio recording
pynput>=1.7.6        # Keyboard input
pyperclip>=1.8.2     # Clipboard functionality
plyer>=2.4.0         # Desktop notifications
```

### System Requirements
- **Linux**: Any modern distribution with notification support
- **Notification Daemon**: One of the following:
  - `libnotify` (built-in on most distributions)
  - `dunst` (lightweight notification daemon)
  - `gnome-shell` notifications
  - `plasma` notifications

### Installing Notification Support
```bash
# Ubuntu/Debian
sudo apt-get install libnotify-bin python3-dbus

# Arch Linux
sudo pacman -S libnotify python-dbus

# Fedora
sudo dnf install libnotify python3-dbus
```

## 🏗️ Architecture

### Key Components

1. **PushToTalk Class**
   - Main application logic
   - Audio recording and processing
   - Transcription management

2. **Notification System**
   - Platform- `agnostic notification viaplyer`
   - Fallback to console output when notifications unavailable
   - Configurable timeouts and messages

3. **Transcription Storage**
   - Automatic directory creation
   - JSON metadata preservation
   - Timestamp-based file naming

4. **Error Handling**
   - Graceful degradation when dependencies missing
   - Informative error messages
   - Recovery from common failure modes

### Method Overview

- `_send_notification()`: Sends desktop notifications with fallback
- `_save_transcription()`: Saves transcriptions with metadata
- `start_recording()`: Begins recording with notification
- `stop_recording_and_transcribe()`: Processes and saves transcription
- `_transcribe_audio()`: Core whisper.cpp integration
- `_clean_transcription()`: Filters and cleans output

## 🔍 Troubleshooting

### No Notifications Appear
1. Check if notification daemon is running:
   ```bash
   ps aux | grep -E "(dunst|notification-daemon)"
   ```
2. Install notification support:
   ```bash
   sudo apt-get install libnotify-bin
   ```
3. Test notifications manually:
   ```bash
   python3 test_notifications.py
   ```

### Transcription Not Saving
1. Check write permissions in transcription directory
2. Verify disk space is available
3. Check for JSON encoding errors in logs

### Audio Issues
1. List available devices:
   ```bash
   python3 push_to_talk.py --list-devices
   ```
2. Test audio input:
   ```bash
   python3 test_audio_input.py
   ```

## 🔄 Migration from Previous Version

The enhanced version is backward compatible with existing configurations:

- All existing command-line arguments still work
- Default behavior unchanged except for added notifications
- New `--transcription-dir` argument is optional
- Automatic transcription saving can be disabled by setting `--transcription-dir ""`

## 📋 Future Enhancements

Potential improvements for future versions:

1. **Audio File Saving**: Optionally save recorded audio files
2. **Batch Processing**: Process multiple recordings
3. **Export Formats**: Support for different export formats (TXT, CSV)
4. **Cloud Integration**: Upload transcriptions to cloud storage
5. **Web Interface**: Browser-based management interface
6. **Advanced Filtering**: Custom transcription filters
7. **Audio Visualization**: Real-time audio level display

## 🏆 Benefits

- **Productivity**: Never lose important voice notes
- **User Experience**: Clear feedback through notifications
- **Reliability**: Automatic saving prevents data loss
- **Flexibility**: Customizable storage locations
- **Transparency**: Rich metadata for tracking and analysis
- **Compatibility**: Works with existing whisper.cpp setups