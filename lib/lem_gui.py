import tkinter as tk
from gui_classes import *
from lem import Lem


class LemApp(tk.Tk):
    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.lem_state = Lem()

        self.tk_setPalette(background='#181818', foreground='#DDD78D')

        self.title("lem Looper Emulator")

        self.app_bar = AppBar(state=self.lem_state, master=self)
        self.app_bar.pack()
        self.record_button = RecordButton(master=self, state="disabled")
        self.record_button.pack(fill="x")
        self.tracklist = TrackList(master=self)
        self.tracklist.pack(fill="both", expand=1)

        self.mainloop()

    def set_bpm(self, bpm: int) -> None:
        # invoke state's set bpm, change appbar's bpm label, enable rec button, delete the set bpm button
        self.lem_state.set_bpm(bpm=bpm)

        self.app_bar.update_bpm(bpm=bpm)
        self.record_button["state"] = "normal"
        self.app_bar.dialog_button.destroy()


if __name__ == "__main__":
    app = LemApp()
