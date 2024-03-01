# Project log
#fl = for later, so I can search for them
## 15.9.2023
### Portaudio #fl
I am trying to install pyaudio -> dependency portaudio. I ran 

~~~
sudo apt-get install portaudio19-dev python-all-dev
~~~

and in a __jackd__ dialog, I disabled realtime priority, since the dialog informed me enabling it could lead to a complete freeze of a system.

The above command apparently did what I spent half a day trying to do.
### Alsa not working #fl
I ran a simple script, and... well:

~~~bash
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.center_lfe
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.side
ALSA lib pcm_route.c:877:(find_matching_chmap) Found no matching channel map
ALSA lib pcm_route.c:877:(find_matching_chmap) Found no matching channel map
ALSA lib pcm_route.c:877:(find_matching_chmap) Found no matching channel map
ALSA lib pcm_route.c:877:(find_matching_chmap) Found no matching channel map
connect(2) call to /dev/shm/jack-1000/default/jack_0 failed (err=No such file or directory)
attempt to connect to server failed
connect(2) call to /dev/shm/jack-1000/default/jack_0 failed (err=No such file or directory)
attempt to connect to server failed
ALSA lib pcm_oss.c:397:(_snd_pcm_oss_open) Cannot open device /dev/dsp
ALSA lib pcm_oss.c:397:(_snd_pcm_oss_open) Cannot open device /dev/dsp
ALSA lib confmisc.c:160:(snd_config_get_card) Invalid field card
ALSA lib pcm_usb_stream.c:482:(_snd_pcm_usb_stream_open) Invalid card 'card'
ALSA lib confmisc.c:160:(snd_config_get_card) Invalid field card
ALSA lib pcm_usb_stream.c:482:(_snd_pcm_usb_stream_open) Invalid card 'card'
connect(2) call to /dev/shm/jack-1000/default/jack_0 failed (err=No such file or directory)
attempt to connect to server failed
~~~

I'm gonna go to bed now.

__EDIT 16.9.: I read on stack overflow that there is no need to solve this. So at least now, there is really no need to do so.__

## 16.9.
Firstly, some knowledge I gained: when deciding about sampling frequency and bit depth, I'd decide for the basics: 44.1 kHz, 16 bit depth. I am still not sure in what format I would like to store my loops.

I am gonna try using sounddevice library now, since manipulating the audio in bytes scares me a byte (kms)... and sounddevice stores the audio in np arrays.

One eternity later: I found this on reddit: 
> PyAudio is simply a wrapper for portaudio, sounddevice is a wrapper that tries to make portaudio pythonic.

and it quite sums up my feelings. I am gonna try to use sounddevice.

### Iupyter issue
I got really stuck on iupyter kernel not working properly...
~~~ bash
LibsndfileError: Error opening 'lib/samples/CantinaBand3.wav': System error. 
~~~
for now just fuck it, I'm gonna do it without iupiee playground.

__Edit: the path was the problem. All the fucking time. Oh boy, I have got to learn to check those easy things first...__ 

### Recording volume issue
it seems like I have some recording params set wrong, because the sound is very distorted - I need to somehow change the recording volume.

\> Ok, the recording volume is a big problem all around my laptop - this project, audacity and even whatsapp online just do not work properly.

\> I just lowered the recording volume in pulseaudio, the problem is fixed. It is possible Iturned it up when playing with pulse audio yesterday XD.

### Lets synthesize a metronome!
I figured out how does storing of the data in np works, so I am going to try to synthesize a metronome.
It works like this:
~~~python
        # two channels (stereo)
        # v   v
array([[-44, -20],  # values of one sample
       [-64, -59],
       [ -3,  17],
       [ 36, -26],
       [  4,   8],
       [ 45, -47],
       [ 31, -39],
       [ 46, -81],
       [ 39, -20],
       [ 99, -78]], dtype=int16)
~~~

\> The metronome is (almost) done! The problem is, there is a small chirp between each iteration = between each audio play. This coud probably be solved, but to do it, we shall undergo a dangerous way: _Deeper! The Stream awaits us..._

## 17.9.
I now feel confident enough to name some of the first challenges:

- resolve mixing of signals with preventing sampling format overflow (probably should be an arithmetic mean of the values, but that distorts the signal at rounding...)
    - -> it seems like using floating point could offer enough precision to avoid this.
    - __YES IT WORKS BEAUTIFULLY <3__

- think through the main principle - maybe it will need parallelism? Or will just a clever callback func be enough?
- make BPM mechanics. This should probably work on rounding the number of samples of a recording to some fixed numbers?
### Input underflow #fl
A strange behaviour occured when I plugged my guitar headphone amp into my microphone socket and then switched from VS Code, where the program was running, to youtube. Suddenly, CLI was full of ```input underflow```, and a strange clipping noise appeared. My settings were ```--blocksize 1```.

## 14.11.
### Blocksize discoveries
After reading some documentation of sounddevice at https://python-sounddevice.readthedocs.io/en/0.4.6/api/misc.html, I have realized what might have been going on in the prev issue:

>In a stream opened with a non-zero blocksize, it indicates that one or more zero samples have been inserted into the input buffer to compensate for an input underflow.

My hypothesis is that switching to youtube cuts off the input from my mic socket. Another option is that it replaces the input with the youtube audio, which could have different sampling frequency. Therefore, causing lack of input samples.

#### Application in callback
Additionally, setting blocksize might solve the question of varying input/output data size, which is applicable in the callback.

### Assigning data in a callback
SD docs:
>In Python, assigning to an identifier merely re-binds the identifier to another object, so this will not work as expected:
>```python
>outdata = my_data  # Don't do this!
>```
>To actually assign data to the buffer itself, you can use indexing, e.g.:
>```python
>outdata[:] = my_data
>```
>… which fills the whole buffer, or:
>```python
>outdata[:, 1] = my_channel_data
>```
>… which only fills one channel.

