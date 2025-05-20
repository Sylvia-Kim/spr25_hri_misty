# How to run this file: python3 study.py 192.168.0.206

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading, websocket, sys, os, time
from io import BytesIO
import requests

# Add local Python-SDK path for MistyPy
SDK_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Python-SDK'))
if SDK_PATH not in sys.path:
    sys.path.insert(0, SDK_PATH)

from mistyPy.Robot import Robot
from mistyPy.Events import Events

# Default facial expression
DEFAULT_EXPRESSION = "e_DefaultContent.jpg"

# Scripted intro and outro messages
INTRO_MESSAGE = (
    "Hello and welcome! Thank you for participating in our study. "
    "I will provide guidance and encouragement throughout the session."
)
OUTRO_MESSAGE = (
    "This concludes our session. Thank you for your time and effort! "
    "Please proceed to complete any remaining surveys."
)

# Condition-specific phrases with associated expressions
NARRATIVE_PHRASES = [
    ("We’re on a mission—defuse the bomb before time runs out!", "e_Fear.jpg"),
    ("Great job! Only a few puzzles left on our quest.", "e_Joy.jpg"),
    ("The countdown’s ticking—let’s push forward, teammate!", "e_Surprise.jpg"),
]
COACHING_PHRASES = [
    ("You’re doing great, keep going at your own pace.", "e_Content.jpg"),
    ("Remember to breathe; you’ve got this!", "e_Admiration.jpg"),
    ("Nice work—stay focused and you’ll finish soon.", "e_Joy.jpg"),
]
GENERIC_PHRASES = [
    ("Keep up the great work!", "e_Joy2.jpg"),
    ("Feel free to take a short break if needed.", "e_Sleepy.jpg"),
    ("Stay relaxed and focused.", "e_DefaultContent.jpg"),
]/

class MistyGUI:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.geometry("900x900")
        self.root.title("Misty GUI")

        # Initialize Robot instance
        global misty
        misty = Robot(ip_address)

        # Section 1: Timer
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

        # Section 2: Speech Control Panel
        tk.Label(self.root, text="Speech Control Panel", font=("Arial", 18)).pack()
        eframe = tk.Frame(self.root); eframe.pack(pady=5)
        self.textbox = tk.Entry(eframe, width=60, font=("Arial", 10))
        self.textbox.grid(row=0, column=0, padx=5)
        tk.Button(eframe, text="Speak", command=self.on_speak).grid(row=0, column=1, padx=5)
        tk.Button(eframe, text="Clear", command=self.text_erase).grid(row=0, column=2, padx=5)

        # Scripted Messages
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(self.root, text="Scripted Messages", font=("Arial", 14)).pack(pady=(0,5))
        sf = tk.Frame(self.root); sf.pack(pady=5)
        tk.Button(sf, text="Intro", width=30, bg="#ade8f4",
                  command=lambda: self.queue_speech(INTRO_MESSAGE, DEFAULT_EXPRESSION)).grid(row=0, column=0, padx=5, pady=2)
        tk.Button(sf, text="Outro", width=30, bg="#ffc8dd",
                  command=lambda: self.queue_speech(OUTRO_MESSAGE, DEFAULT_EXPRESSION)).grid(row=0, column=1, padx=5, pady=2)

        # Narrative phrases
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(self.root, text="Narrative Phrases", font=("Arial", 14)).pack(pady=(0,5))
        nf = tk.Frame(self.root); nf.pack(pady=5)
        for idx, (msg, exp) in enumerate(NARRATIVE_PHRASES, 1):
            tk.Button(nf, text=f"{idx}. {msg}", anchor='w', width=80,
                      command=lambda m=msg, e=exp: self.queue_speech(m, e)).pack(pady=2)

        # Coaching phrases
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(self.root, text="Coaching Phrases", font=("Arial", 14)).pack(pady=(0,5))
        cf = tk.Frame(self.root); cf.pack(pady=5)
        for idx, (msg, exp) in enumerate(COACHING_PHRASES, 1):
            tk.Button(cf, text=f"{idx}. {msg}", anchor='w', width=80,
                      command=lambda m=msg, e=exp: self.queue_speech(m, e)).pack(pady=2)

        # Generic phrases
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(self.root, text="Generic Phrases", font=("Arial", 14)).pack(pady=(0,5))
        gf = tk.Frame(self.root); gf.pack(pady=5)
        for idx, (msg, exp) in enumerate(GENERIC_PHRASES, 1):
            tk.Button(gf, text=f"{idx}. {msg}", anchor='w', width=80,
                      command=lambda m=msg, e=exp: self.queue_speech(m, e)).pack(pady=2)

        # Section 3: Action Control Panel
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=20)
        tk.Label(self.root, text="Action Control Panel", font=("Arial", 18)).pack(pady=(0,5))
        af = tk.Frame(self.root); af.pack(pady=5)
        tk.Button(af, text="Move Head 1",
                  command=lambda: self.queue_action("move_head_1")).grid(row=0, column=0, padx=5)

        self.root.mainloop()

    def on_speak(self):
        text = self.textbox.get()
        if text:
            self.queue_speech(text, DEFAULT_EXPRESSION)

    def queue_speech(self, phrase, expression):
        threading.Thread(target=self._robot_speak, args=(phrase, expression), daemon=True).start()

    def _robot_speak(self, phrase, expression):
        # 1) Display chosen expression
        try:
            misty.display_image(expression, expression, 0, 0)
        except Exception as e:
            print(f"Failed to display expression {expression}: {e}")
        # 2) Speak the phrase
        misty.speak(phrase)

    def queue_action(self, phrase):
        threading.Thread(target=self._robot_action, args=(phrase,), daemon=True).start()

    def _robot_action(self, phrase):
        if phrase == "move_head_1":
            misty.move_head(-15, 0, 0, 80)

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

# Run the GUI
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 lab_4_misty_woz_gui.py <Misty IP Address>")
        sys.exit(1)
    ip_address = sys.argv[1]
    MistyGUI()
