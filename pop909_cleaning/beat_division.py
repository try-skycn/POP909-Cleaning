from dataclasses import dataclass
import numpy as np


__all__ = [
    'BeatDivision'
]


@dataclass
class BeatDivision:
    divisions: int
    beats: np.array  # [LEN]
    abeats: np.array  # [1+LEN], Appended Beats
    lengths: np.array  # [LEN], Beat Lengths
    mean_length: float
    med_length: float
    min_length: float
    max_length: float
    fine_beats: np.array  # [(#DIV + $EXT) * LEN]

    @classmethod
    def create(cls, beats: np.array, divisions=12, extended_beats=4):
        abeats = np.insert(beats, 0, 0)  # [1+LEN]
        lengths = beats - abeats[:-1]
        mean_length = lengths.mean()
        med_length = np.median(lengths)
        min_length = lengths.min()
        max_length = lengths.max()
        print(f'Mean: {mean_length:.5g}, Median: {med_length:.5g}, Min: {min_length:.5g}, Max: {max_length:.5g}')
        fine_beats = np.expand_dims(lengths, axis=-1) * np.arange(divisions) / divisions
        fine_beats = np.expand_dims(abeats[:-1], axis=1) + fine_beats
        fine_beats = fine_beats.flatten()
        fine_beats = np.concatenate((fine_beats, abeats[-1] + np.arange(extended_beats * divisions) / divisions * lengths[-1]))
        return cls(divisions, beats, abeats, lengths, mean_length, med_length, min_length, max_length, fine_beats)

    def shift(self, beat_shift: float):
        return BeatDivision(
            self.divisions, self.beats + beat_shift, self.abeats + beat_shift,
            self.lengths, self.mean_length, self.med_length, self.min_length, self.max_length,
            self.fine_beats + beat_shift
        )
