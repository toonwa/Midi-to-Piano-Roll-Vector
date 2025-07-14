import mido
import numpy as np
from svgwrite import Drawing
import os


# Configuration variables
MIDI_FILE_NAME = input("Enter the name of the MIDI file (excluding .mid extension): ") + ".mid"  # Name of the MIDI file
BLANK_SPACE_MM = 75  # Blank space at beginning in mm
BLANK_SPACE_END_MM = 200  # Blank space at the end in mm
BASE_LENGTH_MM = 2.1  # Base length for scaling the shortest note in mm

# Probably fine like this
LONG_NOTE_MIN_LENGTH_MM = 20  # Minimum length in mm for a note to be considered long
BRIDGE_WIDTH_MM = 0.55  # Width of the bridge between note segments in mm
BRIDGE_ROUNDING = 1.75 # For the rounding of the edges of long notes. 2 is fully circular, 0 is flat
SUSTAIN_ADJUST = 2 # How far note 18 (sustain pedal) is displaced on the roll. 1 is no adjustment.
CUT_LINE_SEGMENT_LENGTH = 15  # Length of each cut line segment in mm
CUT_LINE_SEGMENT_GAP = 0.3  # Gap between cut line segments in mm
HORIZONTAL_CUT_LINES = True  # Toggle for horizontal cutting lines
DOUBLE_CUT = True  # True to draw notes twice in the same spot for double cutting

# No touching
TIME_STEP = 0.01  # Time step for MIDI processing in seconds
NOTE_RANGE = (17, 110)  # Range of MIDI note numbers to include
NOTE_HEIGHT = 1.91  # Height of each note hole in mm
EXTRA_PAPER_WIDTH = 0.8  # Paper width configuration, + is wider, should be 286 mm irl
VERTICAL_GAP = 0.917  # Gap between different notes in mm
NOTE_VERTICAL_OFFSET = 6.75  # Vertical offset for notes in mm within the two lines (+ is holes up/right)

def midi_to_piano_roll(midi_file, time_step=TIME_STEP, note_range=NOTE_RANGE):
    print("Loading MIDI file...")
    midi = mido.MidiFile(midi_file)
    total_time = sum([msg.time for msg in midi if not msg.is_meta])
    num_steps = int(total_time / time_step)
    roll_matrix = np.zeros((note_range[1] - note_range[0] + 1, num_steps), dtype=int)

    print("Processing MIDI events...")
    current_time = 0
    active_notes = {}
    note_durations = []

    for msg in midi:
        if not msg.is_meta:
            current_time += msg.time
            step_index = int(current_time / time_step)

            if msg.type == 'note_on' and msg.velocity > 0:
                note_index = msg.note - note_range[0]
                if 0 <= note_index < roll_matrix.shape[0]:
                    active_notes[msg.note] = step_index  # Store the start time for this note
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                note_index = msg.note - note_range[0]
                if msg.note in active_notes:
                    start_index = active_notes.pop(msg.note)
                    roll_matrix[note_index, start_index:step_index] = 1  # Fill the duration
                    duration = step_index - start_index
                    note_durations.append(duration)

    min_duration = min(note_durations) if note_durations else 1
    print("MIDI file successfully processed.")
    return roll_matrix, min_duration

