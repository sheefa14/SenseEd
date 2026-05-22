# config.py
import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
import platform

@dataclass
class SpeechConfig:
    """Configuration for speech module"""
    speech_rate: int = 150
    speech_volume: float = 0.9
    voice_id: Optional[int] = None
    use_gtts: bool = True
    timeout: int = 5
    phrase_time_limit: int = 5
    language: str = 'en'

@dataclass
class VisionConfig:
    """Configuration for vision module"""
    camera_index: int = 0
    camera_width: int = 1280
    camera_height: int = 720
    camera_fps: int = 30
    yolo_model_path: str = 'yolov8n.pt'
    ocr_language: str = 'eng'
    confidence_threshold: float = 0.5

@dataclass
class GestureConfig:
    """Configuration for gesture module"""
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.5
    max_num_hands: int = 2
    gesture_timeout: int = 3

@dataclass
class TextConfig:
    """Configuration for text module"""
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_formats: List[str] = None
    default_encoding: str = 'utf-8'
    max_summary_length: int = 150
    num_keywords: int = 10
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.txt', '.pdf', '.docx', '.csv', '.html', '.htm']

@dataclass
class NLPConfig:
    """Configuration for NLP processor"""
    model_name: str = 'en_core_web_sm'
    qa_model: str = 'distilbert-base-cased-distilled-squad'
    sentiment_model: str = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
    text_generation_model: str = 'gpt2'
    max_response_length: int = 100
    temperature: float = 0.7

@dataclass
class AccessibilityConfig:
    """Configuration for accessibility features"""
    high_contrast: bool = False
    large_text: bool = False
    audio_feedback: bool = True
    haptic_feedback: bool = False
    screen_reader_compatible: bool = True
    keyboard_navigation: bool = True
    voice_commands: bool = True
    gesture_commands: bool = True

@dataclass
class LearningConfig:
    """Configuration for learning features"""
    adaptive_learning: bool = True
    progress_tracking: bool = True
    difficulty_adjustment: bool = True
    content_personalization: bool = True
    learning_analytics: bool = True
    feedback_frequency: str = 'medium'  # low, medium, high

@dataclass
class SystemConfig:
    """System-wide configuration"""
    log_level: str = 'INFO'
    log_file: str = 'senseed.log'
    data_directory: str = 'data'
    models_directory: str = 'models'
    cache_directory: str = 'cache'
    response_timeout: float = 0.9  # Target response time in seconds
    max_concurrent_requests: int = 5
    debug_mode: bool = False

