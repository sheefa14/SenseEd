#!/usr/bin/env python3
"""
Test script to verify sign language integration
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sign_language_module():
    """Test the sign language module directly"""
    try:
        from modules.sign_language_module import SignLanguageModule
        
        print("Testing Sign Language Module...")
        print("=" * 40)
        
        # Create sign language module
        sign_module = SignLanguageModule()
        
        # Test dataset loading
        phrases = sign_module.get_available_phrases()
        print(f"Loaded {len(phrases)} sign language phrases")
        
        if phrases:
            print("\nSample phrases:")
            for i, phrase in enumerate(phrases[:10]):
                print(f"  {i+1}. {phrase}")
            
            # Test phrase info
            sample_phrase = phrases[0]
            info = sign_module.get_phrase_info(sample_phrase)
            print(f"\nInfo for '{sample_phrase}':")
            print(f"  - Available: {info['available']}")
            if info['available']:
                print(f"  - Image count: {info['image_count']}")
                print(f"  - Sample images: {len(info['image_paths'])}")
        
        # Test module status
        status = sign_module.get_module_status()
        print(f"\nModule Status:")
        print(f"  - Available: {status['available']}")
        print(f"  - MediaPipe: {status['mediapipe_available']}")
        print(f"  - Phrases loaded: {status['phrases_loaded']}")
        print(f"  - Data folder: {status['data_folder']}")
        
        sign_module.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Sign language module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gesture_module_integration():
    """Test gesture module with sign language integration"""
    try:
        from modules.gesture_module import GestureModule
        
        print("\nTesting Gesture Module Integration...")
        print("=" * 40)
        
        # Create gesture module
        gesture_module = GestureModule()
        
        # Test sign language status
        sign_status = gesture_module.get_sign_language_status()
        print(f"Sign Language Status:")
        print(f"  - Available: {sign_status.get('available', False)}")
        
        if sign_status.get('available'):
            phrases = gesture_module.get_sign_language_phrases()
            print(f"  - Phrases available: {len(phrases)}")
            
            if phrases:
                print(f"  - Sample phrases: {phrases[:5]}")
        else:
            print(f"  - Error: {sign_status.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Gesture module integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_integration():
    """Test GUI integration"""
    try:
        print("\nTesting GUI Integration...")
        print("=" * 40)
        
        # Test if we can import the GUI
        from src.gui.minimalist_window import MinimalistSenseEdGUI
        
        print("GUI import successful")
        print("Sign language integration should be available in the GUI")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] GUI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Sign Language Integration Test")
    print("=" * 50)
    
    # Test sign language module
    sign_success = test_sign_language_module()
    
    # Test gesture module integration
    gesture_success = test_gesture_module_integration()
    
    # Test GUI integration
    gui_success = test_gui_integration()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  - Sign Language Module: {'[PASS]' if sign_success else '[FAIL]'}")
    print(f"  - Gesture Integration: {'[PASS]' if gesture_success else '[FAIL]'}")
    print(f"  - GUI Integration: {'[PASS]' if gui_success else '[FAIL]'}")
    
    if all([sign_success, gesture_success, gui_success]):
        print("\n[SUCCESS] All sign language integration tests passed!")
        print("You can now use sign language recognition in the GUI.")
        print("\nTo test:")
        print("1. Run: python run_minimalist_gui.py")
        print("2. Click 'Start Camera'")
        print("3. Click 'Start Sign Language'")
        print("4. Try signing phrases from the dataset")
        return 0
    else:
        print("\n[ERROR] Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())




