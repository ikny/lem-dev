import tkinter as tk
import tkinter.ttk as ttk
from typing import Any


class AppBar(ttk.Frame):
    def __init__(self, master: Any = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.bpm_input = BpmInputBox(master=self).pack()


class BpmInputBox(ttk.Frame):
    def __init__(self, master: Any = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.text = ttk.Label(master=master, text="BPM: ").pack(
            side="left", padx=5, pady=10)
        self.inputbox = ttk.Entry(master=master, width=3).pack(
            side="right", padx=5, pady=10)


class RecordButton(ttk.Button):
    def __init__(self, master: Any = None, **kwargs: Any) -> None:
        super().__init__(master, text="Press to start recording (or press SPACE)", **kwargs)
        self.pack(fill="both", expand=1)


class TrackList(ttk.Frame):
    def __init__(self, master: Any = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.scrollable = tk.Listbox(master=self).pack(
            side="left", fill="both", expand=1)
        self.scroller = ttk.Scrollbar(
            master=self).pack(side="right", fill="y", expand=1)


class Track(ttk.Frame):
    def __init__(self, master: Any = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
