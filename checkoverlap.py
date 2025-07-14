import mido
import pretty_midi
from collections import defaultdict

def note_number_to_name(note_number):
    return pretty_midi.note_number_to_name(note_number)

def find_overlapping_notes(midi_file):
    midi = mido.MidiFile(midi_file)
    ticks_per_beat = midi.ticks_per_beat

    # Find first tempo (default to 500000 µs/beat if not set)
    tempo = 500000
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break

    # Build global list of (absolute_tick, msg) from all tracks
    merged_events = []
    for track in midi.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            if msg.type in ['note_on', 'note_off']:
                merged_events.append((abs_tick, msg))

    # Sort by absolute tick
    merged_events.sort(key=lambda x: x[0])

    # Track overlapping notes
    active_notes = defaultdict(int)
    overlapping_info = []

    for abs_tick, msg in merged_events:
        if msg.type == 'note_on' and msg.velocity > 0:
            active_notes[msg.note] += 1
            if active_notes[msg.note] > 1:
                time_sec = mido.tick2second(abs_tick, ticks_per_beat, tempo)
                overlapping_info.append((abs_tick, time_sec, msg.note, note_number_to_name(msg.note)))
        else:  # note_off or note_on with velocity 0
            active_notes[msg.note] -= 1

    return overlapping_info

# Prompt user
midi_path = input("Enter the name of the MIDI file (excluding .mid extension): ") + ".mid"
overlaps = find_overlapping_notes(midi_path)

# Display results
if overlaps:
    print("Overlapping notes detected:")
    for tick, seconds, note_num, note_name in overlaps:
        minutes = int(seconds // 60)
        secs = seconds % 60
        time_str = f"{minutes}m {secs:.3f}s" if minutes > 0 else f"{secs:.3f}s"
        print(f"- Tick: {tick}, Time: {time_str}, Note: {note_name} (MIDI {note_num})")
else:
    print("No overlapping notes found.")

