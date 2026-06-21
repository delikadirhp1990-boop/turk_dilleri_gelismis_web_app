from typing import List, Dict, Any, Optional

class SearchEngine:
    @staticmethod
    def search(records: List[Dict[str, Any]],
               query: str = "",
               language: Optional[str] = None,
               category: Optional[str] = None) -> List[Dict[str, Any]]:
        results = records
        if query:
            q = query.lower()
            def match(rec):
                if q in rec.get("title", "").lower():
                    return True
                content = rec.get("content", {})
                for v in content.values():
                    if isinstance(v, str) and q in v.lower():
                        return True
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, str) and q in item.lower():
                                return True
                return False
            results = [r for r in results if match(r)]
        if language:
            results = [r for r in results if r.get("language") == language]
        if category:
            results = [r for r in results if r.get("category") == category]
        return results