# test_vision_module.py
import unittest
import sys
import os
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.vision_module import VisionModule

class TestVisionModule(unittest.TestCase):
    """Test cases for VisionModule"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'camera_index': 0,
            'camera_width': 1280,
            'camera_height': 720,
            'confidence_threshold': 0.5,
            'yolo_model_path': 'yolov8n.pt'
        }
        
        # Mock external dependencies
        with patch('modules.vision_module.cv2.VideoCapture'), \
             patch('modules.vision_module.YOLO'), \
             patch('modules.vision_module.BlipProcessor'), \
             patch('modules.vision_module.BlipForConditionalGeneration'):
            self.vision_module = VisionModule(self.config)
    
    def test_initialization(self):
        """Test VisionModule initialization"""
        self.assertIsNotNone(self.vision_module)
        self.assertEqual(self.vision_module.config, self.config)
    
    @patch('modules.vision_module.cv2.VideoCapture')
    def test_initialize_camera_success(self, mock_cv2):
        """Test successful camera initialization"""
        mock_camera = Mock()
        mock_camera.isOpened.return_value = True
        mock_cv2.return_value = mock_camera
        
        result = self.vision_module.initialize_camera(0)
        self.assertTrue(result)
        mock_cv2.assert_called_once_with(0)
    
    @patch('modules.vision_module.cv2.VideoCapture')
    def test_initialize_camera_failure(self, mock_cv2):
        """Test camera initialization failure"""
        mock_camera = Mock()
        mock_camera.isOpened.return_value = False
        mock_cv2.return_value = mock_camera
        
        result = self.vision_module.initialize_camera(0)
        self.assertFalse(result)
    
    @patch('modules.vision_module.cv2.VideoCapture')
    def test_capture_image_success(self, mock_cv2):
        """Test successful image capture"""
        # Mock camera
        mock_camera = Mock()
        mock_camera.isOpened.return_value = True
        mock_camera.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2.return_value = mock_camera
        
        self.vision_module.camera = mock_camera
        
        result = self.vision_module.capture_image()
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (480, 640, 3))
    
    @patch('modules.vision_module.cv2.VideoCapture')
    def test_capture_image_failure(self, mock_cv2):
        """Test image capture failure"""
        # Mock camera
        mock_camera = Mock()
        mock_camera.isOpened.return_value = False
        mock_cv2.return_value = mock_camera
        
        self.vision_module.camera = mock_camera
        
        result = self.vision_module.capture_image()
        self.assertIsNone(result)
    
    @patch('modules.vision_module.pytesseract.image_to_string')
    def test_extract_text_from_image_success(self, mock_tesseract):
        """Test successful OCR text extraction"""
        mock_tesseract.return_value = "Hello World"
        
        # Create test image
        test_image = Image.new('RGB', (100, 100), color='white')
        
        result = self.vision_module.extract_text_from_image(test_image)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['text'], "Hello World")
        self.assertEqual(result['language'], 'eng')
    
    @patch('modules.vision_module.pytesseract.image_to_string')
    def test_extract_text_from_image_failure(self, mock_tesseract):
        """Test OCR text extraction failure"""
        mock_tesseract.side_effect = Exception("OCR failed")
        
        # Create test image
        test_image = Image.new('RGB', (100, 100), color='white')
        
        result = self.vision_module.extract_text_from_image(test_image)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['text'], "")
        self.assertIn('error', result)
    
    def test_extract_text_from_image_file_path(self):
        """Test OCR from file path"""
        with patch('modules.vision_module.Image.open') as mock_open, \
             patch('modules.vision_module.pytesseract.image_to_string') as mock_tesseract:
            
            mock_image = Mock()
            mock_open.return_value = mock_image
            mock_tesseract.return_value = "File text"
            
            result = self.vision_module.extract_text_from_image("test.jpg")
            
            self.assertTrue(result['success'])
            self.assertEqual(result['text'], "File text")
            mock_open.assert_called_once_with("test.jpg")
    
    def test_extract_text_from_image_numpy_array(self):
        """Test OCR from numpy array"""
        with patch('modules.vision_module.Image.fromarray') as mock_fromarray, \
             patch('modules.vision_module.pytesseract.image_to_string') as mock_tesseract:
            
            mock_image = Mock()
            mock_fromarray.return_value = mock_image
            mock_tesseract.return_value = "Array text"
            
            test_array = np.zeros((100, 100, 3), dtype=np.uint8)
            result = self.vision_module.extract_text_from_image(test_array)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['text'], "Array text")
    
    @patch('modules.vision_module.BlipProcessor')
    @patch('modules.vision_module.BlipForConditionalGeneration')
    def test_describe_scene_success(self, mock_blip_model, mock_blip_processor):
        """Test successful scene description"""
        # Mock BLIP components
        mock_processor_instance = Mock()
        mock_processor_instance.return_value = {'input_ids': Mock(), 'pixel_values': Mock()}
        mock_blip_processor.from_pretrained.return_value = mock_processor_instance
        
        mock_model_instance = Mock()
        mock_model_instance.generate.return_value = [[1, 2, 3, 4, 5]]
        mock_blip_model.from_pretrained.return_value = mock_model_instance
        
        mock_processor_instance.decode.return_value = "A beautiful landscape"
        
        # Set up vision module with mocked models
        self.vision_module.blip_processor = mock_processor_instance
        self.vision_module.blip_model = mock_model_instance
        
        # Create test image
        test_image = Image.new('RGB', (100, 100), color='blue')
        
        result = self.vision_module.describe_scene(test_image)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['description'], "A beautiful landscape")
        self.assertEqual(result['model'], 'BLIP')
    
    def test_describe_scene_no_model(self):
        """Test scene description without BLIP model"""
        # Create test image
        test_image = Image.new('RGB', (100, 100), color='blue')
        
        result = self.vision_module.describe_scene(test_image)
        
        self.assertFalse(result['success'])
        self.assertIn('BLIP model not loaded', result['description'])
    
    @patch('modules.vision_module.YOLO')
    def test_detect_objects_success(self, mock_yolo):
        """Test successful object detection"""
        # Mock YOLO model
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        # Mock detection results
        mock_box = Mock()
        mock_box.xyxy = [Mock()]
        mock_box.xyxy[0].cpu.return_value.numpy.return_value = [10, 10, 50, 50]
        mock_box.conf = [Mock()]
        mock_box.conf[0].cpu.return_value.numpy.return_value = 0.9
        mock_box.cls = [Mock()]
        mock_box.cls[0].cpu.return_value.numpy.return_value = 0
        
        mock_result = Mock()
        mock_result.boxes = mock_box
        mock_model.return_value = [mock_result]
        mock_model.names = {0: 'person'}
        
        self.vision_module.yolo_model = mock_model
        
        # Create test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = self.vision_module.detect_objects(test_image)
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['objects']), 1)
        self.assertEqual(result['objects'][0]['class'], 'person')
        self.assertEqual(result['objects'][0]['confidence'], 0.9)
    
    def test_detect_objects_no_model(self):
        """Test object detection without YOLO model"""
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = self.vision_module.detect_objects(test_image)
        
        self.assertFalse(result['success'])
        self.assertEqual(len(result['objects']), 0)
        self.assertIn('YOLO model not initialized', result['error'])
    
    def test_analyze_image_comprehensive(self):
        """Test comprehensive image analysis"""
        with patch.object(self.vision_module, 'extract_text_from_image') as mock_ocr, \
             patch.object(self.vision_module, 'detect_objects') as mock_objects, \
             patch.object(self.vision_module, 'describe_scene') as mock_scene:
            
            # Mock results
            mock_ocr.return_value = {'success': True, 'text': 'OCR text'}
            mock_objects.return_value = {'success': True, 'objects': []}
            mock_scene.return_value = {'success': True, 'description': 'Scene description'}
            
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            result = self.vision_module.analyze_image_comprehensive(test_image)
            
            self.assertTrue(result['success'])
            self.assertIn('ocr', result)
            self.assertIn('objects', result)
            self.assertIn('scene_description', result)
            self.assertIn('timestamp', result)
    
    def test_draw_detections(self):
        """Test drawing detections on image"""
        import cv2
        
        # Create test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Mock detections
        detections = {
            'success': True,
            'objects': [{
                'class': 'person',
                'confidence': 0.9,
                'bbox': [10, 10, 50, 50]
            }]
        }
        
        with patch('modules.vision_module.cv2.rectangle'), \
             patch('modules.vision_module.cv2.putText'), \
             patch('modules.vision_module.cv2.getTextSize'):
            
            result = self.vision_module.draw_detections(test_image, detections)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.shape, test_image.shape)
    
    def test_get_camera_status(self):
        """Test getting camera status"""
        status = self.vision_module.get_camera_status()
        
        self.assertIn('camera_available', status)
        self.assertIn('yolo_available', status)
        self.assertIn('blip_available', status)
    
    def test_release_camera(self):
        """Test camera release"""
        mock_camera = Mock()
        self.vision_module.camera = mock_camera
        
        self.vision_module.release_camera()
        
        mock_camera.release.assert_called_once()

if __name__ == '__main__':
    unittest.main()