## 15.11.
Now the real shit begins! My first attempt for a low-level interaction is as follows:

### Endless sine player
**Goal**: Play the pre-generated sine signal until keyboard interrupt

- sampling frequency: 44100
- bit depth: 16bit -> using int16 -> the amplitude range is -32768 to 32767
- I am going to generate a full one second of 100Hz tone, so it is gonna be 100 periods

Okay, 90 min later: I have got the sine generator, but I did not manage to write the callback. I think the only thing left is indexing for playing once and a modulo for playing endlessly.

## 19.11.
I have finished the endless sine player. A few discoveries worth noting follow:
- The modulo mechanism worked for those samples (arrays), whose lenght is divisible by the blocksize; I could write the general mechanism, but I will wait with that until I have thought through the BPM mechanism.
- Sometimes, an underrun occured. This was observable through a clipping noise and a high CPU usage. 
    - In contrast with the documentation, the underrun itself was not preceded by high CPU usage. (*"Indicates that output data (or a gap) was inserted, possibly because the stream callback is using too much CPU time."*)
    - #TODO - error handling: when over/underrun occurs, it is necessary to just fill the data with zeros or cut some samples, so the flow can recover. One click is ok, endless clipping sound is not...

### Consultation
My tasks for the consultation are as follows:

**Oct**
- propose a solution
- description in README.md
- research of resources

**Nov**
- record and play one track

## 20.11.
Getting ready for consultation
### Propose a solution
In this part I want to create an architecture plan.
Here is what I have got by myself:

**GUI** <-> **State** + **Modules** <-> **OS, Hardware**

#### GUI
Functions:
- shows user the state
- enables the user to control the state

Vision:
- minimalistic and intuitive
- dark-mode
- not the thing I want to spend doing majority of time

Library: 
- Kivy

#### State
Functions:
- the core of the program, contains all the abstraction
- stores the tracks
- plays, pauses and mixes them


Vision:
- just a few core classes, but it is not going to be this easy

Libraries:
- NumPy
- sounddevice

#### Modules
Functions:
- exporting audio
- manipulating audio (np arrays)

Vision:
- one module = one area of competence

Libraries:
- sys
- NumPy

---
Seeing this, I have realized I will need much more detailed plan. Thus, it is necessary to sum up all the functions I want my program to have and prioritize them somehow, so it is possible to programm just the *minimum viable product (MVP)*. **Modularity** is necessary as I will add more features if there is time left.

#### Sum of the functions:
*Compulsory:*
1. set BPM
    1. x[BPM] = a fixed amount of time; given a sampling frequency, a fixed amount of time = a fixed number of samples, *therefore* => set BPM = determine the lenghts which can the recordings exist in
        - problem with unprecise bpm, if the sampling frequency is not a multiple of the BPM
2. record a track
    1. cut recording after pre-set bpms **or** round the recording to nearest bpms
    2. store tracks
3. delete a track
4. merge two tracks
5. play multiple tracks in a loop
    1. play one track in a loop
    2. store one mixed track **or** mix it live **or** play it through output channels of one stream
        1. mix live
            - computationally demanding, but simple math could be possible
            - otherwise solves all the problems
        2. store mixed track
            - re-mix after any change of volume etc.
        3. channels
            - limited number of channels
            - not a clean solution lol, channels are not supposed to be used for this

*Voluntary:*
1. Windows & MacOS
2. pause and unpause tracks
3. export of a song (live)
    - start a recording of the output, stop it, save it

*Bonus:* \
= my added ones, which would contribute greatly to the UX
1. metronome
2. volume knob for individual tracks
3. grouping the tracks for muting at once
4. 


Show of the use of an actual looper: \
https://youtu.be/3vBwRfQbXkg?si=Er9PKJ66MBy93lCl

## 26.11.
### Kivy
Today, I have tackled kivy. As I progressed furtheer in its "Pong" tutorial, my antipaties grew greater... however, it is not that i haven't discovered a lot of new possibilities concerning GUI frameworks. I have rather realized that kivy might be an overkill for the job I want it to do.

**Conclusion:**\
If it is possible, I want my GUI library to be *very simple*. Rather than using complicated optimalization strategies built into a huge library, I want to use asynchronous programming or threading for the optimalization.

Ideas: pygame, tkinter...

## 27.11.
### Questions, plans
- is pygame the right one?
- write a Readme.md
- plan detailed architecture

### Pygame
It seems it is the right one!

### Plan the architecture
Planning in progress, but on a paper. Currently the question is between async and threading, as I need the audio loop to be really fast, so the sound is smooth, however, this is not the case with the GUI loop. To reduce CPU usage, I might use threading: one thread for sound, another one for GUI.

## 28.11.
I was battling with poetry and github and IT TOOK FUCKING FOREVER AAARGH

but finally, it is done I hope.

### Metronome
I sort of solved the core of the bpm mechanics: the metronome. I downloaded a free sample, cut the silence and came up with a formula for number of samples per beat, given sampling frequency and bpm. With this formula, I can add the accurate amount of zeros to the sample. Playing it in a loop then results in a metronome track.

However, there is small inaccuracy. But since the inacuracy is in terms of one sample (if 44100 fps: 0,000022676 second inaccuracy per beat), I am going to ignore it.

## 29.11.
Experiment: simulate user input/GUI work with sleep(20ms) -> will the music go on smoothly?

### wire_metronome
Mixing is 'aight, but sth is wierd with the BPM. Set to 120 works like wonder, set it to 130 and you get
```
sum = metronome[current_frame%len(metronome):current_frame%len(metronome)+BLOCKSIZE] + indata

ValueError: operands could not be broadcast together with shapes (3,2) (10,2)
```
Thirty seconds later: Apparently, it is len(metronome)%BLOCKSIZE. I thought this was okay because of the modulo mechanisms I created, but now I remember it only worked for multiples of blocksize. I am gonna try to set it to one, but that will most probably just trigger output underflow.

