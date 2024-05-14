import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import random

class TypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Practice App")
        self.root.geometry("800x400")
        self.root.configure(bg="#2c3e50")

        self.texts = [
            "while form small thing that who number part still home however group say because possible real what system form same down",
            "each life people around write allow know mean number early great world again general between sentence again open study",
            "start head story now eye seem problem sometimes public call money read hold kind thought while also often always here every"
        ]
        self.text_to_type = random.choice(self.texts)
        self.user_input = []
        self.current_index = 0
        self.start_time = None
        self.correct_typed = 0
        self.incorrect_typed = 0
        self.blink_state = True
        self.stats_running = True

        self.style = ttk.Style()
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TLabel', background='#2c3e50', foreground='#ecf0f1', font=("Helvetica", 14))
        self.style.configure('TButton', font=("Helvetica", 14), foreground='#ecf0f1', background='#1abc9c')
        self.style.map('TButton', background=[('active', '#16a085')])

        self.container = ttk.Frame(root, style='TFrame')
        self.container.pack(padx=20, pady=20, fill="both", expand=True)

        self.text_display = tk.Text(self.container, font=("Courier", 18), fg="#ecf0f1", bg="#1c1c1c", wrap="none", height=4, width=50, insertbackground="#ecf0f1")
        self.text_display.pack(anchor="w", pady=(0, 20), fill="both", expand=True)

        self.text_display.insert("1.0", self.text_to_type)
        self.text_display.config(state=tk.DISABLED)

        self.stats_frame = ttk.Frame(self.container, style='TFrame')
        self.stats_frame.pack(anchor="w", pady=10, fill="x")

        self.wpm_label = ttk.Label(self.stats_frame, text="WPM: 0.00", style='TLabel')
        self.wpm_label.pack(side="left", padx=(0, 20))

        self.accuracy_label = ttk.Label(self.stats_frame, text="Accuracy: 0.00%", style='TLabel')
        self.accuracy_label.pack(side="left")

        self.result_label = ttk.Label(self.container, text="", style='TLabel')
        self.result_label.pack(anchor="w", pady=10)

        self.restart_button = ttk.Button(self.container, text="Restart", style='TButton', command=self.restart)
        self.restart_button.pack(anchor="w", pady=10)

        self.root.bind("<KeyPress>", self.check_input)
        self.root.bind("<Button-1>", self.set_focus)

        self.countdown_label = ttk.Label(self.container, text="", style='TLabel')
        self.countdown_label.pack(anchor="w", pady=10)

        self.reset_stats()
        self.countdown(3)
        self.blink_cursor()

        self.root.bind("<Configure>", self.on_resize)

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

        display_text = self.text_to_type[max(0, self.current_index - 50):self.current_index + 50]
        self.text_display.insert("1.0", display_text)

        for i, char in enumerate(display_text):
            global_index = max(0, self.current_index - 50) + i
            if global_index < self.current_index:
                if global_index < len(self.user_input):
                    typed_char = self.user_input[global_index]
                    tag = "correct" if typed_char == self.text_to_type[global_index] else "incorrect"
                    self.text_display.tag_add(tag, f"1.{i}", f"1.{i+1}")
            elif global_index == self.current_index:
                self.text_display.tag_add("current", f"1.{i}", f"1.{i+1}")
            else:
                self.text_display.tag_add("untouched", f"1.{i}", f"1.{i+1}")

        self.text_display.tag_config("correct", foreground="#2ecc71")
        self.text_display.tag_config("incorrect", foreground="#e74c3c")
        self.text_display.tag_config("current", foreground="#ecf0f1" if self.blink_state else "#1c1c1c", background="#1c1c1c")
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
            self.show_restart_alert()
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
        accuracy = (self.correct_typed / len(self.user_input)) * 100 if len(self.user_input) > 0 else 0
        self.result_label.config(text=f"Final WPM: {words_per_minute:.2f}, Final Accuracy: {accuracy:.2f}%")
        self.stats_running = False
        self.root.unbind("<KeyPress>")
        self.show_restart_alert()

    def restart(self):
        self.text_to_type = random.choice(self.texts)
        self.user_input = []
        self.reset_stats()
        self.countdown(3)

    def show_restart_alert(self):
        response = messagebox.askyesno("Restart", "Do you want to restart?")
        if response:
            self.restart()

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
