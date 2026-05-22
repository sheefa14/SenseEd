# vision_module.py
import cv2
import pytesseract
from PIL import Image
import numpy as np
import logging
from typing import Optional, Dict, List, Any, Tuple
import os
from ultralytics import YOLO
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import base64
import io

class VisionModule:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize vision module with OCR, object detection, and scene description
        
        Args:
            config: Configuration dictionary with vision settings
        """
        self.config = config or {}
        self.camera = None
        self.yolo_model = None
        self.blip_processor = None
        self.blip_model = None
        self.setup_logging()
        self.initialize_models()
        
    def setup_logging(self):
        """Setup logging for vision module"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def initialize_models(self):
        """Initialize AI models for object detection and scene description"""
        try:
            # Initialize YOLO for object detection
            model_path = self.config.get('yolo_model_path', 'yolov8n.pt')
            self.yolo_model = YOLO(model_path)
            self.logger.info("YOLO model initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize YOLO model: {e}")
            self.yolo_model = None
        
        try:
            # Initialize BLIP for image captioning
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.logger.info("BLIP model initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize BLIP model: {e}")
            self.blip_processor = None
            self.blip_model = None
    
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """
        Initialize webcam with error handling
        
        Args:
            camera_index: Index of the camera to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if self.camera.isOpened():
                # Set camera properties for better quality
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.camera.set(cv2.CAP_PROP_FPS, 30)
                self.logger.info(f"Camera {camera_index} initialized successfully")
                return True
            else:
                self.logger.error(f"Failed to open camera {camera_index}")
                return False
        except Exception as e:
            self.logger.error(f"Error initializing camera: {e}")
            return False
    
    def capture_image(self) -> Optional[np.ndarray]:
        """
        Capture image from camera with error handling
        
        Returns:
            Captured frame or None if failed
        """
        if not self.camera or not self.camera.isOpened():
            self.logger.error("Camera not initialized")
            return None
        
        try:
            ret, frame = self.camera.read()
            if ret:
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                return frame
            else:
                self.logger.warning("Failed to capture frame")
                return None
        except Exception as e:
            self.logger.error(f"Error capturing image: {e}")
            return None
    
    def extract_text_from_image(self, image_input, language: str = 'eng') -> Dict[str, Any]:
        """
        OCR to extract text from images with enhanced processing
        
        Args:
            image_input: Image path, PIL Image, or numpy array
            language: Language for OCR (default: English)
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Convert input to PIL Image
            if isinstance(image_input, str):
                # File path
                image = Image.open(image_input)
            elif isinstance(image_input, np.ndarray):
                # OpenCV frame
                image = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
            elif isinstance(image_input, Image.Image):
                # Already PIL Image
                image = image_input
            else:
                raise ValueError("Unsupported image input type")
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_ocr(image)
            
            # Extract text with different OCR configurations
            ocr_results = {}
            
            # Standard OCR
            try:
                text = pytesseract.image_to_string(processed_image, lang=language)
                ocr_results['standard'] = text.strip()
            except Exception as e:
                self.logger.warning(f"Standard OCR failed: {e}")
                ocr_results['standard'] = ""
            
            # OCR with confidence scores
            try:
                data = pytesseract.image_to_data(processed_image, lang=language, output_type=pytesseract.Output.DICT)
                ocr_results['detailed'] = data
            except Exception as e:
                self.logger.warning(f"Detailed OCR failed: {e}")
                ocr_results['detailed'] = {}
            
            # Get bounding boxes for text regions
            try:
                boxes = pytesseract.image_to_boxes(processed_image, lang=language)
                ocr_results['boxes'] = boxes
            except Exception as e:
                self.logger.warning(f"Box OCR failed: {e}")
                ocr_results['boxes'] = ""
            
            return {
                'text': ocr_results['standard'],
                'confidence_data': ocr_results['detailed'],
                'bounding_boxes': ocr_results['boxes'],
                'success': True,
                'language': language
            }
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return {
                'text': "",
                'confidence_data': {},
                'bounding_boxes': "",
                'success': False,
                'error': str(e)
            }
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy"""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Apply denoising
            img_array = cv2.fastNlMeansDenoising(img_array)
            
            # Apply thresholding
            _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Convert back to PIL Image
            return Image.fromarray(img_array)
            
        except Exception as e:
            self.logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def describe_scene(self, image_input) -> Dict[str, Any]:
        """
        Use AI to describe what's in the image
        
        Args:
            image_input: Image path, PIL Image, or numpy array
            
        Returns:
            Dictionary with scene description and metadata
        """
        if not self.blip_processor or not self.blip_model:
            return {
                'description': "Scene description not available - BLIP model not loaded",
                'success': False,
                'error': "BLIP model not initialized"
            }
        
        try:
            # Convert input to PIL Image
            if isinstance(image_input, str):
                image = Image.open(image_input)
            elif isinstance(image_input, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
            elif isinstance(image_input, Image.Image):
                image = image_input
            else:
                raise ValueError("Unsupported image input type")
            
            # Process image with BLIP
            inputs = self.blip_processor(image, return_tensors="pt")
            
            # Generate caption
            with torch.no_grad():
                out = self.blip_model.generate(**inputs, max_length=50, num_beams=5)
            
            # Decode caption
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            
            return {
                'description': caption,
                'success': True,
                'model': 'BLIP'
            }
            
        except Exception as e:
            self.logger.error(f"Scene description failed: {e}")
            return {
                'description': "Failed to describe scene",
                'success': False,
                'error': str(e)
            }
    
    def detect_objects(self, image_input) -> Dict[str, Any]:
        """
        Detect objects in the image using YOLO
        
        Args:
            image_input: Image path, PIL Image, or numpy array
            
        Returns:
            Dictionary with detected objects and metadata
        """
        if not self.yolo_model:
            return {
                'objects': [],
                'success': False,
                'error': "YOLO model not initialized"
            }
        
        try:
            # Convert input to appropriate format
            if isinstance(image_input, str):
                # File path - YOLO can handle this directly
                results = self.yolo_model(image_input)
            elif isinstance(image_input, np.ndarray):
                # OpenCV frame
                results = self.yolo_model(image_input)
            elif isinstance(image_input, Image.Image):
                # PIL Image
                results = self.yolo_model(image_input)
            else:
                raise ValueError("Unsupported image input type")
            
            # Process results
            objects = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get confidence and class
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.yolo_model.names[class_id]
                        
                        objects.append({
                            'class': class_name,
                            'confidence': float(confidence),
                            'bbox': [float(x1), float(y1), float(x2), float(y2)],
                            'class_id': class_id
                        })
            
            return {
                'objects': objects,
                'success': True,
                'model': 'YOLOv8',
                'total_objects': len(objects)
            }
            
        except Exception as e:
            self.logger.error(f"Object detection failed: {e}")
            return {
                'objects': [],
                'success': False,
                'error': str(e)
            }
    
    def analyze_image_comprehensive(self, image_input) -> Dict[str, Any]:
        """
        Perform comprehensive image analysis including OCR, object detection, and scene description
        
        Args:
            image_input: Image path, PIL Image, or numpy array
            
        Returns:
            Comprehensive analysis results
        """
        results = {
            'timestamp': self._get_timestamp(),
            'ocr': {},
            'objects': {},
            'scene_description': {},
            'success': False
        }
        
        try:
            # Perform OCR
            results['ocr'] = self.extract_text_from_image(image_input)
            
            # Detect objects
            results['objects'] = self.detect_objects(image_input)
            
            # Describe scene
            results['scene_description'] = self.describe_scene(image_input)
            
            # Determine overall success
            results['success'] = (
                results['ocr']['success'] or 
                results['objects']['success'] or 
                results['scene_description']['success']
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive image analysis failed: {e}")
            results['error'] = str(e)
            return results
    
    def draw_detections(self, image: np.ndarray, detections: Dict[str, Any]) -> np.ndarray:
        """
        Draw object detection results on image
        
        Args:
            image: Input image
            detections: Detection results from detect_objects
            
        Returns:
            Image with drawn detections
        """
        if not detections.get('success', False):
            return image
        
        result_image = image.copy()
        
        for obj in detections.get('objects', []):
            bbox = obj['bbox']
            class_name = obj['class']
            confidence = obj['confidence']
            
            # Draw bounding box
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(result_image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            cv2.putText(result_image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return result_image
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_camera_status(self) -> Dict[str, Any]:
        """Get camera status information"""
        return {
            'camera_available': self.camera is not None and self.camera.isOpened(),
            'yolo_available': self.yolo_model is not None,
            'blip_available': self.blip_processor is not None and self.blip_model is not None
        }
    
    def release_camera(self):
        """Release camera resources"""
        if self.camera:
            self.camera.release()
            self.logger.info("Camera released")
    
    def __del__(self):
        """Cleanup resources"""
        self.release_camera()