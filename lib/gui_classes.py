import tkinter as tk
from typing import Any

from lem import Lem
from lem_gui import LemApp


class BpmPopup(tk.Toplevel):
    def __init__(self, master: LemApp, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.master: LemApp = master

        self.title("enter BPM")

        self.entry_line = tk.Frame(master=self)
        self.message = tk.Label(
            master=self.entry_line, text="Insert the desired BPM value: ")
        self.message.pack(side="left")
        self.bpm_entry = tk.Entry(master=self.entry_line, width=3)

        self.bpm_entry.pack(side="right")
        self.entry_line.pack(side="top", padx=30, pady=5)

        self.instructions = tk.Label(
            master=self, text="BPM value must be a whole number between 1 and 400")
        self.instructions.pack()

        self.confirm = tk.Button(
            master=self, text="Confirm!", command=self.set_bpm)
        self.confirm.pack(side="bottom", padx=5, pady=5)

    def validate(self, value: str) -> bool:
        try:
            val = int(value)
        except ValueError:
            return False

        return val > 0 and val <= 400

    def set_bpm(self) -> None:
        entry_value = self.bpm_entry.get()
        if not self.validate(value=entry_value):
            return
        # get entry val, close this popup
        bpm = int(entry_value)
        self.master.set_bpm(bpm=bpm)
        self.destroy()


class AppBar(tk.Frame):
    def __init__(self, state: Lem, master: LemApp, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.master: LemApp = master

        self._bpm_lbl = tk.Label(master=self, text="BPM: ")
        self._bpm_lbl.pack(side="left", padx=5, pady=5)

        self.dialog_button = tk.Button(
            master=self, text="set BPM", command=self.invoke_dialog)
        self.dialog_button.pack(side="right", padx=5, pady=5)

    def update_bpm(self, bpm: int) -> None:
        self._bpm_lbl.config(text=f"BPM: {bpm}")

    def invoke_dialog(self) -> None:
        top = BpmPopup(master=self.master)


class RecordButton(tk.Button):
    def __init__(self, master: LemApp, **kwargs: Any) -> None:
        super().__init__(master, text="Press to start recording (or press SPACE)", height=2,
                         command=self.clicked, **kwargs)
        self.pack(fill="x", expand=0)
        self.master: LemApp = master
        self._state = "waiting"

    def clicked(self) -> None:
        if self._state == "waiting":
            self.master.lem_state.recording = True
            self._state = "recording"
            self.config(text="Press to stop recording (or press SPACE)")
        else:
            self.master.lem_state.recording = False
            self.master.lem_state.post_production()
            self._state = "waiting"
            self.config(text="Press to start recording (or press SPACE)")
            self.master.tracklist.add_track()


class TrackList(tk.Frame):
    def __init__(self, master: LemApp, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self._tracks: dict[int, Track] = {}
        self._free_id = 0

        self.scrollable = tk.Canvas(master=self, height=200, width=280)
        self.scrollable.pack(side="left", fill="both", expand=1)

        self.track_frame = tk.Frame(master=self.scrollable)
        self.track_frame.pack(side="left", fill="both", expand=1)

        self.scroller = tk.Scrollbar(
            master=self, command=self.scrollable.yview)
        self.scroller.pack(side="right", fill="y", expand=0)

        self.scrollable.create_window(
            (0, 0), window=self.track_frame, anchor="nw")
        self.scrollable.config(yscrollcommand=self.scroller.set)

    def add_track(self) -> None:
        track = Track(id=self._free_id,
                      master=self.track_frame, tracklist=self)
        self._tracks[self._free_id] = track
        self._free_id += 1
        track.pack(fill="both", expand=1, pady=1)
        self._update_sizes()

    def _update_sizes(self) -> None:
        self.track_frame.update()
        self.scrollable.config(scrollregion=(
            0, 0, 0, self.track_frame.winfo_height()))

    def delete_track(self, track_id: int) -> None:
        self._tracks.pop(track_id)
        self._update_sizes()


class Track(tk.Frame):
    def __init__(self, id: int, master: tk.Frame, tracklist: TrackList, **kwargs: Any) -> None:
        super().__init__(master, highlightbackground="#DDD78D", highlightthickness=1, **kwargs)
        self.tracklist = tracklist

        self.track_id = id
        self.name = tk.Label(master=self, text=f"track {id}")
        self.name.pack(side="left", padx=10, pady=10)

        image = tk.PhotoImage(file="lib/images/trash-bin.png")
        self.image = image.subsample(10)
        self.delete_button = tk.Button(
            master=self, text="delete", image=self.image, command=self.destroy)
        self.delete_button.pack(side="right")

    def destroy(self) -> None:
        self.tracklist.delete_track(track_id=self.track_id)
        return super().destroy()
