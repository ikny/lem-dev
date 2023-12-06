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