#!/usr/bin/env python3
"""
GUI Speech Test Script for SenseEd
This script tests the speech functionality specifically in the GUI context
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_speech_in_gui_context():
    """Test speech module in GUI context"""
    print("Testing Speech Module in GUI Context...")
    
    try:
        from modules.speech_module import SpeechModule
        
        # Initialize speech module
        speech = SpeechModule()
        
        # Test system TTS
        print("Testing system TTS...")
        success1 = speech.speak_text("Hello! This is a test of system TTS from the GUI context.", use_gtts=False)
        print(f"System TTS result: {success1}")
        
        # Test Google TTS
        print("Testing Google TTS...")
        success2 = speech.speak_text("Hello! This is a test of Google TTS from the GUI context.", use_gtts=True)
        print(f"Google TTS result: {success2}")
        
        # Test async speech
        print("Testing async speech...")
        speech.speak_async("Hello! This is an async test from the GUI context.")
        print("Async speech started...")
        
        # Wait a bit for async to complete
        import time
        time.sleep(3)
        
        # Get speech status
        status = speech.get_speech_status()
        print(f"Speech status: {status}")
        
        return success1 or success2
        
    except Exception as e:
        print(f"Error testing speech in GUI context: {e}")
        return False

def test_gui_speech_button():
    """Test the GUI speech button functionality"""
    print("\nTesting GUI Speech Button Functionality...")
    
    try:
        # Create a simple test GUI
        root = tk.Tk()
        root.title("Speech Test")
        root.geometry("400x200")
        
        # Create speech module
        from modules.speech_module import SpeechModule
        speech = SpeechModule()
        
        def test_speak():
            """Test speech function"""
            try:
                text = "Hello! This is a test from the GUI speech button."
                success = speech.speak_text(text, use_gtts=False)
                if success:
                    messagebox.showinfo("Success", "Speech test successful!")
                else:
                    messagebox.showerror("Error", "Speech test failed!")
            except Exception as e:
                messagebox.showerror("Error", f"Speech error: {e}")
        
        def test_google_speak():
            """Test Google TTS function"""
            try:
                text = "Hello! This is a Google TTS test from the GUI speech button."
                success = speech.speak_text(text, use_gtts=True)
                if success:
                    messagebox.showinfo("Success", "Google TTS test successful!")
                else:
                    messagebox.showerror("Error", "Google TTS test failed!")
            except Exception as e:
                messagebox.showerror("Error", f"Google TTS error: {e}")
        
        # Create buttons
        tk.Button(root, text="Test System TTS", command=test_speak, 
                 font=("Arial", 12), bg="lightblue", padx=20, pady=10).pack(pady=10)
        
        tk.Button(root, text="Test Google TTS", command=test_google_speak, 
                 font=("Arial", 12), bg="lightgreen", padx=20, pady=10).pack(pady=10)
        
        tk.Button(root, text="Exit", command=root.quit, 
                 font=("Arial", 12), bg="lightcoral", padx=20, pady=10).pack(pady=10)
        
        print("GUI created. Click buttons to test speech functionality.")
        print("Close the window when done testing.")
        
        # Run GUI
        root.mainloop()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"Error creating test GUI: {e}")
        return False

def main():
    """Main test function"""
    print("SenseEd GUI Speech Test")
    print("=" * 40)
    
    # Test 1: Speech in GUI context
    result1 = test_speech_in_gui_context()
    
    # Test 2: GUI speech button
    result2 = test_gui_speech_button()
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    print("=" * 40)
    print(f"GUI Context Speech Test: {'[PASS]' if result1 else '[FAIL]'}")
    print(f"GUI Speech Button Test: {'[PASS]' if result2 else '[FAIL]'}")
    
    if result1 and result2:
        print("\n[SUCCESS] All GUI speech tests passed!")
        print("The speech functionality should work in the main GUI.")
    else:
        print("\n[WARNING] Some GUI speech tests failed.")
        print("There may be issues with speech in the main GUI.")

if __name__ == "__main__":
    main()

