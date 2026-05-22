import cv2
import numpy as np
import math
from typing import List, Dict, Any, Tuple

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not available - using OpenCV-based gesture recognition")

# Import the new sign language module
try:
    from .sign_language_module import SignLanguageModule
    SIGN_LANGUAGE_AVAILABLE = True
except ImportError:
    SIGN_LANGUAGE_AVAILABLE = False
    print("Sign language module not available")

class GestureModule:
    def __init__(self):
        self.mediapipe_available = MEDIAPIPE_AVAILABLE
        self.sign_language_available = SIGN_LANGUAGE_AVAILABLE
        
        if MEDIAPIPE_AVAILABLE:
            # Use MediaPipe if available
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            print("MediaPipe gesture recognition initialized")
        else:
            # Use OpenCV-based gesture recognition
            self.hands = None
            self.mp_drawing = None
            self.setup_opencv_gesture_recognition()
        
        # Initialize sign language recognition if available
        if SIGN_LANGUAGE_AVAILABLE:
            try:
                self.sign_language_module = SignLanguageModule()
                print("Sign language recognition initialized")
            except Exception as e:
                print(f"Failed to initialize sign language module: {e}")
                self.sign_language_module = None
                self.sign_language_available = False
        else:
            self.sign_language_module = None
        
        # Common gesture definitions
        self.gesture_names = {
            'open_hand': 'Open Hand',
            'fist': 'Fist', 
            'thumbs_up': 'Thumbs Up',
            'thumbs_down': 'Thumbs Down',
            'peace': 'Peace',
            'pointing': 'Pointing',
            'ok': 'OK',
            'rock': 'Rock On',
            'three': 'Three',
            'four': 'Four'
        }
    
    def setup_opencv_gesture_recognition(self):
        """Setup OpenCV-based gesture recognition"""
        # Initialize background subtractor for hand detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        
        # Skin color range in HSV
        self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Gesture recognition parameters
        self.min_contour_area = 1000
        self.max_contour_area = 50000
        
        # Convex hull and defects for finger counting
        self.min_defect_area = 1000
        
        print("OpenCV-based gesture recognition initialized")
    
    def detect_gesture(self, frame):
        """Detect hand gestures from a video frame"""
        if self.mediapipe_available:
            return self._detect_gesture_mediapipe(frame)
        else:
            return self._detect_gesture_opencv(frame)
    
    def _detect_gesture_mediapipe(self, frame):
        """Detect gestures using MediaPipe"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            gestures = []

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    # Draw landmarks on the frame
                    if self.mp_drawing:
                        self.mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS
                        )

                    # Extract landmark positions
                    landmarks = [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
                    
                    # Get hand label (Left or Right)
                    hand_label = handedness.classification[0].label

                    # Classify the gesture
                    gesture = self.classify_gesture_mediapipe(landmarks, hand_label)
                    gestures.append({'hand': hand_label, 'gesture': gesture})

            return gestures
            
        except Exception as e:
            print(f"Error in MediaPipe gesture detection: {e}")
            return []
    
    def _detect_gesture_opencv(self, frame):
        """Detect gestures using OpenCV"""
        try:
            # Apply background subtraction
            fg_mask = self.bg_subtractor.apply(frame)
            
            # Apply skin color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            skin_mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
            
            # Combine masks
            combined_mask = cv2.bitwise_and(fg_mask, skin_mask)
            
            # Apply morphological operations
            kernel = np.ones((5, 5), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            gestures = []
            if contours:
                # Find the largest contour (likely the hand)
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                
                if self.min_contour_area < area < self.max_contour_area:
                    # Analyze the contour to determine gesture
                    gesture = self._analyze_contour_gesture(largest_contour, frame)
                    if gesture:
                        gestures.append({'hand': 'Unknown', 'gesture': gesture})
            
            return gestures
            
        except Exception as e:
            print(f"Error in OpenCV gesture detection: {e}")
            return []
    
    def _analyze_contour_gesture(self, contour, frame):
        """Analyze contour to determine gesture type"""
        try:
            # Approximate the contour
            epsilon = 0.0005 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Find convex hull
            hull = cv2.convexHull(contour, returnPoints=False)
            
            # Find convexity defects
            defects = cv2.convexityDefects(contour, hull)
            
            # Count fingers based on convexity defects
            finger_count = 0
            if defects is not None:
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(contour[s][0])
                    end = tuple(contour[e][0])
                    far = tuple(contour[f][0])
                    
                    # Calculate the angle between the lines
                    a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                    b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                    c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                    
                    # Calculate angle using cosine rule
                    angle = math.acos((b**2 + c**2 - a**2) / (2*b*c))
                    
                    # If angle is less than 90 degrees, it's a finger
                    if angle <= math.pi/2 and d > self.min_defect_area:
                        finger_count += 1
            
            # Classify gesture based on finger count
            if finger_count == 0:
                return "Fist"
            elif finger_count == 1:
                return "Pointing"
            elif finger_count == 2:
                return "Peace"
            elif finger_count == 3:
                return "Three"
            elif finger_count == 4:
                return "Four"
            elif finger_count >= 5:
                return "Open Hand"
            else:
                return "Unknown"
                
        except Exception as e:
            print(f"Error analyzing contour: {e}")
            return "Unknown"
    
    def classify_gesture_mediapipe(self, landmarks, hand_label):
        """Classify gesture based on MediaPipe landmarks"""
        # Landmark indices
        THUMB_TIP = 4
        INDEX_TIP = 8
        MIDDLE_TIP = 12
        RING_TIP = 16
        PINKY_TIP = 20
        WRIST = 0
        
        # Check which fingers are extended
        finger_tips = [THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]
        
        fingers_extended = [
            self.is_finger_extended(landmarks, tip, hand_label) 
            for tip in finger_tips
        ]
        
        thumb, index, middle, ring, pinky = fingers_extended
        
        # Calculate distances for specific gestures
        thumb_index_dist = self.calculate_distance(
            landmarks[THUMB_TIP], 
            landmarks[INDEX_TIP]
        )
        
        # Gesture classification
        if all(fingers_extended):
            return "Open Hand"
        elif not any(fingers_extended):
            return "Fist"
        elif thumb and not any([index, middle, ring, pinky]):
            if landmarks[THUMB_TIP][1] < landmarks[WRIST][1]:
                return "Thumbs Up"
            else:
                return "Thumbs Down"
        elif index and middle and not ring and not pinky:
            index_middle_dist = self.calculate_distance(
                landmarks[INDEX_TIP],
                landmarks[MIDDLE_TIP]
            )
            if index_middle_dist > 0.05:
                return "Peace"
            else:
                return "Two Fingers"
        elif index and not any([middle, ring, pinky]):
            return "Pointing"
        elif thumb and index and not middle and not ring and not pinky:
            if thumb_index_dist < 0.05:
                return "Pinch"
        elif thumb and index and middle and ring and pinky:
            if thumb_index_dist < 0.05:
                return "OK"
        elif index and pinky and not middle and not ring:
            return "Rock On"
        elif index and middle and ring and not pinky:
            return "Three"
        elif not thumb and index and middle and ring and pinky:
            return "Four"
        
        return "Unknown"
    
    def is_finger_extended(self, landmarks, tip_idx, hand_label):
        """Check if a finger is extended"""
        pip_idx = tip_idx - 2
        
        # Special handling for thumb
        if tip_idx == 4:  # THUMB_TIP
            ip_idx = 3
            if hand_label == "Right":
                return landmarks[tip_idx][0] > landmarks[ip_idx][0]
            else:
                return landmarks[tip_idx][0] < landmarks[ip_idx][0]
        else:
            return landmarks[tip_idx][1] < landmarks[pip_idx][1]
    
    def calculate_distance(self, p1, p2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)
    
    def get_gesture_info(self, frame):
        """Get gesture information with frame drawing"""
        gestures = self.detect_gesture(frame)
        
        # Draw gesture labels on frame
        y_offset = 30
        for i, gesture_data in enumerate(gestures):
            hand = gesture_data['hand']
            gesture = gesture_data['gesture']
            text = f"{hand}: {gesture}"
            cv2.putText(frame, text, (10, y_offset + i * 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return gestures
    
    def detect_sign_language(self, frame):
        """
        Detect sign language phrases using the dataset
        
        Args:
            frame: Input video frame
            
        Returns:
            Dictionary with sign language recognition results
        """
        if not self.sign_language_available or not self.sign_language_module:
            return {
                'phrase': '',
                'confidence': 0.0,
                'status': 'unavailable',
                'error': 'Sign language module not available'
            }
        
        try:
            # Process frame for sign language recognition
            result = self.sign_language_module.process_frame(frame)
            
            # Draw recognition information on frame
            frame = self.sign_language_module.draw_recognition_info(frame, result)
            
            return result
            
        except Exception as e:
            return {
                'phrase': '',
                'confidence': 0.0,
                'status': 'error',
                'error': str(e)
            }
    
    def get_sign_language_phrases(self):
        """Get list of available sign language phrases"""
        if self.sign_language_available and self.sign_language_module:
            return self.sign_language_module.get_available_phrases()
        return []
    
    def get_sign_language_status(self):
        """Get sign language module status"""
        if self.sign_language_available and self.sign_language_module:
            return self.sign_language_module.get_module_status()
        return {
            'available': False,
            'error': 'Sign language module not available'
        }
    
    def get_gesture_status(self):
        """Get the status of gesture recognition"""
        if self.mediapipe_available:
            return {
                'available': True,
                'method': 'MediaPipe',
                'gestures': list(self.gesture_names.keys())
            }
        else:
            return {
                'available': True,
                'method': 'OpenCV',
                'gestures': ['fist', 'pointing', 'peace', 'three', 'four', 'open_hand']
            }
    
    def close(self):
        """Release resources"""
        if self.hands:
            self.hands.close()


# Example usage
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    gesture_detector = GestureModule()
    
    print("Gesture Recognition Started. Press 'q' to quit.")
    print("Supported gestures: Open Hand, Fist, Thumbs Up/Down, Peace,")
    print("Pointing, Pinch, OK, Rock On, Three, Four")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)  # Mirror the frame
        gestures = gesture_detector.get_gesture_info(frame)
        
        cv2.imshow('Gesture Recognition', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    gesture_detector.close()