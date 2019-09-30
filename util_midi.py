import argparse
import random
import os
import numpy as np
from math import floor
from pyknon.genmidi import Midi
from pyknon.music import NoteSeq, Note
import music21
from pathlib import Path


VIOLINLIKE=["Violin", "Viola", "Cello", "Violincello", "Violoncello", "Flute", 
            "Oboe", "Clarinet", "Recorder", "Voice", "Piccolo",
            "StringInstrument", "Bassoon", "Horn"]
PIANOLIKE=["Piano", "Harp", "Harpsichord", "Organ", ""]


def get_stream(fname):
    mf=music21.midi.MidiFile()
    mf.open(fname)
    mf.read()
    mf.close()
    midi_stream = music21.midi.translate.midiFileToStream(mf)
    return midi_stream

def stream_to_chordwise(midi_stream, chamber, sample_freq, note_offset, note_range):

    numInstruments = 2 if chamber else 1
    maxTimeStep = floor(midi_stream.duration.quarterLength * sample_freq) + 1

    notes = []
    instrumentID = 0

    note_filter = music21.stream.filters.ClassFilter('Note')
    chord_filter = music21.stream.filters.ClassFilter('Chord')

    # append note events to notes[]
    for n in midi_stream.recurse().addFilter(note_filter):
        if chamber:
            instr = n.activeSite.getInstrument()
            instrumentID = None
            if str(instr) in PIANOLIKE:
                instrumentID = 0
            elif str(instr) in VIOLINLIKE:
                instrumentID = 1
            else:
                print("Warning, unknown instrument: " + str(instr))
                instrumendID = -1
            if instrumentID == -1:
                print("This would return an empty array")
        notes.append(
            (n.pitch.midi - note_offset, 
            floor(n.offset * sample_freq), 
            floor(n.duration.quarterLength * sample_freq), 
            instrumentID)
        )

    # append chord events to notes[]
    for c in midi_stream.recurse().addFilter(chord_filter):
        pitchesInChord = c.pitches
        if chamber:
            instr = c.activeSite.getInstrument()
            instrumentID = None            
            if str(instr) in PIANOLIKE:
                instrumentID = 0
            elif str(instr) in VIOLINLIKE:
                instrumentID = 1
            else:
                print("Warning, unknown instrument: "+str(instr))
                instrumendID = -1
            if instrumentID == -1:
                print("This would return an empty array")
        for p in pitchesInChord:
            notes.append(
                (p.midi - note_offset, 
                floor(c.offset * sample_freq), 
                floor(c.duration.quarterLength * sample_freq), 
                instrumentID))

    # score_arr[] (filled with 0/1)
    score_arr = np.zeros((maxTimeStep, numInstruments, note_range))
    for n in notes:
        pitch=n[0]
        while pitch<0:
            pitch+=12
        while pitch>=note_range:
            pitch-=12
        if n[3]==1:
            while pitch<22:
                pitch+=12
        score_arr[n[1], n[3], pitch] = 1                  
        score_arr[n[1]+1:n[1]+n[2], n[3], pitch] = 2

    # score_string_arr[] (p00000000000000010000000000000000000000)
    instr={}
    instr[0]="p"
    instr[1]="v"
    score_string_arr=[]
    for timestep in score_arr:
        for i in list(reversed(range(len(timestep)))):
            score_string_arr.append(instr[i]+''.join([str(int(note)) for note in timestep[i]]))      

    # data augmentation
    modulated = []
    notes_range = len(score_string_arr[0]) - 1
    for i in range(0,12):
        for chord in score_string_arr:
            padded = '000000' + chord[1:] + '000000'
            modulated.append(chord[0] + padded[i:i + notes_range])

    return " ".join(modulated)

def chord_to_notewise(score_string_arr, sample_freq):

    translated_list=[]
    for chord_index in range(len(score_string_arr)):
        chord = score_string_arr[chord_index]
        next_chord = ""
        for k in range(chord_index + 1, len(score_string_arr)):
            if score_string_arr[k][0] == chord[0]:
                next_chord = score_string_arr[k]
                break
        prefix = chord[0]
        chord = chord[1:]
        next_chord = next_chord[1:]
        for i in range(len(chord)):
            if chord[i] == "0":
                continue
            note = prefix + str(i) 
            if chord[i] == "1":
                translated_list.append(note)
            if next_chord == "" or next_chord[i] == "0":      
                translated_list.append("end" + note)
        if prefix == "p":
            translated_list.append("wait")
            
    i = 0
    translated_string = ""
    while i < len(translated_list):
        wait_count = 1
        if translated_list[i] == 'wait':
            while (
                wait_count <= sample_freq * 2
                and i + wait_count < len(translated_list)
                and translated_list[i + wait_count] == 'wait'
            ):
                wait_count += 1
            translated_list[i] = 'wait' + str(wait_count)
        translated_string += translated_list[i] + " "
        i += wait_count

    return translated_string

