#!/usr/bin/env python3
"""
SenseEd - Multimodal AI Learning Assistant
Main application entry point

This application provides an accessible, multimodal learning experience
combining speech recognition, computer vision, gesture recognition, and NLP.
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.chatbot import SenseEdChatbot
from src.core.config import get_config

def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """Setup application logging"""
    # Create logs directory
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    else:
        handlers.append(logging.FileHandler(logs_dir / 'senseed.log'))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    SenseEd AI Assistant                      ║
    ║                                                              ║
    ║              Multimodal Learning for Everyone                ║
    ║                                                              ║
    ║  Features:                                                   ║
    ║  • Speech Recognition & Text-to-Speech                      ║
    ║  • Computer Vision & OCR                                    ║
    ║  • Gesture Recognition                                      ║
    ║  • Natural Language Processing                              ║
    ║  • Document Reading & Analysis                              ║
    ║  • Accessibility-First Design                               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_help():
    """Print help information"""
    help_text = """
    SenseEd - Multimodal AI Learning Assistant
    
    USAGE:
        python main.py [OPTIONS]
    
    OPTIONS:
        -h, --help              Show this help message
        -c, --config FILE       Use custom configuration file
        -l, --log-level LEVEL   Set logging level (DEBUG, INFO, WARNING, ERROR)
        -g, --gui               Launch with GUI interface
        -m, --minimalist        Launch with minimalist GUI interface
        -t, --text-only         Text-only mode (no speech/vision)
        -v, --verbose           Verbose output
        --version               Show version information
    
    MODES:
        Interactive Mode (default):
            Start the full multimodal chatbot experience
        
        GUI Mode:
            Launch with full-featured graphical user interface
        
        Minimalist GUI Mode:
            Launch with clean, minimalist graphical interface
        
        Text-only Mode:
            Run without speech and vision capabilities
    
    EXAMPLES:
        python main.py                          # Start in interactive mode
        python main.py --gui                    # Start with full GUI
        python main.py --minimalist             # Start with minimalist GUI
        python main.py --text-only              # Text-only mode
        python main.py -c my_config.yaml        # Use custom config
        python main.py --log-level DEBUG        # Debug logging
    
    ACCESSIBILITY:
        SenseEd is designed to be accessible to users with various needs:
        - Voice commands and speech output
        - Gesture recognition for hands-free interaction
        - High contrast and large text options
        - Screen reader compatibility
        - Keyboard navigation support
    
    For more information, visit: https://github.com/your-repo/senseed
    """
    print(help_text)

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import speech_recognition
    except ImportError:
        missing_deps.append("SpeechRecognition")
    
    try:
        import pyttsx3
    except ImportError:
        missing_deps.append("pyttsx3")
    
    try:
        import mediapipe
    except ImportError:
        missing_deps.append("mediapipe")
        print("⚠️  MediaPipe not available - gesture recognition will be disabled")
    
    try:
        import spacy
    except ImportError:
        missing_deps.append("spacy")
    
    try:
        import transformers
    except ImportError:
        missing_deps.append("transformers")
    
    if missing_deps:
        print("⚠️  Some optional dependencies are missing:")
        for dep in missing_deps:
            if dep == "mediapipe":
                print(f"   - {dep} (gesture recognition will be disabled)")
            else:
                print(f"   - {dep}")
        print("\n💡 Install missing dependencies with:")
        print(f"   pip install {' '.join(missing_deps)}")
        print("\n   Or install all dependencies with:")
        print("   pip install -r requirements.txt")
        print("\n   Note: The application will work with reduced functionality.")
        # Don't return False - let the app continue with reduced functionality
    
    return True

def run_interactive_mode(config_file: Optional[str] = None):
    """Run in interactive mode"""
    print("🚀 Starting SenseEd in interactive mode...")
    
    try:
        # Initialize chatbot
        chatbot = SenseEdChatbot(config_file)
        
        # Check system status
        status = chatbot.get_status()
        print(f"📊 System Status:")
        print(f"   Speech Module: {'✅' if status['modules']['speech']['microphone_available'] else '❌'}")
        print(f"   Vision Module: {'✅' if status['modules']['vision']['camera_available'] else '❌'}")
        print(f"   Text Module: {'✅' if status['modules']['text']['spacy_available'] else '❌'}")
        print(f"   NLP Module: {'✅' if status['modules']['nlp']['spacy_available'] else '❌'}")
        
        # Start session
        chatbot.start_session()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Thanks for using SenseEd.")
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Application error: {e}", exc_info=True)

def run_gui_mode(config_file: Optional[str] = None):
    """Run in GUI mode"""
    print("🖥️  Starting SenseEd in Multimodal GUI mode...")
    
    try:
        # Import GUI components
        from src.gui.main_window import SenseEdGUI
        
        # Initialize GUI
        gui = SenseEdGUI(config_file)
        gui.run()
        
    except ImportError as e:
        print(f"❌ GUI components not available: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        print("\n💡 Falling back to interactive mode...")
        run_interactive_mode(config_file)
    except Exception as e:
        print(f"❌ GUI Error: {e}")
        logging.error(f"GUI error: {e}", exc_info=True)

def run_minimalist_gui_mode(config_file: Optional[str] = None):
    """Run in minimalist GUI mode"""
    print("🎨 Starting SenseEd in Minimalist GUI mode...")
    
    try:
        # Import minimalist GUI components
        from src.gui.minimalist_window import MinimalistSenseEdGUI
        
        # Initialize minimalist GUI
        gui = MinimalistSenseEdGUI(config_file)
        gui.run()
        
    except ImportError as e:
        print(f"❌ Minimalist GUI components not available: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        print("\n💡 Falling back to standard GUI mode...")
        run_gui_mode(config_file)
    except Exception as e:
        print(f"❌ Minimalist GUI Error: {e}")
        logging.error(f"Minimalist GUI error: {e}", exc_info=True)

def run_text_only_mode(config_file: Optional[str] = None):
    """Run in text-only mode"""
    print("📝 Starting SenseEd in text-only mode...")
    
    try:
        # Initialize chatbot with text-only configuration
        chatbot = SenseEdChatbot(config_file)
        
        # Disable speech and vision modules
        chatbot.speech_module = None
        chatbot.vision_module = None
        chatbot.gesture_module = None
        
        print("💬 Text-only mode active. Type your messages:")
        print("   Type 'exit' or 'quit' to end the session")
        print("   Type 'help' for available commands")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                if user_input.lower() == 'help':
                    print(chatbot._get_help_message())
                    continue
                
                if not user_input:
                    continue
                
                # Process text input
                input_data = {
                    'type': 'text',
                    'content': user_input,
                    'timestamp': chatbot._get_timestamp()
                }
                
                response = chatbot.process_input(input_data)
                
                if response.get('text'):
                    print(f"SenseEd: {response['text']}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error processing input: {e}")
        
        print("\n👋 Goodbye! Thanks for using SenseEd.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Text-only mode error: {e}", exc_info=True)

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="SenseEd - Multimodal AI Learning Assistant",
        add_help=False
    )
    
    parser.add_argument('-h', '--help', action='store_true', help='Show help message')
    parser.add_argument('-c', '--config', type=str, help='Configuration file path')
    parser.add_argument('-l', '--log-level', type=str, default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging level')
    parser.add_argument('-g', '--gui', action='store_true', help='Launch with GUI')
    parser.add_argument('-m', '--minimalist', action='store_true', help='Launch with minimalist GUI')
    parser.add_argument('-t', '--text-only', action='store_true', help='Text-only mode')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--version', action='store_true', help='Show version')
    
    args = parser.parse_args()
    
    # Handle special arguments
    if args.help:
        print_help()
        return
    
    if args.version:
        print("SenseEd AI Assistant v1.0.0")
        print("Multimodal Learning for Everyone")
        return
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else args.log_level
    setup_logging(log_level)
    
    # Print banner
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Load configuration
    config = get_config()
    if args.config:
        config.import_config(args.config)
    
    # Run in appropriate mode
    try:
        if args.minimalist:
            run_minimalist_gui_mode(args.config)
        elif args.gui:
            run_gui_mode(args.config)
        elif args.text_only:
            run_text_only_mode(args.config)
        else:
            run_interactive_mode(args.config)
            
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()