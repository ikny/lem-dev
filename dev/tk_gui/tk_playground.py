import tkinter as tk
import tkinter.ttk as ttk
from typing import Any
import tk_gui_elements as gui


DARK_GREY = "181818"
DARK_GREEN = "2E5D5B"
BONE = "B1C6CF"


class App(tk.Tk):
    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.title("test Looper Emulator")

        self.style = ttk.Style()
        self.style.theme_use("clam")


        self.label = ttk.Label(master=self, text="Hello, world!").pack(side="top", expand=True, fill="both")
        self.button = ttk.Button(master=self, text="record!!").pack(side="top", expand=True, fill="both")
        self.tracklist = gui.TrackList(master=self).pack(side="top", expand=True, fill="both")
        self.mainloop()


if __name__ == "__main__":
    a = App()
