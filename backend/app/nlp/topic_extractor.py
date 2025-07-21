import spacy
from keybert import KeyBERT
from collections import Counter
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class TopicExtractor:
    def __init__(self):
        self.nlp = None
        self.keybert_model = None
        self.hospitality_keywords = {
            # Service categories
            'service': ['service', 'staff', 'employee', 'waiter', 'waitress', 'manager', 'reception', 'front desk'],
            'room': ['room', 'bedroom', 'bathroom', 'bed', 'shower', 'toilet', 'amenities', 'minibar'],
            'food': ['food', 'meal', 'breakfast', 'lunch', 'dinner', 'restaurant', 'dining', 'kitchen', 'chef'],
            'cleanliness': ['clean', 'dirty', 'hygiene', 'sanitize', 'tidy', 'mess', 'housekeeping'],
            'location': ['location', 'area', 'neighborhood', 'transport', 'parking', 'accessibility'],
            'value': ['price', 'cost', 'expensive', 'cheap', 'value', 'money', 'worth', 'budget'],
            'booking': ['booking', 'reservation', 'check-in', 'check-out', 'website', 'payment'],
            'facilities': ['wifi', 'internet', 'pool', 'gym', 'spa', 'elevator', 'ac', 'heating', 'tv'],
            'atmosphere': ['atmosphere', 'ambiance', 'noise', 'quiet', 'peaceful', 'crowded', 'busy']
        }
        
    async def initialize(self):
        """Initialize the topic extraction models"""
        try:
            logger.info("Initializing topic extraction models...")
            
            # Initialize spaCy model (try different models)
            for model_name in ['en_core_web_sm', 'en_core_web_md', 'en_core_web_lg']:
                try:
                    self.nlp = spacy.load(model_name)
                    logger.info(f"Loaded spaCy model: {model_name}")
                    break
                except OSError:
                    continue
            
            if self.nlp is None:
                logger.warning("No spaCy model found, using basic tokenization")
            
            # Initialize KeyBERT
            self.keybert_model = KeyBERT()
            logger.info("Topic extraction models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize topic extraction models: {e}")
    
    def _extract_with_keybert(self, text: str, top_k: int = 5) -> List[str]:
        """Extract keywords using KeyBERT"""
        try:
            if self.keybert_model:
                keywords = self.keybert_model.extract_keywords(
                    text, 
                    keyphrase_ngram_range=(1, 2), 
                    stop_words='english',
                    use_maxsum=True,
                    nr_candidates=20,
                    top_k=top_k
                )
                return [keyword[0] for keyword in keywords]
            return []
        except Exception as e:
            logger.error(f"KeyBERT extraction failed: {e}")
            return []
    
    def _extract_with_spacy(self, text: str) -> List[str]:
        """Extract entities and important terms using spaCy"""
        try:
            if self.nlp is None:
                return []
                
            doc = self.nlp(text)
            
            # Extract named entities
            entities = [ent.text.lower() for ent in doc.ents 
                       if ent.label_ in ['ORG', 'PRODUCT', 'EVENT', 'FAC']]
            
            # Extract noun phrases
            noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks 
                           if len(chunk.text.split()) <= 2 and len(chunk.text) > 2]
            
            # Extract important nouns and adjectives
            important_tokens = [token.lemma_.lower() for token in doc 
                              if token.pos_ in ['NOUN', 'ADJ'] 
                              and not token.is_stop 
                              and not token.is_punct 
                              and len(token.text) > 2]
            
            return list(set(entities + noun_phrases + important_tokens))
            
        except Exception as e:
            logger.error(f"spaCy extraction failed: {e}")
            return []
    
    def _categorize_topics(self, topics: List[str]) -> Dict[str, List[str]]:
        """Categorize topics into hospitality-specific categories"""
        categorized = {}
        
        for category, keywords in self.hospitality_keywords.items():
            category_topics = []
            for topic in topics:
                for keyword in keywords:
                    if keyword in topic.lower() or topic.lower() in keyword:
                        category_topics.append(topic)
                        break
            
            if category_topics:
                categorized[category] = list(set(category_topics))
        
        # Add uncategorized topics
        all_categorized = set()
        for cat_topics in categorized.values():
            all_categorized.update(cat_topics)
        
        uncategorized = [topic for topic in topics if topic not in all_categorized]
        if uncategorized:
            categorized['other'] = uncategorized[:3]  # Limit to top 3
        
        return categorized
    
    def _clean_and_filter_topics(self, topics: List[str]) -> List[str]:
        """Clean and filter extracted topics"""
        cleaned_topics = []
        
        for topic in topics:
            # Clean the topic
            topic = re.sub(r'[^\w\s-]', '', topic)  # Remove special chars except hyphens
            topic = topic.strip().lower()
            
            # Filter criteria
            if (len(topic) >= 2 and 
                len(topic) <= 25 and 
                not topic.isdigit() and
                topic not in ['the', 'and', 'for', 'with', 'this', 'that', 'very', 'good', 'bad']):
                cleaned_topics.append(topic)
        
        return cleaned_topics
    
    async def extract_topics(self, text: str, max_topics: int = 5) -> Dict[str, Any]:
        """
        Extract topics from text
        Returns: {
            'topics': List[str],  # Top extracted topics
            'categories': Dict[str, List[str]],  # Categorized topics
            'all_topics': List[str]  # All extracted topics before filtering
        }
        """
        try:
            all_topics = []
            
            # Extract using KeyBERT
            keybert_topics = self._extract_with_keybert(text, top_k=10)
            all_topics.extend(keybert_topics)
            
            # Extract using spaCy
            spacy_topics = self._extract_with_spacy(text)
            all_topics.extend(spacy_topics)
            
            # Clean and filter topics
            cleaned_topics = self._clean_and_filter_topics(all_topics)
            
            # Count frequency and get top topics
            topic_counts = Counter(cleaned_topics)
            top_topics = [topic for topic, count in topic_counts.most_common(max_topics)]
            
            # Categorize topics
            categories = self._categorize_topics(top_topics)
            
            return {
                'topics': top_topics,
                'categories': categories,
                'all_topics': list(set(all_topics))
            }
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return {
                'topics': [],
                'categories': {},
                'all_topics': []
            }

# Global topic extractor instance
topic_extractor = TopicExtractor()