Yes, it did. Therefore, it is time to come up with another formula for looping in tracks!

### Looping formula
One solution would certainly be to yield len(indata) from sample. The other one is indexing magic, which is what I am trying to accomplish now. And a peculiar thing!

Given arr of len 10,
```python
print(arr[12])
```
throws index error. But
```python
print(arr[12:15])
```
returns just an empty list. Quite incoherent, isn't it?

And that is not numpy, that is python!

Okay, the easiest solution:
```python
frame=0
for i in range(n):
    start=frame%len(arr)
    end=(frame+BLOCKSIZE)%len(arr)
    print(start, end)
    if end<start:
        print(np.concatenate((arr[start:], arr[:end])))
    else:
        print(arr[start:end])
    frame += BLOCKSIZE
```

If I end up using this for every track, there could be optimizations... a few perhaps in the way it is written (not duplicating len(arr) could reduce time IF creating new variable is not slower that accessing arr and computing its len). Another approach would be to pre-compute those and stack them in a queue. This would bring the problem of cancelling future events of deleted tracks.

### Mixing tracks
The problem of overflow or distortion when mixing int16 is imminent, thus I shall address it now.

Overflow (when adding the tracks) is a no-go, so distortion (when dividing) is the way of jedi. First of all, **test whether it is significant**.

Options if the distortion is significant:
1. convert -> mix -> convert
2. use different format?

### Callback
When studying callback function, I came to realize that I could use the param "frames" instead of the constant BLOCKSIZE. I have switched for now, but I do not know whether one of them is faster.

### 04_record_loops
It is ten PM, I am gonna stretch and go to sleep. The biggest experiment so far is almost done, with breakpoints setted where I see potential bug or as todos. Good night, lets continue tomorrow!

## 30.11.
### debugging 04_record_loops
After first few buggs an actual error: output underflow, sadly. \
\> enlarge BLOCKSIZE \
\> that helped

\> we have a lot of trouble concerning shapes and dtypes, definitely will use numpy in the clean version!
- the trouble happens when the callback 
\> it is necessary to come up with another way of keeping the stream alive, input() gets mixed with input_checker

After one extensive round of debugging, I have moved to these problems:
- metronome sound is extremely distorted (somewhere there is a conversion fault)
- even after setting blocksize to 1000, I occasionally face output underflow.

-> BLOCKSIZE = 10000 # for research purposes
-> the mixing was wrong, as dividing by num_tracks forgets to count in the indata
- apparently that was not the problem
- the indata is ridiculously small, so when converting to int16, they become zeros.
```python
indata: 
[[-0.00106812 -0.00106812]
 [-0.00106812 -0.00112915]
 [-0.00115967 -0.00112915]
 ...
 [-0.00048828 -0.00054932]
 [-0.0005188  -0.00054932]
 [-0.00057983 -0.00054932]]
```

In wire_metronome, the numbers are higher:
```python
indata: 
[[173 174]
 [173 175]
 [162 163]
 ...
 [-82 -82]
 [-68 -67]
 [-44 -44]]
metroslice 
[[  0.     0.  ]
 [  0.     0.  ]
 [  0.     0.  ]
 ...
 [ 61.75 -11.25]
 [ 52.5  -12.75]
 [ 33.5  -19.75]]
mixed 
[[ 86.5    87.   ]
 [ 86.5    87.5  ]
 [ 81.     81.5  ]
 ...
 [-10.125 -46.625]
 [ -7.75  -39.875]
 [ -5.25  -31.875]]
```

the next step is to look more into these values and the conversions/typing. After that will be solved, it is time to experiment with blocksize and optimalizations without classes. If sufficient optimalization can be reached, try with classes. Then again, with GUI.

## 2.12.
### loudness
Today! I will answer the fundamental question! How loud is too loud?!?

Set up playground with the same code I have in wire_metronome and record_loops, try multiplying and see, where is the problem.

Logically, it is the boundaries of int16, -32768 to 32767.

Obviously, now it is necessary to compare those two codes and print the max values after every manipulation with the sample.

### endless_sine
One question was chasing me for two days now: how is it that the higher the generated frequency, the higher (louder) is the sample. What was I looking on was print(metronome), which prints just the **beginning** and ending of the sample. And OBVIOUSLY, the higer the frequency, the faster the numbers get high in the beginning.

### Conversions
Loudness in wire metronome:
- metronome: 19001
- indata: around 4000 was the highest

Loudness in recored loops:
- metronome is the same
- indata strangely small (0.03)
    - after experimenting with indata, they would never go above 0.9999...

#### Conclusion
**Metronome**: it is not the "loudness", but the distortion, which can be introduced in two places:
- metronome_generator
- mixer of the callback

Since the former is easier to test, I will begin with it.

**Indata**: indata are probably given as float. \
Goal: determine why.

## 4.12.
In just half an hour I have got my endodoncy surgery, but it is time to code!

### Indata
Dtype of indata is actually float32

## 5.12.
### Indata
Found this in my code...:
```python
try:
        with sd.Stream(samplerate=SAMPLERATE, blocksize=BLOCKSIZE, dtype="float32",
                       channels=2, callback=callback):
```
...quite self-explanatory.
Fixed for now.

### Distortion
#### In metronome generator
I do not have access to sound rn xd... One source of distortion I can think of is rounding the integers after division and then multiplying again. I am going to plot the metronome sample after every operation so I can observe the changes.

That was fun. However, I could have deduced from
1) both ```wire_metronome.py``` and ```record_loops.py``` contain metronome generator
2) only ```record_loops.py``` contains mixer
3) ```wire_metronome.py``` is not distorted
4) ```record_loops.py``` is distorted

that metronome_generator is not the faulty part of a program.

I was not sure, as I slightly changed metronome_generator with the type annotations - but even considering solely the code, in metronome_generator there is no code which could distort the audio significantly.

