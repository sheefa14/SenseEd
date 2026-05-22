# text_module.py
import os
import logging
from typing import Optional, Dict, List, Any, Union
import re
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import nltk
from textblob import TextBlob

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️  spaCy not available - some NLP features disabled")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers not available - summarization disabled")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PyPDF2 not available - PDF reading disabled")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️  python-docx not available - DOCX reading disabled")

class TextModule:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize text processing module for document reading and text conversion
        
        Args:
            config: Configuration dictionary with text processing settings
        """
        self.config = config or {}
        self.setup_logging()
        self.initialize_nlp_models()
        
    def setup_logging(self):
        """Setup logging for text module"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def initialize_nlp_models(self):
        """Initialize NLP models for text processing"""
        self.nlp = None
        self.summarizer = None
        
        if SPACY_AVAILABLE:
            try:
                # Initialize spaCy model
                self.nlp = spacy.load("en_core_web_sm")
                self.logger.info("spaCy model loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load spaCy model: {e}")
                self.nlp = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                # Initialize summarization pipeline
                self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
                self.logger.info("Summarization model loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load summarization model: {e}")
                self.summarizer = None
    
    def read_document(self, file_path: str) -> Dict[str, Any]:
        """
        Read text from various document formats with enhanced detail extraction
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary with extracted text, metadata, and structured information
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'content': '',
                'success': False,
                'error': f"File not found: {file_path}"
            }
        
        file_extension = file_path.suffix.lower()
        
        try:
            # Read the basic content
            if file_extension == '.txt':
                result = self._read_text_file(file_path)
            elif file_extension == '.pdf' and PDF_AVAILABLE:
                result = self._read_pdf_file(file_path)
            elif file_extension == '.docx' and DOCX_AVAILABLE:
                result = self._read_docx_file(file_path)
            elif file_extension == '.csv':
                result = self._read_csv_file(file_path)
            elif file_extension in ['.html', '.htm']:
                result = self._read_html_file(file_path)
            else:
                return {
                    'content': '',
                    'success': False,
                    'error': f"Unsupported file format: {file_extension}"
                }
            
            if result.get('success', False):
                # Extract additional details and structure
                text_content = result.get('text', '')
                enhanced_result = self._extract_document_details(text_content, file_path)
                
                # Merge results
                result.update(enhanced_result)
                result['content'] = text_content  # Rename for consistency
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error reading document {file_path}: {e}")
            return {
                'content': '',
                'success': False,
                'error': str(e)
            }
    
    def _read_text_file(self, file_path: Path) -> Dict[str, Any]:
        """Read plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return {
                'text': text,
                'success': True,
                'file_type': 'text',
                'file_size': file_path.stat().st_size
            }
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                return {
                    'text': text,
                    'success': True,
                    'file_type': 'text',
                    'file_size': file_path.stat().st_size,
                    'encoding': 'latin-1'
                }
            except Exception as e:
                return {
                    'text': '',
                    'success': False,
                    'error': f"Encoding error: {e}"
                }
    
    def _read_pdf_file(self, file_path: Path) -> Dict[str, Any]:
        """Read PDF file"""
        if not PDF_AVAILABLE:
            return {
                'text': '',
                'success': False,
                'error': 'PDF support not available'
            }
        
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return {
                'text': text.strip(),
                'success': True,
                'file_type': 'pdf',
                'file_size': file_path.stat().st_size,
                'pages': len(pdf_reader.pages)
            }
        except Exception as e:
            return {
                'text': '',
                'success': False,
                'error': f"PDF reading error: {e}"
            }
    
    def _read_docx_file(self, file_path: Path) -> Dict[str, Any]:
        """Read DOCX file"""
        if not DOCX_AVAILABLE:
            return {
                'text': '',
                'success': False,
                'error': 'DOCX support not available'
            }
        
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return {
                'text': text.strip(),
                'success': True,
                'file_type': 'docx',
                'file_size': file_path.stat().st_size
            }
        except Exception as e:
            return {
                'text': '',
                'success': False,
                'error': f"DOCX reading error: {e}"
            }
    
    def _read_csv_file(self, file_path: Path) -> Dict[str, Any]:
        """Read CSV file and convert to text"""
        try:
            df = pd.read_csv(file_path)
            # Convert DataFrame to readable text format
            text = df.to_string(index=False)
            
            return {
                'text': text,
                'success': True,
                'file_type': 'csv',
                'file_size': file_path.stat().st_size,
                'rows': len(df),
                'columns': len(df.columns)
            }
        except Exception as e:
            return {
                'text': '',
                'success': False,
                'error': f"CSV reading error: {e}"
            }
    
    def _read_html_file(self, file_path: Path) -> Dict[str, Any]:
        """Read HTML file and extract text"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            
            return {
                'text': text.strip(),
                'success': True,
                'file_type': 'html',
                'file_size': file_path.stat().st_size
            }
        except Exception as e:
            return {
                'text': '',
                'success': False,
                'error': f"HTML reading error: {e}"
            }
    
    def read_web_content(self, url: str) -> Dict[str, Any]:
        """
        Read text content from a web URL
        
        Args:
            url: Web URL to read content from
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    'text': '',
                    'success': False,
                    'error': 'Invalid URL format'
                }
            
            # Fetch content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                'text': text,
                'success': True,
                'url': url,
                'title': soup.title.string if soup.title else '',
                'content_length': len(text)
            }
            
        except requests.RequestException as e:
            return {
                'text': '',
                'success': False,
                'error': f"Network error: {e}"
            }
        except Exception as e:
            return {
                'text': '',
                'success': False,
                'error': f"Content extraction error: {e}"
            }
    
    def process_text(self, text: str, operations: List[str] = None) -> Dict[str, Any]:
        """
        Process text with various NLP operations
        
        Args:
            text: Input text to process
            operations: List of operations to perform
            
        Returns:
            Dictionary with processing results
        """
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'Empty text provided'
            }
        
        operations = operations or ['sentiment', 'keywords']
        results = {
            'original_text': text,
            'success': True,
            'operations': {}
        }
        
        try:
            # Sentiment analysis
            if 'sentiment' in operations:
                results['operations']['sentiment'] = self._analyze_sentiment(text)
            
            # Text summarization
            if 'summary' in operations and self.summarizer:
                results['operations']['summary'] = self._summarize_text(text)
            
            # Keyword extraction
            if 'keywords' in operations:
                results['operations']['keywords'] = self._extract_keywords(text)
            
            # Text statistics
            if 'stats' in operations:
                results['operations']['stats'] = self._get_text_statistics(text)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Text processing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        try:
            if self.nlp:
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
            else:
                # Fallback to simple word frequency
                words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                word_freq = {}
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                return sorted(word_freq, key=word_freq.get, reverse=True)[:num_keywords]
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def _summarize_text(self, text: str, max_length: int = 150) -> Dict[str, Any]:
        """Summarize text using transformer model"""
        if not self.summarizer:
            return {'error': 'Summarization model not available'}
        
        try:
            # Split text into chunks if too long
            max_chunk_length = 1000
            if len(text) > max_chunk_length:
                chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
                summaries = []
                
                for chunk in chunks:
                    summary = self.summarizer(chunk, max_length=max_length//len(chunks), min_length=30, do_sample=False)
                    summaries.append(summary[0]['summary_text'])
                
                summary_text = ' '.join(summaries)
            else:
                summary = self.summarizer(text, max_length=max_length, min_length=30, do_sample=False)
                summary_text = summary[0]['summary_text']
            
            return {
                'summary': summary_text,
                'original_length': len(text),
                'summary_length': len(summary_text),
                'compression_ratio': len(summary_text) / len(text)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_text_statistics(self, text: str) -> Dict[str, Any]:
        """Get basic text statistics"""
        try:
            blob = TextBlob(text)
            
            return {
                'character_count': len(text),
                'word_count': len(blob.words),
                'sentence_count': len(blob.sentences),
                'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
                'average_word_length': sum(len(word) for word in blob.words) / len(blob.words) if blob.words else 0,
                'average_sentence_length': len(blob.words) / len(blob.sentences) if blob.sentences else 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_document_details(self, text: str, file_path: Path) -> Dict[str, Any]:
        """
        Extract detailed information from document text for model training
        
        Args:
            text: Extracted text content
            file_path: Path to the original file
            
        Returns:
            Dictionary with extracted details and structured information
        """
        try:
            details = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'file_type': file_path.suffix.lower(),
                'extraction_timestamp': pd.Timestamp.now().isoformat()
            }
            
            # Basic text statistics
            basic_stats = self._get_text_statistics(text)
            details.update(basic_stats)
            
            # Extract key information using NLP
            if self.nlp:
                doc = self.nlp(text)
                
                # Extract named entities
                entities = []
                for ent in doc.ents:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
                details['named_entities'] = entities
                
                # Extract key phrases and topics
                noun_phrases = [chunk.text for chunk in doc.noun_chunks]
                details['key_phrases'] = list(set(noun_phrases))[:20]  # Top 20 unique phrases
                
                # Extract sentences for training
                sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
                details['sentences'] = sentences[:50]  # First 50 sentences for training
                
                # Extract keywords (frequent important words)
                keywords = []
                for token in doc:
                    if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                        not token.is_stop and 
                        not token.is_punct and 
                        len(token.text) > 2):
                        keywords.append(token.lemma_.lower())
                
                # Count keyword frequency
                from collections import Counter
                keyword_counts = Counter(keywords)
                details['keywords'] = dict(keyword_counts.most_common(20))
            
            # Extract structured data patterns
            details.update(self._extract_structured_patterns(text))
            
            # Generate summary if available
            if self.summarizer and len(text) > 100:
                try:
                    # Truncate text if too long for summarization
                    max_length = 1000
                    text_for_summary = text[:max_length] if len(text) > max_length else text
                    
                    summary_result = self.summarizer(text_for_summary, max_length=100, min_length=30, do_sample=False)
                    details['summary'] = summary_result[0]['summary_text']
                except Exception as e:
                    self.logger.warning(f"Summarization failed: {e}")
                    details['summary'] = text[:200] + "..." if len(text) > 200 else text
            
            # Extract training-ready data
            details['training_data'] = self._prepare_training_data(text, details)
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error extracting document details: {e}")
            return {'error': f"Detail extraction failed: {str(e)}"}
    
    def _extract_structured_patterns(self, text: str) -> Dict[str, Any]:
        """Extract structured patterns from text"""
        patterns = {}
        
        try:
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            if emails:
                patterns['emails'] = list(set(emails))
            
            # Extract phone numbers
            phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
            phones = re.findall(phone_pattern, text)
            if phones:
                patterns['phone_numbers'] = [''.join(phone) for phone in phones]
            
            # Extract URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, text)
            if urls:
                patterns['urls'] = urls
            
            # Extract dates
            date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b'
            dates = re.findall(date_pattern, text, re.IGNORECASE)
            if dates:
                patterns['dates'] = dates
            
            # Extract monetary amounts
            money_pattern = r'\$[\d,]+\.?\d*'
            money = re.findall(money_pattern, text)
            if money:
                patterns['monetary_amounts'] = money
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error extracting patterns: {e}")
            return {}
    
    def _prepare_training_data(self, text: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data suitable for model training"""
        try:
            training_data = {
                'raw_text': text,
                'preprocessed_text': self._preprocess_text_for_training(text),
                'metadata': {
                    'word_count': details.get('word_count', 0),
                    'sentence_count': details.get('sentence_count', 0),
                    'file_type': details.get('file_type', 'unknown'),
                    'extraction_timestamp': details.get('extraction_timestamp')
                }
            }
            
            # Add structured features
            if 'named_entities' in details:
                training_data['entities'] = details['named_entities']
            
            if 'keywords' in details:
                training_data['keywords'] = details['keywords']
            
            if 'key_phrases' in details:
                training_data['phrases'] = details['key_phrases']
            
            # Add sentences for sequence training
            if 'sentences' in details:
                training_data['sentences'] = details['sentences']
            
            return training_data
            
        except Exception as e:
            self.logger.error(f"Error preparing training data: {e}")
            return {'error': str(e)}
    
    def _preprocess_text_for_training(self, text: str) -> str:
        """Preprocess text for better model training"""
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters but keep punctuation
            text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
            
            # Normalize case (keep first letter capitalized for sentences)
            sentences = text.split('. ')
            normalized_sentences = []
            for sentence in sentences:
                if sentence.strip():
                    sentence = sentence.strip().lower()
                    if sentence:
                        sentence = sentence[0].upper() + sentence[1:]
                    normalized_sentences.append(sentence)
            
            return '. '.join(normalized_sentences)
            
        except Exception as e:
            self.logger.error(f"Error preprocessing text: {e}")
            return text
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get text module status"""
        return {
            'spacy_available': self.nlp is not None,
            'summarizer_available': self.summarizer is not None,
            'pdf_available': PDF_AVAILABLE,
            'docx_available': DOCX_AVAILABLE,
            'supported_formats': ['.txt', '.csv', '.html', '.htm'] + (['.pdf'] if PDF_AVAILABLE else []) + (['.docx'] if DOCX_AVAILABLE else [])
        }
