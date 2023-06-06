import sys
import mido
from mido import MidiFile

tempos = []

def parse_midi_file(filename):
    midi_file = MidiFile(filename)

    notes = {}
    order = {}
    current_time = 0.0
    tpb = midi_file.ticks_per_beat

    for tempo in midi_file:
        if tempo.type == 'set_tempo':
            tempos.append(tempo.tempo)

    for msg in midi_file:
        current_time += msg.time

        if msg.type == 'note_on':
            if msg.channel not in notes.keys():
                notes[msg.channel] = {}
            if msg.note not in notes[msg.channel].keys():
                notes[msg.channel][msg.note] = []
            notes[msg.channel][msg.note].append([current_time, 0.0])
            if msg.channel not in order.keys():
                order[msg.channel] = []
            order[msg.channel].append(msg.note)
        elif msg.type == 'note_off':
            notes[msg.channel][msg.note][len(notes[msg.channel][msg.note]) - 1][1] = current_time

    return order, notes, tpb

def note_to_name(note_number):
    note_names = ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b']
    octave = note_number // 12 - 1
    note_name = note_names[note_number % 12]
    return f"{note_name}{octave}"

def message_delays(d):
    while d > 0:
        if d >= 1000:
            print("    &message_delay_1000,")
            d -= 1000
        elif d >= 500:
            print("    &message_delay_500,")
            d -= 500
        elif d >= 250:
            print("    &message_delay_250,")
            d -= 250
        elif d >= 100:
            print("    &message_delay_100,")
            d -= 100
        elif d >= 50:
            print("    &message_delay_50,")
            d -= 50
        elif d >= 25:
            print("    &message_delay_25,")
            d -= 25
        elif d >= 10:
            print("    &message_delay_10,")
            d -= 10
        elif d >= 1:
            print("    &message_delay_1,")
            d -= 1

def print_notes(order, cnotes, tpb):
    for channel, notes in order.items():
        time = -1.0
        same_time = []
        print("#include <notification/notification_messages.h>")
        print("#include <notification/notification.h>")
        print("")
        print(f"const NotificationSequence channel{channel} = " + "{")

        for note in notes:
            start = cnotes[channel][note][0][0]
            if time == -1.0:
                time = start
            if start == time:
                same_time.append(note)
            else:
                note_name = note_to_name(max(same_time))
                dur = cnotes[channel][max(same_time)][0][1] - cnotes[channel][max(same_time)][0][0]
                durms = int(dur * 1000)
                print(f"    &message_note_{note_name},")
                message_delays(durms)
                if start - dur != time:
                    print("    &message_click,")
                    message_delays(int((start - (time + dur)) * 1000))
                for n in same_time:
                    cnotes[channel][n].pop(0)
                time = start
                same_time = [note]

        try:
            note_name = note_to_name(max(same_time))
            dur = cnotes[channel][max(same_time)][0][1] - cnotes[channel][max(same_time)][0][0]
            durms = int(dur * 1000)
            print(f"    &message_note_{note_name},")
            message_delays(durms)
            print("    NULL,")
            print("};")
            for n in same_time:
                cnotes[channel][n].pop(0)
        except IndexError:
            pass

        print("")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("Expecting a filename")
        sys.exit(1)
    midi_filename = sys.argv[1]
    order, notes, tpb = parse_midi_file(midi_filename)
    print_notes(order, notes, tpb)
