#!/usr/bin/env python3
"""
Multimodal GUI Launcher for SenseEd
This script launches the enhanced GUI with camera, speech, and gesture integration
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import numpy as np
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        import speech_recognition as sr
    except ImportError:
        missing_deps.append("SpeechRecognition")
    
    try:
        import pyttsx3
    except ImportError:
        missing_deps.append("pyttsx3")
    
    try:
        import gtts
    except ImportError:
        missing_deps.append("gtts")
    
    try:
        import pytesseract
    except ImportError:
        missing_deps.append("pytesseract")
    
    try:
        from ultralytics import YOLO
    except ImportError:
        missing_deps.append("ultralytics")
    
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
    except ImportError:
        missing_deps.append("transformers")
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing_deps.append("beautifulsoup4")
    
    try:
        from textblob import TextBlob
    except ImportError:
        missing_deps.append("textblob")
    
    try:
        import mediapipe as mp
    except ImportError:
        print("Warning: MediaPipe not available - gesture recognition will use OpenCV fallback")
    
    return missing_deps

def main():
    """Main function to launch the multimodal GUI"""
    print("SenseEd Multimodal GUI Launcher")
    print("=" * 40)
    
    # Check dependencies
    print("Checking dependencies...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print("Please install them using: pip install " + " ".join(missing_deps))
        
        # Show GUI error dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(
            "Missing Dependencies", 
            f"Please install the following packages:\n\n" + 
            "\n".join(missing_deps) + 
            "\n\nRun: pip install " + " ".join(missing_deps)
        )
        root.destroy()
        return
    
    print("All dependencies found!")
    
    try:
        # Import and launch GUI
        from src.gui.main_window import SenseEdGUI
        
        print("Launching SenseEd Multimodal GUI...")
        print("Features available:")
        print("- Text chat interface")
        print("- Voice input and output")
        print("- Live camera feed")
        print("- Hand gesture recognition")
        print("- OCR text extraction")
        print("- Object detection")
        print("- Scene description")
        print("\nPress Ctrl+C to exit")
        
        # Create and run GUI
        gui = SenseEdGUI()
        gui.run()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all SenseEd modules are properly installed")
    except Exception as e:
        print(f"Error launching GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
