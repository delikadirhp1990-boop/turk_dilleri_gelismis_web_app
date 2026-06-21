from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Any

class Statistics:
    @staticmethod
    def calculate(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(records)
        lang_counts = Counter(r.get("language", "?") for r in records)
        cat_counts = Counter(r.get("category", "?") for r in records)
        tag_counter = Counter()
        for r in records:
            tags = r.get("metadata", {}).get("tags", [])
            tag_counter.update(tags)
        daily = defaultdict(int)
        for r in records:
            created = r.get("metadata", {}).get("created_at", "")
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace("Z", ""))
                    daily[dt.strftime("%Y-%m-%d")] += 1
                except:
                    pass
        return {
            "total": total,
            "language_counts": dict(lang_counts),
            "category_counts": dict(cat_counts),
            "top_tags": dict(tag_counter.most_common(10)),
            "daily_counts": dict(sorted(daily.items()))
        }