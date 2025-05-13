# lab_4_misty_woz_gui.py
# How to run this file: python3 study.py 192.168.0.206

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading, websocket, sys, os, time

SDK_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Python-SDK'))

# Add MistyPy SDK path
if SDK_PATH not in sys.path:
    sys.path.insert(0, SDK_PATH)
from mistyPy.Robot import Robot

# class DummyRobot:
#     """
#     Dummy robot for offline testing; prints instead of sending commands.
#     """
#     def speak(self, phrase):
#         print(f"[DummyRobot] speak: {phrase}")
#     def move_head(self, x, y, z, speed):
#         print(f"[DummyRobot] move_head: x={x}, y={y}, z={z}, speed={speed}")
#     def enable_camera_service(self):
#         print("[DummyRobot] enable_camera_service called")
#         class Resp: status_code = 200
#         return Resp()
#     def start_video_streaming(self, **kwargs):
#         print(f"[DummyRobot] start_video_streaming: {kwargs}")
#         class Resp: status_code = 200
#         return Resp()

# Scripted intro and outro messages
INTRO_MESSAGE = (
    "Hello and welcome! Thank you for participating in our study. "
    "I will provide guidance and encouragement throughout the session."
)
OUTRO_MESSAGE = (
    "This concludes our session. Thank you for your time and effort! "
    "Please proceed to complete any remaining surveys."
)

# Condition-specific phrases
NARRATIVE_PHRASES = [
    "We’re on a mission—defuse the bomb before time runs out!",
    "Great job! Only a few puzzles left on our quest.",
    "The countdown’s ticking—let’s push forward, teammate!",
]
COACHING_PHRASES = [
    "You’re doing great, keep going at your own pace.",
    "Remember to breathe; you’ve got this!",
    "Nice work—stay focused and you’ll finish soon.",
]
# Generic phrases for ad-hoc encouragement
GENERIC_PHRASES = [
    "Keep up the great work!",
    "Feel free to take a short break if needed.",
    "Stay relaxed and focused.",
]

class MistyGUI:
    def __init__(self):
        # Initialize root window
        self.root = tk.Tk()
        self.root.geometry("900x900")
        self.root.title("Misty GUI")

        # Robot instance: real or dummy
        global misty
        misty = Robot(ip_address)
        # if Robot is not None:
        #     misty = Robot(ip_address)
        # else:
        #     misty = DummyRobot()

        # Section 1: Timer
        tk.Label(self.root, text="Timer", font=("Arial", 20)).pack(pady=(10,0))
        self.time_elapsed, self.running = 0, False
        self.time_display = tk.Label(self.root, text="0:00", font=("Arial", 18))
        self.time_display.pack()
        tf = tk.Frame(self.root); tf.pack(pady=5)
        tk.Button(tf, text="Start", command=self.start).grid(row=0, column=0, padx=5)
        tk.Button(tf, text="Stop", command=self.stop).grid(row=0, column=1, padx=5)
        tk.Button(tf, text="Reset", command=self.reset).grid(row=0, column=2, padx=5)
        self.update_time()
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=20)

        # Section 2: Speech Control Panel
        tk.Label(self.root, text="Speech Control Panel", font=("Arial", 18)).pack()
        ef = tk.Frame(self.root); ef.pack(pady=5)
        self.textbox = tk.Entry(ef, width=80, font=("Arial", 10))
        self.textbox.grid(row=0, column=0, padx=5)
        tk.Button(ef, text="Speak", command=lambda: self.speak(self.textbox.get())).grid(row=0, column=1, padx=5)
        tk.Button(ef, text="Clear", command=self.text_erase).grid(row=0, column=2, padx=5)

        # Scripted intro/outro
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(self.root, text="Scripted Messages", font=("Arial", 14)).pack()
        sf = tk.Frame(self.root); sf.pack(pady=5)
        tk.Button(sf, text="Intro", width=30, bg="#ade8f4",
                  command=lambda: self.speak(INTRO_MESSAGE)).grid(row=0, column=0, padx=5, pady=2)
        tk.Button(sf, text="Outro", width=30, bg="#ffc8dd",
                  command=lambda: self.speak(OUTRO_MESSAGE)).grid(row=0, column=1, padx=5, pady=2)

        # Condition-split phrases
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(self.root, text="Narrative Phrases", font=("Arial", 14)).pack(pady=(5,0))
        nf = tk.Frame(self.root); nf.pack(pady=5)
        for idx, msg in enumerate(NARRATIVE_PHRASES, 1):
            tk.Button(nf, text=f"{idx}. {msg}", anchor='w', width=80,
                      command=lambda m=msg: self.speak(m)).pack(pady=2)
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(self.root, text="Coaching Phrases", font=("Arial", 14)).pack(pady=(5,0))
        cf = tk.Frame(self.root); cf.pack(pady=5)
        for idx, msg in enumerate(COACHING_PHRASES, 1):
            tk.Button(cf, text=f"{idx}. {msg}", anchor='w', width=80,
                      command=lambda m=msg: self.speak(m)).pack(pady=2)

        # Generic phrases
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(self.root, text="Generic Phrases", font=("Arial", 14)).pack(pady=(5,0))
        gf = tk.Frame(self.root); gf.pack(pady=5)
        for idx, msg in enumerate(GENERIC_PHRASES, 1):
            tk.Button(gf, text=f"{idx}. {msg}", anchor='w', width=80,
                      command=lambda m=msg: self.speak(m)).pack(pady=2)

        # Section 3: Action Control Panel
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=20)
        tk.Label(self.root, text="Action Control Panel", font=("Arial", 18)).pack()
        af = tk.Frame(self.root); af.pack(pady=5)
        tk.Button(af, text="Move Head 1", command=lambda: self.action("move_head_1")).grid(row=0, column=0, padx=5)

        self.root.mainloop()

    def speak(self, phrase):
        print(f"Speak: {phrase}")
        misty.speak(phrase)

    def action(self, phrase):
        print(f"Action: {phrase}")
        if phrase == "move_head_1":
            misty.move_head(-15,0,0,80)

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
