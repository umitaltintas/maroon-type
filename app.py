import tkinter as tk
from tkinter import messagebox, ttk, font, IntVar, StringVar, colorchooser
import time
import random
import json
import os
import bisect


SETTINGS_FILE = "settings.json"
TEXT_FILE = "20k.txt"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    return {
        "font_name": "JetBrains Mono",
        "font_size": 15,
        "bg_color": "#282828",
        "text_color": "#d8d8d8",
        "difficulty": "Medium",
    }


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)


def get_words():
    with open(TEXT_FILE, "r") as file:
        words = file.read().splitlines()
        filtered_words = [word for word in words if len(word) >= 3 and len(word) <= 8]
        return filtered_words


def generate_word(words):
    total_words = len(words)
    total_weight = total_words * (total_words + 1) // 2
    rand_weight = random.randint(1, total_weight)

    # Precompute cumulative weights
    cumulative_weights = []
    cumulative_weight = 0
    for index in range(total_words):
        weight = total_words - index
        cumulative_weight += weight
        cumulative_weights.append(cumulative_weight)

    # Use binary search to find the word corresponding to rand_weight
    word_index = bisect.bisect_left(cumulative_weights, rand_weight)
    return words[word_index]


def generate_sentence(weighted_words, min_words, max_words):
    num_words = random.randint(min_words, max_words)
    sentence = " ".join(generate_word(weighted_words) for _ in range(num_words))
    return sentence


def generate_paragraph(
    weighted_words, min_sentences, max_sentences, min_words, max_words
):
    num_sentences = random.randint(min_sentences, max_sentences)
    paragraph = " ".join(
        generate_sentence(weighted_words, min_words, max_words)
        for _ in range(num_sentences)
    )
    return paragraph


def generate_text(
    weighted_words,
    min_paragraphs,
    max_paragraphs,
    min_sentences,
    max_sentences,
    min_words,
    max_words,
):
    num_paragraphs = random.randint(min_paragraphs, max_paragraphs)
    text = " ".join(
        generate_paragraph(
            weighted_words, min_sentences, max_sentences, min_words, max_words
        )
        for _ in range(num_paragraphs)
    )
    return text