def modify_chord_rests(chords_string):
    # change rests
    chords_string_replaced = chords_string.replace("2", "0")
    single_rest = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chords = chords_string_replaced.split(" ")
    noterange = len(chords[0]) - 1
    i = 0
    while i < len(chords):
        j = 1
        if chords[i][1:] == "0" * noterange:
            num_prev_notes = 0
            for j in range(-10, 0):
                if i + j >= 0:
                    if chords[i + j] == "":
                        continue
                    for c in chords[i + j][1:]:
                        if c == "1":
                            num_prev_notes += 1
            num_prev_notes = min(num_prev_notes, len(single_rest) - 1)
            chords[i] = chords[i][0] + single_rest[num_prev_notes] * noterange
        i = i + 1
    return " ".join(chords)

def arr_to_chord_stream(score, sample_freq, note_offset):
    speed = 1. / sample_freq
    piano_notes = []
    violin_notes = []
    time_offset = 0
    for i in range(len(score)):
        current_chord = score[i]
        if len(current_chord) == 0:
            print("chord len is 0, no note played, continue")
            continue
        for j in range(1, len(current_chord)):
            if current_chord[j] == "1":
                duration = 2  # why 2 ???
                new_note = music21.note.Note(j + note_offset)    
                new_note.duration = music21.duration.Duration(duration * speed)
                new_note.offset = (i + time_offset) * speed
                if current_chord[0] == 'p':
                    piano_notes.append(new_note)
                elif current_chord[0] == 'v':
                    violin_notes.append(new_note)
    violin = music21.instrument.fromString("Violin")
    piano = music21.instrument.fromString("Piano")
    violin_notes.insert(0, violin)
    piano_notes.insert(0, piano)
    violin_stream = music21.stream.Stream(violin_notes)
    piano_stream = music21.stream.Stream(piano_notes)
    main_stream = music21.stream.Stream([violin_stream, piano_stream])
    return main_stream

def arr_to_note_stream(score, sample_freq, note_offset):
    speed = 1./sample_freq
    piano_notes = []
    violin_notes = []
    time_offset = 0
    i = 0
    while i < len(score):
        if score[i][:9] == "p_octave_":
            add_wait = ""
            if score[i][-3:] == "eoc":
                add_wait = "eoc"
                score[i] = score[i][:-3]
            this_note = score[i][9:]
            score[i] = "p" + this_note
            score.insert(i + 1, "p" + str(int(this_note) + 12) + add_wait)
            i += 1
        i += 1
    for i in range(len(score)):
        if score[i] in ["", " ", "<eos>", "<unk>"]:
            continue
        elif score[i][:3] == "end":
            if score[i][-3:] == "eoc":
                time_offset += 1
            continue
        elif score[i][:4] == "wait":
            time_offset += int(score[i][4:])
            continue
        else:
            duration = 1
            has_end = False
            note_string_len = len(score[i])
            for j in range(1,200):
                if i + j == len(score):
                    break
                if score[i + j][:4] ==" wait":
                    duration += int(score[i + j][4:])
                if score[i + j][:3 + note_string_len] == "end" + score[i] or score[i + j][:note_string_len] == score[i]:
                    has_end = True
                    break
                if score[i + j][-3:] == "eoc":
                    duration += 1
            if not has_end:
                duration = 12
            add_wait = 0
            if score[i][-3:] == "eoc":
                score[i] = score[i][:-3]
                add_wait = 1
            try: 
                new_note = music21.note.Note(int(score[i][1:]) + note_offset)    
                new_note.duration = music21.duration.Duration(duration * speed)
                new_note.offset = time_offset * speed
                if score[i][0] == "v":
                    violin_notes.append(new_note)
                else:
                    piano_notes.append(new_note)
            except:
                print("Unknown note: " + score[i])           
            time_offset += add_wait
    violin = music21.instrument.fromString("Violin")
    piano = music21.instrument.fromString("Piano")
    violin_notes.insert(0, violin)
    piano_notes.insert(0, piano)
    violin_stream = music21.stream.Stream(violin_notes)
    piano_stream = music21.stream.Stream(piano_notes)
    main_stream = music21.stream.Stream([violin_stream, piano_stream])
    return main_stream

def string_to_stream(string, sample_freq, note_offset, chordwise):
    # convert to array
    score_i = string.split(" ")
    if chordwise:
        return arr_to_chord_stream(score_i, sample_freq, note_offset)
    else:
        return arr_to_note_stream(score_i, sample_freq, note_offset)

def translate_piece(fname):
    sample_freqs=[4,12]
    note_ranges=[38,62]
    note_offsets={}
    note_offsets[38]=45
    note_offsets[62]=33

    sample_freq = sample_freqs[0] # 4
    note_range = note_ranges[0]   # 38
    note_offset = note_offsets[note_range]
    chamber = False

    midi_stream = get_stream(fname)
    chords_string = stream_to_chordwise(midi_stream, chamber, sample_freq, note_offset, note_range)
    chords_string_arr = chords_string.split(" ")
    notes_string = chord_to_notewise(chords_string_arr, sample_freq)

    # differentiate rests
    chords_string_modified = modify_chord_rests(chords_string)

    return chords_string_modified, notes_string

def save_stream(stream, fname, path=None):
    # returns full path to file
    if path:
        fname = f"{path}/{fname}"
    return stream.write('midi', fname)
    