"""
Foresight — NLP Detection Service Tests
=========================================
Tests for the core NLP pipeline: text cleaning, TF-IDF, clustering,
keyword extraction, and stage classification.
"""

import pytest
from app.services.detection import (
    clean_text,
    tokenize,
    compute_tfidf,
    cosine_similarity,
    dbscan_cluster,
    extract_keywords,
    classify_stage,
    compute_confidence,
    _generate_action_prompt,
)
from app.models.database import SpreadStage


# ── Text Preprocessing ───────────────────────────────────────────

class TestCleanText:
    def test_removes_urls(self):
        text = "Check out https://example.com/foo and http://bar.com"
        result = clean_text(text)
        assert "https" not in result
        assert "http" not in result

    def test_removes_mention_symbols(self):
        result = clean_text("Follow @foresight for updates")
        assert "@" not in result
        assert "foresight" in result

    def test_removes_hashtag_symbols(self):
        result = clean_text("Trending #AI #machinelearning")
        assert "#" not in result
        assert "ai" in result.lower()

    def test_normalizes_whitespace(self):
        result = clean_text("too   many    spaces  here")
        assert "  " not in result

    def test_lowercases(self):
        result = clean_text("UPPERCASE TEXT Here")
        assert result == result.lower()


class TestTokenize:
    def test_removes_stop_words(self):
        tokens = tokenize("the cat is on the mat")
        assert "the" not in tokens
        assert "cat" in tokens
        assert "mat" in tokens

    def test_removes_short_words(self):
        tokens = tokenize("an ox is by it")
        assert "an" not in tokens
        assert "ox" not in tokens  # too short (2 chars)

    def test_extracts_meaningful_words(self):
        tokens = tokenize("artificial intelligence machine learning trends")
        assert "artificial" in tokens
        assert "intelligence" in tokens
        assert "machine" in tokens


# ── TF-IDF ───────────────────────────────────────────────────────

class TestTFIDF:
    def test_empty_documents(self):
        vectors, idf = compute_tfidf([])
        assert vectors == []
        assert idf == {}

    def test_single_document(self):
        vectors, idf = compute_tfidf([["hello", "world"]])
        assert len(vectors) == 1
        # With single doc, IDF should be 0 (log(1/1) = 0)
        assert all(v == 0.0 for v in vectors[0].values())

    def test_multiple_documents(self):
        docs = [
            ["artificial", "intelligence", "machine"],
            ["machine", "learning", "deep"],
            ["artificial", "neural", "network"],
        ]
        vectors, idf = compute_tfidf(docs)
        assert len(vectors) == 3
        # "machine" appears in 2/3 docs, should have lower IDF than unique terms
        assert idf["machine"] < idf["neural"]

    def test_cosine_similarity_identical(self):
        vec = {"ai": 0.5, "ml": 0.3}
        sim = cosine_similarity(vec, vec)
        assert abs(sim - 1.0) < 0.001

    def test_cosine_similarity_orthogonal(self):
        vec_a = {"ai": 1.0}
        vec_b = {"blockchain": 1.0}
        sim = cosine_similarity(vec_a, vec_b)
        assert sim == 0.0


# ── DBSCAN Clustering ───────────────────────────────────────────

class TestDBSCAN:
    def test_no_clusters_with_diverse_signals(self):
        # Very different vectors should not cluster
        vectors = [
            {"ai": 1.0},
            {"blockchain": 1.0},
            {"cooking": 1.0},
        ]
        labels = dbscan_cluster(vectors, eps=0.3, min_samples=2)
        assert all(l == -1 for l in labels)  # All noise

    def test_clusters_similar_signals(self):
        # Similar vectors should cluster together
        vectors = [
            {"ai": 0.8, "machine": 0.5, "learning": 0.3},
            {"ai": 0.7, "machine": 0.6, "learning": 0.4},
            {"ai": 0.9, "machine": 0.4, "learning": 0.5},
            {"blockchain": 0.9, "crypto": 0.7},  # Outlier
        ]
        labels = dbscan_cluster(vectors, eps=0.5, min_samples=2)
        # First 3 should be in same cluster
        assert labels[0] == labels[1] == labels[2]
        # Last one should be noise
        assert labels[3] == -1

    def test_empty_input(self):
        labels = dbscan_cluster([], eps=0.3, min_samples=2)
        assert labels == []


# ── Keyword Extraction ───────────────────────────────────────────

class TestKeywordExtraction:
    def test_extracts_top_keywords(self):
        docs = [
            ["artificial", "intelligence", "trend"],
            ["artificial", "intelligence", "growing"],
            ["intelligence", "trend", "viral"],
        ]
        idf = {"artificial": 0.4, "intelligence": 0.1, "trend": 0.4, "growing": 0.8, "viral": 0.8}
        keywords = extract_keywords(docs, idf, top_k=3)
        assert len(keywords) <= 3
        assert isinstance(keywords, list)

    def test_empty_documents(self):
        keywords = extract_keywords([], {}, top_k=5)
        assert keywords == []


# ── Stage Classification ─────────────────────────────────────────

class TestClassifyStage:
    def test_embryonic(self):
        assert classify_stage(3, 0.5) == SpreadStage.EMBRYONIC

    def test_emerging(self):
        assert classify_stage(10, 2.0) == SpreadStage.EMERGING

    def test_accelerating(self):
        assert classify_stage(50, 10.0) == SpreadStage.ACCELERATING

    def test_peaking(self):
        assert classify_stage(200, 5.0) == SpreadStage.PEAKING

    def test_declining(self):
        assert classify_stage(50, -3.0) == SpreadStage.DECLINING


class TestComputeConfidence:
    def test_low_confidence(self):
        conf = compute_confidence(2, 0.1, 1)
        assert 0.0 <= conf <= 0.3

    def test_high_confidence(self):
        conf = compute_confidence(100, 50.0, 5)
        assert conf >= 0.7

    def test_range(self):
        conf = compute_confidence(10, 5.0, 3)
        assert 0.0 <= conf <= 1.0


class TestActionPrompt:
    def test_generates_for_all_stages(self):
        for stage in SpreadStage:
            prompt = _generate_action_prompt("AI", stage, 5.0)
            assert isinstance(prompt, str)
            assert len(prompt) > 10
            assert "AI" in prompt
