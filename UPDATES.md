# Voice2Clip - Push-to-Talk Updates

## What's New

### 1. **Cross-Platform Notification System with KDE Enhancements**
- Automatic detection of KDE Plasma desktop environment
- KDE-specific notification hints for better integration
- Falls back to standard notifications on other desktops
- Urgency levels: critical, normal, low

### 2. **Configuration File (config.json)**
Easy path management via JSON configuration:
```json
{
  "whisper_path": "/home/brabus/git/whisper.cpp/build/bin/whisper-cli",
  "model_path": "/home/brabus/git/whisper.cpp/models/ggml-large-v3.bin",
  "audio_device": null,
  "transcription_dir": "./transcriptions",
  "push_to_talk_key": "alt_l"
}
```

### 3. **System-Wide Dependencies**
- Removed virtual environment requirement
- Dependencies installed system-wide via pacman/pip
- Automatically checks and installs missing packages

### 4. **Updated Paths**
- Whisper CLI: `/home/brabus/git/whisper.cpp/build/bin/whisper-cli`
- Model: `/home/brabus/git/whisper.cpp/models/ggml-large-v3.bin`

## Changes Made

### push_to_talk.py
- Added `config.json` loading with `_load_config()` method
- Added KDE detection with `_is_kde()` method
- Enhanced `_send_notification()` with:
  - Urgency parameter (critical, normal, low)
  - KDE-specific hints when KDE detected
  - Better app name integration
- Updated `__init__()` to use config file defaults
- All notification calls updated with appropriate urgency levels

### run_push_to_talk.sh
- Removed virtual environment creation
- Added `--break-system-packages` for pip install
- Added KDE detection and logging
- Reads paths from config.json
- Improved error handling and user feedback

### config.json (NEW)
- Centralized configuration file
- Easy path customization
- Audio device selection support

## Usage

### Basic Usage
```bash
./run_push_to_talk.sh
```

### With Custom Configuration
Edit `config.json` to customize paths and settings.

### Command Line Options
```bash
./run_push_to_talk.sh --help                    # Show help
./run_push_to_talk.sh --list-devices            # List audio devices
./run_push_to_talk.sh --audio-device 11         # Use specific device
```

### Controls
- Hold **LEFT ALT** to record
- Release to transcribe
- Press **ESC** to quit

## Notification System

### Priority Order
1. **notify-send** (Primary - Cross-Platform)
   - Works on all Linux with notification daemon
   - KDE-enhanced when running on KDE Plasma
   
2. **plyer** (Fallback - Cross-Platform)
   - Works on Windows, macOS, Linux
   - Only used if notify-send fails
   
3. **Console** (Last Resort)
   - Prints to terminal

### KDE-Specific Features
When KDE is detected:
- App name: "Voice2Clip"
- Desktop entry: voice2clip
- X-KDE display appname hint
- Proper urgency levels

### Notification Types
- 🎤 Recording started (normal urgency, 1s timeout)
- 🔄 Processing/Transcribing (normal urgency, 1s timeout)
- ✅ Transcription complete (low urgency, 1s timeout)
- ⏰ Timeout errors (critical urgency, 5s timeout)
- 👋 Application stopped (normal urgency, 3s timeout)

## Dependencies

### System Packages (pacman)
```bash
sudo pacman -S python-pyaudio python-pyperclip
```

### Python Packages (pip)
```bash
pip3 install pynput plyer --break-system-packages
```

All dependencies are automatically installed when running the launcher script.

## Troubleshooting

### No Notifications
- Check if notification daemon is running: `ps aux | grep -i notify`
- Test manually: `notify-send "Test" "Message"`
- Ensure libnotify is installed: `pacman -Q libnotify`

### Audio Issues
- List devices: `./run_push_to_talk.sh --list-devices`
- Select specific device: `--audio-device <number>`
- Check microphone permissions in system settings

### Model Not Found
- Verify config.json paths
- Ensure model file exists
- Download model if needed

## File Structure
```
/home/brabus/app/voice2clip/
├── push_to_talk.py          # Main Python script
├── run_push_to_talk.sh      # Launcher script
├── config.json              # Configuration file (NEW)
├── requirements.txt         # Python dependencies
├── transcriptions/          # Output directory (auto-created)
└── UPDATES.md              # This file
```
