import sys


class Config:
    WORD_LIST_URL = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt"
    QUOTE_API_URL = "https://api.quotable.io/random?minLength=50&maxLength=140"
    LOCAL_WORDS = [
        "maroon", "type", "focus", "fluid", "shadow", "glow", "gradient", "cursor",
        "quiet", "quick", "brown", "fox", "lazy", "craft", "code", "night", "sun",
        "ember", "flare", "shift", "frame", "storm", "mellow", "pulse", "breeze"
    ]
    FONT_FAMILY = "JetBrains Mono" if sys.platform == "win32" else "Menlo"
    FONT_FALLBACK = "JetBrains Mono, Fira Code, Menlo, Consolas, monospace"
    FONT_SIZE = 26

    THEMES = {
        "midnight": {
            "bg": "#0f172a",
            "bg_alt": "#0b1224",
            "surface": "#111827",
            "surface_alt": "#1c2540",
            "border": "#22304d",
            "text_main": "#e5e7eb",
            "text_sub": "#9ca3af",
            "accent": "#f97316",
            "correct": "#4ade80",
            "error": "#f43f5e",
            "cursor": "#22d3ee",
            "active_mode": "#fb923c",
            "death": "#ef4444",
            "glow": "#22c55e",
        },
        "dawn": {
            "bg": "#fef6e4",
            "bg_alt": "#fdebd1",
            "surface": "#ffffff",
            "surface_alt": "#ffe8c8",
            "border": "#f3c492",
            "text_main": "#2b2b2b",
            "text_sub": "#6b7280",
            "accent": "#ef4444",
            "correct": "#16a34a",
            "error": "#dc2626",
            "cursor": "#2563eb",
            "active_mode": "#dc682a",
            "death": "#b91c1c",
            "glow": "#22c55e",
        },
    }

    ACTIVE_THEME = "midnight"
    COLORS = THEMES[ACTIVE_THEME]

    @classmethod
    def set_theme(cls, name: str):
        if name in cls.THEMES:
            cls.ACTIVE_THEME = name
            cls.COLORS = cls.THEMES[name]
