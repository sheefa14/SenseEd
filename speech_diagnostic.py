#!/usr/bin/env python3
"""
Speech Diagnostic Script for SenseEd
This script provides detailed diagnostics for speech functionality
"""

import sys
import os
import platform

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_audio_system():
    """Check if audio system is working"""
    print("=== Audio System Check ===")
    
    # Check platform
    print(f"Platform: {platform.system()} {platform.release()}")
    
    # Check if we can import audio libraries
    try:
        import pyttsx3
        print("[OK] pyttsx3 imported successfully")
        
        # Test TTS engine initialization
        engine = pyttsx3.init()
        print("[OK] TTS engine initialized")
        
        # Get voices
        voices = engine.getProperty('voices')
        print(f"[OK] Available voices: {len(voices) if voices else 0}")
        
        if voices:
            for i, voice in enumerate(voices):
                print(f"  Voice {i}: {voice.name} - {voice.languages}")
        
        # Test speech
        print("Testing speech output...")
        engine.say("Audio system test successful")
        engine.runAndWait()
        print("[OK] Speech test completed")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Audio system check failed: {e}")
        return False

def check_google_tts():
    """Check Google TTS functionality"""
    print("\n=== Google TTS Check ===")
    
    try:
        from gtts import gTTS
        print("✓ gTTS imported successfully")
        
        # Test TTS creation
        tts = gTTS(text="Google TTS test", lang='en', slow=False)
        print("✓ TTS object created")
        
        # Test file creation
        temp_file = "test_audio.mp3"
        tts.save(temp_file)
        print("✓ Audio file created")
        
        # Test playback
        if platform.system() == "Windows":
            os.system(f"start {temp_file}")
        elif platform.system() == "Darwin":  # macOS
            os.system(f"afplay {temp_file}")
        else:  # Linux
            os.system(f"mpg123 {temp_file}")
        
        print("✓ Audio playback started")
        
        # Clean up
        import time
        time.sleep(3)
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print("✓ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ Google TTS check failed: {e}")
        return False

def check_speech_module():
    """Check SenseEd speech module"""
    print("\n=== SenseEd Speech Module Check ===")
    
    try:
        from modules.speech_module import SpeechModule
        print("✓ Speech module imported successfully")
        
        # Initialize module
        speech = SpeechModule()
        print("✓ Speech module initialized")
        
        # Check status
        status = speech.get_speech_status()
        print(f"✓ Module status: {status}")
        
        # Test system TTS
        print("Testing system TTS...")
        success1 = speech.speak_text("SenseEd speech module test", use_gtts=False)
        print(f"System TTS result: {success1}")
        
        # Test Google TTS
        print("Testing Google TTS...")
        success2 = speech.speak_text("SenseEd Google TTS test", use_gtts=True)
        print(f"Google TTS result: {success2}")
        
        return success1 or success2
        
    except Exception as e:
        print(f"✗ Speech module check failed: {e}")
        return False

def check_dependencies():
    """Check required dependencies"""
    print("\n=== Dependencies Check ===")
    
    dependencies = [
        'pyttsx3',
        'gtts',
        'speech_recognition',
        'pyaudio'
    ]
    
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"[OK] {dep} available")
        except ImportError:
            print(f"[MISSING] {dep} missing")
            all_good = False
    
    return all_good

def main():
    """Main diagnostic function"""
    print("SenseEd Speech Diagnostic Tool")
    print("=" * 50)
    
    results = []
    
    # Run all checks
    results.append(("Dependencies", check_dependencies()))
    results.append(("Audio System", check_audio_system()))
    results.append(("Google TTS", check_google_tts()))
    results.append(("Speech Module", check_speech_module()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Diagnostic Results Summary:")
    print("=" * 50)
    
    for check_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{check_name}: {status}")
    
    passed_checks = sum(1 for _, success in results if success)
    total_checks = len(results)
    
    print(f"\nPassed checks: {passed_checks}/{total_checks}")
    
    if passed_checks == total_checks:
        print("\n[SUCCESS] All speech functionality is working correctly!")
        print("The speech output should work in the GUI.")
    elif passed_checks >= 2:
        print("\n[PARTIAL] Some speech functionality is working.")
        print("The GUI should have at least one working TTS method.")
    else:
        print("\n[FAILURE] Most speech functionality is not working.")
        print("Please check your audio system and dependencies.")
        
        print("\nTroubleshooting steps:")
        print("1. Make sure your speakers/headphones are working")
        print("2. Check Windows audio settings and volume")
        print("3. Try running as administrator")
        print("4. Install missing dependencies:")
        print("   pip install pyttsx3 gtts SpeechRecognition pyaudio")
        print("5. Check if Windows Speech Platform is enabled")

if __name__ == "__main__":
    main()
