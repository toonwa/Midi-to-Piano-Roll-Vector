import mido

input_midi_file = input("Enter the name of the MIDI file (excluding .mid extension): ") + ".mid"  # Name of the MIDI file



def add_sustain_note_with_controls(filename):
    # Load the MIDI file
    midi = mido.MidiFile(filename)
    new_tracks = []

    for track in midi.tracks:
        # Step 1: Convert delta times to absolute times
        events = []
        running_time = 0
        for msg in track:
            running_time += msg.time
            events.append((running_time, msg))

        # Step 2: Process events to add sustain notes
        new_events = []
        sustain_on = False
        sustain_note_start_time = 0

        for abs_time, msg in events:
            # Add the original message
            new_events.append((abs_time, msg))

            # Check for sustain pedal control changes
            if msg.type == 'control_change' and msg.control == 64:
                if msg.value > 0 and not sustain_on:  # Sustain pedal pressed
                    sustain_on = True
                    sustain_note_start_time = abs_time
                    # Add Note On for note 18 with velocity 1
                    new_events.append((abs_time, mido.Message('note_on', note=18, velocity=1, time=0)))
                elif msg.value == 0 and sustain_on:  # Sustain pedal released
                    sustain_on = False
                    # Add Note Off for note 18
                    sustain_duration = abs_time - sustain_note_start_time
                    new_events.append((abs_time, mido.Message('note_off', note=18, velocity=1, time=0)))
                    sustain_note_start_time = 0

        # If sustain was left on at the end of the track, turn off the note
        if sustain_on:
            sustain_duration = running_time - sustain_note_start_time
            new_events.append((running_time, mido.Message('note_off', note=18, velocity=1, time=0)))

        # Step 3: Convert absolute times back to delta times
        new_track = mido.MidiTrack()
        prev_time = 0
        for abs_time, msg in sorted(new_events, key=lambda x: x[0]):
            msg.time = abs_time - prev_time
            prev_time = abs_time
            new_track.append(msg)

        new_tracks.append(new_track)

    # Create a new MIDI file with the modified tracks
    new_midi = mido.MidiFile()
    new_midi.tracks.extend(new_tracks)

    # Save the modified MIDI file, overwriting the original
    new_midi.save(filename)
    print(f"Modified MIDI file saved and overwritten as {filename}")


add_sustain_note_with_controls(input_midi_file)
