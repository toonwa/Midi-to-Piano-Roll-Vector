# Midi-to-Piano-Roll-Vector
Python script that turns midi files into svg files to be (laser)cut by a plotter and played on a player piano.
Also includes a similar script for making the common 20 note rolls used by organs from deleika, raffin, etc.

!!Before cutting out an entire song, I recommend doing some testing and, if necessarry, adjusting the configuration variables at the top of the main scripts.


HELPER SCRIPTS:

Checkoverlap.py - For identifying any overlapping notes in the midi file
I recommend running this script before making the svg, overlapping notes may cause some unexpected results so make sure there are none. There is 1 overlap in the example file to test out this script.

Sustainadd.py - Useful for downloaded midi files that may have the sustain pedal as program changes. This script adds a note at note 18 (used for the sustain pedal) whenever control 64 is above 0, until control 64 is at 0 again. Try it out on the example file.


MAIN SCRIPTS:

Miditoroll.py - Turns a midi file into a piano roll svg.
The svg will be scaled based on the shortest note found in the midi file. It's up to you to arrange your music in a way that is playable on the piano.
Note 18 (used for the sustain pedal) is placed slightly to the left on the svg to better align with the tracking hole that reads this. If you have a different tracking bar on your piano, edit the configuration variable in the script.

Miditoorgan.py - Turns a midi file into a 20 note organ roll svg. Make sure the midi file only uses the notes included in the example file + 4 extra holes above the standard 20 for percussion etc is supported


HOW TO USE:

First time: Set up a python environment and install the libraries that you run into.

- Put a midi file in the same folder as the script
- Open startup.bat and make a selection, or activate the environment and the script manually
- Enter the name of the midi file (without the .mid extension)
