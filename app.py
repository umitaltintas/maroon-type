import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import random
from tkinter import font, messagebox
from tkinter import IntVar, StringVar
import json
import os

SETTINGS_FILE = "settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    return None


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)


class TypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Practice App")
        self.root.geometry("800x400")

        # Initialize settings variables
        settings = load_settings()
        if settings:
            self.font_name = StringVar(value=settings.get("font_name", "Courier"))
            self.font_size = IntVar(value=settings.get("font_size", 18))
            self.bg_color = StringVar(value=settings.get("bg_color", "#1c1c1c"))
            self.text_color = StringVar(value=settings.get("text_color", "#ecf0f1"))
            self.difficulty = StringVar(value=settings.get("difficulty", "Medium"))
        else:
            self.font_name = StringVar(value="Courier")
            self.font_size = IntVar(value=18)
            self.bg_color = StringVar(value="#1c1c1c")
            self.text_color = StringVar(value="#ecf0f1")
            self.difficulty = StringVar(value="Medium")

        # Texts based on difficulty levels
        self.texts = {
            "Easy": [
                "the quick brown fox jumps over the lazy dog",
                "an apple a day keeps the doctor away",
            ],
            "Medium": [
                "while form small thing that who number part still home however group say because possible real what system form same down",
                "each life people around write allow know mean number early great world again general between sentence again open study",
            ],
            "Hard": [
                "pneumonoultramicroscopicsilicovolcanoconiosis is a lung disease caused by the inhalation of very fine silicate or quartz dust",
                "supercalifragilisticexpialidocious even though the sound of it is something quite atrocious",
            ],
        }

        # Select initial text to type
        self.text_to_type = random.choice(self.texts[self.difficulty.get()])

        # User input tracking
        self.user_input = []
        self.current_index = 0
        self.start_time = None
        self.correct_typed = 0
        self.incorrect_typed = 0
        self.blink_state = True
        self.stats_running = True

        # Setup and create widgets
        self.setup_styles()
        self.create_widgets()
        self.bind_events()

        self.reset_stats()
        self.countdown(3)
        self.blink_cursor()

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
            wrap="none",
            height=4,
            width=50,
            insertbackground=self.text_color.get(),
        )
        self.text_display.pack(anchor="w", pady=(0, 20), fill="both", expand=True)
        self.text_display.config(state=tk.DISABLED)

        self.stats_frame = ttk.Frame(self.container, style="TFrame")
        self.stats_frame.pack(anchor="w", pady=10, fill="x")
        self.wpm_label = ttk.Label(self.stats_frame, text="WPM: 0.00", style="TLabel")
        self.wpm_label.pack(side="left", padx=(0, 20))
        self.accuracy_label = ttk.Label(
            self.stats_frame, text="Accuracy: 0.00%", style="TLabel"
        )
        self.accuracy_label.pack(side="left")

        self.result_label = ttk.Label(self.container, text="", style="TLabel")
        self.result_label.pack(anchor="w", pady=10)
        self.restart_button = ttk.Button(
            self.container, text="Restart", style="TButton", command=self.restart
        )
        self.restart_button.pack(anchor="w", pady=10)
        self.settings_button = ttk.Button(
            self.container, text="Settings", style="TButton", command=self.open_settings
        )
        self.settings_button.pack(anchor="w", pady=10)

        self.countdown_label = ttk.Label(self.container, text="", style="TLabel")
        self.countdown_label.pack(anchor="w", pady=10)

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x450")

        settings_frame = ttk.Frame(settings_window, padding="10", style="TFrame")
        settings_frame.pack(fill="both", expand=True)

        # Font selection
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

        # Difficulty selection
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

        # Font size slider
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

        # Background color entry
        ttk.Label(settings_frame, text="Background Color:", style="TLabel").pack(
            anchor="w", pady=5
        )
        bg_color_entry = ttk.Entry(settings_frame, textvariable=self.bg_color)
        bg_color_entry.pack(anchor="w", fill="x", pady=5)

        # Text color entry
        ttk.Label(settings_frame, text="Text Color:", style="TLabel").pack(
            anchor="w", pady=5
        )
        text_color_entry = ttk.Entry(settings_frame, textvariable=self.text_color)
        text_color_entry.pack(anchor="w", fill="x", pady=5)

        apply_button = ttk.Button(
            settings_frame,
            text="Apply",
            command=lambda: self.apply_settings(settings_window),
        )
        apply_button.pack(anchor="center", pady=20)

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
        self.text_to_type = random.choice(self.texts[self.difficulty.get()])
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

        display_text = self.text_to_type[
            max(0, self.current_index - 50) : self.current_index + 50
        ]
        self.text_display.insert("1.0", display_text)

        for i, char in enumerate(display_text):
            global_index = max(0, self.current_index - 50) + i
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
            foreground="#ecf0f1" if self.blink_state else "#5c5c5c",
            background="#2c2c2c",
        )
        self.text_display.tag_config("untouched", foreground="#95a5a6")

        self.text_display.config(state=tk.DISABLED)

    def update_stats(self):
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        if elapsed_time > 0:
            words_per_minute = (self.correct_typed / 5) / (elapsed_time / 60)
            if len(self.user_input) > 0:
                accuracy = (self.correct_typed / len(self.user_input)) * 100
                self.accuracy_label.config(text=f"Accuracy: {accuracy:.2f}%")
            self.wpm_label.config(text=f"WPM: {words_per_minute:.2f}")

    def update_stats_real_time(self):
        if self.stats_running:
            self.update_stats()
            self.root.after(1000, self.update_stats_real_time)

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
            typed_char = event.char
            correct_char = self.text_to_type[self.current_index]

            self.user_input.append(typed_char)
            self.current_index += 1

            if typed_char == correct_char:
                self.correct_typed += 1
            else:
                self.incorrect_typed += 1

            if self.current_index == len(self.text_to_type):
                self.finish_typing()

        self.update_display()
        self.update_stats()

    def finish_typing(self):
        time_taken = time.time() - self.start_time
        correct_words = self.correct_typed / 5
        words_per_minute = correct_words / (time_taken / 60)
        accuracy = (
            (self.correct_typed / len(self.user_input)) * 100
            if len(self.user_input) > 0
            else 0
        )
        self.result_label.config(
            text=f"Final WPM: {words_per_minute:.2f}, Final Accuracy: {accuracy:.2f}%"
        )
        self.stats_running = False
        self.root.unbind("<KeyPress>")
        self.show_restart_popup()

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

        # Set focus to the Yes button
        yes_button.focus()

        # Configure the appearance of the Yes button when focused
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

    def reset_stats(self):
        self.current_index = 0
        self.start_time = None
        self.correct_typed = 0
        self.incorrect_typed = 0
        self.user_input = []
        self.result_label.config(text="")
        self.wpm_label.config(text="WPM: 0.00")
        self.accuracy_label.config(text="Accuracy: 0.00%")
        self.stats_running = True
        self.update_display()

    def blink_cursor(self):
        self.blink_state = not self.blink_state
        self.update_display()
        if self.stats_running:
            self.root.after(500, self.blink_cursor)

    def on_resize(self, event):
        new_width = event.width // 10
        self.text_display.config(width=new_width)


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingApp(root)
    root.mainloop()
