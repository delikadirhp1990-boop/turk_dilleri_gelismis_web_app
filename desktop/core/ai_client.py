import requests
from typing import List, Dict, Any

class AIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _post(self, endpoint: str, json_data: dict = None):
        try:
            resp = self.session.post(f"{self.base_url}{endpoint}", json=json_data, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return None

    def analyze_grammar(self, text: str) -> dict:
        return self._post("/analyze-grammar", {"text": text})

    def auto_tag(self, text: str) -> list:
        result = self._post("/auto-tag", {"text": text})
        return result.get("tags", []) if result else []

    def get_embedding(self, text: str) -> list:
        result = self._post("/embed", {"text": text})
        return result.get("embedding", []) if result else []

    def similarity_search(self, query: str, records: List[Dict]) -> List[Dict]:
        result = self._post("/similarity-search", {"query": query, "records": records})
        return result.get("results", []) if result else []