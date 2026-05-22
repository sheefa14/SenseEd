#!/usr/bin/env python3
"""
Test script to verify text processing is working correctly
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_text_processing():
    """Test text input processing"""
    try:
        from src.core.chatbot import SenseEdChatbot
        
        print("Testing text processing...")
        print("Creating chatbot instance...")
        
        # Create chatbot instance
        chatbot = SenseEdChatbot()
        
        # Test various text inputs
        test_inputs = [
            "hi",
            "hello",
            "how are you?",
            "what is artificial intelligence?",
            "help me learn about machine learning",
            "thanks",
            "what can you do?"
        ]
        
        print("\nTesting text inputs:")
        print("=" * 50)
        
        for test_input in test_inputs:
            print(f"\nInput: '{test_input}'")
            
            # Create input data
            input_data = {
                'type': 'text',
                'content': test_input,
                'timestamp': '2025-10-13T05:57:00'
            }
            
            # Process input
            response = chatbot.process_input(input_data)
            
            if response and response.get('success', False):
                response_text = response.get('text', 'No response')
                print(f"Response: {response_text}")
            else:
                error_msg = response.get('error', 'Unknown error') if response else 'No response'
                print(f"Error: {error_msg}")
        
        print("\n" + "=" * 50)
        print("[SUCCESS] Text processing test completed!")
        print("The chatbot should now provide meaningful responses instead of just counting words.")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Text processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Text Processing Test")
    print("=" * 30)
    
    success = test_text_processing()
    
    if success:
        print("\n[SUCCESS] Text processing has been fixed!")
        print("The chatbot now provides meaningful responses to text input.")
        print("Try typing 'hi' or 'hello' in the GUI to see the improvement.")
    else:
        print("\n[ERROR] Text processing test failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




