import random
import threading
from typing import List

import requests

from .config import Config


class WordService:
    """Kelimeleri ve alıntıları internetten çeken servis."""
    _instance = None

    def __init__(self):
        self.word_pool = Config.LOCAL_WORDS.copy()
        self.lock = threading.Lock()
        self._start_download()

    def _start_download(self):
        threading.Thread(target=self._download_worker, daemon=True).start()

    def _download_worker(self):
        try:
            r = requests.get(Config.WORD_LIST_URL, timeout=10)
            words = [w for w in r.text.splitlines() if 3 <= len(w) <= 10 and w.isalpha()]
            with self.lock:
                self.word_pool = words
        except Exception as e:
            print(f"Word download failed: {e}")

    def get_words(self, count: int) -> List[str]:
        with self.lock:
            if not self.word_pool:
                return Config.LOCAL_WORDS[:count]
            pool_len = len(self.word_pool)
            return [self.word_pool[int(random.triangular(0, pool_len, 0))] for _ in range(count)]

    def get_quote(self) -> str:
        try:
            r = requests.get(Config.QUOTE_API_URL, verify=False, timeout=3)
            data = r.json()
            content = data.get("content", "")
            author = data.get("author", "Unknown")
            formatted = content.replace("’", "'").replace("“", '"').replace("”", '"')
            return f"{formatted} — {author}"
        except Exception:
            return "The quick brown fox jumps over the lazy dog. — Fallback"
