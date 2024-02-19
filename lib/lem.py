# types
from typing import Any
import numpy.typing as npt
# libs
import sounddevice as sd
import numpy as np
import soundfile as sf
import threading
from time import sleep
# parts of project
from constants import *
from tracks import RecordedTrack, PlayingTrack
from custom_exceptions import InvalidSamplerateError


class Lem():
    """Handles the logic of the looper emulator. 
    While LoopStreamManager only knows how to record a track and update its tracks data, 
    Lem operates on a higher level, featuring a metronome,
    adding, removing and modifying individual tracks. 
    """

    def __init__(self, bpm: int) -> None:
        """Initialize a new instance of Lem (looper emulator).

        Args:
            bpm (int): Beats per minute. This class presumes that 0 < bpm < musically reasonable value (400).
        """
        # rounding to int introduces a slight distortion of bpm
        self._len_beat = int(60*SAMPLERATE/bpm)
        self._stream_manager = LoopStreamManager()
        self._tracks: list[PlayingTrack] = []

        self.initialize_metronome()
        self._stream_manager.start_stream()

    def initialize_metronome(self) -> None:
        """Prepare the metronome so that the sample is long exactly one beat of the set BPM.

        Raises:
            InvalidSamplerateError: If the samplerate of the audio file on path is not the same as SAMPLERATE.
            soundfile.LibsndfileError: If the file on path could not be opened.
            TypeError: If the dtype could not be recognized.
            ZeroDivisionError: If bpm = 0.
        """
        sample: npt.NDArray[DTYPE]
        sample, samplerate = sf.read(
            file=METRONOME_SAMPLE_PATH, dtype=STR_DTYPE)
        if samplerate != SAMPLERATE:
            raise InvalidSamplerateError()

        if len(sample) <= self._len_beat:
            sample = np.concatenate(
                (sample, np.zeros(shape=(self._len_beat-len(sample), CHANNELS), dtype=DTYPE)))
        else:
            sample = sample[:self._len_beat]

        self._tracks.append(PlayingTrack(data=sample))
        self._update_tracks()

    def terminate(self) -> None:
        """Delegate the closing of the stream to stream manager.
        """
        self._stream_manager.end_stream()

    def start_recording(self) -> None:
        """Delegate the start to its stream manager.
        """
        self._stream_manager.start_recording()

    def stop_recording(self) -> bool:
        """Delegate the stop to its stream manager. 
        This returns the new track, which is then passed to post production method.

        Returns:
            bool: Passes the value returned by the post_production method.
        """
        recorded_track = self._stream_manager.stop_recording()
        return self.post_production(recorded_track=recorded_track)

    def post_production(self, recorded_track: RecordedTrack) -> bool:
        """Cut/fill newly recorded track to whole bpm and add it to tracks.

        Args:
            recorded_track (npt.NDArray[DTYPE]): The audio data to be modified.

        Returns:
            bool: True if the track was long at least one beat, thus it was actually added into tracks. 
            False if the rounding resulted in an empty track.
        """
        data = recorded_track.data
        remainder = len(data) % self._len_beat

        if remainder > self._len_beat/2:
            zeros = np.zeros(
                shape=(self._len_beat-remainder, CHANNELS), dtype=DTYPE)
            data = np.concatenate([data, zeros])
        elif remainder <= self._len_beat/2:
            data = data[:len(
                data)-remainder]

        if len(data):
            self._tracks.append(PlayingTrack(data=data))
            self._update_tracks()
            return True
        return False

    def delete_track(self, idx: int) -> None:
        """Removes the track on index idx+1, because the first track is the metronome sample.

        Args:
            idx (int): The index of the track which is being deleted.
        """
        self._tracks.pop(idx+1)
        self._update_tracks()

    def _update_tracks(self) -> None:
        """Pass self._tracks to update_tracks method of its stream manager.
        """
        self._stream_manager.update_tracks(tracks=self._tracks)


