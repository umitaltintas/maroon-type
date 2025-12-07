import sys


class Config:
    WORD_LIST_URL = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt"
    QUOTE_API_URL = "https://api.quotable.io/random?minLength=50&maxLength=140"
    FONT_FAMILY = "Consolas" if sys.platform == "win32" else "Menlo"
    FONT_SIZE = 26

    COLORS = {
        "bg": "#1e1e2e", "surface": "#313244", "border": "#45475a",
        "text_main": "#cdd6f4", "text_sub": "#6c7086", "accent": "#89b4fa",
        "correct": "#a6e3a1", "error": "#f38ba8", "cursor": "#f5c2e7",
        "active_mode": "#fab387", "death": "#ff5555"
    }
