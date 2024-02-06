import tkinter as tk
from gui_classes import *
from lem import Lem


class LemApp(tk.Tk):
    """The main class of this app. Provides a GUI and creates its own state.
    """

    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        """Initializes a new instance of LemApp and start running.

        Args (from tkinter documentation):
            Return a new Toplevel widget on screen SCREENNAME. A new Tcl interpreter will
            be created. BASENAME will be used for the identification of the profile file (see
            readprofile).
            It is constructed from sys.argv[0] without extensions if None is given. CLASSNAME
            is the name of the widget class.
        """
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.lem_state = Lem()

        # set GUI to darkmode
        self.tk_setPalette(background='#181818', foreground='#DDD78D')

        self.title("lem Looper Emulator")

        # create GUI elements
        self.app_bar = AppBar(state=self.lem_state, master=self)
        self.app_bar.pack()
        self.record_button = RecordButton(
            master=self, state="disabled", on_start_recording=self.on_start_recording, on_stop_recording=self.on_stop_recording)
        self.record_button.pack(fill="x", expand=0)
        self.tracklist = TrackList(master=self)
        self.tracklist.pack(fill="both", expand=1)

        # TODO: set_bpm call is just a debug option
        self.set_bpm(123)

        # start running
        self.mainloop()

    def set_bpm(self, bpm: int) -> None:
        """Prepares the state and the GUI for the actual recording flow. 

        Args:
            bpm (int): The value the user has entered into BpmPopup.
        """
        self.lem_state.initialize_stream(bpm=bpm)

        self.app_bar.update_bpm(bpm=bpm)
        self.record_button["state"] = "normal"

    def destroy(self) -> None:
        """A method to be called when the user closes the app's main window. Ensures the state has terminated.
        """
        self.lem_state.terminate()
        return super().destroy()

    """ The following functions are callbacks for various GUI elements """

    def on_start_recording(self) -> None:
        """A method to be passed as a callback to the RecordButton. Delegates the action to its state object.
        """
        self.lem_state.start_recording()

    def on_stop_recording(self) -> None:
        """A method to be passed as a callback to the RecordButton.
        Adds track in the GUI only if the track was added in the logic (see Lem.post_production for more details).
        """
        if self.lem_state.stop_recording():
            self.tracklist.add_track()


if __name__ == "__main__":
    app = LemApp()

# TODO: `method` vs `function`
