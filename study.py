# How to run this file: python3 study.py 192.168.0.206

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading, sys, os, time
from mistyPy.Robot import Robot
from mistyPy.Events import Events

# Default facial expression and movements (arms and head)
DEFAULT_EXPRESSION = "e_DefaultContent.jpg"
# Always move arms and head (nod before speaking)
DEFAULT_MOVEMENTS = [
    ("move_arms", 0, 0),
    ("move_head", 0, 0, 0)
]

# Scripted intro, instruction, and outro messages
INTRO_MESSAGE = "Hello! Let's solve a fun number puzzle together."
INSTRUCTION_MESSAGE = (
    "To play KenKen, pick a number and place it in each small box so it matches the number in the colored area. "
    "Remember, you can't use the same number twice in any row or column."
)
OUTRO_MESSAGE = "You did it! Thanks for playing with me today."

# Instruction phrases tailored to KenKen puzzle context
# Narrative style: encouraging and clear, 3 phases
NARRATIVE_PHRASES = [
    (
        "Welcome! Look at the outlined cages and put the right number in each box.",
        "e_Content.jpg",
        DEFAULT_MOVEMENTS
    ),
    (
        "Great job! Keep going, you're filling in the boxes one by one.",
        "e_Joy.jpg",
        DEFAULT_MOVEMENTS
    ),
    (
        "Awesome! Just a few more to finish your puzzle.",
        "e_Admiration.jpg",
        DEFAULT_MOVEMENTS
    ),
]

# Coaching style: stern, focused on completion, 3 phases
COACHING_PHRASES = [
    (
        "Lock in those single cell cages first. Grab the guaranteed points.",
        "e_Content.jpg",
        DEFAULT_MOVEMENTS
    ),
    (
        "List out your valid combinations, then place numbers decisively.",
        "e_Joy.jpg",
        DEFAULT_MOVEMENTS
    ),
    (
        "You're almost done. Don't lose focus!",
        "e_Admiration.jpg",
        DEFAULT_MOVEMENTS
    ),
]

class MistyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("900x900")
        self.root.title("Misty GUI")

        # Initialize Robot instance
        global misty
        misty = Robot(ip_address)

        # Timer panel
        tk.Label(self.root, text="Timer", font=("Arial", 20)).pack(pady=(10,0))
        self.time_elapsed = 0
        self.running = False
        self.time_display = tk.Label(self.root, text="0:00", font=("Arial", 18))
        self.time_display.pack()
        tframe = tk.Frame(self.root); tframe.pack(pady=5)
        tk.Button(tframe, text="Start", command=self.start).grid(row=0, column=0, padx=5)
        tk.Button(tframe, text="Stop", command=self.stop).grid(row=0, column=1, padx=5)
        tk.Button(tframe, text="Reset", command=self.reset).grid(row=0, column=2, padx=5)
        self.update_time()
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=20)

        # Speech control
        tk.Label(self.root, text="Speech Control Panel", font=("Arial", 18)).pack()
        eframe = tk.Frame(self.root); eframe.pack(pady=5)
        self.textbox = tk.Entry(eframe, width=60, font=("Arial", 10))
        self.textbox.grid(row=0, column=0, padx=5)
        tk.Button(eframe, text="Speak", command=self.on_speak).grid(row=0, column=1, padx=5)
        tk.Button(eframe, text="Clear", command=self.text_erase).grid(row=0, column=2, padx=5)

        # Scripted messages
        sf = tk.Frame(self.root); sf.pack(pady=5)
        tk.Button(sf, text="Intro", width=20, bg="#ade8f4",
                  command=lambda: self.queue_speech(INTRO_MESSAGE, DEFAULT_EXPRESSION, DEFAULT_MOVEMENTS)).grid(row=0, column=0, padx=5)
        tk.Button(sf, text="Instructions", width=20, bg="#aaffaa",
                  command=lambda: self.queue_speech(INSTRUCTION_MESSAGE, DEFAULT_EXPRESSION, DEFAULT_MOVEMENTS)).grid(row=0, column=1, padx=5)
        tk.Button(sf, text="Outro", width=20, bg="#ffc8dd",
                  command=lambda: self.queue_speech(OUTRO_MESSAGE, DEFAULT_EXPRESSION, DEFAULT_MOVEMENTS)).grid(row=0, column=2, padx=5)

        # Narrative instruction
        tk.Label(self.root, text="Narrative Instruction", font=("Arial", 14)).pack(pady=(10,5))
        nf = tk.Frame(self.root); nf.pack(pady=5)
        for idx, (msg, exp, moves) in enumerate(NARRATIVE_PHRASES, 1):
            tk.Button(nf, text=f"{idx}. {msg}", anchor='w', width=80,
                      command=lambda m=msg, e=exp, mv=moves: self.queue_speech(m, e, mv)).pack(pady=2)

        # Coaching instruction
        tk.Label(self.root, text="Coaching Instruction", font=("Arial", 14)).pack(pady=(10,5))
        cf = tk.Frame(self.root); cf.pack(pady=5)
        for idx, (msg, exp, moves) in enumerate(COACHING_PHRASES, 1):
            tk.Button(cf, text=f"{idx}. {msg}", anchor='w', width=80,
                      command=lambda m=msg, e=exp, mv=moves: self.queue_speech(m, e, mv)).pack(pady=2)

        self.root.mainloop()

    def on_speak(self):
        text = self.textbox.get()
        if text:
            self.queue_speech(text, DEFAULT_EXPRESSION, DEFAULT_MOVEMENTS)

    def queue_speech(self, phrase, expression, movements):
        threading.Thread(target=self._robot_speak, args=(phrase, expression, movements), daemon=True).start()

    def _robot_speak(self, phrase, expression, movements):
        # Nod before speaking
        try:
            misty.move_head(60, 0, 0)
            misty.move_head(-60, 0, 0)
            misty.move_head(60, 0, 0)
            time.sleep(0.1)
        except:
            pass
        # Display expression
        try:
            misty.display_image(expression, expression, 0, 0)
        except:
            pass
        # Execute default movements
        for mv in movements:
            try:
                action, *args = mv
                getattr(misty, action)(*args)
            except:
                pass
        # Speak with reduced speed
        misty.speak(text=phrase, speechRate=0.75)

    def text_erase(self):
        self.textbox.delete(0, tk.END)

    def update_time(self):
        if self.running:
            self.time_elapsed += 1
            mins, secs = divmod(self.time_elapsed, 60)
            self.time_display.config(text=f"{mins}:{secs:02}")
        self.root.after(1000, self.update_time)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def reset(self):
        self.running = False
        self.time_elapsed = 0
        self.time_display.config(text="0:00")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 study.py <Misty IP Address>")
        sys.exit(1)
    ip_address = sys.argv[1]
    MistyGUI()
