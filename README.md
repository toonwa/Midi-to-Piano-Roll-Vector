# Midi-to-Piano-Roll-Vector-
Python script that turns midi files into svg files to be (laser)cut by a plotter and played on a player piano.
Also includes a similar script for making the common 20 note rolls used by organs by deleika, raffin, etc.


SCRIPTS
Checkoverlap.py - For identifying any overlapping notes in the midi file
Miditoroll.py - Turns a midi file into a piano roll svg
Miditoorgan.py - Turns a midi file into a 20 note organ svg. Make sure the midi file uses these notes: https://www.mmdigest.com/Tech/20er_gamma.html  4 extra holes above the standard 20 for percussion etc is supported

HOW TO USE:
- Put a midi file in the same folder as all this
- Open startup.bat and make a selection, or activate the environment and the script manually
- Enter the name of the midi file (without the .mid extension)

I recommend running checkoverlap.py before making the svg, overlapping notes may cause some unexpected results so make sure there are none. There is 1 overlap in the example file to test out this script.
