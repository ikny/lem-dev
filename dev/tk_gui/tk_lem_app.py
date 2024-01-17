import tkinter as tk
from typing import Any
import tk_gui_elements as gui


class Lem:
    def __init__(self) -> None:
        self.root = tk.Tk(className="lem Looper Emulator")
        self.appbar = gui.AppBar(master=self.root).pack(fill="y")
        self.record_button = gui.RecordButton(master=self.root)
        self.tracks = gui.TrackList(master=self.root).pack(fill="both", expand=1)
        self.root.mainloop()


if __name__ == "__main__":
    l = Lem()
