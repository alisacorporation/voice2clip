#!/usr/bin/env python3
"""
Test script for notification clearing functionality
"""

import sys
import time

# Test the enhanced notification system
sys.path.insert(0, '/home/amg/dev/voice-input/whisp-to-clipboard')

from push_to_talk import PushToTalk

def test_notification_clearing():
    """Test that notifications are cleared quickly"""
    print("🔔 Testing notification clearing system...")
    
    # Create a PushToTalk instance (without audio setup)
    ptt = PushToTalk.__new__(PushToTalk)
    ptt._send_notification = PushToTalk._send_notification.__get__(ptt)
    ptt._clear_notifications = PushToTalk._clear_notifications.__get__(ptt)
    
    try:
        print("📤 Sending test notifications with clearing...")
        
        # Test 1: Recording notification with clearing
        print("1. Sending recording notification...")
        ptt._clear_notifications()
        ptt._send_notification("🎤 Recording", "Hold ALT to speak", timeout=1)
        time.sleep(0.5)
        
        # Test 2: Processing notification with clearing  
        print("2. Sending processing notification...")
        ptt._clear_notifications()
        ptt._send_notification("🔄 Transcribing", "Converting speech", timeout=1)
        time.sleep(0.5)
        
        # Test 3: Success notification with clearing
        print("3. Sending success notification...")
        ptt._clear_notifications()
        ptt._send_notification("✅ Done", "Transcribed and saved", timeout=1)
        time.sleep(0.5)
        
        # Test 4: Quick succession test
        print("4. Testing quick succession...")
        ptt._clear_notifications()
        ptt._send_notification("🎤 1", "First", timeout=1)
        time.sleep(0.2)
        ptt._clear_notifications()
        ptt._send_notification("🎤 2", "Second", timeout=1)
        time.sleep(0.2)
        ptt._clear_notifications()
        ptt._send_notification("🎤 3", "Third", timeout=1)
        
        print("✅ Notification clearing test completed!")
        print("📱 Check your desktop - notifications should clear quickly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_notification_clearing()
    sys.exit(0 if success else 1)