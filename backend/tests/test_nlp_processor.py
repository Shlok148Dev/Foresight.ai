"""
Tests for NLP Processor (Phase 2A)
"""

import pytest
from app.services.nlp_processor import SignalProcessor

@pytest.fixture
def processor():
    return SignalProcessor()

def test_entity_extraction(processor):
    result = processor.process_signal("Apple released the new iPhone 15 today in California.", "twitter")
    assert result is not None
    # 'apple' and 'california' should be recognized as entities
    assert any(ent.lower() in ['apple', 'iphone 15', 'california'] for ent in result["entities"])

def test_sentiment_classification_positive(processor):
    result = processor.process_signal("This is absolutely amazing and wonderful! I love it!", "twitter")
    assert result is not None
    assert result["sentiment"] == "positive"

def test_sentiment_classification_negative(processor):
    result = processor.process_signal("This is terrible, awful, and I hate it completely.", "twitter")
    assert result is not None
    assert result["sentiment"] == "negative"

def test_deduplication(processor):
    text = "Just learned about the new AI breakthrough!"
    result1 = processor.process_signal(text, "twitter")
    result2 = processor.process_signal(text, "reddit")
    
    assert result1 is not None
    assert result2 is None  # Should be filtered out as duplicate

def test_category_classification(processor):
    result = processor.process_signal("Bitcoin and crypto trading are volatile.", "twitter")
    assert result is not None
    assert result["category"] == "finance"

def test_text_normalization(processor):
    result = processor.process_signal("Check out this link http://example.com @elonmusk #AI", "twitter")
    assert result is not None
    assert "http" not in result["normalized_text"]
    assert "@elonmusk" not in result["normalized_text"]
    assert "ai" in result["normalized_text"]
