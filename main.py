import pop909_cleaning as cleaning


def process(music_index: int):
    dirs = cleaning.Directories(music_index)
    music = dirs.read_midi()
    beat_div = cleaning.BeatDivision.create(dirs.read_beat())
    print('---')
    disc = cleaning.FirstDiscretize.create(music, beat_div, 0)
    beat_shift = disc.get_beat_shift()
    print(f'Beat shift: {beat_shift}')
    shifted_beat_div = beat_div.shift(beat_shift)
    discrete_shift = disc.suggest_discrete_shift()
    print(f'Suggested discrete shift: {discrete_shift}')
    print('---')
    disc = cleaning.FirstDiscretize.create(music, shifted_beat_div, discrete_shift)
    new_music = disc.to_music()
    dirs.write_midi(new_music)
    dirs.write_discrete(disc.to_object())


def main():
    for i in range(1, 909 + 1):
        process(i)


if __name__ == '__main__':
    main()
