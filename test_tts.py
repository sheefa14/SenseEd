#!/usr/bin/env python3
"""
TTS Test Script for SenseEd
This script tests different TTS methods to ensure voice output works
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_system_tts():
    """Test system TTS engine"""
    print("Testing System TTS...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Configure TTS
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"Available voices: {len(voices) if voices else 0}")
        
        if voices:
            for i, voice in enumerate(voices):
                print(f"Voice {i}: {voice.name} - {voice.languages}")
        
        # Test speech
        print("Speaking test message...")
        engine.say("Hello! This is a test of the text to speech system.")
        engine.runAndWait()
        
        print("[OK] System TTS working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] System TTS failed: {e}")
        return False

def test_google_tts():
    """Test Google TTS"""
    print("\nTesting Google TTS...")
    try:
        from gtts import gTTS
        import platform
        import subprocess
        import tempfile
        
        # Create TTS object
        tts = gTTS(text="Hello! This is a test of Google text to speech.", lang='en', slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            temp_path = temp_file.name
        
        # Play audio based on platform
        print("Playing audio...")
        if platform.system() == "Windows":
            os.system(f"start {temp_path}")
        elif platform.system() == "Darwin":  # macOS
            os.system(f"afplay {temp_path}")
        else:  # Linux
            os.system(f"mpg123 {temp_path}")
        
        # Clean up
        import time
        time.sleep(3)
        os.unlink(temp_path)
        
        print("[OK] Google TTS working!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Google TTS failed: {e}")
        return False

def test_speech_module():
    """Test SenseEd speech module"""
    print("\nTesting SenseEd Speech Module...")
    try:
        from modules.speech_module import SpeechModule
        
        speech = SpeechModule()
        
        # Test TTS
        print("Testing speech module TTS...")
        success = speech.speak_text("Hello! This is a test of the SenseEd speech module.", use_gtts=False)
        
        if success:
            print("[OK] SenseEd Speech Module working!")
            return True
        else:
            print("[FAIL] SenseEd Speech Module TTS failed")
            return False
            
    except Exception as e:
        print(f"[FAIL] SenseEd Speech Module failed: {e}")
        return False

def main():
    """Main test function"""
    print("SenseEd TTS Test Suite")
    print("=" * 40)
    
    results = []
    
    # Test system TTS
    results.append(("System TTS", test_system_tts()))
    
    # Test Google TTS
    results.append(("Google TTS", test_google_tts()))
    
    # Test SenseEd speech module
    results.append(("SenseEd Speech Module", test_speech_module()))
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    print("=" * 40)
    
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{test_name}: {status}")
    
    working_methods = sum(1 for _, success in results if success)
    total_methods = len(results)
    
    print(f"\nWorking TTS methods: {working_methods}/{total_methods}")
    
    if working_methods > 0:
        print("[SUCCESS] At least one TTS method is working!")
        print("The GUI should be able to speak responses.")
    else:
        print("[WARNING] No TTS methods are working.")
        print("Please check your audio system and dependencies.")
        print("\nTroubleshooting:")
        print("1. Make sure your speakers/headphones are working")
        print("2. Check Windows audio settings")
        print("3. Try running as administrator")
        print("4. Install missing dependencies: pip install pyttsx3 gtts")

if __name__ == "__main__":
    main()
