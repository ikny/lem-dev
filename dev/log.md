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

__EDIT 16.9.: I read on stack overflow that there is no need to solve this. So at least now, there is really no nedd to do so.__

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

28.11.
I was battling with poetry and github and IT TOOK FUCKING FOREVER AAARGH

but finally, it is done I hope.