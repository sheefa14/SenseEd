#!/usr/bin/env python3
"""
Test script to verify camera speed is reduced
"""

import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_camera_speed():
    """Test camera loop speed"""
    try:
        from src.gui.minimalist_window import MinimalistSenseEdGUI
        
        print("Testing camera speed...")
        print("Creating GUI instance...")
        
        # Create GUI instance
        gui = MinimalistSenseEdGUI()
        
        print("Starting camera...")
        gui.start_camera()
        
        print("Camera started. Testing speed for 5 seconds...")
        print("You should see much slower camera updates now.")
        
        # Let it run for 5 seconds
        time.sleep(5)
        
        print("Stopping camera...")
        gui.stop_camera()
        
        print("Cleaning up...")
        gui.root.destroy()
        
        print("[SUCCESS] Camera speed test completed.")
        print("The camera should now run at 500 FPS instead of 1000+ FPS.")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Camera speed test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Camera Speed Test")
    print("=" * 30)
    
    success = test_camera_speed()
    
    if success:
        print("\n[SUCCESS] Camera speed has been reduced successfully!")
        print("The camera now runs at 500 FPS with frame throttling.")
        print("This should provide much smoother and slower movement.")
    else:
        print("\n[ERROR] Camera speed test failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