class ConfigManager:
    """Configuration manager for SenseEd system"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file (JSON or YAML)
        """
        self.config_file = config_file or self._get_default_config_path()
        self.setup_logging()
        self.load_config()
    
    def setup_logging(self):
        """Setup logging for config manager"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        config_dir = Path.home() / '.senseed'
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / 'config.yaml')
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                self._load_from_file()
                self.logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                self.logger.error(f"Failed to load config from {self.config_file}: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _load_from_file(self):
        """Load configuration from file"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        
        # Load each configuration section
        self.speech = SpeechConfig(**config_data.get('speech', {}))
        self.vision = VisionConfig(**config_data.get('vision', {}))
        self.gesture = GestureConfig(**config_data.get('gesture', {}))
        self.text = TextConfig(**config_data.get('text', {}))
        self.nlp = NLPConfig(**config_data.get('nlp', {}))
        self.accessibility = AccessibilityConfig(**config_data.get('accessibility', {}))
        self.learning = LearningConfig(**config_data.get('learning', {}))
        self.system = SystemConfig(**config_data.get('system', {}))
    
    def _create_default_config(self):
        """Create default configuration"""
        self.logger.info("Creating default configuration")
        
        # Create default configurations
        self.speech = SpeechConfig()
        self.vision = VisionConfig()
        self.gesture = GestureConfig()
        self.text = TextConfig()
        self.nlp = NLPConfig()
        self.accessibility = AccessibilityConfig()
        self.learning = LearningConfig()
        self.system = SystemConfig()
        
        # Adjust for platform
        self._adjust_for_platform()
        
        # Save default configuration
        self.save_config()
    
    def _adjust_for_platform(self):
        """Adjust configuration based on platform"""
        system = platform.system()
        
        if system == "Windows":
            # Windows-specific adjustments
            self.speech.use_gtts = True  # Better compatibility
            self.vision.camera_index = 0
        elif system == "Darwin":  # macOS
            # macOS-specific adjustments
            self.speech.use_gtts = False  # Use system TTS
            self.vision.camera_index = 0
        else:  # Linux
            # Linux-specific adjustments
            self.speech.use_gtts = True
            self.vision.camera_index = 0
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'speech': asdict(self.speech),
                'vision': asdict(self.vision),
                'gesture': asdict(self.gesture),
                'text': asdict(self.text),
                'nlp': asdict(self.nlp),
                'accessibility': asdict(self.accessibility),
                'learning': asdict(self.learning),
                'system': asdict(self.system)
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def update_config(self, section: str, **kwargs):
        """
        Update configuration section
        
        Args:
            section: Configuration section name
            **kwargs: Configuration parameters to update
        """
        try:
            if hasattr(self, section):
                config_obj = getattr(self, section)
                for key, value in kwargs.items():
                    if hasattr(config_obj, key):
                        setattr(config_obj, key, value)
                    else:
                        self.logger.warning(f"Unknown configuration parameter: {section}.{key}")
                
                self.save_config()
                self.logger.info(f"Updated {section} configuration")
            else:
                self.logger.error(f"Unknown configuration section: {section}")
                
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            'speech': asdict(self.speech),
            'vision': asdict(self.vision),
            'gesture': asdict(self.gesture),
            'text': asdict(self.text),
            'nlp': asdict(self.nlp),
            'accessibility': asdict(self.accessibility),
            'learning': asdict(self.learning),
            'system': asdict(self.system)
        }
    
    def get_section_config(self, section: str) -> Dict[str, Any]:
        """Get configuration for specific section"""
        if hasattr(self, section):
            return asdict(getattr(self, section))
        else:
            self.logger.error(f"Unknown configuration section: {section}")
            return {}
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration and return list of issues
        
        Returns:
            List of validation issues
        """
        issues = []
        
        # Validate speech config
        if not 50 <= self.speech.speech_rate <= 300:
            issues.append("Speech rate should be between 50 and 300")
        
        if not 0.0 <= self.speech.speech_volume <= 1.0:
            issues.append("Speech volume should be between 0.0 and 1.0")
        
        # Validate vision config
        if self.vision.camera_index < 0:
            issues.append("Camera index should be non-negative")
        
        if not 0.0 <= self.vision.confidence_threshold <= 1.0:
            issues.append("Confidence threshold should be between 0.0 and 1.0")
        
        # Validate gesture config
        if not 0.0 <= self.gesture.min_detection_confidence <= 1.0:
            issues.append("Min detection confidence should be between 0.0 and 1.0")
        
        if not 0.0 <= self.gesture.min_tracking_confidence <= 1.0:
            issues.append("Min tracking confidence should be between 0.0 and 1.0")
        
        # Validate system config
        if self.system.response_timeout <= 0:
            issues.append("Response timeout should be positive")
        
        if self.system.max_concurrent_requests <= 0:
            issues.append("Max concurrent requests should be positive")
        
        return issues
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.logger.info("Resetting configuration to defaults")
        self._create_default_config()
    
    def export_config(self, export_path: str):
        """
        Export configuration to file
        
        Args:
            export_path: Path to export configuration
        """
        try:
            config_data = self.get_config_dict()
            
            with open(export_path, 'w', encoding='utf-8') as f:
                if export_path.endswith('.yaml') or export_path.endswith('.yml'):
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Configuration exported to {export_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
    
    def import_config(self, import_path: str):
        """
        Import configuration from file
        
        Args:
            import_path: Path to import configuration from
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                if import_path.endswith('.yaml') or import_path.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Update configurations
            if 'speech' in config_data:
                self.speech = SpeechConfig(**config_data['speech'])
            if 'vision' in config_data:
                self.vision = VisionConfig(**config_data['vision'])
            if 'gesture' in config_data:
                self.gesture = GestureConfig(**config_data['gesture'])
            if 'text' in config_data:
                self.text = TextConfig(**config_data['text'])
            if 'nlp' in config_data:
                self.nlp = NLPConfig(**config_data['nlp'])
            if 'accessibility' in config_data:
                self.accessibility = AccessibilityConfig(**config_data['accessibility'])
            if 'learning' in config_data:
                self.learning = LearningConfig(**config_data['learning'])
            if 'system' in config_data:
                self.system = SystemConfig(**config_data['system'])
            
            self.save_config()
            self.logger.info(f"Configuration imported from {import_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")

# Global configuration instance
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    return config_manager