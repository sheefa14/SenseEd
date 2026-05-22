# minimalist_window.py
"""
Minimalist GUI for SenseEd
Clean, accessible, and professional interface following minimalist design principles
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
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

class MinimalistSenseEdGUI:
    """Minimalist GUI interface for SenseEd with clean design"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize minimalist GUI
        
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
        
        # Minimalist color palette
        self.colors = {
            'background': '#ffffff',      # Pure white
            'surface': '#f8f9fa',        # Light gray
            'primary': '#2563eb',        # Blue
            'secondary': '#64748b',      # Slate gray
            'text': '#1e293b',           # Dark slate
            'text_secondary': '#64748b', # Medium gray
            'border': '#e2e8f0',         # Light border
            'accent': '#10b981',         # Green
            'warning': '#f59e0b',        # Amber
            'error': '#ef4444'           # Red
        }
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the minimalist GUI interface"""
        # Create main window
        self.root = tk.Tk()
        self.root.title("SenseEd")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.colors['background'])
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main container with generous padding
        main_container = tk.Frame(self.root, bg=self.colors['background'], padx=32, pady=32)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.columnconfigure(0, weight=2)  # Chat area
        main_container.columnconfigure(1, weight=1)  # Controls area
        main_container.rowconfigure(1, weight=1)
        
        # Header with minimal branding
        self.setup_header(main_container)
        
        # Main content area
        self.setup_main_content(main_container)
        
        # Initialize modules
        self.init_modules()
    
    def setup_header(self, parent):
        """Setup minimal header"""
        header_frame = tk.Frame(parent, bg=self.colors['background'], height=80)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 24))
        header_frame.grid_propagate(False)
        
        # Title with clean typography
        title_label = tk.Label(
            header_frame, 
            text="SenseEd", 
            font=("Segoe UI", 32, "normal"),
            fg=self.colors['text'], 
            bg=self.colors['background']
        )
        title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame, 
            text="AI Learning Assistant", 
            font=("Segoe UI", 14, "normal"),
            fg=self.colors['text_secondary'], 
            bg=self.colors['background']
        )
        subtitle_label.pack(side=tk.LEFT, anchor=tk.W, padx=(12, 0), pady=(8, 0))
        
        # Status indicator
        self.status_indicator = tk.Label(
            header_frame,
            text="●",
            font=("Segoe UI", 16),
            fg=self.colors['secondary'],
            bg=self.colors['background']
        )
        self.status_indicator.pack(side=tk.RIGHT, anchor=tk.E, pady=(8, 0))
        
        self.status_text = tk.Label(
            header_frame,
            text="Ready",
            font=("Segoe UI", 12, "normal"),
            fg=self.colors['text_secondary'],
            bg=self.colors['background']
        )
        self.status_text.pack(side=tk.RIGHT, anchor=tk.E, padx=(8, 0), pady=(8, 0))
    
    def setup_main_content(self, parent):
        """Setup main content area with clean layout"""
        # Chat area
        self.setup_chat_area(parent)
        
        # Controls area
        self.setup_controls_area(parent)
    
    def setup_chat_area(self, parent):
        """Setup clean chat interface"""
        # Chat container with subtle border
        chat_container = tk.Frame(parent, bg=self.colors['surface'], relief='flat', bd=1)
        chat_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 16))
        chat_container.columnconfigure(0, weight=1)
        chat_container.rowconfigure(1, weight=1)
        
        # Chat header
        chat_header = tk.Frame(chat_container, bg=self.colors['surface'], height=48)
        chat_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=16, pady=16)
        chat_header.grid_propagate(False)
        
        chat_title = tk.Label(
            chat_header, 
            text="Conversation", 
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text'], 
            bg=self.colors['surface']
        )
        chat_title.pack(side=tk.LEFT, anchor=tk.W)
        
        # Chat display with clean styling
        self.chat_display = scrolledtext.ScrolledText(
            chat_container, 
            height=20,
            width=60,
            bg=self.colors['background'],
            fg=self.colors['text'],
            font=("Segoe UI", 13),
            insertbackground=self.colors['primary'],
            selectbackground=self.colors['primary'],
            selectforeground=self.colors['background'],
            relief='flat',
            bd=0,
            wrap=tk.WORD,
            padx=16,
            pady=16
        )
        self.chat_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=16, pady=(0, 16))
        
        # Input area with clean design
        input_container = tk.Frame(chat_container, bg=self.colors['surface'])
        input_container.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=16, pady=(0, 16))
        input_container.columnconfigure(0, weight=1)
        
        # Text input with minimal styling
        self.text_input = tk.Entry(
            input_container,
            font=("Inter", 14),
            bg=self.colors['background'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightcolor=self.colors['primary'],
            highlightbackground=self.colors['border']
        )
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 12), pady=12, ipady=8)
        self.text_input.bind('<Return>', self.send_message)
        self.text_input.bind('<FocusIn>', self.on_input_focus_in)
        self.text_input.bind('<FocusOut>', self.on_input_focus_out)
        
        # Send button with clean design
        self.send_button = tk.Button(
            input_container, 
            text="Send", 
            command=self.send_message,
            font=("Inter", 14, "bold"),
            bg=self.colors['primary'],
            fg=self.colors['background'],
            relief='flat',
            bd=0,
            padx=24,
            pady=12,
            cursor='hand2',
            activebackground=self.colors['primary'],
            activeforeground=self.colors['background']
        )
        self.send_button.grid(row=0, column=1, padx=(0, 0), pady=12)
        
        # Voice button
        self.voice_button = tk.Button(
            input_container, 
            text="🎤", 
            command=self.start_voice_input,
            font=("Segoe UI", 16),
            bg=self.colors['surface'],
            fg=self.colors['text_secondary'],
            relief='flat',
            bd=1,
            padx=16,
            pady=12,
            cursor='hand2',
            activebackground=self.colors['border'],
            activeforeground=self.colors['text']
        )
        self.voice_button.grid(row=0, column=2, padx=(12, 0), pady=12)
        
        # File upload button
        self.file_button = tk.Button(
            input_container, 
            text="📁", 
            command=self.upload_file,
            font=("Segoe UI", 16),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            relief='flat',
            bd=0,
            padx=12,
            pady=12,
            cursor='hand2',
            activebackground=self.colors['border'],
            activeforeground=self.colors['text']
        )
        self.file_button.grid(row=0, column=3, padx=(12, 0), pady=12)
    
    def setup_controls_area(self, parent):
        """Setup minimal controls area"""
        # Controls container
        controls_container = tk.Frame(parent, bg=self.colors['surface'], relief='flat', bd=1)
        controls_container.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        controls_container.columnconfigure(0, weight=1)
        
        # Camera section
        self.setup_camera_section(controls_container)
        
        # Sign language section
        self.setup_sign_language_section(controls_container)
        
        # Vision analysis section
        self.setup_vision_section(controls_container)
        
        # Speech controls section
        self.setup_speech_section(controls_container)
        
        # Session controls section
        self.setup_session_section(controls_container)
    
    def setup_camera_section(self, parent):
        """Setup camera controls with minimal design"""
        # Section header
        section_header = tk.Frame(parent, bg=self.colors['surface'], height=48)
        section_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=16, pady=(16, 8))
        section_header.grid_propagate(False)
        
        section_title = tk.Label(
            section_header, 
            text="Camera", 
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text'], 
            bg=self.colors['surface']
        )
        section_title.pack(side=tk.LEFT, anchor=tk.W)
        
        # Camera display with clean border
        self.camera_label = tk.Label(
            parent, 
            text="Camera not active", 
            font=("Inter", 12),
            bg=self.colors['background'], 
            fg=self.colors['text_secondary'],
            relief='flat', 
            bd=1,
            padx=16,
            pady=16
        )
        self.camera_label.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=16, pady=(0, 16))
        
        # Camera controls
        camera_controls = tk.Frame(parent, bg=self.colors['surface'])
        camera_controls.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=16, pady=(0, 16))
        camera_controls.columnconfigure(0, weight=1)
        camera_controls.columnconfigure(1, weight=1)
        
        self.camera_button = tk.Button(
            camera_controls, 
            text="Start Camera", 
            command=self.toggle_camera,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['primary'], 
            fg=self.colors['background'],
            relief='flat', 
            bd=0, 
            padx=16, 
            pady=8,
            cursor='hand2'
        )
        self.camera_button.grid(row=0, column=0, padx=(0, 8), sticky=(tk.W, tk.E))
        
        self.gesture_button = tk.Button(
            camera_controls, 
            text="Gestures", 
            command=self.toggle_gesture_tracking,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['surface'], 
            fg=self.colors['text'],
            relief='flat', 
            bd=1, 
            padx=16, 
            pady=8,
            cursor='hand2'
        )
        self.gesture_button.grid(row=0, column=1, padx=(8, 0), sticky=(tk.W, tk.E))
    
    def setup_sign_language_section(self, parent):
        """Setup sign language recognition controls"""
        # Section header
        section_header = tk.Frame(parent, bg=self.colors['surface'], height=48)
        section_header.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=16, pady=(16, 8))
        section_header.grid_propagate(False)
        
        section_title = tk.Label(
            section_header, 
            text="Sign Language", 
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text'], 
            bg=self.colors['surface']
        )
        section_title.pack(side=tk.LEFT, anchor=tk.W)
        
        # Sign language controls
        sign_controls = tk.Frame(parent, bg=self.colors['surface'])
        sign_controls.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=16, pady=(0, 16))
        sign_controls.columnconfigure(0, weight=1)
        sign_controls.columnconfigure(1, weight=1)
        
        # Sign language recognition button
        self.sign_language_button = tk.Button(
            sign_controls, 
            text="Start Sign Language", 
            command=self.toggle_sign_language,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['accent'], 
            fg=self.colors['background'],
            relief='flat', 
            bd=0, 
            padx=16, 
            pady=8,
            cursor='hand2'
        )
        self.sign_language_button.grid(row=0, column=0, padx=(0, 8), pady=4, sticky=(tk.W, tk.E))
        
        # Show phrases button
        phrases_button = tk.Button(
            sign_controls, 
            text="Show Phrases", 
            command=self.show_sign_language_phrases,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['surface'], 
            fg=self.colors['text'],
            relief='flat', 
            bd=1, 
            padx=16, 
            pady=8,
            cursor='hand2'
        )
        phrases_button.grid(row=0, column=1, padx=(8, 0), pady=4, sticky=(tk.W, tk.E))
        
        # Status label
        self.sign_language_status = tk.Label(
            sign_controls,
            text="Sign language recognition ready",
            font=("Segoe UI", 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['surface']
        )
        self.sign_language_status.grid(row=1, column=0, columnspan=2, pady=4, sticky=(tk.W, tk.E))
    
    def setup_vision_section(self, parent):
        """Setup vision analysis controls"""
        # Section header
        section_header = tk.Frame(parent, bg=self.colors['surface'], height=48)
        section_header.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=16, pady=(16, 8))
        section_header.grid_propagate(False)
        
        section_title = tk.Label(
            section_header, 
            text="Vision Analysis", 
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text'], 
            bg=self.colors['surface']
        )
        section_title.pack(side=tk.LEFT, anchor=tk.W)
        
        # Vision buttons with clean grid
        vision_buttons = tk.Frame(parent, bg=self.colors['surface'])
        vision_buttons.grid(row=6, column=0, sticky=(tk.W, tk.E), padx=16, pady=(0, 16))
        vision_buttons.columnconfigure(0, weight=1)
        vision_buttons.columnconfigure(1, weight=1)
        
        # OCR button
        ocr_button = tk.Button(
            vision_buttons, 
            text="Extract Text", 
            command=self.analyze_ocr,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['surface'], 
            fg=self.colors['text'],
            relief='flat', 
            bd=1, 
            padx=12, 
            pady=8,
            cursor='hand2'
        )
        ocr_button.grid(row=0, column=0, padx=(0, 8), pady=4, sticky=(tk.W, tk.E))
        
        # Object detection button
        object_button = tk.Button(
            vision_buttons, 
            text="Detect Objects", 
            command=self.analyze_objects,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['surface'], 
            fg=self.colors['text'],
            relief='flat', 
            bd=1, 
            padx=12, 
            pady=8,
            cursor='hand2'
        )
        object_button.grid(row=0, column=1, padx=(8, 0), pady=4, sticky=(tk.W, tk.E))
        
        # Scene description button
        scene_button = tk.Button(
            vision_buttons, 
            text="Describe Scene", 
            command=self.analyze_scene,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['surface'], 
            fg=self.colors['text'],
            relief='flat', 
            bd=1, 
            padx=12, 
            pady=8,
            cursor='hand2'
        )
        scene_button.grid(row=1, column=0, columnspan=2, pady=4, sticky=(tk.W, tk.E))
    
    def setup_speech_section(self, parent):
        """Setup speech controls"""
        # Section header
        section_header = tk.Frame(parent, bg=self.colors['surface'], height=48)
        section_header.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=16, pady=(16, 8))
        section_header.grid_propagate(False)
        
        section_title = tk.Label(
            section_header, 
            text="Speech", 
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text'], 
            bg=self.colors['surface']
        )
        section_title.pack(side=tk.LEFT, anchor=tk.W)
        
        # Speech button
        speech_controls = tk.Frame(parent, bg=self.colors['surface'])
        speech_controls.grid(row=6, column=0, sticky=(tk.W, tk.E), padx=16, pady=(0, 16))
        
        self.tts_button = tk.Button(
            speech_controls, 
            text="Speak Response", 
            command=self.speak_last_response,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['accent'], 
            fg=self.colors['background'],
            relief='flat', 
            bd=0, 
            padx=16, 
            pady=8,
            cursor='hand2'
        )
        self.tts_button.grid(row=0, column=0, pady=4, sticky=(tk.W, tk.E))
    
    def setup_session_section(self, parent):
        """Setup session controls"""
        # Section header
        section_header = tk.Frame(parent, bg=self.colors['surface'], height=48)
        section_header.grid(row=7, column=0, sticky=(tk.W, tk.E), padx=16, pady=(16, 8))
        section_header.grid_propagate(False)
        
        section_title = tk.Label(
            section_header, 
            text="Session", 
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text'], 
            bg=self.colors['surface']
        )
        section_title.pack(side=tk.LEFT, anchor=tk.W)
        
        # Session buttons
        session_controls = tk.Frame(parent, bg=self.colors['surface'])
        session_controls.grid(row=8, column=0, sticky=(tk.W, tk.E), padx=16, pady=(0, 16))
        session_controls.columnconfigure(0, weight=1)
        session_controls.columnconfigure(1, weight=1)
        
        start_button = tk.Button(
            session_controls, 
            text="Start", 
            command=self.start_session,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['accent'], 
            fg=self.colors['background'],
            relief='flat', 
            bd=0, 
            padx=16, 
            pady=8,
            cursor='hand2'
        )
        start_button.grid(row=0, column=0, padx=(0, 8), pady=4, sticky=(tk.W, tk.E))
        
        stop_button = tk.Button(
            session_controls, 
            text="Stop", 
            command=self.stop_session,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['error'], 
            fg=self.colors['background'],
            relief='flat', 
            bd=0, 
            padx=16, 
            pady=8,
            cursor='hand2'
        )
        stop_button.grid(row=0, column=1, padx=(8, 0), pady=4, sticky=(tk.W, tk.E))
        
        help_button = tk.Button(
            session_controls, 
            text="Help", 
            command=self.show_help,
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['surface'], 
            fg=self.colors['text'],
            relief='flat', 
            bd=1, 
            padx=16, 
            pady=8,
            cursor='hand2'
        )
        help_button.grid(row=1, column=0, columnspan=2, pady=4, sticky=(tk.W, tk.E))
    
    def on_input_focus_in(self, event):
        """Handle input focus in"""
        self.text_input.config(highlightbackground=self.colors['primary'])
    
    def on_input_focus_out(self, event):
        """Handle input focus out"""
        self.text_input.config(highlightbackground=self.colors['border'])
    
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
            
            self.update_status("Ready", "success")
            self.add_message("System", "SenseEd initialized successfully. Click 'Start' to begin.")
            
        except Exception as e:
            self.update_status(f"Error: {e}", "error")
            self.add_message("System", f"Error: {e}")
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update status with color coding"""
        colors = {
            "success": self.colors['accent'],
            "error": self.colors['error'],
            "warning": self.colors['warning'],
            "info": self.colors['secondary']
        }
        
        self.status_indicator.config(fg=colors.get(status_type, self.colors['secondary']))
        self.status_text.config(text=message)
        self.root.update_idletasks()
    
    def add_message(self, sender: str, message: str):
        """Add message to chat display with clean formatting"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        
        # Clean formatting without excessive colors
        if sender == "System":
            formatted_message = f"[{timestamp}] {message}\n"
        elif sender == "SenseEd":
            formatted_message = f"[{timestamp}] SenseEd: {message}\n"
        else:
            formatted_message = f"[{timestamp}] {sender}: {message}\n"
        
        # Insert message
        self.chat_display.insert(tk.END, formatted_message)
        
        # Scroll to bottom and update
        self.chat_display.see(tk.END)
        self.root.update_idletasks()
    
    # Camera and Vision Methods (simplified from original)
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
                self.camera_button.config(text="Stop Camera", bg=self.colors['error'])
                self.update_status("Camera active", "success")
                self.add_message("System", "Camera started.")
                
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
            self.camera_button.config(text="Start Camera", bg=self.colors['primary'])
            self.gesture_button.config(text="Gestures", bg=self.colors['surface'])
            self.update_status("Ready", "info")
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
                    # Only detect when gesture tracking is explicitly enabled AND user is performing gestures
                    if self.gesture_tracking and self.gesture_module and frame_count % 5 == 0:
                        # Check for sign language recognition if active
                        if self.sign_language_active:
                            sign_result = self.gesture_module.detect_sign_language(frame)
                            if sign_result and sign_result.get('phrase') and sign_result.get('status') == 'completed':
                                self.process_sign_language(sign_result)
                        
                        # Also check for basic gestures
                        gestures = self.gesture_module.get_gesture_info(frame)
                        if gestures:
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
            max_width, max_height = 300, 200
            
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
            self.gesture_button.config(text="Stop Gestures", bg=self.colors['error'])
            self.add_message("System", "Gesture tracking started")
        else:
            self.gesture_button.config(text="Gestures", bg=self.colors['surface'])
            self.add_message("System", "Gesture tracking stopped")
    
    def process_gestures(self, gestures):
        """Process detected gestures"""
        for gesture_data in gestures:
            hand = gesture_data['hand']
            gesture = gesture_data['gesture']
            self.add_message("Gesture", f"{hand} hand: {gesture}")
    
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
    
    def toggle_sign_language(self):
        """Toggle sign language recognition"""
        if hasattr(self, 'sign_language_active'):
            self.sign_language_active = not self.sign_language_active
        else:
            self.sign_language_active = True
        
        if self.sign_language_active:
            self.sign_language_button.config(text="Stop Sign Language", bg=self.colors['accent'])
            self.sign_language_status.config(text="Sign language recognition active")
            self.add_message("System", "Sign language recognition started")
        else:
            self.sign_language_button.config(text="Start Sign Language", bg=self.colors['surface'])
            self.sign_language_status.config(text="Sign language recognition ready")
            self.add_message("System", "Sign language recognition stopped")
    
    def show_sign_language_phrases(self):
        """Show available sign language phrases"""
        if self.gesture_module:
            phrases = self.gesture_module.get_sign_language_phrases()
            if phrases:
                # Show first 20 phrases
                display_phrases = phrases[:20]
                phrases_text = "Available Sign Language Phrases:\n\n" + "\n".join(f"• {phrase}" for phrase in display_phrases)
                if len(phrases) > 20:
                    phrases_text += f"\n\n... and {len(phrases) - 20} more phrases"
                
                self.add_message("Sign Language", phrases_text)
            else:
                self.add_message("Sign Language", "No sign language phrases available")
        else:
            self.add_message("Sign Language", "Sign language module not available")
    
    # Vision Analysis Methods (simplified)
    def analyze_ocr(self):
        """Analyze current frame for text using OCR"""
        if self.current_frame is None:
            self.add_message("System", "No frame available for OCR analysis")
            return
        
        try:
            result = self.vision_module.extract_text_from_image(self.current_frame)
            if result['success'] and result['text']:
                self.add_message("OCR", f"Extracted: {result['text']}")
                self.process_vision_input("text", result['text'])
            else:
                self.add_message("OCR", "No text found")
        except Exception as e:
            self.add_message("System", f"OCR error: {e}")
    
    def analyze_objects(self):
        """Analyze current frame for objects"""
        if self.current_frame is None:
            self.add_message("System", "No frame available for object analysis")
            return
        
        try:
            result = self.vision_module.detect_objects(self.current_frame)
            if result['success'] and result['objects']:
                objects_text = ", ".join([f"{obj['class']}" for obj in result['objects'][:3]])
                self.add_message("Objects", f"Detected: {objects_text}")
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
                self.process_vision_input("scene", result['description'])
            else:
                self.add_message("Scene", "Failed to describe scene")
        except Exception as e:
            self.add_message("System", f"Scene analysis error: {e}")
    
    def process_vision_input(self, input_type, content):
        """Process vision analysis results with chatbot"""
        try:
            if not self.chatbot:
                self.add_message("System", "Chatbot not available")
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
    
    # Speech Methods (simplified)
    def start_voice_input(self):
        """Start voice input"""
        try:
            if not self.speech_module:
                self.add_message("System", "Speech module not initialized")
                return
            
            # Update button appearance
            self.voice_button.config(text="🎤...", bg=self.colors['warning'])
            self.update_status("Listening...", "warning")
            
            # Start voice input in thread
            thread = threading.Thread(target=self.process_voice_input)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.add_message("System", f"Error starting voice input: {e}")
            self.voice_button.config(text="🎤", bg=self.colors['surface'])
    
    def process_voice_input(self):
        """Process voice input in background thread"""
        try:
            text = self.speech_module.listen_to_speech(timeout=5, phrase_time_limit=5)
            self.root.after(0, self.handle_voice_result, text)
        except Exception as e:
            self.root.after(0, self.handle_voice_error, str(e))
    
    def handle_voice_result(self, text):
        """Handle voice recognition result"""
        self.voice_button.config(text="🎤", bg=self.colors['surface'])
        self.update_status("Ready", "success")
        
        if text:
            self.add_message("Voice", f"You said: {text}")
            self.process_message(text)
        else:
            self.add_message("Voice", "No speech detected")
    
    def handle_voice_error(self, error):
        """Handle voice recognition error"""
        self.voice_button.config(text="🎤", bg=self.colors['surface'])
        self.update_status("Voice error", "error")
        self.add_message("System", f"Voice input error: {error}")
    
    def upload_file(self):
        """Handle file upload for document processing"""
        try:
            from tkinter import filedialog
            
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
                self.update_status("Processing file...", "warning")
                
                # Process file in background thread
                thread = threading.Thread(target=self.process_uploaded_file, args=(file_path,))
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            self.add_message("System", f"Error uploading file: {e}")
            self.update_status("Upload error", "error")
    
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
                
                self.update_status("File processed successfully", "success")
            else:
                error_msg = result.get('error', 'Unknown error')
                self.add_message("File Upload", f"Failed to process {filename}: {error_msg}")
                self.update_status("File processing failed", "error")
                
        except Exception as e:
            self.add_message("System", f"Error handling file result: {e}")
            self.update_status("File processing error", "error")
    
    def handle_file_processing_error(self, error, file_path):
        """Handle file processing error"""
        filename = os.path.basename(file_path)
        self.add_message("System", f"Error processing {filename}: {error}")
        self.update_status("File processing error", "error")
    
    def speak_last_response(self):
        """Speak the last response from SenseEd"""
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
                    parts = line.split("SenseEd:", 1)
                    if len(parts) > 1:
                        last_response = parts[1].strip()
                        break
            
            if last_response:
                self.add_message("System", "Speaking response...")
                
                # Reset speech module state
                if hasattr(self.speech_module, 'is_speaking'):
                    self.speech_module.is_speaking = False
                
                # Try to speak
                success = self.speech_module.speak_text(last_response, use_gtts=False, interrupt=True)
                if not success:
                    self.speech_module.speak_text(last_response, use_gtts=True, interrupt=True)
                
                if success:
                    self.add_message("System", "Response spoken")
                else:
                    self.add_message("System", "Failed to speak response")
            else:
                self.add_message("System", "No response found to speak")
                
        except Exception as e:
            self.add_message("System", f"Error speaking response: {e}")
    
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
                
                # Auto-speak the response
                self.auto_speak_response(response_text)
            else:
                error_msg = response.get('error', 'Unknown error') if response else 'No response from chatbot'
                self.add_message("System", f"Error: {error_msg}")
                
        except Exception as e:
            self.add_message("System", f"Error processing message: {e}")
    
    def auto_speak_response(self, text: str):
        """Automatically speak SenseEd responses"""
        try:
            if not self.speech_module or not text:
                return
            
            def speak_in_background():
                try:
                    # Reset speech module state
                    if hasattr(self.speech_module, 'is_speaking'):
                        self.speech_module.is_speaking = False
                    
                    # Try to speak
                    success = self.speech_module.speak_text(text, use_gtts=False, interrupt=True)
                    if not success:
                        self.speech_module.speak_text(text, use_gtts=True, interrupt=True)
                except Exception as e:
                    print(f"Auto-speak error: {e}")
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
                self.update_status("Session active", "success")
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
                self.update_status("Session stopped", "info")
                self.add_message("System", "Session stopped.")
            else:
                self.add_message("System", "Chatbot not initialized")
        except Exception as e:
            self.add_message("System", f"Error stopping session: {e}")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
SenseEd - Minimalist AI Learning Assistant

Text Interaction:
• Type messages and press Enter or click Send
• Click 🎤 to speak your message

Camera Features:
• Click "Start Camera" to begin live video feed
• Click "Gestures" to enable hand gesture recognition
• Use "Extract Text" to read text from camera
• Use "Detect Objects" to identify objects in view
• Use "Describe Scene" to get AI description

Speech Features:
• Click 🎤 to speak your input
• Click "Speak Response" to have SenseEd speak its last response

Session Controls:
• Click "Start" to begin interaction
• Click "Stop" to end interaction
• Click "Help" to show this dialog

Features:
• Clean, minimalist interface
• Multimodal interaction (text, voice, vision, gestures)
• Real-time camera feed with gesture recognition
• OCR text extraction from images
• Object detection and scene description
• Voice input and text-to-speech output
        """
        
        messagebox.showinfo("SenseEd Help", help_text)
    
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