#### In mixer
I found a few bugs, but before even fixing them, the audio is not distorted anymore! The thing was I was playing int16 metronome into float32 output!

### More bugs (one more bug)
After finishing recording of a track, myteriously the track changes shape from (BLOCKSIZE, CHANNELS) to (BLOCKSIZE,). That means that the track array has len BLOCKSIZE in one dimension, but has no other dimension, like the following one: 
```python
[0, 1, 2, ..., BLOCKSIZE]
```

instead, it should look like this:
```python
[[0, 1, 2, ..., BLOCKSIZE],
 [0, 1, 2, ..., BLOCKSIZE]]
```

There are two places I am getting error on:
1. ```data += trackslice``` in callback
    - ValueError: operands could not be broadcast together with shapes (10000,2) (10000,) (10000,2)
2. ```recorded_track = np.concatenate([recorded_track, zeros])``` in post_production
    - recorded track has shape (10000,), whereas zeros have shape (10000, 2)

Couldn't it be dependant on BPM? Lets try:

**BPM -> error number (1 or 2 as mentioned above)**\
120 -> 2\
127 -> 2\
130 -> 2\
140 -> 1\
135 -> 1\
132 -> 2\
133 -> 1 => BPM>133: Err 1\
60 -> 1\
90 -> 1\
105 -> 2\
100 -> 2\
95 -> 2\
93 -> 1\
94 -> 2 => BPM<94: Err 1

If BPM is between 94-133, it passes through callback and gets caught in post_production.

Why? I do not have a single idea. But that is probably not necessary for solving the problem, so I will be focusing on that for now.

**Oh, the previous research is not true! I just got the first error with 120 BPM!**

Perhaps it is more about the timing of ending the recording.

#### The actual bug
This is interesting:

shape of recorded track before anything was added: ```(0, 2)```\
shape of indata, which we add: ```(10000, 2)```\
shape of recorded track after first appending: ```(20000,)```

lets closely examine the part of code!

Okay, isolated it in a playground, that is the problem!!
> Ladies and gentleman, we've got him!

#### Recap
It seems like I haven't understood and tested numpy.append properly, which caused a bug in the development.

Ah, yes, definitely:
>axis : int, optional\
>    The axis along which values are appended. If axis is not given, both arr and values are flattened before use.

## 6.12.
### Shape bug solution
Turns out I can do this thing in two ways:
1. ```recorded_track = np.append(arr=recorded_track, values=indata, axis=0)```
    - this requires the one extra argument ```axis```
    - furthermore, it calls the second solution inside
2. ```recorded_track = np.concatenate([recorded_track, indata])```

### Further action
My code is now *oficially* debugged, but it is not robust - I can break the program in a few ways, e.g. recording too short loop results in division by zero in modulo. The question is, will I make it more robust now, or shall I do it with the transition to classes?

### Issues
1. add error handling for:
    - under/overrun
    - recorded track len 0
2. Two options\
    a) try to optimalize the code so it is able to run smoothly without the GUI\
    b) create the GUI so the "first version" is complete

#update: it is most certainly the optimalisation!
The coolest way to do it would be to time all the pieces of code now and then see the results on my way.

Some current values:
BLOCKSIZE = 10000, BPM = 70 => max loops before underrun = 3\
BLOCKSIZE = 5000, BPM = 70 => max loops before underrun = 4\
BLOCKSIZE = 1000, BPM = 70 => program crashed after while (just metronome)

```
ALSA lib pcm.c:8568:(snd_pcm_recover) underrun occurred
Expression 'err' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 3355
Expression 'ContinuePoll( self, StreamDirection_In, &pollTimeout, &pollCapture )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 3907
Expression 'PaAlsaStream_WaitForFrames( stream, &framesAvail, &xrun )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 4285
```

## 7.12.
### Timing the code for optimalisation using ```timeit``` module.
The file ```timing_record_loops.ipynb``` contains the according documentation.

## 8.12.
Continuing optimalisation.

## 10.12.
I am gonna start to work on the GUI now, as Kryl thinks it is wiser.

#fl
### sleeping pygame
> pygame.time.wait()
>
>    pause the program for an amount of time
>    wait(milliseconds) -> time
>
>    Will pause for a given number of milliseconds. This function sleeps the process to share the processor with other programs. A program that waits for even a few milliseconds will consume very little processor time. It is slightly less accurate than the pygame.time.delay() function.
>
>    This returns the actual number of milliseconds used.

## 13.12.
Figured out that pygame does not have a GUI support, so I would have to program all the GUI by myself... which sounds exciting, but not as exciting as optimalization. I would definitely take my OOP skills to tthe next level, but it would also consume a lot of time.

There is a great alternative, a package called ```pygame_gui```. It seems to be the right one for this job, is recently created and moreover seems well-documented. 

## 14.12.
Switched to tkinter

## 15.12.
I am trying to work my way through creating the interface in tkinter. Plan:
- think it through on a paper (gui x state)
- experiment with the themes that come with the ```ttk``` package

## 11.1
Today I have done a vast amount of work on the GUI. I have not commented nearly anything, so it is going to be real fun, unless I do it tomorrow or saturday.
Things that are still wrong on the end of the day:
- track trash icon is not loading
- track delete button is not clickable
- tracks do not fill the whole available space vertically 
- canvas starts small y-wise

## 12.1.
- canvas starts small y-wise
- track shlould have a border

## 16.1.
- ~~canvas starts small y-wise~~
- tracks should fill the canvas horizontally
- ~~add bpm entry validation~~
    - ~~should be a whole number between 1 and 400~~
(- add metronome button (+ metronome flag in the callback))
- write comments for all the code
- write the logic
    - solve the threading challenges
    - implement deletion of tracks
- encapsulate those properties that should be

### First test run
Thread with endless loop works, but does not stop after closing tkinter
- -> add terminate function to Lem, which will end the thread (maybe just set ```stream_active=false```?)

