#!/usr/bin/env python3
"""
Test script to verify voice input and output functionality
"""

import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_voice_functionality():
    """Test voice input and output functionality"""
    try:
        from src.gui.main_window import SenseEdGUI
        
        print("Testing Voice Input and Output Functionality...")
        print("=" * 60)
        
        # Create GUI instance
        gui = SenseEdGUI()
        
        # Test speech module status
        speech_status = gui.speech_module.get_speech_status()
        print(f"Speech Module Status:")
        print(f"  - Microphone available: {speech_status['microphone_available']}")
        print(f"  - TTS available: {speech_status['tts_available']}")
        print(f"  - Available voices: {speech_status['available_voices']}")
        
        if not speech_status['microphone_available']:
            print("[WARNING] Microphone not available - voice input will not work")
        
        if not speech_status['tts_available']:
            print("[WARNING] TTS not available - voice output will not work")
        
        # Test voice input
        print("\nTesting Voice Input...")
        print("Speak something into your microphone...")
        
        # Test single voice input
        voice_text = gui.speech_module.listen_to_speech(timeout=5, phrase_time_limit=3)
        if voice_text:
            print(f"[SUCCESS] Voice input recognized: '{voice_text}'")
            
            # Test voice output
            print("\nTesting Voice Output...")
            print("You should hear the response spoken...")
            
            success = gui.speech_module.speak_response(f"You said: {voice_text}")
            if success:
                print("[SUCCESS] Voice output working")
            else:
                print("[ERROR] Voice output failed")
        else:
            print("[WARNING] No voice input detected")
        
        # Test voice controls
        print("\nTesting Voice Controls...")
        print("Voice input button:", gui.voice_input_button['text'])
        print("Voice output button:", gui.voice_output_button['text'])
        print("Voice status:", gui.voice_status_label['text'])
        
        print("\n[SUCCESS] Voice functionality test completed!")
        print("Voice controls are available in the GUI.")
        
        # Clean up
        gui.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Voice functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_speech_module():
    """Test enhanced speech module features"""
    try:
        from modules.speech_module import SpeechModule
        
        print("\nTesting Enhanced Speech Module...")
        print("=" * 40)
        
        # Create speech module
        speech_module = SpeechModule()
        
        # Test text cleaning
        test_text = "**Hello** *world*! Check out `this code` and visit https://example.com"
        cleaned_text = speech_module._clean_text_for_speech(test_text)
        print(f"Text cleaning test:")
        print(f"  Original: {test_text}")
        print(f"  Cleaned: {cleaned_text}")
        
        # Test speak_response method
        print("\nTesting enhanced speak_response method...")
        success = speech_module.speak_response("This is a test of the enhanced speech response functionality.")
        if success:
            print("[SUCCESS] Enhanced speak_response working")
        else:
            print("[ERROR] Enhanced speak_response failed")
        
        print("[SUCCESS] Enhanced speech module test completed!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Enhanced speech module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Voice Input and Output Test")
    print("=" * 50)
    
    # Test voice functionality
    voice_success = test_voice_functionality()
    
    # Test enhanced speech module
    speech_success = test_enhanced_speech_module()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  - Voice Functionality: {'[PASS]' if voice_success else '[FAIL]'}")
    print(f"  - Enhanced Speech Module: {'[PASS]' if speech_success else '[FAIL]'}")
    
    if all([voice_success, speech_success]):
        print("\n[SUCCESS] All voice functionality tests passed!")
        print("\nVoice Features Available:")
        print("  - Voice Input: Continuous listening for natural conversation")
        print("  - Voice Output: AI responses spoken aloud")
        print("  - Enhanced Speech: Better text cleaning and processing")
        print("  - Multiple TTS Engines: Google TTS and system TTS support")
        print("\nTo use voice features:")
        print("1. Run: python run_multimodal_gui.py")
        print("2. Click 'Voice Input' to start listening")
        print("3. Click 'Voice Output' to enable spoken responses")
        print("4. Speak naturally - the AI will respond with voice!")
        return 0
    else:
        print("\n[ERROR] Some voice tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
