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
from utils import Queue, CircularBuffer, UserRecordingEvents


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
        self._stream_manager = LoopStreamManager(len_beat=self._len_beat)
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
        # TODO: solve this typing mess
        first: int = recorded_track.first_frame_time  # type: ignore
        start: int = recorded_track.start_rec_time  # type: ignore
        stop: int = recorded_track.stop_rec_time  # type: ignore
        data = recorded_track.data
        length = len(data)

        half_beat = int(self._len_beat/2)

        print(f"beat, halfbeat: {self._len_beat, half_beat}")
        print(f"first: {first}")
        print(f"start: {start}")
        print(f"stop: {stop}")
        print(f"length: {length}")

        # TODO: the data were not long in beats (lb: 48109, ld: 48282)
        if start - first < half_beat:
            start = 0
        else:
            start = self._len_beat
            first += self._len_beat
        print(f"rounded start: {start}")

        if (stop - first) % self._len_beat < half_beat:
            stop = length - self._len_beat
        else:
            stop = length
        print(f"rounded stop: {stop}")

        data = data[start:stop]
        print(f"rounded data len: {len(data)}")

        if len(data):
            print(f"first again: {first}")
            self._tracks.append(PlayingTrack(
                data=data, playing_from_frame=first))
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

    def __init__(self, len_beat: int) -> None:
        """Initialize a new LoopStreamManager object.
        """
        if len_beat < 0:
            raise ValueError("len_beat must not be negative")
        self._len_beat = len_beat
        self._current_frame = 0

        self._stream_active = True

        self._recording = False
        self._stopping_recording = False
        self._event_queue = Queue()

        # audio data
        self._stream_thread: threading.Thread
        self._tracks: list[PlayingTrack] = []
        self._tracks_copy: list[PlayingTrack] = self._tracks
        self._tracks_lock: threading.Lock = threading.Lock()

        self._last_beat = CircularBuffer(
            length=self._len_beat, channels=CHANNELS, dtype=DTYPE)
        self._recorded_track = RecordedTrack()
        self._recorded_tracks_queue = Queue()

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
        self._event_queue.push(UserRecordingEvents.START)

    def stop_recording(self) -> RecordedTrack:
        # TODO: check all the documentation for correct types
        """Sets the _recording flag to False. 
        Waits until the recording stops and afterwards prepares _recording_track for new recording.

        Returns:
            npt.NDArray[DTYPE]: The recorded track.
        """
        self._event_queue.push(UserRecordingEvents.STOP)
        while True:
            try:
                recorded_track: RecordedTrack = self._recorded_tracks_queue.pop()
                break
            except IndexError:
                sleep(0.001)
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

            # These events change the state
            if not self._event_queue.empty():
                event = self._event_queue.pop()
                if event == UserRecordingEvents.START:
                    self._initialize_recording()
                elif event == UserRecordingEvents.STOP:
                    # note when the stop_recording came
                    self._recorded_track.stop_rec_time = self._current_frame

            if self._recording:
                self._recorded_track.append(data=indata)
            if self._stopping_recording and self.on_beat():
                self._finish_recording()

            # this happens every callback
            self._last_beat.write(data=indata)
            outdata[:] = slice_and_mix(indata=indata, frames=frames)
            self._current_frame += frames

        with sd.Stream(samplerate=SAMPLERATE, blocksize=BLOCKSIZE, dtype=STR_DTYPE, channels=CHANNELS, callback=callback):
            while self._stream_active:
                sleep(1)

    def on_beat(self) -> bool:
        """Determine whether beat will happen in next BLOCKSIZE frames.

        Returns:
            bool: True if beat happens, False if it does not.
        """
        position_in_beat = self._current_frame % self._len_beat
        if position_in_beat+BLOCKSIZE >= self._len_beat:
            return True
        return False

    def _initialize_recording(self) -> None:
        if self._stopping_recording:
            # override the old one
            self._prepare_new_recording()
        # initialize recording
        self._recorded_track.first_frame_time = self._current_frame-self._last_beat.position()
        self._recorded_track.start_rec_time = self._current_frame
        self._recorded_track.append(
            data=self._last_beat.start_to_index())
        self._recording = True

    def _finish_recording(self) -> None:
        # finish the recording and prepare for new one
        self._recorded_tracks_queue.push(item=self._recorded_track)
        self._prepare_new_recording()

    def _prepare_new_recording(self) -> None:
        self._recorded_track = RecordedTrack()
        self._recording = False
        self._stopping_recording = False
