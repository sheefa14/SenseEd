# text_module.py
import os
import logging
from typing import Optional, Dict, List, Any, Union
import re
from pathlib import Path
import PyPDF2
import docx
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import nltk
from textblob import TextBlob
import spacy
from transformers import pipeline

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
        try:
            # Initialize spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.info("spaCy model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load spaCy model: {e}")
            self.nlp = None
        
        try:
            # Initialize summarization pipeline
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            self.logger.info("Summarization model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load summarization model: {e}")
            self.summarizer = None
    
    def read_document(self, file_path: str) -> Dict[str, Any]:
        """
        Read text from various document formats
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'text': '',
                'success': False,
                'error': f"File not found: {file_path}"
            }
        
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.txt':
                return self._read_text_file(file_path)
            elif file_extension == '.pdf':
                return self._read_pdf_file(file_path)
            elif file_extension == '.docx':
                return self._read_docx_file(file_path)
            elif file_extension == '.csv':
                return self._read_csv_file(file_path)
            elif file_extension in ['.html', '.htm']:
                return self._read_html_file(file_path)
            else:
                return {
                    'text': '',
                    'success': False,
                    'error': f"Unsupported file format: {file_extension}"
                }
        except Exception as e:
            self.logger.error(f"Error reading document {file_path}: {e}")
            return {
                'text': '',
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
        
        operations = operations or ['sentiment', 'entities', 'summary', 'keywords']
        results = {
            'original_text': text,
            'success': True,
            'operations': {}
            }
        
        try:
            # Sentiment analysis
            if 'sentiment' in operations:
                results['operations']['sentiment'] = self._analyze_sentiment(text)
            
            # Named entity recognition
            if 'entities' in operations and self.nlp:
                results['operations']['entities'] = self._extract_entities(text)
            
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
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""
        if not self.nlp:
            return {'error': 'spaCy model not available'}
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            return {
                'entities': entities,
                'count': len(entities)
            }
        except Exception as e:
            return {'error': str(e)}
    
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
    
    def _extract_keywords(self, text: str, num_keywords: int = 10) -> Dict[str, Any]:
        """Extract keywords from text"""
        try:
            blob = TextBlob(text)
            
            # Get noun phrases as keywords
            noun_phrases = blob.noun_phrases
            
            # Get word frequencies
            words = blob.words
            word_freq = {}
            
            for word in words:
                word_lower = word.lower()
                if len(word_lower) > 3 and word_lower.isalpha():  # Filter short words and non-alphabetic
                    word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            
            # Sort by frequency
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            top_words = [word for word, freq in sorted_words[:num_keywords]]
            
            return {
                'keywords': top_words,
                'noun_phrases': list(noun_phrases)[:num_keywords],
                'word_frequencies': dict(sorted_words[:num_keywords])
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
    
    def convert_text_format(self, text: str, target_format: str) -> Dict[str, Any]:
        """
        Convert text to different formats
        
        Args:
            text: Input text
            target_format: Target format ('html', 'markdown', 'json')
            
        Returns:
            Converted text in target format
        """
        try:
            if target_format.lower() == 'html':
                # Convert to HTML with basic formatting
                html_text = text.replace('\n', '<br>')
                html_text = f"<html><body><p>{html_text}</p></body></html>"
                return {
                    'converted_text': html_text,
                    'format': 'html',
                    'success': True
                }
            
            elif target_format.lower() == 'markdown':
                # Convert to basic markdown
                md_text = text.replace('\n', '\n\n')
                return {
                    'converted_text': md_text,
                    'format': 'markdown',
                    'success': True
                }
            
            elif target_format.lower() == 'json':
                # Convert to JSON format
                import json
                json_data = {
                    'content': text,
                    'metadata': {
                        'length': len(text),
                        'word_count': len(text.split())
                    }
                }
                return {
                    'converted_text': json.dumps(json_data, indent=2),
                    'format': 'json',
                    'success': True
                }
            
            else:
                return {
                    'converted_text': '',
                    'format': target_format,
                    'success': False,
                    'error': f'Unsupported format: {target_format}'
                }
                
        except Exception as e:
            return {
                'converted_text': '',
                'format': target_format,
                'success': False,
                'error': str(e)
            }
    
    def search_in_text(self, text: str, query: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for query in text
        
        Args:
            text: Text to search in
            query: Search query
            case_sensitive: Whether search should be case sensitive
            
        Returns:
            Search results with positions and context
        """
        try:
            if not case_sensitive:
                search_text = text.lower()
                search_query = query.lower()
            else:
                search_text = text
                search_query = query
            
            # Find all occurrences
            positions = []
            start = 0
            while True:
                pos = search_text.find(search_query, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            # Get context around each match
            context_window = 50
            results = []
            
            for pos in positions:
                start_context = max(0, pos - context_window)
                end_context = min(len(text), pos + len(query) + context_window)
                context = text[start_context:end_context]
                
                results.append({
                    'position': pos,
                    'context': context,
                    'match': text[pos:pos + len(query)]
                })
            
            return {
                'query': query,
                'matches_found': len(positions),
                'results': results,
                'success': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get text module status"""
            return {
            'spacy_available': self.nlp is not None,
            'summarizer_available': self.summarizer is not None,
            'supported_formats': ['.txt', '.pdf', '.docx', '.csv', '.html', '.htm']
            }