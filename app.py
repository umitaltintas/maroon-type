import tkinter as tk
from tkinter import messagebox
import time
import random

class TypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Practice App")
        self.root.geometry("800x400")
        self.root.configure(bg="#1e1e1e")

        self.texts = [
            "while form small thing that who number part still home however group say because possible real what system form same down",
            "each life people around write allow know mean number early great world again general between sentence again open study",
            "start head story now eye seem problem sometimes public call money read hold kind thought while also often always here every"
        ]
        self.text_to_type = random.choice(self.texts)
        self.current_index = 0
        self.start_time = None
        self.total_typed = 0
        self.incorrect_typed = 0

        self.container = tk.Frame(root, bg="#1e1e1e")
        self.container.pack(padx=20, pady=20, fill="both", expand=True)

        self.text_display = tk.Text(self.container, font=("Courier", 18), fg="#dcdcdc", bg="#1e1e1e", wrap="none", height=4, width=90)
        self.text_display.pack(anchor="w", pady=(0, 20))
        self.text_display.insert("1.0", self.text_to_type)
        self.text_display.config(state=tk.DISABLED)

        self.stats_frame = tk.Frame(self.container, bg="#1e1e1e")
        self.stats_frame.pack(anchor="w", pady=10, fill="x")

        self.wpm_label = tk.Label(self.stats_frame, text="WPM: 0.00", font=("Courier", 18), fg="#dcdcdc", bg="#1e1e1e")
        self.wpm_label.pack(side="left", padx=(0, 20))

        self.accuracy_label = tk.Label(self.stats_frame, text="Accuracy: 0.00%", font=("Courier", 18), fg="#dcdcdc", bg="#1e1e1e")
        self.accuracy_label.pack(side="left")

        self.result_label = tk.Label(self.container, text="", font=("Courier", 18), fg="#dcdcdc", bg="#1e1e1e")
        self.result_label.pack(anchor="w", pady=10)

        self.restart_button = tk.Button(self.container, text="Restart", font=("Courier", 18), fg="#dcdcdc", bg="#3e3e3e", command=self.restart)
        self.restart_button.pack(anchor="w", pady=10)

        self.root.bind("<KeyPress>", self.check_input)
        self.root.bind("<Button-1>", self.set_focus)

        self.countdown_label = tk.Label(self.container, text="", font=("Courier", 18), fg="#dcdcdc", bg="#1e1e1e")
        self.countdown_label.pack(anchor="w", pady=10)

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

        display_text = self.text_to_type[self.current_index:]
        self.text_display.insert("1.0", display_text)

        for i, char in enumerate(display_text):
            if i < self.current_index:
                typed_char = self.text_to_type[i]
                if typed_char == char:
                    self.text_display.insert(tk.END, char, ("correct",))
                else:
                    self.text_display.insert(tk.END, char, ("incorrect",))
            elif i == 0:
                self.text_display.insert(tk.END, char, ("current",))
            else:
                self.text_display.insert(tk.END, char, ("untouched",))

        self.text_display.tag_config("correct", foreground="#00FF00")
        self.text_display.tag_config("incorrect", foreground="#FF0000")
        self.text_display.tag_config("current", foreground="#dcdcdc", background="#333333")
        self.text_display.tag_config("untouched", foreground="#555555")

        self.text_display.config(state=tk.DISABLED)

    def update_stats(self):
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        if elapsed_time > 0:
            words_per_minute = (self.current_index / 5) / (elapsed_time / 60)
            if self.total_typed > 0:
                accuracy = ((self.current_index - self.incorrect_typed) / self.total_typed) * 100
                self.accuracy_label.config(text=f"Accuracy: {accuracy:.2f}%")
            self.wpm_label.config(text=f"WPM: {words_per_minute:.2f}")

    def update_stats_real_time(self):
        self.update_stats()
        self.root.after(1000, self.update_stats_real_time)

    def check_input(self, event):
        if self.start_time is None:
            self.start_time = time.time()

        if event.keysym == "BackSpace":
            pass  # Disable backspace functionality
        elif event.keysym == "Tab":
            self.show_restart_alert()
        elif event.char and len(event.char) == 1 and event.char.isprintable():
            typed_char = event.char
            correct_char = self.text_to_type[self.current_index]

            self.total_typed += 1
            if typed_char == correct_char:
                self.current_index += 1
            else:
                self.incorrect_typed += 1
                self.current_index += 1

            if self.current_index == len(self.text_to_type):
                self.finish_typing()

        self.update_display()
        self.update_stats()

    def finish_typing(self):
        time_taken = time.time() - self.start_time
        words_per_minute = len(self.text_to_type.split()) / (time_taken / 60)
        if self.total_typed > 0:
            accuracy = ((self.current_index - self.incorrect_typed) / self.total_typed) * 100
        else:
            accuracy = 0
        self.result_label.config(text=f"Final WPM: {words_per_minute:.2f}, Final Accuracy: {accuracy:.2f}%")
        self.root.unbind("<KeyPress>")
        self.show_restart_alert()

    def restart(self):
        self.text_to_type = random.choice(self.texts)
        self.reset_stats()
        self.countdown(3)

    def show_restart_alert(self):
        response = messagebox.askyesno("Restart", "Do you want to restart?")
        if response:
            self.restart()

    def reset_stats(self):
        self.current_index = 0
        self.start_time = None
        self.total_typed = 0
        self.incorrect_typed = 0
        self.result_label.config(text="")
        self.wpm_label.config(text="WPM: 0.00")
        self.accuracy_label.config(text="Accuracy: 0.00%")
        self.update_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingApp(root)
    root.mainloop()
