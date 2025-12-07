#!/bin/bash
# Push-to-Talk launcher script with notifications and transcription saving
# This script helps you run the enhanced push-to-talk functionality with proper setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎤 Push-to-Talk with whisper.cpp + Notifications Launcher"
echo "========================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Check if notification system is available
echo ""
echo "🔔 Checking notification system..."
if command -v notify-send &> /dev/null; then
    echo "✅ libnotify (notify-send) is available"
elif command -v dunstify &> /dev/null; then
    echo "✅ dunst notification daemon is available"
else
    echo "⚠️  No Linux notification daemon found"
    echo "   To install notifications, run:"
    echo "   sudo apt-get install libnotify-bin    # Ubuntu/Debian"
    echo "   sudo pacman -S libnotify              # Arch Linux"
    echo "   sudo dnf install libnotify            # Fedora"
fi

# Check if whisper.cpp is available
WHISPER_CLI="/home/amg/Desktop/local_voice_input/whisper.cpp/build/bin/whisper-cli"
if [ ! -f "$WHISPER_CLI" ]; then
    echo "❌ whisper-cli not found at $WHISPER_CLI"
    echo "Please check the path and ensure whisper.cpp is built"
    exit 1
fi

# Check for model
MODEL_PATH="/home/amg/Desktop/local_voice_input/whisper.cpp/models/ggml-base.en.bin"
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Model not found at $MODEL_PATH"
    echo "Please download the English base model"
    exit 1
fi

echo ""
echo "🚀 Starting Enhanced Push-to-Talk..."
echo "Features:"
echo "  • Real-time recording with notifications"
echo "  • Automatic speech-to-text transcription"
echo "  • Desktop notifications for all events"
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

# Run the script with the correct paths and enable transcription saving
source venv/bin/activate
python3 push_to_talk.py \
    --whisper-path "$WHISPER_CLI" \
    --model "$MODEL_PATH" \
    --transcription-dir "./transcriptions" \
    "$@"