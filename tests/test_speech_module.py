# test_speech_module.py
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.speech_module import SpeechModule

class TestSpeechModule(unittest.TestCase):
    """Test cases for SpeechModule"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'speech_rate': 150,
            'speech_volume': 0.9,
            'voice_id': 0,
            'use_gtts': True
        }
        
        # Mock external dependencies
        with patch('modules.speech_module.sr.Microphone'), \
             patch('modules.speech_module.pyttsx3.init'), \
             patch('modules.speech_module.sr.Recognizer'):
            self.speech_module = SpeechModule(self.config)
    
    def test_initialization(self):
        """Test SpeechModule initialization"""
        self.assertIsNotNone(self.speech_module)
        self.assertEqual(self.speech_module.config, self.config)
    
    @patch('modules.speech_module.sr.Recognizer')
    def test_listen_to_speech_success(self, mock_recognizer):
        """Test successful speech recognition"""
        # Mock recognizer
        mock_recognizer_instance = Mock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_recognizer_instance.recognize_google.return_value = "Hello world"
        
        # Mock microphone context manager
        with patch('modules.speech_module.sr.Microphone') as mock_mic:
            mock_mic.return_value.__enter__.return_value = Mock()
            
            result = self.speech_module.listen_to_speech(timeout=5)
            self.assertEqual(result, "Hello world")
    
    @patch('modules.speech_module.sr.Recognizer')
    def test_listen_to_speech_failure(self, mock_recognizer):
        """Test speech recognition failure"""
        # Mock recognizer to raise exception
        mock_recognizer_instance = Mock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_recognizer_instance.recognize_google.side_effect = Exception("Recognition failed")
        
        with patch('modules.speech_module.sr.Microphone') as mock_mic:
            mock_mic.return_value.__enter__.return_value = Mock()
            
            result = self.speech_module.listen_to_speech(timeout=5)
            self.assertIsNone(result)
    
    @patch('modules.speech_module.gTTS')
    @patch('modules.speech_module.os.system')
    def test_speak_text_gtts(self, mock_os_system, mock_gtts):
        """Test text-to-speech with Google TTS"""
        # Mock gTTS
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance
        
        result = self.speech_module.speak_text("Hello world", use_gtts=True)
        self.assertTrue(result)
        mock_gtts.assert_called_once_with(text="Hello world", lang='en', slow=False)
        mock_tts_instance.save.assert_called_once()
    
    @patch('modules.speech_module.pyttsx3.init')
    def test_speak_text_system_tts(self, mock_pyttsx3):
        """Test text-to-speech with system TTS"""
        # Mock pyttsx3
        mock_engine = Mock()
        mock_pyttsx3.return_value = mock_engine
        
        # Create speech module with mocked engine
        speech_module = SpeechModule(self.config)
        speech_module.tts_engine = mock_engine
        
        result = speech_module.speak_text("Hello world", use_gtts=False)
        self.assertTrue(result)
        mock_engine.say.assert_called_once_with("Hello world")
        mock_engine.runAndWait.assert_called_once()
    
    def test_speak_text_empty(self):
        """Test speaking empty text"""
        result = self.speech_module.speak_text("")
        self.assertFalse(result)
        
        result = self.speech_module.speak_text(None)
        self.assertFalse(result)
    
    @patch('modules.speech_module.pyttsx3.init')
    def test_get_available_voices(self, mock_pyttsx3):
        """Test getting available voices"""
        # Mock voices
        mock_voice1 = Mock()
        mock_voice1.name = "Voice 1"
        mock_voice1.languages = ["en"]
        
        mock_voice2 = Mock()
        mock_voice2.name = "Voice 2"
        mock_voice2.languages = ["en", "es"]
        
        mock_engine = Mock()
        mock_engine.getProperty.return_value = [mock_voice1, mock_voice2]
        mock_pyttsx3.return_value = mock_engine
        
        speech_module = SpeechModule(self.config)
        speech_module.tts_engine = mock_engine
        
        voices = speech_module.get_available_voices()
        self.assertEqual(len(voices), 2)
        self.assertEqual(voices[0]['name'], "Voice 1")
        self.assertEqual(voices[1]['name'], "Voice 2")
    
    @patch('modules.speech_module.pyttsx3.init')
    def test_set_voice(self, mock_pyttsx3):
        """Test setting voice"""
        mock_engine = Mock()
        mock_voice = Mock()
        mock_voice.id = "voice_id"
        mock_engine.getProperty.return_value = [mock_voice]
        mock_pyttsx3.return_value = mock_engine
        
        speech_module = SpeechModule(self.config)
        speech_module.tts_engine = mock_engine
        
        result = speech_module.set_voice(0)
        self.assertTrue(result)
        mock_engine.setProperty.assert_called_with('voice', 'voice_id')
    
    def test_get_speech_status(self):
        """Test getting speech module status"""
        status = self.speech_module.get_speech_status()
        
        self.assertIn('microphone_available', status)
        self.assertIn('tts_available', status)
        self.assertIn('is_speaking', status)
        self.assertIn('available_voices', status)
    
    def test_recognize_with_fallback(self):
        """Test speech recognition with fallback engines"""
        # Mock audio data
        mock_audio = Mock()
        
        # Mock recognizer with different engines
        with patch('modules.speech_module.sr.Recognizer') as mock_recognizer:
            mock_recognizer_instance = Mock()
            mock_recognizer.return_value = mock_recognizer_instance
            
            # First engine fails, second succeeds
            mock_recognizer_instance.recognize_google.side_effect = Exception("Google failed")
            mock_recognizer_instance.recognize_bing.return_value = "Hello from Bing"
            
            result = self.speech_module.recognize_with_fallback(mock_audio)
            self.assertEqual(result, "Hello from Bing")

if __name__ == '__main__':
    unittest.main()



