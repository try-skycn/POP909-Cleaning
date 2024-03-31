from dataclasses import dataclass
import numpy as np
import pretty_midi
from .beat_division import BeatDivision


__all__ = [
    'FirstDiscretize'
]


@dataclass
class FirstDiscretizeInstrument:
    ins: pretty_midi.Instrument
    beat_div: BeatDivision
    notes: np.array  # [#NOTES, 2]
    abs_diff_argmin: np.array  # [#NOTES, 2]
    diff_abs_min: np.array  # [NOTES, 2]
    med_diff_abs_min: np.array  # [#NOTES, 2]
    abs_diff_min: np.array  # [#NOTES, 2]
    augmented_discrete_notes: np.array  # [#NOTES, 2]

    @classmethod
    def create(cls, ins: pretty_midi.Instrument, beat_div: BeatDivision, discrete_shift: int):
        print(f'Processing instrument: {ins.name}')
        notes = np.array([[note.start, note.end] for note in ins.notes])  # [#NOTES, 2]
        diff = np.expand_dims(notes, axis=-1) - beat_div.fine_beats  # [#NOTES, 2, #FINE_BEATS]
        abs_diff = np.absolute(diff)  # [#NOTES, 2, #FINE_BEATS]
        abs_diff_argmin = abs_diff.argmin(axis=-1)  # [#NOTES, 2]
        diff_abs_min = np.take_along_axis(diff, np.expand_dims(abs_diff_argmin, axis=-1), axis=-1)  # [#NOTES, 2, 1]
        diff_abs_min = np.squeeze(diff_abs_min, axis=-1)  # [#NOTES, 2]
        med_diff_abs_min = np.median(diff_abs_min, axis=0)  # [2]
        print(f'Median, left: {med_diff_abs_min[0]}, right: {med_diff_abs_min[1]}')
        abs_diff_min = abs_diff.min(axis=-1)  # [#NOTES, 2]
        abs_diff_min_max_all = abs_diff_min.max()
        rel_abs_diff_min_max_all = abs_diff_min_max_all / (beat_div.mean_length / beat_div.divisions)
        abs_diff_min_max_part = abs_diff_min.max(axis=0)
        abs_diff_min_argmax_part = abs_diff_min.argmax(axis=0)
        print(f'Maximum deviation: {abs_diff_min_max_all:.2g}, relative {rel_abs_diff_min_max_all:.2%}')
        print(f'Left: {abs_diff_min_max_part[0]:.2g}, Right: {abs_diff_min_max_part[1]:.2g}')
        print(f'Left argmax on {abs_diff_min_argmax_part[0]}: {abs_diff_min[abs_diff_min_argmax_part[0]]}')
        print(f'Right argmax on {abs_diff_min_argmax_part[1]}: {abs_diff_min[abs_diff_min_argmax_part[1]]}')
        augmented_discrete_notes = abs_diff_argmin + discrete_shift
        discrete_lengths = augmented_discrete_notes[:, 1] - augmented_discrete_notes[:, 0]
        print(f'Minimum discrete lengths: {discrete_lengths.min()}, position: {discrete_lengths.argmin()}')
        print(augmented_discrete_notes[:10])
        print('---')
        return cls(ins, beat_div, notes, abs_diff_argmin, diff_abs_min, med_diff_abs_min, abs_diff_min, augmented_discrete_notes)

    def to_music(self):
        print(f'Building instrument: {self.ins.name}')
        instrument = pretty_midi.Instrument(self.ins.program, is_drum=self.ins.is_drum, name=self.ins.name)

        for nid, ((st, ed), note) in enumerate(zip(self.augmented_discrete_notes, self.ins.notes)):
            start = st / self.beat_div.divisions * self.beat_div.mean_length
            assert st <= ed
            if st == ed:
                print(f'{nid}, {(self.notes[nid, 1] - self.notes[nid, 0]) / (self.beat_div.mean_length / self.beat_div.divisions):.2%}')
                ed = ed + 1
            end = ed / self.beat_div.divisions * self.beat_div.mean_length
            new_note = pretty_midi.Note(note.velocity, note.pitch, start, end)
            instrument.notes.append(new_note)

        return instrument

    def to_object(self):
        return dict(
            notes=self.notes,
            abs_diff_argmin=self.abs_diff_argmin,
            diff_abs_min=self.diff_abs_min,
            med_diff_abs_min=self.med_diff_abs_min,
            abs_diff_min=self.abs_diff_min
        )

    def get_beat_shift(self):
        return self.med_diff_abs_min[0]

    def get_min_start(self):
        return self.augmented_discrete_notes.min()


@dataclass
class FirstDiscretize:
    music: pretty_midi.PrettyMIDI
    beat_div: BeatDivision
    instruments: list[FirstDiscretizeInstrument]
    discrete_shift: int

    @classmethod
    def create(cls, music: pretty_midi.PrettyMIDI, beat_div: BeatDivision, discrete_shift: int):
        instruments = []
        for ins in music.instruments:
            dis_ins = FirstDiscretizeInstrument.create(ins, beat_div, discrete_shift)
            instruments.append(dis_ins)
        return cls(music, beat_div, instruments, discrete_shift)

    def to_music(self):
        music = pretty_midi.PrettyMIDI(resolution=self.music.resolution, initial_tempo=60 / self.beat_div.mean_length)
        for ins in self.instruments:
            music.instruments.append(ins.to_music())
        return music

    def to_object(self):
        return [ins.to_object() for ins in self.instruments]

    def get_beat_shift(self):
        return self.instruments[0].get_beat_shift()

    def suggest_discrete_shift(self):
        min_starts = [ins.get_min_start() for ins in self.instruments]
        suggested_start = min_starts[2]
        suggested_discrete_shift = - suggested_start
        while min(min_starts) + suggested_discrete_shift < 0:
            suggested_discrete_shift += 4 * self.beat_div.divisions
        return suggested_discrete_shift