### test run 2
with the proper main func, I immediatelly got this err:
```
    data += track_slice
ValueError: operands could not be broadcast together with shapes (100000,2) (11800,2) (100000,2)
```

## 17.1.
the err above is strange... oh, idea! It could be that the metronome sample is shorter than the blocksize. I did not program this case, as I did not suppose such big blocksize is realistic.. :/
-> It is so!

Now it works, but:
1) I cannot delete tracks
2) it is very unsafe (rn alsa: underrun occured error happened, and the whole stream terminated mid-sesh)

### ??? I store tracks as list[NDarray]
-> that is perhaps why it is so slow

Okay, now i can delete tracks.

- tracks should fill the canvas horizontally
(- add metronome button (+ metronome flag in the callback))
- write comments for all the code
- write the logic
    - add error handling
    - ~~solve the threading challenges~~
    - ~~implement deletion of tracks~~
- encapsulate those properties that should be

## 18.1.
K, general TODO after the consultation:
1) comment all the code using sphinx format
2) encapsulate everything that should be
3) extract the main function from Lem into a separate class
4) ensure error safety with alsa
5) bind the tk buttons to keyboard input
6) do some testing on other computers, so it will not break when my opponent tries to run it.
7) get the sources Kryl gave me and find some useful information in them
8) generate dev documentation
9) make user documentation with screenshots etc

then, if I want to experiment:
- add features
    - wrong bpm input indication (red the text)
    - add metronome switch button
    - add volume control for metronome/tracks
    - add pause project option
- try to improve the performance
    - try some timing using ```timeit```
    - explore the possibility of rewriting the code in ```codon```

Errs list:
- prevent modulo by zero error in callback by asserting no track length is 0

Questions:
- should I decouple the classes using callback pattern?

### Decoupling the classes using callbacks
After some discussion with Github Copilot and Zbyněk, I have decided to:
1) Create ```start_recording``` and ```stop_recording``` functions in ```Lem```. This enables me to use less references to ```Lem``` from the other classes (e.g.: I can call ```post_production``` in the ```stop_recording``` function instead of in ```RecordButton```).
2) Pass those functions as callbacks to the ```RecordButton``` widget.

Additionally, I have two cases in which I am not sure what would the cleanest solution look like:
1) ```BpmPopup``` needs to modify data in ```LemApp``` and in ```Lem```.
2) ```Track```'s delete button needs to modify data in ```Tracklist``` and in ```Lem```.

Should the ```BpmPopup``` call the according method in ```LemApp```, which would call the according method in ```Lem```? Or should it get both the methods as callbacks?

## 31.1.
Finished splitting the logic into two classes, loop stream manager and looper emulator. Time to check up how I am doing:

K, general TODO after the consultation:
1) ~~comment all the code using sphinx format~~
2) ~~encapsulate everything that should be~~
3) ~~extract the main function from Lem into a separate class~~
4) ensure error safety with alsa
5) bind the tk buttons to keyboard input
6) do some testing on other computers, so it will not break when my opponent tries to run it.
7) get the sources Kryl gave me and find some useful information in them
8) generate dev documentation
9) make user documentation with screenshots etc

then, if I want to experiment:
- add features
    - wrong bpm input indication (red the text)
    - add metronome switch button
    - add volume control for metronome/tracks
    - add pause project option
- try to improve the performance
    - ~~try some timing using ```timeit```~~
    - explore the possibility of rewriting the code in ```codon```

Errs list:
- ~~prevent modulo by zero error in callback by asserting no track length is 0~~

Questions:
- ~~should I decouple the classes using callback pattern?~~
- remaining questions are marked together with todos by `# TODO:`

### Next plans
Okay, not bad. Time to update the tasks on the todo.

1) complete the callback in stream manager using numpy methods
2) test the functionality after the update
3) ensure error safety with alsa
4) bind the tk buttons to keyboard input
5) complete the remaining todos
6) do some testing on other computers, so it will not break when my opponent tries to run it.
7) get the sources Kryl gave me and find some useful information in them

**After the code is completed:**
1) generate dev documentation
2) make user documentation with screenshots etc
3) write the thesis

If I want to experiment:
- add features
    - wrong bpm input indication (red the text)
    - add metronome switch button
    - add volume control for metronome/tracks
    - add pause project option
- try to improve the performance
    - try some timing using ```timeit```
        - time thoroughly the whole callback/main
    - try rewriting the code with the use of multiprocessing
    - explore the possibility of rewriting the code in ```codon```

### Bitter reality
I have figured out I cannot speed up the code as I thought, because the tracks have different length, so the have to be in a list.

Also, the results of the first tests:
- deleting tracks and terminating the app does not work, as somehow the lock is not given back
- the metronome is very loud in comparison to the indata
- I have ommited the indata from mixing

2nd test:
- metronome is still too loud
- the lock works now wtf

And everything fails on **EIGHT** tracks, not three like before!! seems like numpy is doing its thing.

> Done for today, yay!


## 1.2.
Trying to get into the error handling, but it seems there is no way I can just ignore the alsa error :C. The easy solution is now to set the blocksize, sampling frequency and datatypes etc. so that the system is robust enough. Maybe also a cap on the number of tracks would be great.


## 3.2.
So, I have found some more bugs: 
- When I delete tracks too fast, apparently it breaks the indexing of `_tracks` somehow lol. Afterwards, any attempt to delete a track fails.
    - -> Some form of lock or a queue would probably improve this situation.
- When the track is too short, it is not added in the logic, but it is added in the GUI
    - -> add tracks from the gui? Adds tight coupling, but there ought to be a way to do it. 

As for the previously discussed error, it would really be best if my program could detect the error and at least restart the stream without loosing all the data...

And after a bit of scientific method (fa & fo):
> If an exception is raised in the callback, it will not be called again.
> - under **callback** at https://python-sounddevice.readthedocs.io/en/0.4.6/api/streams.html#streams-using-numpy-arrays

