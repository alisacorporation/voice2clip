#!/bin/bash
# Push-to-Talk launcher script with notifications and transcription saving
# This script helps you run the enhanced push-to-talk functionality with proper setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎤 Push-to-Talk with whisper.cpp + Notifications Launcher"
echo "========================================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Install system-wide dependencies
echo ""
echo "📦 Checking system-wide dependencies..."
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || {
    echo "✅ Dependencies already installed or installation not needed"
}

# Check if notification system is available
echo ""
echo "🔔 Checking notification system..."
if command -v notify-send &> /dev/null; then
    echo "✅ libnotify (notify-send) is available"
    
    # Detect desktop environment
    if [ "$XDG_CURRENT_DESKTOP" = "KDE" ]; then
        echo "✅ KDE Plasma detected - will use KDE-specific notification enhancements"
    else
        echo "ℹ️  Desktop environment: $XDG_CURRENT_DESKTOP"
    fi
elif command -v dunstify &> /dev/null; then
    echo "✅ dunst notification daemon is available"
else
    echo "⚠️  No Linux notification daemon found"
    echo "   To install notifications, run:"
    echo "   sudo pacman -S libnotify              # Arch Linux"
fi

# Check whisper.cpp availability from config
if [ -f "config.json" ]; then
    WHISPER_CLI=$(python3 -c "import json; config=json.load(open('config.json')); print(config.get('whisper_path', ''))" 2>/dev/null)
    MODEL_PATH=$(python3 -c "import json; config=json.load(open('config.json')); print(config.get('model_path', ''))" 2>/dev/null)
else
    WHISPER_CLI="/home/brabus/git/whisper.cpp/build/bin/whisper-cli"
    MODEL_PATH="/home/brabus/git/whisper.cpp/models/ggml-large-v3.bin"
fi

if [ -z "$WHISPER_CLI" ] || [ ! -f "$WHISPER_CLI" ]; then
    echo "❌ whisper-cli not found at $WHISPER_CLI"
    echo "Please check config.json or ensure whisper.cpp is built"
    exit 1
fi

if [ -z "$MODEL_PATH" ] || [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Model not found at $MODEL_PATH"
    echo "Please check config.json or download the model"
    exit 1
fi

echo ""
echo "✅ whisper-cli found at: $WHISPER_CLI"
echo "✅ Model found at: $MODEL_PATH"

echo ""
echo "🚀 Starting Enhanced Push-to-Talk..."
echo "Features:"
echo "  • Real-time recording with notifications"
echo "  • Automatic speech-to-text transcription"
echo "  • Desktop notifications for all events"
echo "  • KDE-specific notification enhancements (if running on KDE)"
echo "  • Automatic transcription saving to ./transcriptions/"
echo ""
echo "Controls:"
echo "  • Hold LEFT ALT to record, release to transcribe"
echo "  • Press ESC to quit"
echo ""
echo "Notifications:"
echo "  • 🎤 Recording started"
echo "  • 🔄 Processing/transcribing"
echo "  • ✅ Transcription complete"
echo "  • ⚠️  Audio issues or errors"
echo ""

# Run the script
python3 push_to_talk.py "$@"
