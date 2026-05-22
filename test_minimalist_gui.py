#!/usr/bin/env python3
"""
Test script for the minimalist GUI
This script tests if the GUI loads without errors
"""

import sys
import os
import tkinter as tk

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gui_loading():
    """Test if the minimalist GUI loads without errors"""
    try:
        print("Testing minimalist GUI loading...")
        
        # Import the minimalist GUI
        from src.gui.minimalist_window import MinimalistSenseEdGUI
        
        print("[OK] GUI module imported successfully")
        
        # Create a test instance (this will test the GUI setup)
        print("Creating GUI instance...")
        gui = MinimalistSenseEdGUI()
        
        print("[OK] GUI instance created successfully")
        
        # Test if the GUI can be displayed (without running mainloop)
        print("Testing GUI display...")
        gui.root.update()
        
        print("[OK] GUI display test passed")
        
        # Clean up
        gui.root.destroy()
        
        print("[SUCCESS] All tests passed! The minimalist GUI is working correctly.")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_font_compatibility():
    """Test font compatibility"""
    try:
        print("\nTesting font compatibility...")
        
        # Test common fonts
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test Segoe UI font
        try:
            test_label = tk.Label(root, text="Test", font=("Segoe UI", 12, "bold"))
            test_label.destroy()
            print("[OK] Segoe UI font is available")
        except Exception as e:
            print(f"[WARNING] Segoe UI font issue: {e}")
        
        # Test fallback fonts
        fallback_fonts = ["Arial", "Helvetica", "Tahoma", "Verdana"]
        for font in fallback_fonts:
            try:
                test_label = tk.Label(root, text="Test", font=(font, 12, "bold"))
                test_label.destroy()
                print(f"[OK] {font} font is available")
                break
            except Exception:
                continue
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"[ERROR] Font test failed: {e}")
        return False

def main():
    """Main test function"""
    print("SenseEd Minimalist GUI Test")
    print("=" * 40)
    
    # Test font compatibility first
    font_test = test_font_compatibility()
    
    # Test GUI loading
    gui_test = test_gui_loading()
    
    print("\n" + "=" * 40)
    if font_test and gui_test:
        print("[SUCCESS] All tests passed! The minimalist GUI is ready to use.")
        print("\nTo launch the GUI, run:")
        print("  python run_minimalist_gui.py")
        print("  or")
        print("  python main.py --minimalist")
    else:
        print("[ERROR] Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
