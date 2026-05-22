# speech_module.py
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
import os
import threading
import time
import platform
from typing import Optional, Dict, Any
import logging

class SpeechModule:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize speech module with enhanced accessibility features
        
        Args:
            config: Configuration dictionary with speech settings
        """
        self.config = config or {}
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.is_speaking = False
        self.speech_queue = []
        self.setup_logging()
        self.initialize_components()
    
    def setup_logging(self):
        """Setup logging for speech module"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def initialize_components(self):
        """Initialize microphone and TTS engine with enhanced error handling"""
        try:
            # Initialize microphone with better configuration
            self.microphone = sr.Microphone()
            
            # Test microphone availability
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            self.logger.info("Microphone initialized and tested successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize microphone: {e}")
            self.microphone = None
            # Try alternative microphone initialization
            try:
                self.microphone = sr.Microphone(device_index=0)
                self.logger.info("Alternative microphone initialization successful")
            except Exception as e2:
                self.logger.error(f"Alternative microphone initialization failed: {e2}")
                self.microphone = None
        
        try:
            # Initialize TTS engine
            self.tts_engine = pyttsx3.init()
            self.configure_tts()
            self.logger.info("TTS engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.tts_engine = None
    
    def configure_tts(self):
        """Configure text-to-speech settings for accessibility"""
        if not self.tts_engine:
            return
            
        try:
            # Get user preferences from config
            rate = self.config.get('speech_rate', 150)
            volume = self.config.get('speech_volume', 0.9)
            voice_id = self.config.get('voice_id', None)
            
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)
            
            # Set voice if specified
            if voice_id:
                voices = self.tts_engine.getProperty('voices')
                if voices and voice_id < len(voices):
                    self.tts_engine.setProperty('voice', voices[voice_id].id)
                else:
                    # Use first available voice
                    if voices:
                        self.tts_engine.setProperty('voice', voices[0].id)
            
            self.logger.info(f"TTS configured - Rate: {rate}, Volume: {volume}")
        except Exception as e:
            self.logger.error(f"Failed to configure TTS: {e}")
    
    def listen_to_speech(self, timeout: int = 5, phrase_time_limit: int = 5) -> Optional[str]:
        """
        Convert speech to text with enhanced error handling and better detection
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum time to listen for a phrase
            
        Returns:
            Recognized text or None if failed
        """
        if not self.microphone:
            self.logger.error("Microphone not available")
            return None
        
        try:
            with self.microphone as source:
                # Adjust for ambient noise with shorter duration for better responsiveness
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.logger.info("Listening for speech...")
                
                # Set energy threshold for better detection
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                
                # Listen for audio with improved parameters
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Recognize speech using multiple engines for better accuracy
            text = self.recognize_with_fallback(audio)
            if text:
                self.logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            self.logger.info("No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio - try speaking more clearly")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in speech recognition: {e}")
            return None
    
    def recognize_with_fallback(self, audio) -> Optional[str]:
        """Try multiple speech recognition engines for better accuracy"""
        engines = [
            ('google', lambda: self.recognizer.recognize_google(audio)),
            ('bing', lambda: self.recognizer.recognize_bing(audio)),
            ('sphinx', lambda: self.recognizer.recognize_sphinx(audio))
        ]
        
        for engine_name, recognize_func in engines:
            try:
                text = recognize_func()
                if text and len(text.strip()) > 0:
                    return text
            except Exception as e:
                self.logger.debug(f"{engine_name} recognition failed: {e}")
                continue
        
        return None
    
    def speak_text(self, text: str, use_gtts: bool = True, interrupt: bool = False) -> bool:
        """
        Convert text to speech with enhanced accessibility features
        
        Args:
            text: Text to speak
            use_gtts: Whether to use Google TTS (better quality) or system TTS
            interrupt: Whether to interrupt current speech
            
        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            return False
        
        try:
            if interrupt and self.is_speaking:
                self.stop_speaking()
            
            # Reset speaking state to allow multiple speech calls
            self.is_speaking = False
            
            if use_gtts:
                return self._speak_with_gtts(text)
            else:
                return self._speak_with_system_tts(text)
                
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}")
            self.is_speaking = False  # Reset state on error
            return False
    
    def _speak_with_gtts(self, text: str) -> bool:
        """Speak text using Google TTS"""
        try:
            # Create TTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            temp_file = "temp_audio.mp3"
            tts.save(temp_file)
            
            # Play audio based on platform
            if platform.system() == "Windows":
                os.system(f"start {temp_file}")
            elif platform.system() == "Darwin":  # macOS
                os.system(f"afplay {temp_file}")
            else:  # Linux
                os.system(f"mpg123 {temp_file}")
            
            # Clean up temporary file after a longer delay to ensure playback is complete
            threading.Timer(10.0, lambda: self._cleanup_temp_file(temp_file)).start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"GTTS error: {e}")
            return False
    
    def _speak_with_system_tts(self, text: str) -> bool:
        """Speak text using system TTS engine"""
        if not self.tts_engine:
            return False
        
        try:
            self.is_speaking = True
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.is_speaking = False
            return True
            
        except Exception as e:
            self.logger.error(f"System TTS error: {e}")
            self.is_speaking = False
            return False
        finally:
            # Ensure speaking state is always reset
            self.is_speaking = False
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.tts_engine and self.is_speaking:
            try:
                self.tts_engine.stop()
                self.is_speaking = False
            except Exception as e:
                self.logger.error(f"Error stopping speech: {e}")
    
    def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary audio file"""
        try:
            if os.path.exists(file_path):
                # Try to remove the file, with retry logic for Windows
                import time
                for attempt in range(3):
                    try:
                        os.remove(file_path)
                        break
                    except PermissionError:
                        if attempt < 2:  # Don't wait on last attempt
                            time.sleep(1)
                        else:
                            # On Windows, sometimes the file is still in use
                            # Try to remove it later
                            threading.Timer(5.0, lambda: self._cleanup_temp_file(file_path)).start()
                            break
        except Exception as e:
            self.logger.error(f"Error cleaning up temp file: {e}")
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        if not self.tts_engine:
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            return [{'id': i, 'name': voice.name, 'languages': voice.languages} 
                   for i, voice in enumerate(voices)]
        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
            return []
    
    def set_voice(self, voice_id: int) -> bool:
        """Set TTS voice by ID"""
        if not self.tts_engine:
            return False
        
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices and 0 <= voice_id < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_id].id)
                return True
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
        
        return False
    
    def speak_async(self, text: str, use_gtts: bool = True):
        """Speak text asynchronously"""
        thread = threading.Thread(target=self.speak_text, args=(text, use_gtts))
        thread.daemon = True
        thread.start()
    
    def listen_continuously(self, callback_func, stop_event=None):
        """
        Continuously listen for speech and call callback function
        
        Args:
            callback_func: Function to call with recognized text
            stop_event: Event to stop listening
        """
        if not self.microphone:
            self.logger.error("Microphone not available")
            return
        
        def listen_loop():
            while stop_event is None or not stop_event.is_set():
                try:
                    text = self.listen_to_speech(timeout=1, phrase_time_limit=3)
                    if text:
                        callback_func(text)
                except Exception as e:
                    self.logger.error(f"Error in continuous listening: {e}")
                    time.sleep(0.1)
        
        thread = threading.Thread(target=listen_loop)
        thread.daemon = True
        thread.start()
        return thread
    
    def speak_response(self, text: str, use_gtts: bool = True) -> bool:
        """
        Enhanced speak function for AI responses
        
        Args:
            text: Response text to speak
            use_gtts: Whether to use Google TTS
            
        Returns:
            True if successful
        """
        if not text or not text.strip():
            return False
        
        # Clean up the text for better speech
        cleaned_text = self._clean_text_for_speech(text)
        
        # Add a brief pause before speaking
        time.sleep(0.2)
        
        return self.speak_text(cleaned_text, use_gtts=use_gtts, interrupt=True)
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech output"""
        # Remove markdown formatting
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Add pauses for better speech
        text = text.replace('.', '. ')
        text = text.replace('!', '! ')
        text = text.replace('?', '? ')
        
        return text
    
    def get_speech_status(self) -> Dict[str, Any]:
        """Get current speech module status"""
        return {
            'microphone_available': self.microphone is not None,
            'tts_available': self.tts_engine is not None,
            'is_speaking': self.is_speaking,
            'available_voices': len(self.get_available_voices())
        }