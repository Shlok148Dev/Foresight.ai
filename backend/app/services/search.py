"""
Foresight — Elasticsearch Integration
======================================
Phase 2E: Indexing and searching signals using Elasticsearch.
"""

from typing import List, Dict, Optional
import os

try:
    from elasticsearch import Elasticsearch
    HAS_ES = True
except ImportError:
    HAS_ES = False

class SearchService:
    def __init__(self):
        es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        if HAS_ES:
            self.es = Elasticsearch([es_url])
        else:
            self.es = None

    def index_signal(self, signal: Dict) -> None:
        """Index signal in Elasticsearch."""
        if not self.es:
            return
            
        try:
            self.es.index(
                index="signals",
                id=signal.get("id"),
                document={
                    "text": signal.get("text", ""),
                    "entities": signal.get("entities", []),
                    "keywords": signal.get("keywords", []),
                    "sentiment": signal.get("sentiment", "neutral"),
                    "category": signal.get("category", "general"),
                    "timestamp": signal.get("timestamp")
                }
            )
        except Exception as e:
            print(f"Failed to index in ES: {e}")

    def search_signals(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search signals with filters."""
        if not self.es:
            return []

        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["text", "entities", "keywords"]
                }
            }
        }
        
        if filters:
            search_body["query"] = {
                "bool": {
                    "must": search_body["query"],
                    "filter": [
                        {"term": {k: v}} for k, v in filters.items() if v
                    ]
                }
            }
            
        try:
            results = self.es.search(index="signals", body=search_body)
            return [hit["_source"] for hit in results.get("hits", {}).get("hits", [])]
        except Exception as e:
            print(f"ES search failed: {e}")
            return []

# Singleton instance
search_service = SearchService()
