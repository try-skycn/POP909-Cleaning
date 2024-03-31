import os
import json
import numpy as np
import pretty_midi


__all__ = [
    'Directories'
]


class Directories:
    music_index: int
    source_dir: str
    source_music_path: str
    source_music_file: str
    source_beat_file: str
    target_dir: str
    target_music_path: str
    target_music_file: str
    target_discrete_file: str

    def __init__(self, music_index: int):
        self.music_index = music_index

        source_dir = os.getenv('SOURCEDIR')
        assert isinstance(source_dir, str)
        source_dir = os.path.expanduser(source_dir)
        self.source_dir = os.path.join(source_dir, 'POP909')
        assert os.path.exists(self.source_dir)
        self.source_music_path = os.path.join(self.source_dir, f'{self.music_index:03d}')
        assert os.path.exists(self.source_music_path), f'Path \'{self.source_music_path}\' does not exists.'
        self.source_music_file = os.path.join(self.source_music_path, f'{self.music_index:03d}.mid')
        assert os.path.exists(self.source_music_file)
        self.source_beat_file = os.path.join(self.source_music_path, f'beat_midi.txt')
        assert os.path.exists(self.source_beat_file)

        target_dir = os.getenv('TARGETDIR')
        assert isinstance(target_dir, str)
        self.target_dir = os.path.expanduser(target_dir)
        os.makedirs(self.target_dir, exist_ok=True)
        self.target_music_path = os.path.join(self.target_dir, f'{self.music_index:03d}')
        os.makedirs(self.target_music_path, exist_ok=True)
        self.target_music_file = os.path.join(self.target_music_path, f'{self.music_index:03d}.mid')
        self.target_discrete_file = os.path.join(self.target_music_path, f'discrete.txt')

    def read_beat(self):
        beats = []
        with open(self.source_beat_file, 'r') as f:
            for line in f:
                timing, _, _ = line.strip().split()
                beats.append(float(timing))
        return np.array(beats)

    def read_midi(self):
        return pretty_midi.PrettyMIDI(self.source_music_file)

    def write_midi(self, midi: pretty_midi.PrettyMIDI):
        midi.write(self.target_music_file)

    def write_discrete(self, obj):
        with open(self.target_discrete_file, 'w') as f:
            json.dump(obj, f)
