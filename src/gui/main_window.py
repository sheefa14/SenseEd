# main_window.py
"""
GUI Main Window for SenseEd
Enhanced GUI interface with camera, speech, and gesture integration
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import sys
import os
import cv2
import numpy as np
from PIL import Image, ImageTk
from typing import Optional, Dict, Any
import time

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.chatbot import SenseEdChatbot
from modules.vision_module import VisionModule
from modules.speech_module import SpeechModule
from modules.gesture_module import GestureModule

class SenseEdGUI:
    """Enhanced GUI interface for SenseEd with multimodal capabilities"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize GUI
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.chatbot = None
        self.vision_module = None
        self.speech_module = None
        self.gesture_module = None
        
        # Camera and gesture tracking
        self.camera_active = False
        self.gesture_tracking = False
        self.sign_language_active = False
        self.current_frame = None
        
        # Threading
        self.camera_thread = None
        self.gesture_thread = None
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the enhanced HD GUI interface with colorful design"""
        # Create main window with HD resolution
        self.root = tk.Tk()
        self.root.title("SenseEd - Multimodal AI Learning Assistant")
        self.root.geometry("1600x1000")  # Increased resolution for HD
        
        # Set window background color
        self.root.configure(bg='#1e1e2e')
        
        # Configure high DPI scaling for HD display
        try:
            self.root.tk.call('tk', 'scaling', 1.2)  # 120% scaling for HD
        except:
            pass  # Fallback if scaling not supported
        
        # Create main frame with gradient-like background
        main_frame = tk.Frame(self.root, bg='#1e1e2e', padx=15, pady=15)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)  # Left panel (chat)
        main_frame.columnconfigure(1, weight=1)  # Right panel (camera/controls)
        main_frame.rowconfigure(1, weight=1)
        
        # Title with colorful styling
        title_frame = tk.Frame(main_frame, bg='#1e1e2e')
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))
        
        title_label = tk.Label(title_frame, 
                              text="🤖 SenseEd AI Assistant", 
                              font=("Segoe UI", 24, "bold"),  # Larger font for HD
                              fg='#89b4fa', bg='#1e1e2e')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, 
                                 text="Multimodal Learning Interface", 
                                 font=("Segoe UI", 14),  # Larger font for HD
                                 fg='#cdd6f4', bg='#1e1e2e')
        subtitle_label.pack()
        
        # Left Panel - Chat Interface
        self.setup_chat_panel(main_frame)
        
        # Right Panel - Camera and Controls
        self.setup_control_panel(main_frame)
        
        # Initialize modules
        self.init_modules()
    
    def setup_chat_panel(self, parent):
        """Setup the chat interface panel with colorful styling"""
        # Chat frame with custom styling
        chat_frame = tk.Frame(parent, bg='#313244', relief='raised', bd=2)
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(1, weight=1)
        
        # Chat header
        chat_header = tk.Frame(chat_frame, bg='#89b4fa', height=40)
        chat_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        chat_header.grid_propagate(False)
        
        chat_title = tk.Label(chat_header, text="💬 Conversation", 
                             font=("Segoe UI", 14, "bold"),  # Larger font for HD
                             fg='#1e1e2e', bg='#89b4fa')
        chat_title.pack(pady=10)  # More padding for HD
        
        # Chat display with HD styling
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            height=25,  # Increased height for HD
            width=70,   # Increased width for HD
            bg='#11111b',
            fg='#cdd6f4',
            font=("Consolas", 12),  # Larger font for HD
            insertbackground='#89b4fa',
            selectbackground='#585b70',
            selectforeground='#cdd6f4',
            relief='flat',
            bd=0,
            wrap=tk.WORD  # Better text wrapping
        )
        self.chat_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)
        
        # Input frame with colorful styling
        input_frame = tk.Frame(chat_frame, bg='#313244')
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        input_frame.columnconfigure(0, weight=1)
        
        # Text input with HD styling
        self.text_input = tk.Entry(
            input_frame,
            font=("Segoe UI", 13),  # Larger font for HD
            bg='#11111b',
            fg='#cdd6f4',
            insertbackground='#89b4fa',
            relief='flat',
            bd=8  # Larger border for HD
        )
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(8, 8), pady=8)
        self.text_input.bind('<Return>', self.send_message)
        
        # Send button with HD styling
        send_button = tk.Button(
            input_frame, 
            text="📤 Send", 
            command=self.send_message,
            font=("Segoe UI", 12, "bold"),  # Larger font for HD
            bg='#a6e3a1',
            fg='#1e1e2e',
            relief='flat',
            bd=0,
            padx=20,  # More padding for HD
            pady=8,   # More padding for HD
            cursor='hand2'
        )
        send_button.grid(row=0, column=1, padx=(0, 8), pady=8)
        
        # Voice input button with HD styling
        self.voice_button = tk.Button(
            input_frame, 
            text="🎤 Voice", 
            command=self.start_voice_input,
            font=("Segoe UI", 12, "bold"),  # Larger font for HD
            bg='#f9e2af',
            fg='#1e1e2e',
            relief='flat',
            bd=0,
            padx=20,  # More padding for HD
            pady=8,   # More padding for HD
            cursor='hand2'
        )
        self.voice_button.grid(row=0, column=2, padx=(0, 8), pady=8)
        
        # File upload button with HD styling
        self.file_button = tk.Button(
            input_frame, 
            text="📁 Upload File", 
            command=self.upload_file,
            font=("Segoe UI", 12, "bold"),  # Larger font for HD
            bg='#89b4fa',
            fg='#1e1e2e',
            relief='flat',
            bd=0,
            padx=20,  # More padding for HD
            pady=8,   # More padding for HD
            cursor='hand2'
        )
        self.file_button.grid(row=0, column=3, padx=(0, 8), pady=8)
    
    def setup_control_panel(self, parent):
        """Setup the control panel with colorful styling"""
        # Control frame with custom styling
        control_frame = tk.Frame(parent, bg='#313244', relief='raised', bd=2)
        control_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        control_frame.columnconfigure(0, weight=1)
        
        # Status frame with colorful header
        status_frame = tk.Frame(control_frame, bg='#313244')
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        status_header = tk.Frame(status_frame, bg='#f38ba8', height=30)
        status_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        status_header.grid_propagate(False)
        
        status_title = tk.Label(status_header, text="📊 System Status", 
                               font=("Segoe UI", 12, "bold"),  # Larger font for HD
                               fg='#1e1e2e', bg='#f38ba8')
        status_title.pack(pady=6)  # More padding for HD
        
        self.status_label = tk.Label(status_frame, text="Initializing...", 
                                    font=("Segoe UI", 11),  # Larger font for HD
                                    fg='#cdd6f4', bg='#313244')
        self.status_label.grid(row=1, column=0, sticky=tk.W, padx=8, pady=6)  # More padding for HD
        
        # Camera frame with colorful header
        camera_frame = tk.Frame(control_frame, bg='#313244')
        camera_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        camera_frame.columnconfigure(0, weight=1)
        camera_frame.rowconfigure(1, weight=1)
        
        camera_header = tk.Frame(camera_frame, bg='#cba6f7', height=30)
        camera_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        camera_header.grid_propagate(False)
        
        camera_title = tk.Label(camera_header, text="📷 Camera Feed", 
                               font=("Segoe UI", 12, "bold"),  # Larger font for HD
                               fg='#1e1e2e', bg='#cba6f7')
        camera_title.pack(pady=6)  # More padding for HD
        
        # Camera display with colorful border
        self.camera_label = tk.Label(camera_frame, text="📹 Camera not active", 
                                    font=("Segoe UI", 12),
                                    bg='#11111b', fg='#cdd6f4',
                                    relief='sunken', bd=2)
        self.camera_label.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)
        
        # Camera controls with colorful buttons
        camera_controls = tk.Frame(camera_frame, bg='#313244')
        camera_controls.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        
        self.camera_button = tk.Button(camera_controls, text="📹 Start Camera", 
                                      command=self.toggle_camera,
                                      font=("Segoe UI", 11, "bold"),  # Larger font for HD
                                      bg='#a6e3a1', fg='#1e1e2e',
                                      relief='flat', bd=0, padx=15, pady=5,  # More padding for HD
                                      cursor='hand2')
        self.camera_button.grid(row=0, column=0, padx=(0, 8))
        
        self.gesture_button = tk.Button(camera_controls, text="👋 Start Basic Gestures", 
                                       command=self.toggle_gesture_tracking,
                                       font=("Segoe UI", 10, "bold"),  # Slightly smaller to fit text
                                       bg='#fab387', fg='#1e1e2e',
                                       relief='flat', bd=0, padx=12, pady=5,
                                       cursor='hand2')
        self.gesture_button.grid(row=0, column=1)
        
        # Vision analysis frame with colorful header
        vision_frame = tk.Frame(control_frame, bg='#313244')
        vision_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        vision_header = tk.Frame(vision_frame, bg='#89b4fa', height=30)
        vision_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        vision_header.grid_propagate(False)
        
        vision_title = tk.Label(vision_header, text="👁️ Vision Analysis", 
                               font=("Segoe UI", 12, "bold"),  # Larger font for HD
                               fg='#1e1e2e', bg='#89b4fa')
        vision_title.pack(pady=6)  # More padding for HD
        
        vision_buttons = tk.Frame(vision_frame, bg='#313244')
        vision_buttons.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        
        ocr_button = tk.Button(vision_buttons, text="📝 Extract Text", 
                              command=self.analyze_ocr,
                              font=("Segoe UI", 11, "bold"),  # Larger font for HD
                              bg='#f9e2af', fg='#1e1e2e',
                              relief='flat', bd=0, padx=12, pady=5,  # More padding for HD
                              cursor='hand2')
        ocr_button.grid(row=0, column=0, padx=(0, 8), pady=3)
        
        object_button = tk.Button(vision_buttons, text="🎯 Detect Objects", 
                                 command=self.analyze_objects,
                                 font=("Segoe UI", 11, "bold"),  # Larger font for HD
                                 bg='#f38ba8', fg='#1e1e2e',
                                 relief='flat', bd=0, padx=12, pady=5,  # More padding for HD
                                 cursor='hand2')
        object_button.grid(row=0, column=1, pady=3)
        
        scene_button = tk.Button(vision_buttons, text="🌅 Describe Scene", 
                                command=self.analyze_scene,
                                font=("Segoe UI", 11, "bold"),  # Larger font for HD
                                bg='#cba6f7', fg='#1e1e2e',
                                relief='flat', bd=0, padx=12, pady=5,  # More padding for HD
                                cursor='hand2')
        scene_button.grid(row=1, column=0, columnspan=2, pady=3)
        
        # Sign language toggle button (more prominent)
        self.sign_language_button = tk.Button(vision_buttons, text="🤟 Enable Sign Language (97 Phrases)", 
                                            command=self.toggle_sign_language,
                                            font=("Segoe UI", 10, "bold"),  # Slightly smaller to fit text
                                            bg='#a6e3a1', fg='#1e1e2e',  # Green to make it more prominent
                                            relief='flat', bd=0, padx=8, pady=5,
                                            cursor='hand2')
        self.sign_language_button.grid(row=2, column=0, columnspan=2, pady=3)
        
        # Voice interaction frame with colorful header
        voice_frame = tk.Frame(control_frame, bg='#313244')
        voice_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        voice_header = tk.Frame(voice_frame, bg='#94e2d5', height=30)
        voice_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        voice_header.grid_propagate(False)
        
        voice_title = tk.Label(voice_header, text="🎤 Voice Interaction", 
                              font=("Segoe UI", 12, "bold"),  # Larger font for HD
                              fg='#1e1e2e', bg='#94e2d5')
        voice_title.pack(pady=6)  # More padding for HD
        
        voice_controls = tk.Frame(voice_frame, bg='#313244')
        voice_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        
        self.voice_input_button = tk.Button(voice_controls, text="🎤 Voice Input", 
                                           command=self.toggle_voice_input,
                                           font=("Segoe UI", 11, "bold"),  # Larger font for HD
                                           bg='#a6e3a1', fg='#1e1e2e',
                                           relief='flat', bd=0, padx=12, pady=5,  # More padding for HD
                                           cursor='hand2')
        self.voice_input_button.grid(row=0, column=0, padx=(0, 8), pady=3)
        
        self.voice_output_button = tk.Button(voice_controls, text="🔊 Voice Output", 
                                            command=self.toggle_voice_output,
                                            font=("Segoe UI", 11, "bold"),  # Larger font for HD
                                            bg='#fab387', fg='#1e1e2e',
                                            relief='flat', bd=0, padx=12, pady=5,  # More padding for HD
                                            cursor='hand2')
        self.voice_output_button.grid(row=0, column=1, pady=3)
        
        # Voice status
        self.voice_status_label = tk.Label(voice_frame, text="Voice ready", 
                                          font=("Segoe UI", 10),
                                          fg='#cdd6f4', bg='#313244')
        self.voice_status_label.grid(row=2, column=0, sticky=tk.W, padx=8, pady=3)
        
        # Speech controls frame with colorful header
        speech_frame = tk.Frame(control_frame, bg='#313244')
        speech_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        speech_header = tk.Frame(speech_frame, bg='#f9e2af', height=30)
        speech_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        speech_header.grid_propagate(False)
        
        speech_title = tk.Label(speech_header, text="🎤 Speech Controls", 
                               font=("Segoe UI", 12, "bold"),  # Larger font for HD
                               fg='#1e1e2e', bg='#f9e2af')
        speech_title.pack(pady=6)  # More padding for HD
        
        speech_buttons = tk.Frame(speech_frame, bg='#313244')
        speech_buttons.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        
        self.tts_button = tk.Button(speech_buttons, text="🔊 Speak Response", 
                                   command=self.speak_last_response,
                                   font=("Segoe UI", 11, "bold"),  # Larger font for HD
                                   bg='#a6e3a1', fg='#1e1e2e',
                                   relief='flat', bd=0, padx=15, pady=5,  # More padding for HD
                                   cursor='hand2')
        self.tts_button.grid(row=0, column=0, pady=3)
        
        # Session controls frame with colorful header
        session_frame = tk.Frame(control_frame, bg='#313244')
        session_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        session_header = tk.Frame(session_frame, bg='#fab387', height=30)
        session_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        session_header.grid_propagate(False)
        
        session_title = tk.Label(session_header, text="⚙️ Session Controls", 
                                font=("Segoe UI", 12, "bold"),  # Larger font for HD
                                fg='#1e1e2e', bg='#fab387')
        session_title.pack(pady=6)  # More padding for HD
        
        session_buttons = tk.Frame(session_frame, bg='#313244')
        session_buttons.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        
        start_button = tk.Button(session_buttons, text="▶️ Start Session", 
                                command=self.start_session,
                                font=("Segoe UI", 11, "bold"),  # Larger font for HD
                                bg='#a6e3a1', fg='#1e1e2e',
                                relief='flat', bd=0, padx=12, pady=5,  # More padding for HD
                                cursor='hand2')
        start_button.grid(row=0, column=0, padx=(0, 8))
        
        stop_button = tk.Button(session_buttons, text="⏹️ Stop Session", 
                               command=self.stop_session,
                               font=("Segoe UI", 11, "bold"),  # Larger font for HD
                               bg='#f38ba8', fg='#1e1e2e',
                               relief='flat', bd=0, padx=12, pady=5,  # More padding for HD
                               cursor='hand2')
        stop_button.grid(row=0, column=1, padx=(0, 8))
        
        help_button = tk.Button(session_buttons, text="❓ Help", 
                               command=self.show_help,
                               font=("Segoe UI", 11, "bold"),  # Larger font for HD
                               bg='#89b4fa', fg='#1e1e2e',
                               relief='flat', bd=0, padx=12, pady=5,  # More padding for HD
                               cursor='hand2')
        help_button.grid(row=0, column=2)
    
    def init_modules(self):
        """Initialize all modules"""
        try:
            # Initialize chatbot
            self.chatbot = SenseEdChatbot(self.config_file)
            
            # Initialize vision module
            self.vision_module = VisionModule()
            
            # Initialize speech module
            self.speech_module = SpeechModule()
            
            # Initialize gesture module
            self.gesture_module = GestureModule()
            
            self.update_status("All modules initialized successfully")
            self.add_message("System", "SenseEd GUI initialized with multimodal capabilities. Click 'Start Session' to begin.")
            
        except Exception as e:
            self.update_status(f"Error initializing modules: {e}")
            self.add_message("System", f"Error: {e}")
    
    # Camera and Vision Methods
    def toggle_camera(self):
        """Toggle camera on/off"""
        if not self.camera_active:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Start camera feed"""
        try:
            if not self.vision_module:
                self.add_message("System", "Vision module not initialized")
                return
            
            if self.vision_module.initialize_camera():
                self.camera_active = True
                self.camera_button.config(text="Stop Camera")
                self.update_status("Camera started")
                self.add_message("System", "Camera started. You can now see the live feed.")
                
                # Start camera thread
                self.camera_thread = threading.Thread(target=self.camera_loop)
                self.camera_thread.daemon = True
                self.camera_thread.start()
            else:
                self.add_message("System", "Failed to initialize camera")
                
        except Exception as e:
            self.add_message("System", f"Error starting camera: {e}")
    
    def stop_camera(self):
        """Stop camera feed"""
        try:
            self.camera_active = False
            self.gesture_tracking = False
            self.sign_language_active = False
            self.camera_button.config(text="Start Camera")
            self.gesture_button.config(text="Start Gestures")
            self.sign_language_button.config(text="🤟 Enable Sign Language")
            self.update_status("Camera stopped")
            self.add_message("System", "Camera stopped.")
            
            if self.vision_module:
                self.vision_module.release_camera()
                
        except Exception as e:
            self.add_message("System", f"Error stopping camera: {e}")
    
    def camera_loop(self):
        """Camera loop for displaying video feed with controlled speed"""
        frame_count = 0
        while self.camera_active:
            try:
                frame = self.vision_module.capture_image()
                if frame is not None:
                    self.current_frame = frame.copy()
                    
                    # Apply gesture tracking if enabled (every 5th frame for better performance)
                    if self.gesture_tracking and self.gesture_module and frame_count % 5 == 0:
                        # Check for sign language recognition if enabled (97 phrases from dataset)
                        if self.sign_language_active:
                            sign_result = self.gesture_module.detect_sign_language(frame)
                            if sign_result:
                                # Show ongoing recognition for better feedback
                                if sign_result.get('phrase') and sign_result.get('status') in ['new_phrase', 'continuing']:
                                    phrase = sign_result.get('phrase', '')
                                    confidence = sign_result.get('confidence', 0.0)
                                    self.add_message("Sign Language", f"Recognizing: '{phrase}' ({confidence:.2f})")
                                elif sign_result.get('phrase') and sign_result.get('status') == 'completed':
                                    self.process_sign_language(sign_result)
                        else:
                            # Show basic gestures only when sign language is not active
                            gestures = self.gesture_module.get_gesture_info(frame)
                            if gestures:
                                # Process gesture commands
                                self.process_gestures(gestures)
                    
                    # Update display only every 3rd frame to reduce pointer speed
                    if frame_count % 3 == 0:
                        # Convert frame for display
                        display_frame = self.prepare_frame_for_display(frame)
                        
                        # Update GUI in main thread
                        self.root.after(0, self.update_camera_display, display_frame)
                    
                    frame_count += 1
                
                time.sleep(0.1)  # Reduced to 10 FPS for better performance and less continuous detection
                
            except Exception as e:
                print(f"Camera loop error: {e}")
                break
    
    def prepare_frame_for_display(self, frame):
        """Prepare frame for tkinter display"""
        try:
            # Resize frame to fit display
            height, width = frame.shape[:2]
            max_width, max_height = 400, 300
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            return photo
            
        except Exception as e:
            print(f"Error preparing frame: {e}")
            return None
    
    def update_camera_display(self, photo):
        """Update camera display in GUI"""
        try:
            if photo:
                self.camera_label.config(image=photo, text="")
                self.camera_label.image = photo  # Keep a reference
        except Exception as e:
            print(f"Error updating camera display: {e}")
    
    def toggle_gesture_tracking(self):
        """Toggle gesture tracking on/off"""
        if not self.camera_active:
            self.add_message("System", "Please start camera first")
            return
        
        self.gesture_tracking = not self.gesture_tracking
        if self.gesture_tracking:
            self.gesture_button.config(text="👋 Stop Basic Gestures")
            self.add_message("System", "👋 Basic gesture tracking started (Peace, Pointing, etc.)")
            self.add_message("System", "💡 For 97 sign language phrases, enable 'Sign Language' below!")
        else:
            self.gesture_button.config(text="👋 Start Basic Gestures")
            self.add_message("System", "Basic gesture tracking stopped")
    
    def toggle_sign_language(self):
        """Toggle sign language recognition"""
        if not self.camera_active:
            self.add_message("System", "Please start camera first")
            return
        
        self.sign_language_active = not self.sign_language_active
        if self.sign_language_active:
            self.sign_language_button.config(
                text="🤟 Disable Sign Language (97 Phrases)", 
                bg='#f38ba8'  # Red when active
            )
            self.add_message("System", "🤟 Sign language recognition ENABLED - 97 phrases available!")
            
            # Show available phrases
            if self.gesture_module:
                phrases = self.gesture_module.get_sign_language_phrases()
                if phrases:
                    phrase_count = len(phrases)
                    phrase_list = ", ".join(phrases[:8])  # Show first 8 phrases
                    self.add_message("Sign Language", f"📚 {phrase_count} phrases loaded: {phrase_list}...")
                    self.add_message("Sign Language", "💡 Try signing phrases like 'hello', 'thank you', 'help me'")
        else:
            self.sign_language_button.config(
                text="🤟 Enable Sign Language (97 Phrases)", 
                bg='#a6e3a1'  # Green when inactive
            )
            self.add_message("System", "Sign language recognition disabled - basic gestures only")
    
    def process_gestures(self, gestures):
        """Process detected gestures"""
        for gesture_data in gestures:
            hand = gesture_data['hand']
            gesture = gesture_data['gesture']
            
            # Map gestures to commands
            if gesture == "Thumbs Up":
                self.add_message("Gesture", f"{hand} hand: {gesture} - Positive feedback")
            elif gesture == "Thumbs Down":
                self.add_message("Gesture", f"{hand} hand: {gesture} - Negative feedback")
            elif gesture == "Peace":
                self.add_message("Gesture", f"{hand} hand: {gesture} - Victory/OK")
            elif gesture == "Pointing":
                self.add_message("Gesture", f"{hand} hand: {gesture} - Pointing at something")
    
    def process_sign_language(self, sign_result):
        """Process sign language recognition results"""
        phrase = sign_result.get('phrase', '')
        confidence = sign_result.get('confidence', 0.0)
        status = sign_result.get('status', '')
        
        if phrase and status == 'completed':
            # Only process completed phrases
            self.add_message("Sign Language", f"Detected: '{phrase}' (confidence: {confidence:.2f})")
            
            # Process the phrase as text input
            self.process_message(phrase)
        elif phrase and status in ['new_phrase', 'continuing']:
            # Show ongoing recognition
            self.add_message("Sign Language", f"Recognizing: '{phrase}' (confidence: {confidence:.2f})")
    
    def toggle_voice_input(self):
        """Toggle voice input functionality"""
        if not hasattr(self, 'voice_input_active'):
            self.voice_input_active = False
            self.voice_listening_thread = None
            self.voice_stop_event = None
        
        if not self.voice_input_active:
            # Start voice input
            self.voice_input_active = True
            self.voice_input_button.config(text="🔇 Stop Voice Input", bg='#f38ba8')
            self.voice_status_label.config(text="Listening for voice input...")
            
            # Start continuous voice listening
            self.voice_stop_event = threading.Event()
            self.voice_listening_thread = self.speech_module.listen_continuously(
                self.handle_voice_input, 
                self.voice_stop_event
            )
            
            self.add_message("System", "Voice input started. Speak naturally!")
        else:
            # Stop voice input
            self.voice_input_active = False
            self.voice_input_button.config(text="🎤 Voice Input", bg='#a6e3a1')
            self.voice_status_label.config(text="Voice input stopped")
            
            # Stop listening thread
            if self.voice_stop_event:
                self.voice_stop_event.set()
            if self.voice_listening_thread:
                self.voice_listening_thread.join(timeout=1)
            
            self.add_message("System", "Voice input stopped")
    
    def toggle_voice_output(self):
        """Toggle voice output functionality"""
        if not hasattr(self, 'voice_output_active'):
            self.voice_output_active = False
        
        self.voice_output_active = not self.voice_output_active
        
        if self.voice_output_active:
            self.voice_output_button.config(text="🔇 Stop Voice Output", bg='#f38ba8')
            self.add_message("System", "Voice output enabled. Responses will be spoken.")
        else:
            self.voice_output_button.config(text="🔊 Voice Output", bg='#fab387')
            self.add_message("System", "Voice output disabled. Responses will be text only.")
    
    def handle_voice_input(self, text):
        """Handle voice input from continuous listening"""
        if text and text.strip():
            self.add_message("Voice Input", f"You said: {text}")
            self.process_message(text)
    
    def speak_response_if_enabled(self, response_text):
        """Speak response if voice output is enabled"""
        if hasattr(self, 'voice_output_active') and self.voice_output_active:
            self.speech_module.speak_response(response_text)
    
    # Vision Analysis Methods
    def analyze_ocr(self):
        """Analyze current frame for text using OCR"""
        if self.current_frame is None:
            self.add_message("System", "No frame available for OCR analysis")
            return
        
        try:
            result = self.vision_module.extract_text_from_image(self.current_frame)
            if result['success'] and result['text']:
                self.add_message("OCR", f"Extracted text: {result['text']}")
                # Send to chatbot for processing
                self.process_vision_input("text", result['text'])
            else:
                self.add_message("OCR", "No text found in image")
        except Exception as e:
            self.add_message("System", f"OCR analysis error: {e}")
    
    def analyze_objects(self):
        """Analyze current frame for objects"""
        if self.current_frame is None:
            self.add_message("System", "No frame available for object analysis")
            return
        
        try:
            result = self.vision_module.detect_objects(self.current_frame)
            if result['success'] and result['objects']:
                objects_text = ", ".join([f"{obj['class']} ({obj['confidence']:.2f})" 
                                        for obj in result['objects']])
                self.add_message("Objects", f"Detected: {objects_text}")
                # Send to chatbot for processing
                self.process_vision_input("objects", objects_text)
            else:
                self.add_message("Objects", "No objects detected")
        except Exception as e:
            self.add_message("System", f"Object analysis error: {e}")
    
    def analyze_scene(self):
        """Analyze current frame for scene description"""
        if self.current_frame is None:
            self.add_message("System", "No frame available for scene analysis")
            return
        
        try:
            result = self.vision_module.describe_scene(self.current_frame)
            if result['success']:
                self.add_message("Scene", f"Description: {result['description']}")
                # Send to chatbot for processing
                self.process_vision_input("scene", result['description'])
            else:
                self.add_message("Scene", "Failed to describe scene")
        except Exception as e:
            self.add_message("System", f"Scene analysis error: {e}")
    
    def process_vision_input(self, input_type, content):
        """Process vision analysis results with chatbot"""
        try:
            if not self.chatbot:
                self.add_message("System", "Chatbot not available for processing")
                return
            
            input_data = {
                'type': f'vision_{input_type}',
                'content': content,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            
            response = self.chatbot.process_input(input_data)
            if response and response.get('success', False):
                response_text = response.get('text', 'No response available')
                self.add_message("SenseEd", response_text)
            else:
                error_msg = response.get('error', 'Unknown error') if response else 'No response from chatbot'
                self.add_message("System", f"Processing error: {error_msg}")
                
        except Exception as e:
            self.add_message("System", f"Error processing vision input: {str(e)}")
    
    # Speech Methods
    def start_voice_input(self):
        """Start voice input"""
        try:
            if not self.speech_module:
                self.add_message("System", "Speech module not initialized")
                return
            
            # Update button appearance for listening state
            self.voice_button.config(
                text="🎤 Listening...", 
                state="disabled",
                bg='#f38ba8',  # Pink when listening
                fg='#1e1e2e'
            )
            self.update_status("🎤 Listening for speech...")
            
            # Start voice input in thread
            thread = threading.Thread(target=self.process_voice_input)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.add_message("System", f"Error starting voice input: {e}")
            self.voice_button.config(
                text="🎤 Voice", 
                state="normal",
                bg='#f9e2af',  # Back to yellow
                fg='#1e1e2e'
            )
    
    def process_voice_input(self):
        """Process voice input in background thread"""
        try:
            text = self.speech_module.listen_to_speech(timeout=5, phrase_time_limit=5)
            
            # Update GUI in main thread
            self.root.after(0, self.handle_voice_result, text)
            
        except Exception as e:
            self.root.after(0, self.handle_voice_error, str(e))
    
    def handle_voice_result(self, text):
        """Handle voice recognition result"""
        self.voice_button.config(
            text="🎤 Voice", 
            state="normal",
            bg='#f9e2af',  # Back to yellow
            fg='#1e1e2e'
        )
        self.update_status("✅ Ready")
        
        if text:
            self.add_message("Voice", f"You said: {text}")
            # Process with chatbot
            self.process_message(text)
        else:
            self.add_message("Voice", "No speech detected")
    
    def handle_voice_error(self, error):
        """Handle voice recognition error"""
        self.voice_button.config(
            text="🎤 Voice", 
            state="normal",
            bg='#f9e2af',  # Back to yellow
            fg='#1e1e2e'
        )
        self.update_status("❌ Voice error")
        self.add_message("System", f"Voice input error: {error}")
    
    def upload_file(self):
        """Handle file upload for document processing"""
        try:
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Select a file to upload",
                filetypes=[
                    ("All supported files", "*.txt;*.pdf;*.docx;*.csv;*.html;*.htm;*.jpg;*.jpeg;*.png"),
                    ("Text files", "*.txt"),
                    ("PDF files", "*.pdf"),
                    ("Word documents", "*.docx"),
                    ("CSV files", "*.csv"),
                    ("HTML files", "*.html;*.htm"),
                    ("Image files", "*.jpg;*.jpeg;*.png"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.add_message("System", f"Uploading file: {os.path.basename(file_path)}")
                self.update_status("📁 Processing file...")
                
                # Process file in background thread
                thread = threading.Thread(target=self.process_uploaded_file, args=(file_path,))
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            self.add_message("System", f"Error uploading file: {e}")
            self.update_status("❌ Upload error")
    
    def process_uploaded_file(self, file_path):
        """Process uploaded file in background thread"""
        try:
            # Import text module for document processing
            from modules.text_module import TextModule
            
            # Initialize text module
            text_module = TextModule()
            
            # Process the file
            result = text_module.read_document(file_path)
            
            # Update GUI in main thread
            self.root.after(0, self.handle_file_processing_result, result, file_path)
            
        except Exception as e:
            self.root.after(0, self.handle_file_processing_error, str(e), file_path)
    
    def handle_file_processing_result(self, result, file_path):
        """Handle successful file processing result with enhanced detail display"""
        try:
            filename = os.path.basename(file_path)
            
            if result.get('success', False):
                content = result.get('content', '')
                file_type = result.get('file_type', 'unknown')
                
                self.add_message("File Upload", f"Successfully processed {filename} ({file_type})")
                
                # Display extracted details
                if 'training_data' in result:
                    training_data = result['training_data']
                    metadata = training_data.get('metadata', {})
                    
                    # Show file statistics
                    stats_msg = f"📊 File Statistics:\n"
                    stats_msg += f"• Words: {metadata.get('word_count', 0)}\n"
                    stats_msg += f"• Sentences: {metadata.get('sentence_count', 0)}\n"
                    stats_msg += f"• Type: {metadata.get('file_type', 'unknown')}\n"
                    self.add_message("File Analysis", stats_msg)
                
                # Display extracted entities if available
                if 'named_entities' in result and result['named_entities']:
                    entities = result['named_entities'][:10]  # Show first 10 entities
                    entity_msg = "🏷️ Named Entities Found:\n"
                    for entity in entities:
                        entity_msg += f"• {entity['text']} ({entity['label']})\n"
                    self.add_message("Entity Extraction", entity_msg)
                
                # Display keywords if available
                if 'keywords' in result and result['keywords']:
                    keywords = list(result['keywords'].keys())[:10]  # Show top 10 keywords
                    keyword_msg = f"🔑 Key Topics: {', '.join(keywords)}"
                    self.add_message("Topic Analysis", keyword_msg)
                
                # Display summary if available
                if 'summary' in result:
                    self.add_message("Summary", f"📝 Summary:\n{result['summary']}")
                
                # Add extracted content to chat
                if content:
                    # Truncate very long content for display
                    display_content = content[:500] + "..." if len(content) > 500 else content
                    self.add_message("File Content", f"Extracted content:\n{display_content}")
                    
                    # Process the content with the chatbot for analysis
                    analysis_prompt = f"Please analyze this uploaded file content and provide insights:\n\n{content}"
                    self.process_message(analysis_prompt)
                else:
                    self.add_message("File Content", "No text content found in the file")
                
                self.update_status("✅ File processed successfully")
            else:
                error_msg = result.get('error', 'Unknown error')
                self.add_message("File Upload", f"Failed to process {filename}: {error_msg}")
                self.update_status("❌ File processing failed")
                
        except Exception as e:
            self.add_message("System", f"Error handling file result: {e}")
            self.update_status("❌ File processing error")
    
    def handle_file_processing_error(self, error, file_path):
        """Handle file processing error"""
        filename = os.path.basename(file_path)
        self.add_message("System", f"Error processing {filename}: {error}")
        self.update_status("❌ File processing error")
    
    def speak_last_response(self):
        """Speak the last response from SenseEd with improved TTS"""
        try:
            if not self.speech_module:
                self.add_message("System", "Speech module not initialized")
                return
            
            # Get last response from chat
            chat_content = self.chat_display.get("1.0", tk.END)
            lines = chat_content.strip().split('\n')
            
            # Find last SenseEd response
            last_response = None
            for line in reversed(lines):
                if "SenseEd:" in line:
                    # Extract text after timestamp and sender
                    parts = line.split("SenseEd:", 1)
                    if len(parts) > 1:
                        last_response = parts[1].strip()
                        break
            
            if last_response:
                self.add_message("System", "🔊 Speaking response...")
                
                # Reset speech module state to ensure it can speak
                if hasattr(self.speech_module, 'is_speaking'):
                    self.speech_module.is_speaking = False
                
                # Try different TTS methods with interrupt capability
                success = False
                
                # Method 1: Try system TTS first
                if hasattr(self.speech_module, 'tts_engine') and self.speech_module.tts_engine:
                    try:
                        success = self.speech_module.speak_text(last_response, use_gtts=False, interrupt=True)
                        if success:
                            self.add_message("System", "✅ Spoken using system TTS")
                    except Exception as e:
                        self.add_message("System", f"System TTS failed: {e}")
                
                # Method 2: Try Google TTS if system TTS failed
                if not success:
                    try:
                        success = self.speech_module.speak_text(last_response, use_gtts=True, interrupt=True)
                        if success:
                            self.add_message("System", "✅ Spoken using Google TTS")
                    except Exception as e:
                        self.add_message("System", f"Google TTS failed: {e}")
                
                # Method 3: Try async method
                if not success:
                    try:
                        self.speech_module.speak_async(last_response)
                        self.add_message("System", "✅ Speaking asynchronously...")
                        success = True
                    except Exception as e:
                        self.add_message("System", f"Async TTS failed: {e}")
                
                if not success:
                    self.add_message("System", "❌ All TTS methods failed. Please check audio settings.")
            else:
                self.add_message("System", "No SenseEd response found to speak")
                
        except Exception as e:
            self.add_message("System", f"Error speaking response: {e}")
    
    def update_status(self, message: str):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def add_message(self, sender: str, message: str):
        """Add message to chat display with colorful styling"""
        # Get current timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different senders
        colors = {
            'System': '#f38ba8',      # Pink for system messages
            'SenseEd': '#89b4fa',     # Blue for AI responses
            'You': '#a6e3a1',         # Green for user messages
            'Voice': '#f9e2af',       # Yellow for voice input
            'OCR': '#cba6f7',         # Purple for OCR results
            'Objects': '#fab387',     # Orange for object detection
            'Scene': '#89b4fa',       # Blue for scene description
            'Gesture': '#f38ba8',     # Pink for gesture recognition
            'File': '#a6e3a1'         # Green for file processing
        }
        
        # Format message with timestamp and color
        color = colors.get(sender, '#cdd6f4')  # Default color
        formatted_message = f"[{timestamp}] {sender}: {message}\n"
        
        # Insert message
        self.chat_display.insert(tk.END, formatted_message)
        
        # Apply color to the last inserted line
        start_line = self.chat_display.index(tk.END + "-2l")
        end_line = self.chat_display.index(tk.END + "-1l")
        
        # Configure tag for this sender
        tag_name = f"color_{sender}"
        self.chat_display.tag_configure(tag_name, foreground=color)
        self.chat_display.tag_add(tag_name, start_line, end_line)
        
        # Scroll to bottom and update
        self.chat_display.see(tk.END)
        self.root.update_idletasks()
    
    def send_message(self, event=None):
        """Send text message"""
        message = self.text_input.get().strip()
        if not message:
            return
        
        # Clear input
        self.text_input.delete(0, tk.END)
        
        # Add user message to display
        self.add_message("You", message)
        
        # Process message in thread
        thread = threading.Thread(target=self.process_message, args=(message,))
        thread.daemon = True
        thread.start()
    
    def process_message(self, message: str):
        """Process message with chatbot and auto-speak response"""
        try:
            if not self.chatbot:
                self.add_message("System", "Chatbot not initialized")
                return
            
            # Create input data
            input_data = {
                'type': 'text',
                'content': message,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            
            # Process with chatbot
            response = self.chatbot.process_input(input_data)
            
            # Add response to display
            if response and response.get('success', False):
                response_text = response.get('text', 'No response')
                self.add_message("SenseEd", response_text)
                
                # Speak response if voice output is enabled
                self.speak_response_if_enabled(response_text)
            else:
                error_msg = response.get('error', 'Unknown error') if response else 'No response from chatbot'
                self.add_message("System", f"Error: {error_msg}")
                
        except Exception as e:
            self.add_message("System", f"Error processing message: {e}")
    
    def auto_speak_response(self, text: str):
        """Automatically speak SenseEd responses with improved reliability"""
        try:
            if not self.speech_module or not text:
                return
            
            # Speak the response automatically
            def speak_in_background():
                try:
                    # Reset speech module state to ensure it can speak multiple times
                    if hasattr(self.speech_module, 'is_speaking'):
                        self.speech_module.is_speaking = False
                    
                    # Try system TTS first with interrupt capability
                    if hasattr(self.speech_module, 'tts_engine') and self.speech_module.tts_engine:
                        success = self.speech_module.speak_text(text, use_gtts=False, interrupt=True)
                        if not success:
                            # Fallback to Google TTS
                            self.speech_module.speak_text(text, use_gtts=True, interrupt=True)
                    else:
                        # Use Google TTS
                        self.speech_module.speak_text(text, use_gtts=True, interrupt=True)
                except Exception as e:
                    print(f"Auto-speak error: {e}")
                    # Reset state on error
                    if hasattr(self.speech_module, 'is_speaking'):
                        self.speech_module.is_speaking = False
            
            # Run in background thread
            thread = threading.Thread(target=speak_in_background)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"Auto-speak setup error: {e}")
    
    def start_session(self):
        """Start chatbot session"""
        try:
            if self.chatbot:
                self.chatbot.session_active = True
                self.update_status("Session started")
                self.add_message("System", "Session started. You can now interact with SenseEd.")
            else:
                self.add_message("System", "Chatbot not initialized")
        except Exception as e:
            self.add_message("System", f"Error starting session: {e}")
    
    def stop_session(self):
        """Stop chatbot session"""
        try:
            if self.chatbot:
                self.chatbot.session_active = False
                self.update_status("Session stopped")
                self.add_message("System", "Session stopped.")
            else:
                self.add_message("System", "Chatbot not initialized")
        except Exception as e:
            self.add_message("System", f"Error stopping session: {e}")
    
    def open_file(self):
        """Open and process a file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select a file to process",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("PDF files", "*.pdf"),
                    ("Word documents", "*.docx"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.add_message("System", f"Processing file: {file_path}")
                
                # Process file in thread
                thread = threading.Thread(target=self.process_file, args=(file_path,))
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            self.add_message("System", f"Error opening file: {e}")
    
    def process_file(self, file_path: str):
        """Process file with text module"""
        try:
            if not self.chatbot:
                self.add_message("System", "Chatbot not initialized")
                return
            
            # Read file using text module
            result = self.chatbot.text_module.read_document(file_path)
            
            if result.get('success', False):
                text_content = result.get('text', '')
                if text_content:
                    # Truncate if too long
                    if len(text_content) > 500:
                        text_content = text_content[:500] + "..."
                    
                    self.add_message("File", f"Content: {text_content}")
                    
                    # Process text
                    analysis = self.chatbot.text_module.process_text(text_content, ['summary'])
                    if analysis.get('success', False):
                        summary = analysis.get('operations', {}).get('summary', {})
                        if summary and summary.get('summary'):
                            self.add_message("SenseEd", f"Summary: {summary['summary']}")
                else:
                    self.add_message("System", "No text content found in file")
            else:
                self.add_message("System", f"Error reading file: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.add_message("System", f"Error processing file: {e}")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
SenseEd Multimodal GUI Help

Text Interaction:
- Type messages in the text input and press Enter or click Send
- Click "🎤 Voice" to speak your message instead of typing

Camera Features:
- Click "Start Camera" to begin live video feed
- Click "Start Gestures" to enable hand gesture recognition
- Use "Extract Text (OCR)" to read text from camera
- Use "Detect Objects" to identify objects in view
- Use "Describe Scene" to get AI description of what's seen

Speech Features:
- Click "🎤 Voice" to speak your input
- Click "🔊 Speak Response" to have SenseEd speak its last response

Gesture Commands:
- Thumbs Up: Positive feedback
- Thumbs Down: Negative feedback
- Peace Sign: Victory/OK
- Pointing: Indicate something

Session Controls:
- Click "Start Session" to begin interaction
- Click "Stop Session" to end interaction
- Click "Help" to show this dialog

Features:
- Multimodal interaction (text, voice, vision, gestures)
- Real-time camera feed with gesture recognition
- OCR text extraction from images
- Object detection and scene description
- Voice input and text-to-speech output
- Real-time conversation display

For more information, see the README.md file.
        """
        
        messagebox.showinfo("SenseEd Multimodal Help", help_text)
    
    def run(self):
        """Run the GUI"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            print(f"GUI Error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources when closing"""
        try:
            # Stop camera and gesture tracking
            self.stop_camera()
            
            # Stop speech
            if self.speech_module:
                self.speech_module.stop_speaking()
            
            # Close gesture module
            if self.gesture_module:
                self.gesture_module.close()
            
            # End chatbot session
            if self.chatbot:
                self.chatbot.end_session()
                
        except Exception as e:
            print(f"Cleanup error: {e}")



