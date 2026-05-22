#!/usr/bin/env python3
"""
SenseEd Demo Script
Quick demonstration of the multimodal AI learning assistant
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_demo_banner():
    """Print demo banner"""
    banner = """
    ================================================================
    
                    SenseEd Demo                              
    
              Multimodal AI Learning Assistant                
    
    ================================================================
    """
    print(banner)

def demo_speech_features():
    """Demonstrate speech features"""
    print("\nSpeech Features Demo")
    print("=" * 50)
    
    try:
        from modules.speech_module import SpeechModule
        
        print("Initializing speech module...")
        speech = SpeechModule()
        
        print("Speech module initialized successfully!")
        print(f"   Microphone available: {speech.get_speech_status()['microphone_available']}")
        print(f"   TTS available: {speech.get_speech_status()['tts_available']}")
        
        # Test TTS
        print("\nTesting text-to-speech...")
        speech.speak_text("Hello! I'm SenseEd, your AI learning assistant.")
        print("Text-to-speech test completed!")
        
    except Exception as e:
        print(f"Speech demo failed: {e}")

def demo_vision_features():
    """Demonstrate vision features"""
    print("\nVision Features Demo")
    print("=" * 50)
    
    try:
        from modules.vision_module import VisionModule
        
        print("Initializing vision module...")
        vision = VisionModule()
        
        print("✓ Vision module initialized successfully!")
        print(f"   Camera available: {vision.get_camera_status()['camera_available']}")
        print(f"   YOLO available: {vision.get_camera_status()['yolo_available']}")
        print(f"   BLIP available: {vision.get_camera_status()['blip_available']}")
        
        # Test camera initialization
        if vision.initialize_camera():
            print("✓ Camera initialized successfully!")
            
            # Capture a test image
            print("[CAMERA] Capturing test image...")
            frame = vision.capture_image()
            if frame is not None:
                print("✓ Image captured successfully!")
                print(f"   Image shape: {frame.shape}")
            else:
                print("[WARNING]  No image captured")
            
            vision.release_camera()
        else:
            print("[WARNING]  Camera initialization failed")
        
    except Exception as e:
        print(f"✗ Vision demo failed: {e}")

def demo_gesture_features():
    """Demonstrate gesture features"""
    print("\n[HAND] Gesture Features Demo")
    print("=" * 50)
    
    try:
        from modules.gesture_module import GestureModule
        
        print("Initializing gesture module...")
        gesture = GestureModule()
        
        print("✓ Gesture module initialized successfully!")
        print("   Supported gestures: Open Hand, Fist, Thumbs Up/Down, Peace, Pointing, Pinch, OK, Rock On, Three, Four")
        
    except Exception as e:
        print(f"✗ Gesture demo failed: {e}")

def demo_text_features():
    """Demonstrate text features"""
    print("\n[TEXT] Text Features Demo")
    print("=" * 50)
    
    try:
        from modules.text_module import TextModule
        
        print("Initializing text module...")
        text = TextModule()
        
        print("✓ Text module initialized successfully!")
        print(f"   spaCy available: {text.get_module_status()['spacy_available']}")
        print(f"   Summarizer available: {text.get_module_status()['summarizer_available']}")
        
        # Test text processing
        test_text = "Artificial intelligence is transforming education by providing personalized learning experiences and making education more accessible to students with diverse needs."
        
        print(f"\n[DOCUMENT] Processing test text: '{test_text[:50]}...'")
        result = text.process_text(test_text, ['sentiment', 'keywords'])
        
        if result.get('success'):
            print("✓ Text processing completed!")
            
            # Show sentiment
            sentiment = result.get('operations', {}).get('sentiment', {})
            if sentiment:
                print(f"   Sentiment: {sentiment.get('textblob', {}).get('polarity', 'N/A')}")
            
            # Show keywords
            keywords = result.get('operations', {}).get('keywords', [])
            if keywords:
                print(f"   Keywords: {', '.join(keywords[:5])}")
        else:
            print("[WARNING]  Text processing failed")
        
    except Exception as e:
        print(f"✗ Text demo failed: {e}")

def demo_nlp_features():
    """Demonstrate NLP features"""
    print("\n[BRAIN] NLP Features Demo")
    print("=" * 50)
    
    try:
        from src.core.nlp_processor import NLPProcessor
        
        print("Initializing NLP processor...")
        nlp = NLPProcessor()
        
        print("✓ NLP processor initialized successfully!")
        print(f"   spaCy available: {nlp.get_module_status()['spacy_available']}")
        print(f"   QA pipeline available: {nlp.get_module_status()['qa_pipeline_available']}")
        print(f"   Sentiment analyzer available: {nlp.get_module_status()['sentiment_analyzer_available']}")
        
        # Test intent classification
        test_queries = [
            "Hello, how are you?",
            "What is machine learning?",
            "Help me read this document",
            "Show me the settings"
        ]
        
        print("\n[TARGET] Testing intent classification:")
        for query in test_queries:
            result = nlp.process_query(query)
            intent = result.get('intent', 'unknown')
            print(f"   '{query}' → {intent}")
        
    except Exception as e:
        print(f"✗ NLP demo failed: {e}")

def demo_configuration():
    """Demonstrate configuration system"""
    print("\n[GEAR]  Configuration Demo")
    print("=" * 50)
    
    try:
        from src.core.config import get_config
        
        print("Loading configuration...")
        config = get_config()
        
        print("✓ Configuration loaded successfully!")
        print(f"   Speech rate: {config.speech.speech_rate}")
        print(f"   Speech volume: {config.speech.speech_volume}")
        print(f"   Camera index: {config.vision.camera_index}")
        print(f"   Response timeout: {config.system.response_timeout}s")
        print(f"   Audio feedback: {config.accessibility.audio_feedback}")
        
        # Validate configuration
        issues = config.validate_config()
        if issues:
            print(f"[WARNING]  Configuration issues: {len(issues)}")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"   - {issue}")
        else:
            print("✓ Configuration is valid!")
        
    except Exception as e:
        print(f"✗ Configuration demo failed: {e}")

def demo_chatbot():
    """Demonstrate chatbot integration"""
    print("\n[ROBOT] Chatbot Integration Demo")
    print("=" * 50)
    
    try:
        from src.core.chatbot import SenseEdChatbot
        
        print("Initializing chatbot...")
        chatbot = SenseEdChatbot()
        
        print("✓ Chatbot initialized successfully!")
        
        # Get status
        status = chatbot.get_status()
        print(f"   Session active: {status['session_active']}")
        print(f"   Conversation count: {status['conversation_count']}")
        print(f"   Error count: {status['error_count']}")
        
        # Test processing different input types
        print("\n[REFRESH] Testing input processing:")
        
        # Test speech input
        speech_input = {
            'type': 'speech',
            'content': 'Hello, I need help with learning',
            'timestamp': '2024-01-01T00:00:00'
        }
        response = chatbot.process_input(speech_input)
        print(f"   Speech input: {response.get('success', False)}")
        
        # Test gesture input
        gesture_input = {
            'type': 'gesture',
            'content': [{'gesture': 'Thumbs Up', 'hand': 'Right'}],
            'timestamp': '2024-01-01T00:00:00'
        }
        response = chatbot.process_input(gesture_input)
        print(f"   Gesture input: {response.get('success', False)}")
        
        # Test text input
        text_input = {
            'type': 'text',
            'content': 'This is a test document for processing.',
            'timestamp': '2024-01-01T00:00:00'
        }
        response = chatbot.process_input(text_input)
        print(f"   Text input: {response.get('success', False)}")
        
    except Exception as e:
        print(f"✗ Chatbot demo failed: {e}")

def main():
    """Run the complete demo"""
    print_demo_banner()
    
    print("Starting SenseEd demonstration...")
    print("This demo will test all major components of the system.\n")
    
    # Run all demos
    demo_speech_features()
    time.sleep(1)
    
    demo_vision_features()
    time.sleep(1)
    
    demo_gesture_features()
    time.sleep(1)
    
    demo_text_features()
    time.sleep(1)
    
    demo_nlp_features()
    time.sleep(1)
    
    demo_configuration()
    time.sleep(1)
    
    demo_chatbot()
    
    print("\n" + "=" * 60)
    print("[CELEBRATION] Demo completed!")
    print("\nTo start the full application, run:")
    print("   python main.py")
    print("\nFor help, run:")
    print("   python main.py --help")
    print("\nFor GUI mode, run:")
    print("   python main.py --gui")
    print("=" * 60)

if __name__ == "__main__":
    main()