class LoopStreamManager():
    """Manages the sounddevice stream thread including error handling.
    Plays the content of _tracks in a loop. 
    Can record a new track and update _tracks in a thread-safe way.

    For more information about sounddevice library see sounddevice documentation:
    https://python-sounddevice.readthedocs.io/en/0.4.6/api/index.html.
    """

    def __init__(self) -> None:
        """Initialize a new LoopStreamManager object.
        """
        # flags
        self._recording = False
        self._stream_active = True

        self._current_frame = 0

        self._stream_thread: threading.Thread
        # the audio data to be played
        self._tracks: list[PlayingTrack] = []
        # the synchronized backup of _tracks which is used as a data source when the _tracks are being updated
        self._tracks_copy: list[PlayingTrack] = self._tracks
        self._tracks_lock: threading.Lock = threading.Lock()

        self._recorded_track = RecordedTrack()

    def start_stream(self) -> None:
        """Make a new thread, in which the stream will be active
        """
        self._stream_thread = threading.Thread(target=self.main)
        self._stream_thread.start()

    def end_stream(self) -> None:
        """Set stream_active to false and wait for the stream thread to end. 
        If the stream was not initialized yet, there is no waiting.
        """
        self._stream_active = False
        try:
            self._stream_thread.join()
        except AttributeError:
            return

    def start_recording(self) -> None:
        """Set the _recording flag to True. This works because 
        the callback method checks the flag when deciding whether to store indata.
        """
        self._recording = True

    def stop_recording(self) -> RecordedTrack:
        """Set the _recording flag to False and prepare _recording_track for new recording.

        Returns:
            npt.NDArray[DTYPE]: The recorded track.
        """
        self._recording = False
        recorded_track = self._recorded_track
        self._recorded_track = RecordedTrack()
        return recorded_track

    def update_tracks(self, tracks: list[PlayingTrack]) -> None:
        """Update its data in a thread safe manner using lock. First update the backup, 
        from which will the callback read while _tracks are being updated.

        Args:
            tracks (npt.NDArray[DTYPE]): New data by which _tracks will be replaced.
        """
        self._tracks_copy = self._tracks
        with self._tracks_lock:
            self._tracks = tracks

    def main(self) -> None:
        """Open a sounddevice stream and keep it active while flag _stream_active is true.
        """
        def slice_and_mix(indata: npt.NDArray[DTYPE], frames: int) -> npt.NDArray[DTYPE]:
            if not self._tracks_lock.locked():
                tracks = self._tracks
            else:
                tracks = self._tracks_copy

            sliced_data = [indata]
            for track in tracks:
                sliced_data.append(track.slice(
                    from_frame=self._current_frame, frames=frames))

            mixed_data: npt.NDArray[DTYPE] = np.mean(a=sliced_data, axis=0)
            return mixed_data

        def callback(indata: npt.NDArray[DTYPE], outdata: npt.NDArray[DTYPE],
                     frames: int, time: Any, status: sd.CallbackFlags) -> None:
            """The callback method, which is called by the stream every time it needs audio data.
            As mentioned in the sounddevice documentation, the callback has to have these arguments and return None.
            For more information about callback see: https://python-sounddevice.readthedocs.io/en/0.4.6/api/streams.html#streams-using-numpy-arrays.

            Args:
                indata (npt.NDArray[DTYPE]): The input buffer. A two-dimensional numpy array with a shape of (frames, channels).
                outdata (npt.NDArray[DTYPE]): The output buffer. A two-dimensional numpy array with a shape of (frames, channels).
                frames (int): The number of frames to be processed (same as the length of input and output buffers).
                time (Any): A timestamp of the capture of the first indata frame.
                status (sd.CallbackFlags): CallbackFlags object, indicating whether input/output under/overflow is happening.
            """
            # handle errs
            if status.output_underflow:
                outdata.fill(0)
                return

            if self._recording:
                self._recorded_track.append(data=indata)

            outdata[:] = slice_and_mix(indata=indata, frames=frames)

            self._current_frame += frames

        with sd.Stream(samplerate=SAMPLERATE, blocksize=BLOCKSIZE, dtype=STR_DTYPE, channels=CHANNELS, callback=callback):
            while self._stream_active:
                sleep(1)