## 5.2.
Today's plan: Catch **ALSA Err** if you can. If you can't, just note how it works, so you can:
1) find an easy workaround (probably not reading stdout, as that would be time consuming, but idk), or...
2) argument why it is not possible

Afterwards, I can solve the bugs above.

### ALSA Err:
```
(.venv) vojtech@flash-gordon:~/programování/lem/lem-dev$ /home/vojtech/programování/lem/lem-dev/.venv/bin/python /home/vojtech/programování/lem/lem-dev/lib/main.py
ALSA lib pcm.c:8568:(snd_pcm_recover) underrun occurred
Expression 'err' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 3355
Expression 'ContinuePoll( self, StreamDirection_In, &pollTimeout, &pollCapture )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 3907
Expression 'PaAlsaStream_WaitForFrames( stream, &framesAvail, &xrun )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 4285
```

As shown above, those errors are propagated to stderr in such a way I cannot catch them.
Some solutions I came across:
- redirect stderr:
    ```py
    import sys

    class StderrRedirect:
        def write(self, s):
            # Handle the error message here
            pass

        def flush(self):
            pass

    sys.stderr = StderrRedirect()
    ```
- perform various optimizations...
    - I could deploy a worker process to pre-mix the tracks - a lot of work, uncertain...

But, a good point based on github copilot snippet:
**A callback should not be the place, where the heavy processing is done.** To ensure the smoothness of audio playback, the callback shloud only get the data and pass the right amount of it as outdata. Some of the processing can be done beforehand, maybe in a separate process.

#### A design started to crystalize in my mind...
The `callback`: 
- gets [frames] of data from queue, joins it with indata, passes it as outdata
- handles empty queue -> write zeros or sth... or just wire...

The `worker`:
- could be a separate process, so it actually leverages CPU power
- pre-mixes the tracks so that the `callback` only adds the indata
- holds constant length of the premixed queue, sleeps when necessary

## 6.2.
Plan for today: debug and brush up a version I can hand in as a final product. 

Testing the implementation of the above mentioned architecture will be relevant later, as I do not want to be dependant on that (would create immense amount of stress lol).

So, a **TODO** one more time:
- When I delete tracks too fast, apparently it **breaks the indexing of `_tracks`** somehow lol. Afterwards, any attempt to delete a track fails.
    - -> will this persist if I fix the following bug?
- When the **track is too short**, it is not added in the logic, but it **is added in the GUI**
    - -> add tracks from the gui? Adds tight coupling, but there ought to be a way to do it. 
- **stderr redirect**


And just to see what I have already done:
1) ~~complete the callback in stream manager using numpy methods~~
2) ~~test the functionality after the update~~
3) ensure error safety with alsa
4) ~~bind the tk buttons to keyboard input~~
5) complete the remaining todos
6) do some testing on other computers, so it will not break when my opponent tries to run it.
7) get the sources Kryl gave me and find some useful information in them

Nice!

One more task: check whether I have mistaken the words `method` and `function` somewhere!

Track deletion fixed, now stderr!
1) How is it written?
    - apparently it is written in C and propagates to stdout/stderr -> it can be redirected to logger/handling
    - How I imagine it: I make a StderrRedirect class, which upon call will check whether the err is this alsa err. If yes, it will restart the stream and maybe show sth in the GUI.

Perhaps, if the stream is ended by this error, I can just handle this in try-finally block! Check stream_active, and if it is supposed to be active and is not, call start_stream and finish! Maybe such a šaškování complicated thing as redirecting stdout is not necessary at all!

**What The FUCK???**

I have just replaced `while stream_active: pass with while stream_active: print(stream.active)`, and suddenly I can record 30 tracks without crashing? apparently the while True: pass loop is very CPU consuming..?

ChatGPT says that it was a very tight loop... should I replace it with sleeping? And what does `sounddevice` documentation say about this?

# This changes EVERYTHIOAYUNG
By experimentally replacing the tight while loop with `input()`, I was able to reduce blocksize 1000 times. And still record two loops without any problems. When recording the third one, output underflow appeared, and the sound got clippy. But after stopping the recording (stopping allocating new memory? would preparing long zeros track and just changing the values work?) the stream continued just normally... Oh god. I need a moment to take this.

## New plans
Use `sleep()` or other way to block the execution. 
- `stream.wait`?

#### What are my priorities for the app?
1) is theoretically safely written - every scenario is handled
2) functions smoothly for recording ~4 tracks

And voluntarily:

3) is written in an elegant/clever way
4) What also changed now is that all those small features as "turn off the metronome" etc. grew a lot in the level of importance...

So... the plan now is probably to just play with all the TODOs so that the first two criteria are met. Handle all the errs and try to optimalize.

The small errs are just routine. However, the other group of errs is much more difficult to think through and find workarounds. The following I would classify as the other group:
- output underflow
- stream exceptions

Setting the blocksize to 0 kinda works very well! I have to try that with my keyboard so that I know how good it really is for music making. I also want to try whether the stream is smoother using `blocksize = 2^n`.

1) is theoretically safely written - every scenario is handled
    - TODOs
    - err handling
    - testing on other computers
