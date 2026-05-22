# test_chatbot.py
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import threading
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.chatbot import SenseEdChatbot

class TestSenseEdChatbot(unittest.TestCase):
    """Test cases for SenseEdChatbot"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock all external dependencies
        with patch('src.core.chatbot.SpeechModule') as mock_speech, \
             patch('src.core.chatbot.VisionModule') as mock_vision, \
             patch('src.core.chatbot.GestureModule') as mock_gesture, \
             patch('src.core.chatbot.TextModule') as mock_text, \
             patch('src.core.chatbot.NLPProcessor') as mock_nlp, \
             patch('src.core.chatbot.get_config') as mock_config:
            
            # Mock config
            mock_config_instance = Mock()
            mock_config_instance.get_section_config.return_value = {}
            mock_config_instance.system.log_level = 'INFO'
            mock_config_instance.system.response_timeout = 0.9
            mock_config_instance.vision.camera_index = 0
            mock_config_instance.accessibility.audio_feedback = True
            mock_config_instance.system.data_directory = 'data'
            mock_config.return_value = mock_config_instance
            
            # Mock modules
            self.mock_speech = mock_speech.return_value
            self.mock_vision = mock_vision.return_value
            self.mock_gesture = mock_gesture.return_value
            self.mock_text = mock_text.return_value
            self.mock_nlp = mock_nlp.return_value
            
            # Mock module methods
            self.mock_vision.initialize_camera.return_value = True
            self.mock_vision.get_camera_status.return_value = {'camera_available': True}
            self.mock_speech.get_speech_status.return_value = {'microphone_available': True}
            self.mock_text.get_module_status.return_value = {'spacy_available': True}
            self.mock_nlp.get_module_status.return_value = {'spacy_available': True}
            
            self.chatbot = SenseEdChatbot()
    
    def test_initialization(self):
        """Test chatbot initialization"""
        self.assertIsNotNone(self.chatbot)
        self.assertFalse(self.chatbot.session_active)
        self.assertEqual(len(self.chatbot.conversation_history), 0)
        self.assertEqual(self.chatbot.error_count, 0)
    
    def test_start_session(self):
        """Test starting a session"""
        with patch.object(self.chatbot, 'main_loop') as mock_main_loop:
            # Mock speech module speak_text method
            self.mock_speech.speak_text = Mock()
            
            # Start session in a thread to avoid blocking
            session_thread = threading.Thread(target=self.chatbot.start_session)
            session_thread.daemon = True
            session_thread.start()
            
            # Give it a moment to start
            time.sleep(0.1)
            
            # Check that session is active
            self.assertTrue(self.chatbot.session_active)
            
            # Stop the session
            self.chatbot.session_active = False
            session_thread.join(timeout=1)
    
    def test_process_speech_input(self):
        """Test processing speech input"""
        input_data = {
            'type': 'speech',
            'content': 'Hello, how are you?',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        # Mock NLP processing
        self.mock_nlp.process_query.return_value = {
            'intent': 'greeting',
            'entities': [],
            'tokens': ['Hello', ',', 'how', 'are', 'you', '?']
        }
        
        response = self.chatbot._process_speech_input(input_data, {})
        
        self.assertIn('text', response)
        self.assertTrue(response['success'])
        self.mock_nlp.process_query.assert_called_once_with('Hello, how are you?')
    
    def test_process_gesture_input(self):
        """Test processing gesture input"""
        input_data = {
            'type': 'gesture',
            'content': [{'gesture': 'Thumbs Up', 'hand': 'Right'}],
            'timestamp': '2024-01-01T00:00:00'
        }
        
        response = self.chatbot._process_gesture_input(input_data, {})
        
        self.assertIn('text', response)
        self.assertIn('action', response)
        self.assertEqual(response['action'], 'positive_feedback')
        self.assertIn('Great!', response['text'])
    
    def test_process_text_input(self):
        """Test processing text input"""
        input_data = {
            'type': 'text',
            'content': 'This is a test document with some content.',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        # Mock text processing
        self.mock_text.process_text.return_value = {
            'success': True,
            'operations': {
                'summary': {'summary': 'Test document summary'}
            }
        }
        
        response = self.chatbot._process_text_input(input_data, {})
        
        self.assertIn('text', response)
        self.assertTrue(response['success'])
        self.assertIn('summary', response['text'])
    
    def test_process_image_input(self):
        """Test processing image input"""
        import numpy as np
        
        input_data = {
            'type': 'image',
            'content': np.zeros((100, 100, 3), dtype=np.uint8),
            'timestamp': '2024-01-01T00:00:00'
        }
        
        # Mock vision analysis
        self.mock_vision.analyze_image_comprehensive.return_value = {
            'success': True,
            'ocr': {'text': 'Image text'},
            'objects': {'objects': [{'class': 'person', 'confidence': 0.9}]},
            'scene_description': {'description': 'A person in the image'}
        }
        
        response = self.chatbot._process_image_input(input_data, {})
        
        self.assertIn('text', response)
        self.assertTrue(response['success'])
        self.assertIn('text', response['text'])
        self.assertIn('person', response['text'])
    
    def test_answer_question(self):
        """Test answering questions"""
        question = "What is artificial intelligence?"
        nlp_result = {
            'intent': 'question',
            'entities': [('artificial intelligence', 'CONCEPT')]
        }
        
        # Mock NLP answer_question method
        self.mock_nlp.answer_question.return_value = "AI is the simulation of human intelligence in machines."
        
        answer = self.chatbot._answer_question(question, nlp_result)
        
        self.assertIsInstance(answer, str)
        self.assertGreater(len(answer), 0)
    
    def test_execute_command(self):
        """Test executing commands"""
        command = "read this document"
        input_data = {'type': 'speech', 'content': command}
        response = {}
        
        result = self.chatbot._execute_command(command, input_data, response)
        
        self.assertIn('text', result)
        self.assertIn('action', result)
        self.assertEqual(result['action'], 'read_mode')
    
    def test_generate_greeting_response(self):
        """Test generating greeting responses"""
        response = self.chatbot._generate_greeting_response()
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        self.assertIn('SenseEd', response)
    
    def test_generate_educational_response(self):
        """Test generating educational responses"""
        query = "machine learning"
        response = self.chatbot._generate_educational_response(query)
        
        self.assertIsInstance(response, str)
        self.assertIn('learning', response)
        self.assertIn('machine learning', response)
    
    def test_generate_accessibility_response(self):
        """Test generating accessibility responses"""
        query = "help me read"
        response = self.chatbot._generate_accessibility_response(query)
        
        self.assertIsInstance(response, str)
        self.assertIn('accessible', response)
        self.assertIn('help', response)
    
    def test_get_help_message(self):
        """Test getting help message"""
        help_msg = self.chatbot._get_help_message()
        
        self.assertIsInstance(help_msg, str)
        self.assertIn('SenseEd', help_msg)
        self.assertIn('Speech', help_msg)
        self.assertIn('Gestures', help_msg)
        self.assertIn('Vision', help_msg)
    
    def test_get_relevant_context(self):
        """Test getting relevant context from conversation history"""
        # Add some conversation history
        self.chatbot.conversation_history = [
            {'type': 'user', 'content': 'Hello'},
            {'type': 'assistant', 'content': 'Hi there!'},
            {'type': 'user', 'content': 'How are you?'}
        ]
        
        context = self.chatbot._get_relevant_context("What did I say?")
        
        self.assertIn('Hello', context)
        self.assertIn('How are you?', context)
    
    def test_maintain_response_time_target(self):
        """Test response time monitoring"""
        # Test with good response time
        self.chatbot._maintain_response_time_target(0.5)
        self.assertEqual(len(self.chatbot.response_times), 1)
        
        # Test with slow response time
        self.chatbot._maintain_response_time_target(1.5)
        self.assertEqual(len(self.chatbot.response_times), 2)
    
    def test_deliver_response(self):
        """Test delivering responses"""
        response = {
            'text': 'Hello, how can I help?',
            'audio': True,
            'visual': None,
            'action': None
        }
        
        # Mock speech module
        self.mock_speech.speak_text = Mock()
        
        self.chatbot.deliver_response(response)
        
        # Check that speech was called
        self.mock_speech.speak_text.assert_called_once_with('Hello, how can I help?')
    
    def test_log_interaction(self):
        """Test logging interactions"""
        input_data = {'type': 'speech', 'content': 'Hello'}
        response = {'text': 'Hi there!'}
        processing_time = 0.5
        
        initial_count = len(self.chatbot.conversation_history)
        
        self.chatbot.log_interaction(input_data, response, processing_time)
        
        self.assertEqual(len(self.chatbot.conversation_history), initial_count + 1)
        
        # Check logged interaction
        logged_interaction = self.chatbot.conversation_history[-1]
        self.assertEqual(logged_interaction['input'], input_data)
        self.assertEqual(logged_interaction['response'], response)
        self.assertEqual(logged_interaction['processing_time'], processing_time)
    
    def test_handle_error(self):
        """Test error handling"""
        error = Exception("Test error")
        initial_error_count = self.chatbot.error_count
        
        # Mock speech module
        self.mock_speech.speak_text = Mock()
        
        self.chatbot.handle_error(error)
        
        self.assertEqual(self.chatbot.error_count, initial_error_count + 1)
        self.mock_speech.speak_text.assert_called()
    
    def test_end_session(self):
        """Test ending a session"""
        self.chatbot.session_active = True
        
        # Mock speech module and vision module
        self.mock_speech.speak_text = Mock()
        self.mock_vision.release_camera = Mock()
        
        with patch.object(self.chatbot, '_save_session_data') as mock_save:
            self.chatbot.end_session()
            
            self.assertFalse(self.chatbot.session_active)
            self.mock_vision.release_camera.assert_called_once()
            self.mock_speech.speak_text.assert_called()
            mock_save.assert_called_once()
    
    def test_get_status(self):
        """Test getting chatbot status"""
        status = self.chatbot.get_status()
        
        self.assertIn('session_active', status)
        self.assertIn('conversation_count', status)
        self.assertIn('average_response_time', status)
        self.assertIn('error_count', status)
        self.assertIn('modules', status)
        
        # Check modules status
        modules = status['modules']
        self.assertIn('speech', modules)
        self.assertIn('vision', modules)
        self.assertIn('text', modules)
        self.assertIn('nlp', modules)
    
    def test_process_input_unknown_type(self):
        """Test processing unknown input type"""
        input_data = {
            'type': 'unknown',
            'content': 'test',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        response = self.chatbot.process_input(input_data)
        
        self.assertFalse(response['success'])
        self.assertIn('not sure how to process', response['text'])
    
    def test_process_input_error(self):
        """Test processing input with error"""
        input_data = {
            'type': 'speech',
            'content': 'test',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        # Mock NLP to raise exception
        self.mock_nlp.process_query.side_effect = Exception("NLP error")
        
        response = self.chatbot.process_input(input_data)
        
        self.assertFalse(response['success'])
        self.assertIn('error', response)

if __name__ == '__main__':
    unittest.main()



