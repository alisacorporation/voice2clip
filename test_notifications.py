#!/usr/bin/env python3
"""
Test script for Linux desktop notifications
"""

import sys
import time

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("❌ plyer not available")

def test_notifications():
    """Test desktop notifications"""
    print("🔔 Testing desktop notifications...")
    
    if not PLYER_AVAILABLE:
        print("❌ Cannot test notifications - plyer not installed")
        print("Run: pip install plyer")
        return False
    
    try:
        # Test different notification types
        print("📤 Sending test notifications...")
        
        # Startup notification
        notification.notify(
            title="🎤 Push-to-Talk Test",
            message="Testing notification system...",
            timeout=3
        )
        time.sleep(1)
        
        # Recording notification
        notification.notify(
            title="🎤 Recording Started",
            message="Voice session is being transcribed",
            timeout=2
        )
        time.sleep(1)
        
        # Processing notification
        notification.notify(
            title="🔄 Processing",
            message="Converting speech to text...",
            timeout=2
        )
        time.sleep(1)
        
        # Success notification
        notification.notify(
            title="✅ Transcription Complete",
            message="Text copied to clipboard and saved",
            timeout=3
        )
        time.sleep(1)
        
        # Error notification
        notification.notify(
            title="⚠️  Audio Too Short",
            message="Recording was too brief to transcribe",
            timeout=3
        )
        
        print("✅ All notifications sent successfully!")
        print("📱 Check your desktop for notification popups")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send notifications: {e}")
        print("💡 Make sure a notification daemon is running:")
        print("   • Ubuntu/GNOME: usually built-in")
        print("   • Install: sudo apt-get install libnotify-bin")
        return False

if __name__ == "__main__":
    success = test_notifications()
    sys.exit(0 if success else 1)