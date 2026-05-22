# chatbot.py
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
import queue
import json
from pathlib import Path

# Import modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.speech_module import SpeechModule
from modules.vision_module import VisionModule
from modules.gesture_module import GestureModule
from modules.text_module import TextModule
from src.core.nlp_processor import NLPProcessor
from src.core.config import get_config

class SenseEdChatbot:
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize SenseEd chatbot with enhanced multimodal capabilities
        
        Args:
            config_file: Path to configuration file
        """
        self.config = get_config()
        self.setup_logging()
        
        # Initialize modules
        self.speech_module = SpeechModule(self.config.get_section_config('speech'))
        self.vision_module = VisionModule(self.config.get_section_config('vision'))
        self.gesture_module = GestureModule()
        self.text_module = TextModule(self.config.get_section_config('text'))
        self.nlp_processor = NLPProcessor(self.config.get_section_config('nlp'))
        
        # State management
        self.conversation_history = []
        self.active_mode = "multimodal"
        self.session_active = False
        self.input_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Performance tracking
        self.response_times = []
        self.error_count = 0
        
        # Learning features
        self.user_preferences = {}
        self.learning_progress = {}
        
        self.logger.info("SenseEd chatbot initialized successfully")
    
    def setup_logging(self):
        """Setup logging for chatbot"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, self.config.system.log_level))
    
    def start_session(self):
        """Initialize a new learning session"""
        try:
            self.logger.info("Starting new learning session")
            self.session_active = True
            
            # Initialize camera
            if not self.vision_module.initialize_camera(self.config.vision.camera_index):
                self.logger.warning("Camera initialization failed")
            
            # Welcome message
            welcome_message = "Hello! I'm SenseEd, your AI learning assistant. I can help you with speech, vision, gestures, and text. How can I assist you today?"
            self.speech_module.speak_text(welcome_message)
            print(f"SenseEd: {welcome_message}")
            
            # Start input processing thread
            self.input_thread = threading.Thread(target=self._input_processing_loop, daemon=True)
            self.input_thread.start()
            
            # Main interaction loop
            self.main_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start session: {e}")
            self.handle_error(e)
    
    def main_loop(self):
        """Main interaction loop with enhanced error handling"""
        self.logger.info("Starting main interaction loop")
        
        while self.session_active:
            try:
                # Get input from queue
                if not self.input_queue.empty():
                    input_data = self.input_queue.get(timeout=1)
                    
                    if input_data.get('exit', False):
                        break
                    
                    # Process input with timing
                    start_time = time.time()
                    response = self.process_input(input_data)
                    processing_time = time.time() - start_time
                    
                    # Track response time
                    self.response_times.append(processing_time)
                    self._maintain_response_time_target(processing_time)
                    
                    # Deliver response
                    self.deliver_response(response)
                    
                    # Log interaction
                    self.log_interaction(input_data, response, processing_time)
                    
                else:
                    # Check for gesture input if no other input
                    self._check_gesture_input()
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.handle_error(e)
        
        self.end_session()
    
    def _input_processing_loop(self):
        """Background thread for processing various input types"""
        while self.session_active:
            try:
                # Check for speech input
                speech_text = self.speech_module.listen_to_speech(timeout=1)
                if speech_text:
                    if "exit" in speech_text.lower() or "quit" in speech_text.lower():
                        self.input_queue.put({'exit': True})
                        break
                    else:
                        self.input_queue.put({
                            'type': 'speech',
                            'content': speech_text,
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Check for text input (if any)
                # This could be from file uploads, web content, etc.
                
            except Exception as e:
                self.logger.error(f"Error in input processing loop: {e}")
                time.sleep(0.1)
    
    def _check_gesture_input(self):
        """Check for gesture input"""
        try:
            frame = self.vision_module.capture_image()
            if frame is not None:
                gestures = self.gesture_module.detect_gesture(frame)
                if gestures:
                    self.input_queue.put({
                        'type': 'gesture',
                        'content': gestures,
                        'image': frame,
                        'timestamp': datetime.now().isoformat()
                    })
        except Exception as e:
            self.logger.debug(f"Gesture input check failed: {e}")
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process multimodal input and generate comprehensive response
        
        Args:
            input_data: Input data from various sources
            
        Returns:
            Response dictionary
        """
        response = {
            'text': '',
            'audio': True,
            'visual': None,
            'action': None,
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            input_type = input_data.get('type', 'unknown')
            
            if input_type == 'speech':
                response = self._process_speech_input(input_data, response)
            elif input_type == 'gesture':
                response = self._process_gesture_input(input_data, response)
            elif input_type == 'text':
                response = self._process_text_input(input_data, response)
            elif input_type == 'image':
                response = self._process_image_input(input_data, response)
            else:
                response['text'] = "I'm not sure how to process that type of input. Could you try again?"
                response['success'] = False
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return {
                'text': "I encountered an error processing your input. Please try again.",
                'success': False,
                'error': str(e)
            }
    
    def _process_speech_input(self, input_data: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """Process speech input"""
        speech_text = input_data.get('content', '')
        
        if not speech_text:
            response['text'] = "I didn't catch that. Could you please repeat?"
            return response
        
        # Process with NLP
        nlp_result = self.nlp_processor.process_query(speech_text)
        intent = nlp_result.get('intent', 'general')
        
        # Generate response based on intent
        if intent == 'question':
            response['text'] = self._answer_question(speech_text, nlp_result)
        elif intent == 'command':
            response = self._execute_command(speech_text, input_data, response)
        elif intent == 'greeting':
            response['text'] = self._generate_greeting_response()
        elif intent == 'education':
            response['text'] = self._generate_educational_response(speech_text)
        elif intent == 'accessibility':
            response['text'] = self._generate_accessibility_response(speech_text)
        else:
            response['text'] = self._generate_general_response(speech_text)
        
        return response
    
    def _process_gesture_input(self, input_data: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """Process gesture input"""
        gestures = input_data.get('content', [])
        
        if not gestures:
            return response
        
        # Process each gesture
        for gesture_data in gestures:
            gesture = gesture_data.get('gesture', 'Unknown')
            hand = gesture_data.get('hand', 'Unknown')
            
            # Map gestures to actions
            if gesture == 'Thumbs Up':
                response['text'] = "Great! I'm glad you're satisfied."
                response['action'] = 'positive_feedback'
            elif gesture == 'Thumbs Down':
                response['text'] = "I understand you're not satisfied. How can I help better?"
                response['action'] = 'negative_feedback'
            elif gesture == 'Pointing':
                response['text'] = "I see you're pointing. What would you like me to focus on?"
                response['action'] = 'focus_attention'
            elif gesture == 'Open Hand':
                response['text'] = "I see your open hand. Are you ready for the next step?"
                response['action'] = 'ready_signal'
            elif gesture == 'Fist':
                response['text'] = "I see a fist gesture. Do you want to stop or pause?"
                response['action'] = 'stop_signal'
            else:
                response['text'] = f"I detected a {gesture} gesture with your {hand} hand. How can I help?"
        
        return response
    
    def _process_text_input(self, input_data: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """Process text input (conversational input, not document processing)"""
        text_content = input_data.get('content', '')
        
        if not text_content:
            response['text'] = "No text content to process."
            return response
        
        # Process with NLP (same as speech input)
        nlp_result = self.nlp_processor.process_query(text_content)
        intent = nlp_result.get('intent', 'general')
        
        # Generate response based on intent
        if intent == 'question':
            response['text'] = self._answer_question(text_content, nlp_result)
        elif intent == 'command':
            response = self._execute_command(text_content, input_data, response)
        elif intent == 'greeting':
            response['text'] = self._generate_greeting_response()
        elif intent == 'education':
            response['text'] = self._generate_educational_response(text_content)
        elif intent == 'accessibility':
            response['text'] = self._generate_accessibility_response(text_content)
        else:
            response['text'] = self._generate_general_response(text_content)
        
        return response
    
    def _process_image_input(self, input_data: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """Process image input"""
        image = input_data.get('content')
        
        if image is None:
            response['text'] = "No image to process."
            return response
        
        # Analyze image comprehensively
        analysis = self.vision_module.analyze_image_comprehensive(image)
        
        if analysis.get('success', False):
            # Combine results
            description_parts = []
            
            # OCR text
            ocr_text = analysis.get('ocr', {}).get('text', '')
            if ocr_text:
                description_parts.append(f"I can read this text: {ocr_text}")
            
            # Object detection
            objects = analysis.get('objects', {}).get('objects', [])
            if objects:
                object_names = [obj['class'] for obj in objects[:5]]  # Top 5 objects
                description_parts.append(f"I can see: {', '.join(object_names)}")
            
            # Scene description
            scene_desc = analysis.get('scene_description', {}).get('description', '')
            if scene_desc:
                description_parts.append(f"Scene description: {scene_desc}")
            
            if description_parts:
                response['text'] = ' '.join(description_parts)
            else:
                response['text'] = "I can see the image but couldn't extract specific information from it."
        else:
            response['text'] = "I had trouble analyzing the image. Could you try again?"
            response['success'] = False
        
        return response
    
    def _answer_question(self, question: str, nlp_result: Dict[str, Any]) -> str:
        """Answer user questions"""
        # Try to find context from conversation history
        context = self._get_relevant_context(question)
        
        if context:
            answer = self.nlp_processor.answer_question(question, context)
            if answer and answer != "I'm sorry, I couldn't process your question at the moment.":
                return answer
        
        # Fallback to general response
        return f"That's an interesting question about: {question}. Let me help you find more information about that topic."
    
    def _execute_command(self, command: str, input_data: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """Execute user commands"""
        command_lower = command.lower()
        
        if 'read' in command_lower:
            response['text'] = "I'll help you read content. Please provide the text or document you'd like me to read."
            response['action'] = 'read_mode'
        elif 'show' in command_lower:
            response['text'] = "I'll show you information. What would you like me to display?"
            response['action'] = 'display_mode'
        elif 'help' in command_lower:
            response['text'] = self._get_help_message()
        elif 'settings' in command_lower or 'configure' in command_lower:
            response['text'] = "I'll help you configure settings. What would you like to adjust?"
            response['action'] = 'settings_mode'
        else:
            response['text'] = f"I'll help you with that command: {command}. Let me process your request."
        
        return response
    
    def _generate_greeting_response(self) -> str:
        """Generate greeting response"""
        greetings = [
            "Hello! I'm SenseEd, your AI learning assistant. How can I help you today?",
            "Hi there! I'm here to help with your learning needs. What would you like to know?",
            "Greetings! I'm SenseEd, ready to assist you with accessible learning. How can I help?"
        ]
        import random
        return random.choice(greetings)
    
    def _generate_educational_response(self, query: str) -> str:
        """Generate educational response"""
        return f"That's a great learning question! Let me help you understand: {query}. I'll provide an accessible explanation."
    
    def _generate_accessibility_response(self, query: str) -> str:
        """Generate accessibility-focused response"""
        return f"I'm here to make learning accessible for you. Let me help with: {query}. I'll ensure the information is presented in a way that works for your needs."
    
    def _generate_general_response(self, query: str) -> str:
        """Generate general response"""
        # Provide more helpful responses based on common inputs
        query_lower = query.lower().strip()
        
        if query_lower in ['hi', 'hello', 'hey']:
            return "Hello! I'm SenseEd, your AI learning assistant. How can I help you today?"
        elif query_lower in ['thanks', 'thank you', 'thank']:
            return "You're welcome! I'm here to help. Is there anything else you'd like to know?"
        elif query_lower in ['help', 'what can you do']:
            return self._get_help_message()
        elif 'how are you' in query_lower:
            return "I'm doing well, thank you for asking! I'm here and ready to help you with your learning needs. How can I assist you today?"
        elif 'what is' in query_lower or 'what are' in query_lower:
            return f"That's a great question about: {query}. Let me help you understand this topic better. Could you provide more specific details about what you'd like to know?"
        elif 'how to' in query_lower or 'how do' in query_lower:
            return f"I'd be happy to help you learn how to: {query}. Let me provide you with a step-by-step explanation."
        else:
            return f"I understand you're saying: {query}. I'm here to help! Could you tell me more about what you'd like to know or how I can assist you?"
    
    def _get_help_message(self) -> str:
        """Get help message for users"""
        return """
        I'm SenseEd, your AI learning assistant. Here's how I can help:
        
        Speech: Talk to me naturally - ask questions, give commands, or have conversations
        Gestures: Use hand gestures like thumbs up/down, pointing, or open hand
        Vision: I can read text from images, describe scenes, and detect objects
        Text: I can process documents, web content, and provide summaries
        
        Commands you can try:
        - "Read this document" - I'll read and summarize text
        - "What do you see?" - I'll describe what's in the camera view
        - "Help me learn about..." - I'll provide educational content
        - "Settings" - Configure my behavior and preferences
        
        I'm designed to be accessible and support different learning styles. How can I help you today?
        """
    
    def _get_relevant_context(self, question: str) -> str:
        """Get relevant context from conversation history"""
        # Simple context retrieval - could be enhanced with semantic search
        recent_messages = self.conversation_history[-5:]  # Last 5 messages
        context_parts = []
        
        for msg in recent_messages:
            if msg.get('type') == 'user' and msg.get('content'):
                context_parts.append(msg['content'])
        
        return ' '.join(context_parts) if context_parts else ""
    
    def _maintain_response_time_target(self, processing_time: float):
        """Monitor and maintain response time target"""
        target_time = self.config.system.response_timeout
        
        if processing_time > target_time:
            self.logger.warning(f"Response time {processing_time:.2f}s exceeds target {target_time}s")
            
            # Keep only recent response times
            if len(self.response_times) > 100:
                self.response_times = self.response_times[-50:]
    
    def deliver_response(self, response: Dict[str, Any]):
        """Deliver response through appropriate channels"""
        try:
            if response.get('text'):
                print(f"SenseEd: {response['text']}")
                
                # Speak response if audio is enabled
                if response.get('audio', True) and self.config.accessibility.audio_feedback:
                    self.speech_module.speak_text(response['text'])
            
            # Handle visual responses
            if response.get('visual'):
                self._display_visual_content(response['visual'])
            
            # Execute actions
            if response.get('action'):
                self._execute_action(response['action'])
                
        except Exception as e:
            self.logger.error(f"Error delivering response: {e}")
    
    def _display_visual_content(self, visual_content: Any):
        """Display visual content"""
        # Placeholder for visual content display
        self.logger.info(f"Displaying visual content: {visual_content}")
    
    def _execute_action(self, action: str):
        """Execute specific actions"""
        self.logger.info(f"Executing action: {action}")
        
        if action == 'positive_feedback':
            # Record positive feedback
            pass
        elif action == 'negative_feedback':
            # Record negative feedback and adjust
            pass
        elif action == 'focus_attention':
            # Focus on specific area
            pass
        elif action == 'ready_signal':
            # User is ready for next step
            pass
        elif action == 'stop_signal':
            # Stop current operation
            pass
    
    def log_interaction(self, input_data: Dict[str, Any], response: Dict[str, Any], processing_time: float):
        """Log interaction for learning and analytics"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'input': input_data,
            'response': response,
            'processing_time': processing_time,
            'session_id': id(self)
        }
        
        self.conversation_history.append(interaction)
        
        # Keep conversation history manageable
        if len(self.conversation_history) > 1000:
            self.conversation_history = self.conversation_history[-500:]
    
    def handle_error(self, error: Exception):
        """Handle errors gracefully"""
        self.error_count += 1
        self.logger.error(f"Error #{self.error_count}: {error}")
        
        # Provide user-friendly error message
        error_message = "I encountered an issue. Let me try to help you in a different way."
        self.speech_module.speak_text(error_message)
        print(f"SenseEd: {error_message}")
        
        # If too many errors, suggest restart
        if self.error_count > 10:
            restart_message = "I've encountered several issues. You might want to restart the application."
            self.speech_module.speak_text(restart_message)
            print(f"SenseEd: {restart_message}")
    
    def end_session(self):
        """End the current session"""
        self.logger.info("Ending learning session")
        self.session_active = False
        
        # Release resources
        self.vision_module.release_camera()
        
        # Save session data
        self._save_session_data()
        
        # Farewell message
        farewell_message = "Thank you for using SenseEd! I hope I was helpful. Goodbye!"
        self.speech_module.speak_text(farewell_message)
        print(f"SenseEd: {farewell_message}")
    
    def _save_session_data(self):
        """Save session data for learning and analytics"""
        try:
            session_data = {
                'timestamp': datetime.now().isoformat(),
                'conversation_count': len(self.conversation_history),
                'average_response_time': sum(self.response_times) / len(self.response_times) if self.response_times else 0,
                'error_count': self.error_count,
                'user_preferences': self.user_preferences
            }
            
            # Save to file
            data_dir = Path(self.config.system.data_directory)
            data_dir.mkdir(exist_ok=True)
            
            session_file = data_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get chatbot status"""
        return {
            'session_active': self.session_active,
            'conversation_count': len(self.conversation_history),
            'average_response_time': sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            'error_count': self.error_count,
            'modules': {
                'speech': self.speech_module.get_speech_status(),
                'vision': self.vision_module.get_camera_status(),
                'text': self.text_module.get_module_status(),
                'nlp': self.nlp_processor.get_module_status()
            }
        }