class MaroonTyping:
    def __init__(self, root):
        self.root = root
        self.root.title("Maroon Type")
        self.root.geometry("800x300")
        self.root.minsize(800, 600)

        settings = load_settings()
        self.font_name = StringVar(value=settings.get("font_name", "JetBrains Mono"))
        self.font_size = IntVar(value=settings.get("font_size", 18))
        self.bg_color = StringVar(value=settings.get("bg_color", "#282828"))
        self.text_color = StringVar(value=settings.get("text_color", "#d8d8d8"))
        self.difficulty = StringVar(value=settings.get("difficulty", "Medium"))

        self.words = get_words()
        self.generate_texts()

        self.text_to_type = self.texts[self.difficulty.get()]
        self.user_input = []
        self.current_index = 0
        self.start_time = None
        self.correct_typed = 0
        self.incorrect_typed = 0
        self.blink_state = True
        self.stats_running = True
        self.total_keypresses = 0

        self.setup_styles()
        self.create_widgets()
        self.bind_events()

        self.reset_stats()
        self.countdown(3)
        self.blink_cursor()

    def generate_texts(self):
        self.texts = {
            "Easy": generate_text(
                self.words,
                min_paragraphs=1,
                max_paragraphs=1,
                min_sentences=1,
                max_sentences=2,
                min_words=2,
                max_words=4,
            ),
            "Medium": generate_text(
                self.words,
                min_paragraphs=1,
                max_paragraphs=2,
                min_sentences=1,
                max_sentences=3,
                min_words=3,
                max_words=5,
            ),
            "Hard": generate_text(
                self.words,
                min_paragraphs=2,
                max_paragraphs=3,
                min_sentences=2,
                max_sentences=4,
                min_words=4,
                max_words=6,
            ),
        }

    def setup_styles(self):
        self.root.configure(bg=self.bg_color.get())
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.bg_color.get())
        self.style.configure(
            "TLabel",
            background=self.bg_color.get(),
            foreground=self.text_color.get(),
            font=(self.font_name.get(), 14),
        )
        self.style.configure(
            "TButton",
            font=(self.font_name.get(), 14),
            foreground=self.text_color.get(),
            background="#1abc9c",
        )
        self.style.map("TButton", background=[("active", "#16a085")])

    def create_widgets(self):
        self.container = ttk.Frame(self.root, style="TFrame")
        self.container.pack(padx=20, pady=20, fill="both", expand=True)

        self.text_display = tk.Text(
            self.container,
            font=(self.font_name.get(), self.font_size.get()),
            fg=self.text_color.get(),
            bg=self.bg_color.get(),
            wrap="word",
            height=5,
            width=30,
            insertbackground=self.text_color.get(),
        )
        self.text_display.pack(anchor="center", pady=(0, 20), fill="both", expand=True)
        self.text_display.config(state=tk.DISABLED, padx=10, pady=10)

        self.stats_frame = ttk.Frame(self.container, style="TFrame")
        self.stats_frame.pack(anchor="center", pady=10, fill="x")
        self.wpm_label = ttk.Label(self.stats_frame, text="WPM: 0.00", style="TLabel")
        self.wpm_label.pack(side="left", padx=(0, 20))
        self.accuracy_label = ttk.Label(
            self.stats_frame, text="Accuracy: 0.00%", style="TLabel"
        )
        self.accuracy_label.pack(side="left")

        self.result_label = ttk.Label(self.container, text="", style="TLabel")
        self.result_label.pack(anchor="center", pady=10)
        self.restart_button = ttk.Button(
            self.container,
            text="Restart",
            style="TButton",
            command=self.show_restart_popup,
        )
        self.restart_button.pack(anchor="center", pady=10)
        self.settings_button = ttk.Button(
            self.container, text="Settings", style="TButton", command=self.open_settings
        )
        self.settings_button.pack(anchor="center", pady=10)

        self.countdown_label = ttk.Label(self.container, text="", style="TLabel")
        self.countdown_label.pack(anchor="center", pady=10)

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x450")
        settings_window.configure(bg=self.bg_color.get())

        settings_frame = ttk.Frame(settings_window, padding="10", style="TFrame")
        settings_frame.pack(fill="both", expand=True)

        ttk.Label(settings_frame, text="Font Name:", style="TLabel").pack(
            anchor="w", pady=5
        )
        available_fonts = font.families()
        font_name_combobox = ttk.Combobox(
            settings_frame,
            textvariable=self.font_name,
            values=available_fonts,
            state="readonly",
        )
        font_name_combobox.pack(anchor="w", fill="x", pady=5)

        ttk.Label(settings_frame, text="Select Difficulty:", style="TLabel").pack(
            anchor="w", pady=5
        )
        difficulty_options = ttk.Combobox(
            settings_frame,
            textvariable=self.difficulty,
            values=["Easy", "Medium", "Hard"],
            state="readonly",
        )
        difficulty_options.pack(anchor="w", fill="x", pady=5)

        ttk.Label(settings_frame, text="Adjust Font Size:", style="TLabel").pack(
            anchor="w", pady=5
        )
        font_size_slider = ttk.Scale(
            settings_frame,
            from_=10,
            to=50,
            variable=self.font_size,
            orient="horizontal",
        )
        font_size_slider.pack(anchor="w", fill="x", pady=5)

        ttk.Label(settings_frame, text="Background Color:", style="TLabel").pack(
            anchor="w", pady=5
        )
        bg_color_button = ttk.Button(
            settings_frame, text="Choose Color", command=self.choose_bg_color
        )
        bg_color_button.pack(anchor="w", pady=5)

        ttk.Label(settings_frame, text="Text Color:", style="TLabel").pack(
            anchor="w", pady=5
        )
        text_color_button = ttk.Button(
            settings_frame, text="Choose Color", command=self.choose_text_color
        )
        text_color_button.pack(anchor="w", pady=5)

        apply_button = ttk.Button(
            settings_frame,
            text="Apply",
            command=lambda: self.apply_settings(settings_window),
        )
        apply_button.pack(anchor="center", pady=20)

    def choose_bg_color(self):
        color_code = colorchooser.askcolor(title="Choose Background Color")
        if color_code:
            self.bg_color.set(color_code[1])

    def choose_text_color(self):
        color_code = colorchooser.askcolor(title="Choose Text Color")
        if color_code:
            self.text_color.set(color_code[1])

    def apply_settings(self, settings_window):
        self.setup_styles()
        self.text_display.config(
            font=(self.font_name.get(), self.font_size.get()),
            fg=self.text_color.get(),
            bg=self.bg_color.get(),
        )
        self.restart()
        settings = {
            "font_name": self.font_name.get(),
            "font_size": self.font_size.get(),
            "bg_color": self.bg_color.get(),
            "text_color": self.text_color.get(),
            "difficulty": self.difficulty.get(),
        }
        save_settings(settings)
        settings_window.destroy()

    def bind_events(self):
        self.root.bind("<KeyPress>", self.check_input)
        self.root.bind("<Button-1>", self.set_focus)
        self.root.bind("<Configure>", self.on_resize)

    def restart(self):
        self.generate_texts()
        self.text_to_type = self.texts[self.difficulty.get()]
        self.user_input = []
        self.reset_stats()
        self.countdown(3)

    def countdown(self, count):
        if count > 0:
            self.countdown_label.config(text=f"Starting in {count}...")
            self.root.after(1000, self.countdown, count - 1)
        else:
            self.countdown_label.config(text="")
            self.root.bind("<KeyPress>", self.check_input)
            self.update_stats_real_time()

    def set_focus(self, event):
        self.root.focus_set()

    def update_display(self):
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete("1.0", tk.END)

        line_width = self.text_display.winfo_width()
        if line_width == 0:
            line_width = 1

        start_index = max(0, self.current_index - line_width // 2)
        display_text = self.text_to_type[
            start_index : self.current_index + line_width // 2
        ]

        lines = []
        while display_text:
            lines.append(display_text[:line_width])
            display_text = display_text[line_width:]

        display_text = "\n".join(lines)
        self.text_display.insert("1.0", display_text)

        cursor_pos = self.current_index - start_index
        line, col = divmod(cursor_pos, line_width)
        cursor_index = f"{line + 1}.{col}"
        self.text_display.mark_set("insert", cursor_index)

        for i, char in enumerate(display_text):
            global_index = start_index + i
            if global_index < self.current_index:
                if global_index < len(self.user_input):
                    typed_char = self.user_input[global_index]
                    tag = (
                        "correct"
                        if typed_char == self.text_to_type[global_index]
                        else "incorrect"
                    )
                    self.text_display.tag_add(tag, f"1.{i}", f"1.{i+1}")
            elif global_index == self.current_index:
                self.text_display.tag_add("current", f"1.{i}", f"1.{i+1}")
            else:
                self.text_display.tag_add("untouched", f"1.{i}", f"1.{i+1}")

        self.text_display.tag_config("correct", foreground="#2ecc71")
        self.text_display.tag_config("incorrect", foreground="#e74c3c")
        self.text_display.tag_config(
            "current",
            foreground=self.text_color.get() if self.blink_state else "#5c5c5c",
            background="#2c2c2c",
        )
        self.text_display.tag_config("untouched", foreground="#95a5a6")

        self.text_display.config(state=tk.DISABLED)

    def update_stats(self):
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        if elapsed_time > 0:
            words_per_minute = (self.correct_typed / 5) / (elapsed_time / 60)
            if self.total_keypresses > 0:
                accuracy = (self.correct_typed / self.total_keypresses) * 100
                self.accuracy_label.config(text=f"Accuracy: {accuracy:.2f}%")
            self.wpm_label.config(text=f"WPM: {words_per_minute:.2f}")

    def check_input(self, event):
        if self.start_time is None:
            self.start_time = time.time()

        if event.keysym == "BackSpace":
            if self.current_index > 0:
                self.current_index -= 1
                if len(self.user_input) > 0:
                    last_char = self.user_input.pop()
                    if last_char == self.text_to_type[self.current_index]:
                        self.correct_typed -= 1
                    else:
                        self.incorrect_typed -= 1
        elif event.keysym == "Tab":
            self.show_restart_popup()
        elif event.char and len(event.char) == 1 and event.char.isprintable():
            self.total_keypresses += 1  # Increment total keypress count
            typed_char = event.char
            correct_char = self.text_to_type[self.current_index]

            self.user_input.append(typed_char)
            self.current_index += 1

            if typed_char == correct_char:
                self.correct_typed += 1
            else:
                self.incorrect_typed += 1

            if self.current_index == len(self.text_to_type):
                self.finish_Maroon()

        self.update_display()
        self.update_stats()

    def finish_Maroon(self):
        time_taken = time.time() - self.start_time
        correct_words = self.correct_typed / 5
        words_per_minute = correct_words / (time_taken / 60)
        accuracy = (
            (self.correct_typed / self.total_keypresses) * 100
            if self.total_keypresses > 0
            else 0
        )
        self.result_label.config(
            text=f"Final WPM: {words_per_minute:.2f}, Final Accuracy: {accuracy:.2f}%"
        )
        self.stats_running = False
        self.root.unbind("<KeyPress>")
        self.show_restart_popup()

    def reset_stats(self):
        self.current_index = 0
        self.start_time = None
        self.correct_typed = 0
        self.incorrect_typed = 0
        self.total_keypresses = 0  # Reset total keypress count
        self.user_input = []
        self.result_label.config(text="")
        self.wpm_label.config(text="WPM: 0.00")
        self.accuracy_label.config(text="Accuracy: 0.00%")
        self.stats_running = True
        self.update_display()

    def update_stats_real_time(self):
        if self.stats_running:
            self.update_stats()
            self.root.after(1000, self.update_stats_real_time)

    def show_restart_popup(self):
        restart_window = tk.Toplevel(self.root)
        restart_window.title("Restart")
        restart_window.geometry("300x150")
        restart_window.configure(bg=self.bg_color.get())

        ttk.Label(restart_window, text="Do you want to restart?", style="TLabel").pack(
            pady=20
        )
        button_frame = ttk.Frame(restart_window, style="TFrame")
        button_frame.pack(pady=10)

        yes_button = ttk.Button(
            button_frame,
            text="Yes",
            style="TButton",
            command=self.restart_and_close_popup(restart_window),
        )
        yes_button.pack(side="left", padx=10)
        no_button = ttk.Button(
            button_frame, text="No", style="TButton", command=restart_window.destroy
        )
        no_button.pack(side="left", padx=10)

        restart_window.bind("<Return>", lambda event: yes_button.invoke())
        restart_window.bind("<Escape>", lambda event: no_button.invoke())

        restart_window.focus()
        yes_button.focus_set()

        yes_button.focus()

        restart_window.tk.call(
            "ttk::style",
            "configure",
            "TButton",
            {"background": "#16a085", "foreground": "white"},
        )

        restart_window.mainloop()

    def restart_and_close_popup(self, window):
        def restart():
            self.restart()
            window.destroy()

        return restart

    def blink_cursor(self):
        self.blink_state = not self.blink_state
        self.update_display()
        if self.stats_running:
            self.root.after(500, self.blink_cursor)

    def on_resize(self, event):
        new_width = event.width
        new_text_width = new_width - 40
        if new_text_width < 20:
            new_text_width = 20
        self.text_display.config(width=new_text_width)
        self.update_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = MaroonTyping(root)
    root.mainloop()
