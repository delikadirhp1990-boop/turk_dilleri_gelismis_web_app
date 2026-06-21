import json, os, uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class JsonManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._records: List[Dict[str, Any]] = []
        self._ensure_file()
        self.load()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def load(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self._records = json.load(f)
            logger.info(f"Local JSON yüklendi: {len(self._records)} kayıt")
        except (json.JSONDecodeError, FileNotFoundError):
            logger.error("JSON bozuk, sıfırdan başlatılıyor.")
            self._records = []
            self.save()

    def save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self._records, f, ensure_ascii=False, indent=2)

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._records)

    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        for r in self._records:
            if r.get("id") == record_id:
                return r
        return None

    def add(self, record: Dict[str, Any]) -> str:
        if not record.get("id"):
            record["id"] = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        record.setdefault("metadata", {})
        record["metadata"]["created_at"] = record["metadata"].get("created_at", now)
        record["metadata"]["updated_at"] = now
        self._records.append(record)
        self.save()
        return record["id"]

    def update(self, record_id: str, new_data: Dict[str, Any]) -> bool:
        for i, r in enumerate(self._records):
            if r.get("id") == record_id:
                new_data["id"] = record_id
                new_data.setdefault("metadata", {})
                new_data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                self._records[i] = new_data
                self.save()
                return True
        return False

    def delete(self, record_id: str) -> bool:
        for i, r in enumerate(self._records):
            if r.get("id") == record_id:
                del self._records[i]
                self.save()
                return True
        return False

    def delete_multiple(self, ids: List[str]) -> int:
        before = len(self._records)
        self._records = [r for r in self._records if r.get("id") not in ids]
        deleted = before - len(self._records)
        if deleted:
            self.save()
        return deleted

    def set_all(self, records: List[Dict[str, Any]]):
        self._records = records
        self.save()