def piano_roll_to_svg(matrix, min_duration, filename="piano_roll.svg", note_height=NOTE_HEIGHT, base_length_mm=BASE_LENGTH_MM, vertical_gap=VERTICAL_GAP, note_vertical_offset=NOTE_VERTICAL_OFFSET, long_note_threshold=LONG_NOTE_MIN_LENGTH_MM, bridge_width_mm=BRIDGE_WIDTH_MM, extra_paper_width=EXTRA_PAPER_WIDTH):
    # Scaling factor to correct dimensions
    scaling_factor = 2.82  # Scale to achieve accurate 2mm hole size in Illustrator
    
    # Adjust all measurements by scaling factor
    scaled_note_height = note_height * scaling_factor
    scaled_base_length_mm = base_length_mm * scaling_factor
    scaled_vertical_gap = vertical_gap * scaling_factor
    scaled_note_vertical_offset = note_vertical_offset * scaling_factor
    scaled_blank_space_mm = BLANK_SPACE_MM * scaling_factor
    scaled_blank_space_end_mm = BLANK_SPACE_END_MM * scaling_factor
    scaled_long_note_threshold = long_note_threshold * scaling_factor
    scaled_bridge_width = bridge_width_mm * scaling_factor  # Configurable bridge width
    min_first_part_length = 3 * scaling_factor  # Minimum first part length

    note_width_scaling_factor = scaled_base_length_mm / min_duration  # Adjusted scale based on shortest note
    
    rows, cols = matrix.shape
    total_height = (cols * note_width_scaling_factor) + scaled_blank_space_mm + scaled_blank_space_end_mm
    total_width = (rows * scaled_note_height) + (rows - 1) * scaled_vertical_gap + ((286 + extra_paper_width) * scaling_factor) + 10 * scaling_factor

    dwg = Drawing(filename, size=(total_width, total_height))

    # Add a root group to hold all elements for easier transformations
    root_group = dwg.g()

    # Define cut line positions
    cut_line_x = 5 * scaling_factor  # Position for the left cut line
    right_cut_line_x = cut_line_x + ((286 + extra_paper_width) * scaling_factor)  # Position for the right cut line, 286mm to the right

    # Convert segment length and gap to scaled values
    scaled_cut_line_segment_length = CUT_LINE_SEGMENT_LENGTH * scaling_factor
    scaled_cut_line_segment_gap = CUT_LINE_SEGMENT_GAP * scaling_factor
    
    # Draw the left segmented cut line
    current_y = 0
    while current_y < total_height:
        segment_end = min(current_y + scaled_cut_line_segment_length, total_height)
        root_group.add(dwg.line(
            start=(cut_line_x, current_y),
            end=(cut_line_x, segment_end),
            stroke='red',
            stroke_width=1
        ))
        current_y = segment_end + scaled_cut_line_segment_gap

    # Draw the right segmented cut line
    current_y = 0
    while current_y < total_height:
        segment_end = min(current_y + scaled_cut_line_segment_length, total_height)
        root_group.add(dwg.line(
            start=(right_cut_line_x, current_y),
            end=(right_cut_line_x, segment_end),
            stroke='red',
            stroke_width=1
        ))
        current_y = segment_end + scaled_cut_line_segment_gap

    # Draw horizontal cutting lines if enabled
    if HORIZONTAL_CUT_LINES:
        current_x = cut_line_x
        while current_x <= right_cut_line_x:
            segment_end_x = min(current_x + scaled_cut_line_segment_length, right_cut_line_x)
            root_group.add(dwg.line(
                start=(current_x, 0),
                end=(segment_end_x, 0),
                stroke='red',
                stroke_width=1
            ))
            current_x = segment_end_x + scaled_cut_line_segment_gap

        current_x = cut_line_x
        while current_x <= right_cut_line_x:
            segment_end_x = min(current_x + scaled_cut_line_segment_length, right_cut_line_x)
            root_group.add(dwg.line(
                start=(current_x, total_height),
                end=(segment_end_x, total_height),
                stroke='red',
                stroke_width=1
            ))
            current_x = segment_end_x + scaled_cut_line_segment_gap

    # Draw notes with vertical offset for blank space at the beginning
    for row in range(rows):
        col_start = None
        for col in range(cols):
            if matrix[row, col] == 1:
                if col_start is None:
                    col_start = col
            elif col_start is not None:
                y = (col_start * note_width_scaling_factor) + scaled_blank_space_mm
                
                # Calculate x position, adjust for note 18 (row == 1)
                x = row * (scaled_note_height + scaled_vertical_gap) + scaled_note_vertical_offset + 1 * scaling_factor
                if row == 1:  # Shift note 18 (sustain) towards note 17
                    x -= scaled_note_height / SUSTAIN_ADJUST
                
                duration_height = (col - col_start) * note_width_scaling_factor

                # Split long notes into multiple parts if needed
                if duration_height > scaled_long_note_threshold:
                    remaining_duration = duration_height
                    parts = []
                    
                    # Break into full segments first
                    while remaining_duration > scaled_long_note_threshold + scaled_bridge_width:
                        parts.append(scaled_long_note_threshold)
                        remaining_duration -= scaled_long_note_threshold + scaled_bridge_width

                    # Ensure the first part is at least 3 mm
                    if remaining_duration < min_first_part_length:
                        # Merge the first part with the next part if too short
                        if parts:
                            parts[0] += remaining_duration + scaled_bridge_width
                        else:
                            parts.append(remaining_duration)  # If no other parts, use remaining duration
                        remaining_duration = 0
                    else:
                        # Add remaining duration as the first part
                        parts.insert(0, remaining_duration)

                    # Draw all parts
                    current_y = y
                    for i, part in enumerate(parts):
                        for _ in range(2 if DOUBLE_CUT else 1):  # Draw twice if DOUBLE_CUT is True
                            root_group.add(dwg.rect(
                                insert=(right_cut_line_x - x - scaled_note_height, total_height - current_y - part), 
                                size=(scaled_note_height, part), 
                                fill="black", 
                                rx=BRIDGE_ROUNDING,
                                ry=BRIDGE_ROUNDING
                            ))

                        # Increment y for the next segment, adding a bridge gap only if it's not the last segment
                        current_y += part + (scaled_bridge_width if i < len(parts) - 1 else 0)

                else:
                    for _ in range(2 if DOUBLE_CUT else 1):  # Draw twice if DOUBLE_CUT is True
                        root_group.add(dwg.rect(insert=(right_cut_line_x - x - scaled_note_height, total_height - y - duration_height), 
                                                 size=(scaled_note_height, duration_height), 
                                                 fill="black",
                                                 rx=scaled_note_height / 2, 
                                                 ry=scaled_note_height / 2))
                col_start = None

        # Handle the last note in the column
        if col_start is not None:
            y = (col_start * note_width_scaling_factor) + scaled_blank_space_mm
            
            x = row * (scaled_note_height + scaled_vertical_gap) + scaled_note_vertical_offset + 1 * scaling_factor
            if row == 1:  # Shift note 18 half note height towards note 17
                x -= scaled_note_height / 2
            
            duration_height = (cols - col_start) * note_width_scaling_factor

            if duration_height > scaled_long_note_threshold:
                remaining_duration = duration_height
                parts = []
                
                # Break into full segments first
                while remaining_duration > scaled_long_note_threshold + scaled_bridge_width:
                    parts.append(scaled_long_note_threshold)
                    remaining_duration -= scaled_long_note_threshold + scaled_bridge_width

                # Ensure the first part is at least 3 mm
                if remaining_duration < min_first_part_length:
                    # Merge the first part with the next part if too short
                    if parts:
                        parts[0] += remaining_duration + scaled_bridge_width
                    else:
                        parts.append(remaining_duration)  # If no other parts, use remaining duration
                    remaining_duration = 0
                else:
                    # Add remaining duration as the first part
                    parts.insert(0, remaining_duration)

                # Draw all parts
                current_y = y
                for i, part in enumerate(parts):
                    for _ in range(2 if DOUBLE_CUT else 1):  # Draw twice if DOUBLE_CUT is True
                        root_group.add(dwg.rect(
                            insert=(right_cut_line_x - x - scaled_note_height, total_height - current_y - part), 
                            size=(scaled_note_height, part), 
                            fill="black", 
                            rx=BRIDGE_ROUNDING,
                            ry=BRIDGE_ROUNDING 
                        ))

                    # Increment y for the next segment, adding a bridge gap only if it's not the last segment
                    current_y += part + (scaled_bridge_width if i < len(parts) - 1 else 0)

            else:
                for _ in range(2 if DOUBLE_CUT else 1):  # Draw twice if DOUBLE_CUT is True
                    root_group.add(dwg.rect(insert=(right_cut_line_x - x - scaled_note_height, total_height - y - duration_height), 
                                             size=(scaled_note_height, duration_height), 
                                             fill="black",
                                             rx=scaled_note_height / 2, 
                                             ry=scaled_note_height / 2))

    # Apply mirroring to the root group
    root_group.translate(total_width, 0)  # Translate content to the right edge
    root_group.scale(-1, 1)  # Mirror horizontally
    
    # Add the root group to the SVG
    dwg.add(root_group)
    dwg.save()
    print(f"SVG file '{filename}' created successfully.")


# Main execution
try:
    print("Generating piano roll...")
    piano_roll, min_duration = midi_to_piano_roll(MIDI_FILE_NAME)
    svg_file_name = os.path.splitext(MIDI_FILE_NAME)[0] + ".svg"
    piano_roll_to_svg(piano_roll, min_duration, filename=svg_file_name)
    print("Script completed successfully.")
except Exception as e:
    print(f"An error occurred: {e}")