2) functions smoothly for recording ~4 tracks
    - align not only the length, but also the start & the end of the recording to the BPM (sometimes when I finish a recording of a track, it's end plays again for a little while, I am not sure why)

## 7.2.
I was keen on starting optimalisation, however, I have realized that first it is good to write all the error handling.

Question (after a lot of work was already done, upsiee): is the way I handle errors unnecessary complicated? Could those errors be handled in \_\_main__? And even if yes, would it still work when multithreading/processing?

How should even propper error handling look like? should every function have try except blocks and handle its own errors? For example in metro_gen: should I first check if bpm>0 and raise an error if necessary, or is it ok to just let the error happen? This is some high quality dev shit for tomorrow!

## 8.2.
I am learning about exception patterns, gotta make ipynb just for that... and afterwards, I'll probably delete "exception callbacks" I wrote yesterday, and let those Errs propagate to main, which will handle them.

Now I found out I do not use *Sphinx* docstrings but the *Google* ones. I have decided to keep it like this, because they are more readable in the code.

But for the exceptions: right now, I really do not know how to handle them properly, so I would like to discuss this with Kryl. What can I do now is identify all the places where some exception can occur. Would a solution be to raise my exceptions with meaningful messages in all these places, and in LemApp just pass the message to the GUI? That would be good for the user, but would that be good dev-wise?

However, consultation is not today and I want to finish up, so lets try to work through thiss mess to the right solution. Few principles are already clear:
1) Handle the exception at the level that knows how to handle them.
2) If, at the low-level, you do not intend to log the exception nor do anything else about it, it is fine to omit the try-except block. 
3) However, if the function is likely to raise a specific exception, it should be documented for the caller can handle it based on the provided information.

My added one:
4) this could lead to the need of specifying that in every level of some nested function, so I have decided to just do it at the lowest level. Perhaps Kryl will enlighten me in the matter of exception handling.

### This is strange
Suddenly I am able to record 60 tracks and everything functions normally. Not a single output overflow printed... I will just assume that the program miraculously fixed itself, and focus on the real problem: 

**starting recording on beat**. I suppose the easiest solution would be to implement some sort of clock, and synchronize the metronome sample to it.

After examining the metronome sample in audacity, it seems that the main click is happening in the first 20 ms, so just create a clock on time would probably work and nobody would notice... now I realized that the easiest solution is probably again modulo frames or so... this would start recording on **the next** beat, but would not work to include the bit of sound before the start of recording, if it came slightly later than it should...

## 10.2.
### Starting on a beat
Adding the feature above. If the `post_production` gets the track including the whole beats in which the `start` and the `end` happened, and the indexes ("framestamps") on which they happened, it is very easy to determine which beats should be included in the track and which should not (round the track).

So the `StreamManager` needs to include the starting and the ending beat. 

#### Ending beat
For the ending beat, this should be fairly easy (`stop_recording()` sets flag `stopping recording` to True. Callback calculates where "the beat" is \[there should always be one callback call "on beat"] and if `stopping recording` is True and it is "on beat" callback, `_recording` is set to False).

#### Starting beat
For the starting beat this means to have some sort of buffer containing the past input from the last beat until now. This could be circular buffer, being rewrited every beat ("on beat" is on idx zero). When `start_recording()` happens, \[0:now] (that is \[last_beat:now]) of this buffer is taken as a base for `recorded_track`. 

How to determine "now"? `current_frame % len_beat` should work.

## 13.2.
Currently I am deciding whether it is okay to round the length of a recorded track to whole callback lengths instead of whole frames. It is certain that rounding to whole frames is precise enough, but would callback length sound weird? 

One callback length is 100 frames. Sampling frequency 44100 fps means 2646000 frames per minute. If we set the maximum available BPM (400), there will be 6615 frames per beat. 100/6615 = 0.015..., so the error is 1.5 % BPM. That is low enough for me to try to dismiss it.

I am starting to think that I should take a radically different approach to my callback, perhaps implementing queue would nice things up.

### Testing
When I was testing, a really weird thing happened: when I connect the plug for headphones and mic as "headphones with microphone", the metronomes sound gets reverbed or something like this. The same thing happened on the school PCs. However, I am convinced it did not happen when I was testing the last time.

Apparently, it has to do something with the weird ALSA behaviour... I hope I still have the paper with the table somewhere... I do not, whoops...

So, this weird bug happens also in Audacity and with Alsa... achjoooo. This seems to be a problem connected to either PulseAudio or ALSA. Other programs mentioned when searching for the solution were pavucontrol and jack.

But, after a while, I was able to get my computer to recognize the mic input. Further testing revealed that only the last beat is actually played in a loop afterwards.

I have figured out why, fixed it and got another err:
`TypeError: only integer scalar arrays can be converted to a scalar index`

## 14.2.
Idk what happened, I do not get the err today. K. Anyways, the recording seems to end late or repeat the last two beats... idk man. Lets make it theoretically correct and then test.

Well. Now I see the consequences of tired coding. Nothing actually works the way it should, and all the system is just one big mess. Time to think it through _again_.

## 17.2.
Last days I am really confronted with the situation when I do not have control/good overview of my code and what I am doing. The universe revealed to me that if I was writing code modularly, like lego bricks, then this would not happen: I could only change one brick/one brick structure at a time. Another thing is keeping the bricks small and simple enough, so that each time something needs rebuilding, I can keep a good idea of what I am doing. This requires a lot of levels of abstraction, similarly to a pyramid.

However, this approach requires to build all the basic bricks cleanly, so the higher levels do not collapse. The more general is the low-level brick supposed to be, the more error resistant/precisely defined it has to be.

Moreover, when one follows this brick approach, it is meaningful to write tests for every brick.

---
Made some structural changes: track classes are now in a separate files, which caused the need to move constants to a separate file. I will also move the `Queue` to some sort of `utils` or so.

## 18.2.
Make `time`, which would count frames and beats??? This could make everything really pretty.
I fight some nasty things rn: for every class used in audio it would make sense to know how long one beat is. But to do that, I would have to pass it everywhere, which is repetitive and I do not like it. Instead, I would like to initialize a `MusicalTime` ?object? when I get the BPM. Afterwards, this object could provide:
- methods to add, substract and get the time and its parts, (`time to next beat` method?)
- a timer object, which would implement just those same methods,

I need to initialize the class/module/something, so that every time object afterwards has the same property: len_beat, which it gets from the initializer...

### Late initialization in python
have been reading etc., will probably use `Optional[Type]` for initialization of BPM. This way, **the whole state** will be initialized with <ins>fixed bpm</ins>. Which will save me from a lot of headache in the development.

