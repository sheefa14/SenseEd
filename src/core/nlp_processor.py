# nlp_processor.py
import nltk
import spacy
import logging
from typing import Optional, Dict, List, Any, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from textblob import TextBlob
import re
import json
from datetime import datetime

class NLPProcessor:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize NLP processor with enhanced capabilities
        
        Args:
            config: Configuration dictionary with NLP settings
        """
        self.config = config or {}
        self.setup_logging()
        self.initialize_models()
        self.setup_nltk_data()
        
    def setup_logging(self):
        """Setup logging for NLP processor"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def setup_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk_data = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'vader_lexicon']
            for data in nltk_data:
                try:
                    nltk.data.find(f'tokenizers/{data}')
                except LookupError:
                    nltk.download(data, quiet=True)
            self.logger.info("NLTK data setup completed")
        except Exception as e:
            self.logger.warning(f"NLTK data setup failed: {e}")
    
    def initialize_models(self):
        """Initialize NLP models with error handling"""
        try:
            # Initialize spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.info("spaCy model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load spaCy model: {e}")
            self.nlp = None
        
        try:
            # Initialize question-answering pipeline
            self.qa_pipeline = pipeline("question-answering", 
                                      model="distilbert-base-cased-distilled-squad")
            self.logger.info("QA pipeline loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load QA pipeline: {e}")
            self.qa_pipeline = None
        
        try:
            # Initialize sentiment analysis pipeline
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.logger.info("Sentiment analyzer loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load sentiment analyzer: {e}")
            self.sentiment_analyzer = None
        
        try:
            # Initialize text generation pipeline
            self.text_generator = pipeline("text-generation", 
                                         model="gpt2", 
                                         max_length=100,
                                         do_sample=True,
                                         temperature=0.7)
            self.logger.info("Text generator loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load text generator: {e}")
            self.text_generator = None
    
    def process_query(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Process user query with enhanced NLP capabilities
        
        Args:
            text: Input text to process
            context: Additional context for processing
            
        Returns:
            Dictionary with processing results
        """
        if not text or not text.strip():
            return {
                "original_text": text,
                "success": False,
                "error": "Empty text provided"
            }
        
        try:
            results = {
                "original_text": text,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            # Basic text processing
            if self.nlp:
                doc = self.nlp(text)
                results.update({
                    "entities": [(ent.text, ent.label_) for ent in doc.ents],
                    "tokens": [token.text for token in doc],
                    "lemmas": [token.lemma_ for token in doc],
                    "pos_tags": [(token.text, token.pos_) for token in doc],
                    "sentences": [sent.text for sent in doc.sents]
                })
            
            # Intent classification
            results["intent"] = self.classify_intent(text)
            
            # Sentiment analysis
            results["sentiment"] = self.analyze_sentiment(text)
            
            # Extract key information
            results["keywords"] = self.extract_keywords(text)
            results["questions"] = self.extract_questions(text)
            results["commands"] = self.extract_commands(text)
            
            # Generate response if requested
            if context:
                results["response"] = self.generate_response(text, context)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            return {
                "original_text": text,
                "success": False,
                "error": str(e)
            }
    
    def classify_intent(self, text: str) -> str:
        """
        Enhanced intent classification with more categories
        
        Args:
            text: Input text
            
        Returns:
            Classified intent
        """
        text_lower = text.lower()
        
        # Define intent patterns
        intent_patterns = {
            "question": [
                r'\b(what|how|why|when|where|who|which|can|could|would|should|is|are|do|does|did)\b',
                r'\?'
            ],
            "command": [
                r'\b(show|tell|read|explain|help|open|close|start|stop|run|execute|create|make|generate)\b'
            ],
            "conversion": [
                r'\b(convert|translate|change|transform|switch|turn)\b'
            ],
            "greeting": [
                r'\b(hello|hi|hey|good morning|good afternoon|good evening|greetings)\b'
            ],
            "farewell": [
                r'\b(goodbye|bye|see you|farewell|exit|quit|stop)\b'
            ],
            "request": [
                r'\b(please|can you|could you|would you|i need|i want|i would like)\b'
            ],
            "confirmation": [
                r'\b(yes|no|okay|ok|sure|certainly|absolutely|definitely|maybe|perhaps)\b'
            ],
            "education": [
                r'\b(learn|study|teach|explain|understand|know|lesson|course|tutorial)\b'
            ],
            "accessibility": [
                r'\b(read|speak|listen|see|hear|access|accessible|help|assist|support)\b'
            ]
        }
        
        # Score each intent
        intent_scores = {}
        for intent, patterns in intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            intent_scores[intent] = score
        
        # Return intent with highest score, default to 'general'
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            if intent_scores[best_intent] > 0:
                return best_intent
        
        return "general"
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using multiple methods
        
        Args:
            text: Input text
            
        Returns:
            Sentiment analysis results
        """
        results = {}
        
        try:
            # TextBlob sentiment
            blob = TextBlob(text)
            results['textblob'] = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
            
            # Transformers sentiment analysis
            if self.sentiment_analyzer:
                sentiment_result = self.sentiment_analyzer(text)
                results['transformers'] = {
                    'label': sentiment_result[0]['label'],
                    'score': sentiment_result[0]['score']
                }
            
            # NLTK VADER sentiment
            try:
                from nltk.sentiment import SentimentIntensityAnalyzer
                sia = SentimentIntensityAnalyzer()
                vader_scores = sia.polarity_scores(text)
                results['vader'] = vader_scores
            except Exception as e:
                self.logger.warning(f"VADER sentiment analysis failed: {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return {'error': str(e)}
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        try:
            if not self.nlp:
                # Fallback to simple word frequency
                words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                word_freq = {}
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                return sorted(word_freq, key=word_freq.get, reverse=True)[:num_keywords]
            
            # Use spaCy for better keyword extraction
            doc = self.nlp(text)
            keywords = []
            
            # Extract nouns and proper nouns
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    not token.is_stop and 
                    not token.is_punct and 
                    len(token.text) > 2):
                    keywords.append(token.lemma_.lower())
            
            # Count frequency and return top keywords
            keyword_freq = {}
            for keyword in keywords:
                keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
            
            return sorted(keyword_freq, key=keyword_freq.get, reverse=True)[:num_keywords]
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def extract_questions(self, text: str) -> List[str]:
        """Extract questions from text"""
        try:
            questions = []
            sentences = re.split(r'[.!?]+', text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and ('?' in sentence or 
                               sentence.lower().startswith(('what', 'how', 'why', 'when', 'where', 'who', 'which', 'can', 'could', 'would', 'should', 'is', 'are', 'do', 'does', 'did'))):
                    questions.append(sentence)
            
            return questions
            
        except Exception as e:
            self.logger.error(f"Question extraction failed: {e}")
            return []
    
    def extract_commands(self, text: str) -> List[str]:
        """Extract commands from text"""
        try:
            commands = []
            sentences = re.split(r'[.!?]+', text)
            
            command_verbs = ['show', 'tell', 'read', 'explain', 'help', 'open', 'close', 
                           'start', 'stop', 'run', 'execute', 'create', 'make', 'generate',
                           'convert', 'translate', 'change', 'transform']
            
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    words = sentence.lower().split()
                    if words and words[0] in command_verbs:
                        commands.append(sentence)
            
            return commands
            
        except Exception as e:
            self.logger.error(f"Command extraction failed: {e}")
            return []
    
    def generate_response(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        Generate response to user query
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Generated response
        """
        try:
            intent = self.classify_intent(query)
            
            # Generate response based on intent
            if intent == "greeting":
                response = self._generate_greeting_response()
            elif intent == "question":
                response = self._generate_question_response(query, context)
            elif intent == "command":
                response = self._generate_command_response(query, context)
            elif intent == "education":
                response = self._generate_educational_response(query, context)
            elif intent == "accessibility":
                response = self._generate_accessibility_response(query, context)
            else:
                response = self._generate_general_response(query, context)
            
            return {
                'response': response,
                'intent': intent,
                'confidence': 0.8,  # Placeholder confidence score
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            return {
                'response': "I'm sorry, I couldn't generate a response at the moment.",
                'error': str(e),
                'success': False
            }
    
    def _generate_greeting_response(self) -> str:
        """Generate greeting response"""
        greetings = [
            "Hello! I'm SenseEd, your AI learning assistant. How can I help you today?",
            "Hi there! I'm here to help with your learning needs. What would you like to know?",
            "Greetings! I'm SenseEd, ready to assist you with accessible learning. How can I help?"
        ]
        import random
        return random.choice(greetings)
    
    def _generate_question_response(self, query: str, context: str) -> str:
        """Generate response to questions"""
        if self.qa_pipeline and context:
            try:
                result = self.qa_pipeline(question=query, context=context)
                return result['answer']
            except Exception as e:
                self.logger.warning(f"QA pipeline failed: {e}")
        
        # Fallback response
        return f"I understand you're asking about: {query}. Let me help you with that. Could you provide more context or be more specific?"
    
    def _generate_command_response(self, query: str, context: str) -> str:
        """Generate response to commands"""
        return f"I'll help you with that command: {query}. Let me process your request."
    
    def _generate_educational_response(self, query: str, context: str) -> str:
        """Generate educational response"""
        return f"That's a great learning question! Let me help you understand: {query}. I'll provide an accessible explanation."
    
    def _generate_accessibility_response(self, query: str, context: str) -> str:
        """Generate accessibility-focused response"""
        return f"I'm here to make learning accessible for you. Let me help with: {query}. I'll ensure the information is presented in a way that works for your needs."
    
    def _generate_general_response(self, query: str, context: str) -> str:
        """Generate general response"""
        return f"I understand you're saying: {query}. How can I assist you with that?"
    
    def answer_question(self, question: str, context: str = "") -> str:
        """
        Answer a specific question using QA pipeline
        
        Args:
            question: Question to answer
            context: Context to search for answer
            
        Returns:
            Answer to the question
        """
        if not self.qa_pipeline:
            return "I'm sorry, I don't have the question-answering capability available right now."
        
        if not context:
            return "I need some context to answer your question. Could you provide more information?"
        
        try:
            result = self.qa_pipeline(question=question, context=context)
            return result['answer']
        except Exception as e:
            self.logger.error(f"Question answering failed: {e}")
            return "I'm sorry, I couldn't process your question at the moment."
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get NLP processor status"""
        return {
            'spacy_available': self.nlp is not None,
            'qa_pipeline_available': self.qa_pipeline is not None,
            'sentiment_analyzer_available': self.sentiment_analyzer is not None,
            'text_generator_available': self.text_generator is not None
        }



