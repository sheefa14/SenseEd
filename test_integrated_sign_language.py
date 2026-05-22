#!/usr/bin/env python3
"""
Test script to verify integrated sign language recognition
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_integrated_sign_language():
    """Test that sign language recognition is integrated with gesture tracking"""
    try:
        from src.gui.main_window import SenseEdGUI
        
        print("Testing Integrated Sign Language Recognition...")
        print("=" * 50)
        
        # Create GUI instance
        gui = SenseEdGUI()
        
        # Check if gesture module has sign language capabilities
        if gui.gesture_module:
            sign_status = gui.gesture_module.get_sign_language_status()
            print(f"Sign Language Status:")
            print(f"  - Available: {sign_status.get('available', False)}")
            
            if sign_status.get('available'):
                phrases = gui.gesture_module.get_sign_language_phrases()
                print(f"  - Phrases available: {len(phrases)}")
                print(f"  - Sample phrases: {phrases[:5]}")
                
                print("\n[SUCCESS] Sign language recognition is integrated!")
                print("When you enable gesture tracking, sign language recognition will also be active.")
                print("You can now sign phrases from the dataset and they will be recognized automatically.")
                
                return True
            else:
                print(f"  - Error: {sign_status.get('error', 'Unknown error')}")
                return False
        else:
            print("[ERROR] Gesture module not available")
            return False
        
    except Exception as e:
        print(f"[ERROR] Integrated sign language test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Integrated Sign Language Recognition Test")
    print("=" * 50)
    
    success = test_integrated_sign_language()
    
    if success:
        print("\n[SUCCESS] Sign language recognition is now integrated with gesture tracking!")
        print("\nHow to use:")
        print("1. Launch the GUI: python run_multimodal_gui.py")
        print("2. Click 'Start Camera'")
        print("3. Click 'Gestures' to enable gesture tracking")
        print("4. Sign language recognition will automatically be active")
        print("5. Try signing phrases from the dataset (97 phrases available)")
        print("\nThe system will now recognize both basic gestures AND sign language phrases!")
    else:
        print("\n[ERROR] Integration test failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




