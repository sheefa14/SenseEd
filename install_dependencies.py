#!/usr/bin/env python3
"""
SenseEd Dependencies Installer
This script installs all required dependencies for the multimodal GUI
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"   Error: {e.stderr}")
        return False

def install_dependencies():
    """Install all required dependencies"""
    print("SenseEd Dependencies Installer")
    print("=" * 40)
    print("Installing required packages...")
    print()
    
    # Core dependencies
    dependencies = [
        "torch>=2.0.0",
        "transformers>=4.30.0", 
        "numpy>=1.24.0",
        "opencv-python>=4.8.0",
        "Pillow>=10.0.0",
        "pytesseract>=0.3.10",
        "ultralytics>=8.0.0",
        "SpeechRecognition>=3.10.0",
        "gTTS>=2.3.0",
        "pyttsx3>=2.90",
        "nltk>=3.8.0",
        "spacy>=3.6.0",
        "textblob>=0.17.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "tqdm>=4.65.0",
        "psutil>=5.9.0"
    ]
    
    # Optional dependencies (with fallbacks)
    optional_dependencies = [
        "mediapipe>=0.10.0",  # For gesture recognition
        "pyaudio>=0.2.11",    # For audio input
        "librosa>=0.10.0",    # For audio processing
        "sentence-transformers>=2.2.0",  # For NLP
        "scipy>=1.10.0"       # For scientific computing
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    print("Installing core dependencies...")
    for dep in dependencies:
        if run_command(f"pip install {dep}"):
            success_count += 1
        print()
    
    print("Installing optional dependencies...")
    for dep in optional_dependencies:
        if run_command(f"pip install {dep}"):
            success_count += 1
        print()
    
    print("=" * 40)
    print(f"Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{total_count + len(optional_dependencies)} packages")
    
    if success_count == total_count + len(optional_dependencies):
        print("🎉 All dependencies installed successfully!")
        print("\nYou can now run the multimodal GUI:")
        print("   python run_multimodal_gui.py")
        print("   python main.py --gui")
    else:
        print("⚠️  Some dependencies failed to install.")
        print("The application may work with reduced functionality.")
        print("\nYou can still try running the GUI:")
        print("   python run_multimodal_gui.py")
    
    print("\nFor more information, see the README.md file.")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True

def main():
    """Main function"""
    if not check_python_version():
        sys.exit(1)
    
    print()
    install_dependencies()

if __name__ == "__main__":
    main()
