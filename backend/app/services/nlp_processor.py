"""
Foresight — NLP Signal Processor
=================================
Phase 2A: spaCy NLP Pipeline
Extracts entities, keywords, sentiment, and categories from text.
"""

import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


class SignalProcessor:
    def __init__(self):
        self.processed_signals: Dict[str, datetime] = {}
        self.deduplication_window = timedelta(hours=1)

    def process_signal(self, text: str, platform: str) -> Optional[Dict]:
        """Process signal through NLP pipeline."""
        # Normalize text
        normalized = self._normalize_text(text)

        # Check for duplicates
        signal_hash = hashlib.md5(normalized.encode()).hexdigest()
        if self._is_duplicate(signal_hash):
            return None

        # Process with spaCy
        doc = nlp(normalized)

        # Extract entities
        entities = [ent.text for ent in doc.ents]

        # Extract keywords (nouns and proper nouns)
        keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]

        # Classify sentiment
        sentiment = self._classify_sentiment(text)

        # Classify category
        category = self._classify_category(keywords, entities)

        return {
            "text": text,
            "normalized_text": normalized,
            "entities": list(set(entities)),
            "keywords": list(set(keywords)),
            "sentiment": sentiment,
            "category": category,
            "hash": signal_hash,
            "platform": platform,
            "timestamp": datetime.utcnow()
        }

    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing."""
        # Remove URLs
        text = re.sub(r"http\S+|www\S+", "", text)
        # Remove mentions
        text = re.sub(r"@\w+", "", text)
        # Remove hashtags (keep text)
        text = re.sub(r"#(\w+)", r"\1", text)
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = " ".join(text.split())
        return text

    def _classify_sentiment(self, text: str) -> str:
        """Classify sentiment using a simple dictionary approach (positive, negative, neutral)."""
        positive_words = {"amazing", "good", "great", "excellent", "awesome", "love", "wonderful", "breakthrough", "success", "profit", "bullish"}
        negative_words = {"bad", "terrible", "awful", "hate", "worst", "fail", "failure", "loss", "bearish", "crash", "horrible"}
        
        words = text.lower().split()
        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    def _classify_category(self, keywords: List[str], entities: List[str]) -> str:
        """Classify signal category based on predefined terms."""
        categories = {
            "tech": ["ai", "software", "tech", "app", "startup", "developer", "code", "engineering"],
            "finance": ["stock", "crypto", "bitcoin", "trading", "economy", "market"],
            "entertainment": ["movie", "music", "celebrity", "actor", "game", "film"],
            "politics": ["election", "government", "president", "congress", "policy"],
            "sports": ["game", "player", "team", "championship", "football", "basketball"]
        }

        all_words = [w.lower() for w in keywords + entities]
        for category, keywords_list in categories.items():
            if any(word in all_words for word in keywords_list):
                return category

        return "general"

    def _is_duplicate(self, signal_hash: str) -> bool:
        """Check if signal is duplicate within the time window."""
        now = datetime.utcnow()
        if signal_hash in self.processed_signals:
            timestamp = self.processed_signals[signal_hash]
            if now - timestamp < self.deduplication_window:
                return True

        self.processed_signals[signal_hash] = now
        
        # Periodically clean up old hashes to prevent memory leak
        if len(self.processed_signals) > 10000:
            self._cleanup_hashes()
            
        return False

    def _cleanup_hashes(self):
        """Remove old hashes from memory."""
        now = datetime.utcnow()
        to_remove = [
            h for h, ts in self.processed_signals.items() 
            if now - ts > self.deduplication_window
        ]
        for h in to_remove:
            del self.processed_signals[h]

# Singleton instance
nlp_processor = SignalProcessor()
