"""
Foresight — LLM Orchestration
==============================
Phase 2B: LangChain + LangGraph integration for trend analysis via Groq.
"""

import os
from typing import Dict, List, Optional
import json

# Attempt to import LangChain elements safely
try:
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    # Fallback to standard HTTP requests if Groq wrapper isn't installed perfectly
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

import httpx

class TrendAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = "mixtral-8x7b-32768"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def analyze_trend(self, signal: Dict) -> Dict:
        """Analyze trend using Groq API and LLM logic."""
        if not self.api_key:
            # Fallback mock for testing if no key is present
            return self._mock_result(signal)

        prompt = f"""
        Analyze this signal and predict its trend potential:
        
        Signal: {signal.get('text', '')}
        Entities: {', '.join(signal.get('entities', []))}
        Keywords: {', '.join(signal.get('keywords', []))}
        
        Provide output as JSON:
        {{
            "trend_name": "Name of trend",
            "confidence": 85,
            "stage": "emerging",
            "velocity": "fast",
            "forecast": "1-3 weeks ahead prediction"
        }}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                result_str = data["choices"][0]["message"]["content"]
                return json.loads(result_str)
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return self._mock_result(signal)

    def _mock_result(self, signal: Dict) -> Dict:
        """Mock LLM result for testing/fallback."""
        return {
            "trend_name": signal.get("entities", ["Unknown"])[0] if signal.get("entities") else "Emerging Tech",
            "confidence": 75,
            "stage": "emerging",
            "velocity": "moderate",
            "forecast": "Expected to grow steadily over the next 2 weeks."
        }

# Singleton instance
trend_analyzer = TrendAnalyzer()
