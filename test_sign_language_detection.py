#!/usr/bin/env python3
"""
Test Sign Language Detection
Quick test to verify sign language phrase detection is working
"""

import cv2
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.gesture_module import GestureModule

def test_sign_language_detection():
    """Test sign language detection with webcam"""
    print("Sign Language Detection Test")
    print("=" * 40)
    
    # Initialize gesture module
    gesture_module = GestureModule()
    
    # Check if sign language is available
    status = gesture_module.get_sign_language_status()
    print(f"Sign Language Available: {status.get('available', False)}")
    
    if not status.get('available', False):
        print("Sign language module not available!")
        return
    
    # Get available phrases
    phrases = gesture_module.get_sign_language_phrases()
    print(f"Available phrases: {len(phrases)}")
    print("Sample phrases:", phrases[:10])
    print()
    
    # Start webcam test
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    
    print("Starting sign language detection test...")
    print("Press 'q' to quit")
    print("Try signing phrases from the dataset!")
    print()
    
    frame_count = 0
    last_phrase = ""
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)  # Mirror the frame
        frame_count += 1
        
        # Test sign language detection every 5 frames
        if frame_count % 5 == 0:
            result = gesture_module.detect_sign_language(frame)
            
            if result:
                phrase = result.get('phrase', '')
                confidence = result.get('confidence', 0.0)
                status = result.get('status', '')
                
                # Only print when there's a change or high confidence
                if phrase and (phrase != last_phrase or confidence > 0.5):
                    print(f"[{status}] Phrase: '{phrase}' | Confidence: {confidence:.3f}")
                    last_phrase = phrase
                
                # Draw result on frame
                if phrase:
                    text = f"{phrase} ({confidence:.2f})"
                    cv2.putText(frame, text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.putText(frame, f"Status: {status}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Show instructions
        cv2.putText(frame, "Sign Language Detection Test", (10, frame.shape[0] - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Sign Language Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    gesture_module.close()
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_sign_language_detection()