So now I will try to let the GUI and most of `main` exist, and just rebuild `lem` so that late initialization happens only at the top-most level.

## 19.2.
Funny. I just realized that because it was necessary to implement three more flags, I wanted to create a new data structure for them. Then I saw other opportunities, which seemed connected to the first one, so I made two more classes. But they seemed illogical to me, so I rebuilt the whole system of frames/musical time. And suddenly, here I am, stuck on implementation details of this new `MusicalTime` and `RecordedTrack` classes, which do not even matter for the functionality, only for the cleaniness of the project.

Made backup of current state and reverted most of the made changes. Lets try to start again.

Currently it seems great! I make one change at a time, test it, commit it, and now I am almost where I need to be!

## 20.2.
Plan for today: tests for yesterdays' features, and hopefully bugfixes.

Test one: what will happen if the post prod gets a track not long in beats? This could explain more bugs, but it probably wont explain why the track offset does not work.
- often it will result in short (few callbacks long) tracks
- -> fixed rounding of first with start
- -> the callback should include *beats*, not samples over a beat.
    - do not append the overflowing samples in the callback
    - solve why the overflow was higher than 100

I have rewritten a lot of things, some started to make sense... Now I will go home and start testing.


It wrrrks!!!! bot after recording for too long it seems that the memory is giving up lol.... or idk, I just get alsa error, the same as before.

## 21.2.
Today I am implementing logging, and I am realizing some interesting stuff!
1) the immediate recording stop when in first half of beat feature is broken somehow:
when the program waits for the second half of beat, it rounds correctly, but when it stops in the first half, it round one beat down.
2) I am going to have to deal with redirecting `stderr` because of the alsa err... which should be alright, just tell the user, try to save the data and restart the stream.
3) Gonna try to figure out why does tkinter ommits a func call when spamming the RecordButton. 
    - -> this is probably due to the keypress being so fast tkinter mainloop does not register it. It can be implemented into the redirected stderr.

## 22.2.
Fixed a bug in `is in the first half of a beat omfg I have to shorten this`, but apparently the post-prod does not work either. Lets fix that! Ok, perhaps there was not any... funny. Anyways, Lets get into the redirecting of `stderr`.

### stderr redirect
Why do I do this?
1) My program will then be able to catch the ALSA underrun error and restart the stream.
2) I could also catch the error I raise in post-prod, as it only happens when the user clicks too fast... and notify the user to stop killing their keyboard/mouse, lol.

The ALSA err is apparently printed to stdout, so I will have to redirect that one either. Hopefully it wont break, as it could create an endless loop.
It was alright, but it did not work either. I do not know how the warning is printed... However, I can at least describe what is happening:

When the ALSA error is printed, the stream thread stops/breaks. No more callbacks are invoked. On the other hand, the tkinter (main) thread still runs. It stops only after I click the record button once more, pushing the STOP event into the event queue. The thread is then stuck on my while-sleep loop, which is now effectively endless. From this state it cannot recover in a different manner than keyboard interrupt. However, if I close the window instead of pressing again the rec button, the app closes normally.

Funny. Suddenly, I get the alsa error every time I try to run my code. It could be that ALSA is broken or idk...
Fixed a bug in `is in the first half of a beat omfg I have to shorten this`, but apparently the post-prod does not work either. Lets fix that!


## 23.2.
Made experiments on school PCs. Apparently, the bad clipping sound is caused by headphones port writing into microphone port somehow. When I go to sound settings and lower the volume of either in or out signal, this stops. However, I was not able to test the behaviour of a real microphone/keys plugged in and I think that school PCs do not have internal microphone... I was only able to record noise from me tapping the mic cable on "vnitřní zvukový systém analogové stereo" the sound was delayed significantly (one or two seconds or so), and on "monitor of..." there was no signal.

At home, the solution is to wait exactly one minute before plugging the keys in. Idk why.


## 26.2
najít jednu konfiguraci, ve které to funguje, tu popsat pro uživatele kvůli testování (tedy notebook s vnitrnim mikrofonem, jako mi to doma vzdy funguje).

investigace underrunu - ale ne na moc dlouho


main na top-level uroven


## 27.2.
Stabliní konfigurace: 
1) Používání sluchátek a vnitřního mikrofonu na laptopu s Ubuntu
2) Používání sluchátek a externího mikrofonu na PC s linux Mint

Případné nastavování vstupních/výstupních zařízení nacháváme na systémovém nastavení. 


## 29.2.
Debugging the fixed recording:
- when the stop comes in the first half of a beat, frames over == 0
- when the stop comes in the second half of a beat, frames over == 100*n; n == the number of already finished recordings
- in both cases the length of the beats is higher than it should be, and grows
- in both cases, a strange noise appears - it seems to be a 441 Hz saw wave. This means it has to do something with the callback, probably with the concatenating afterwards.

## 1.3.
- when the stop comes in the first half of a beat, frames over == 0
- ~~when the stop comes in the second half of a beat, frames over == 100*n; n == the number of already finished recordings~~
- ~~in both cases the length of the beats is higher than it should be, and grows~~
- in both cases, a strange noise appears - it seems to be a 441 Hz saw wave. This means it has to do something with the callback, probably with the concatenating afterwards.

The shapes seem to be alright.

Okay, this is a mystery: 
When the recorded track is initialized like this, it produces the strange lengths of bpm.
```py
def __init__(self, data: list[npt.NDArray[DTYPE]] = []) -> None:
    """Initialize an instance of recorded track.
    """
    self.data = data
```

But when it is initialized like this:
```py
def __init__(self) -> None:
    """Initialize an instance of recorded track.
    """
    self.data: list[npt.NDArray[DTYPE]] = []
```
The bpm acts normal.

### !!!
Experiment revealed that in the first case the RecordedTrack is initialized with some data, which it should not be. Turns out, this is a feature of python!

---
https://stackoverflow.com/questions/1132941/least-astonishment-and-the-mutable-default-argument

---
