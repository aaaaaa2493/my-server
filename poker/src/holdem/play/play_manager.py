from typing import List
from os import listdir, mkdir, remove
from os.path import exists
from pickle import load, dump
from random import randint
from shutil import rmtree
from holdem.play.play import Play
from holdem.name_manager import NameManager
from special.debug import Debug
from special.mode import Mode
from special.settings import Settings


class PlayManager:

    Plays = List[Play]

    _initialized = False
    _bank_of_plays: Plays = None
    _best_plays = None

    GenCount: int = 10000
    PlayPath = 'play'

    @staticmethod
    def init():

        Debug.play_manager('Start initialization')

        PlayManager._bank_of_plays = []

        if not exists(f'{PlayManager.PlayPath}'):
            mkdir(f'{PlayManager.PlayPath}')

        if not Settings.game_mode == Mode.Evolution and 'all' in listdir(f'{PlayManager.PlayPath}'):
            PlayManager._initialized = True
            PlayManager._bank_of_plays = load(open(f'{PlayManager.PlayPath}/all', 'rb'))
            for play in PlayManager._bank_of_plays:
                play.busy = False
            PlayManager.GenCount = len(PlayManager._bank_of_plays)
            Debug.play_manager('End initialization (short way)')
            return

        generations = listdir(f'{PlayManager.PlayPath}')

        for gen_path in generations:

            if gen_path == 'all':
                continue

            Debug.play_manager(f'Initialize generation {gen_path}')
            exemplars = listdir(f'{PlayManager.PlayPath}/{gen_path}')

            for ex_path in exemplars:
                Debug.play_manager(f'Initialize exemplar {gen_path} {ex_path}')
                play: Play = load(open(f'{PlayManager.PlayPath}/{gen_path}/{ex_path}', 'rb'))

                if play.generation != int(gen_path):
                    raise ValueError(f'Generation path {gen_path} does not work')

                if play.exemplar != int(ex_path):
                    raise ValueError(f'Exemplar path {ex_path} does not work')

                play.busy = False
                PlayManager._bank_of_plays += [play]

        PlayManager._initialized = True

        PlayManager.fill_zero_gens()
        dump(PlayManager._bank_of_plays, open(f'{PlayManager.PlayPath}/all', 'wb'))

        Debug.play_manager('End initialization')

    @staticmethod
    def delete_bad_plays():

        if not PlayManager._initialized:
            PlayManager.init()

        if Settings.game_mode == Mode.Evolution:

            indexes_to_delete = []

            for index, play in enumerate(PlayManager._bank_of_plays):

                if (play.total_plays > 10 and play.average_places > 0.8 and play.value() < 1 or
                        play.total_plays > 50 and play.average_places > 0.45 and play.value() < 2 or
                        play.total_plays > 100 and play.average_places > 0.40 and play.value() < 3 or
                        play.total_plays > 200 and play.average_places > 0.35 and play.value() < 4 or
                        play.total_plays > 300 and play.average_places > 0.30 and play.value() < 5 or
                        play.total_plays > 400 and play.average_places > 0.25 and play.value() < 6 or
                        play.total_plays > 500 and play.average_places > 0.20 and play.value() < 7 or
                        play.total_plays > 600 and play.average_places > 0.15 and play.value() < 8 or
                        play.total_plays > 700 and play.average_places > 0.13 and play.value() < 9 or
                        play.total_plays > 800 and play.average_places > 0.12 and play.value() < 10):

                    indexes_to_delete += [index]
                    remove(f'{PlayManager.PlayPath}/{play.generation}/{play.exemplar}')

                    Debug.play_manager(f'Delete bad play gen {play.generation} '
                                       f'ex {play.exemplar} after {play.total_plays} games '
                                       f'wins {play.wins} avg {int(play.average_places * 1000)} '
                                       f'new games {len(play.plays_history)} value {round(play.value(), 2)}')

            for index in reversed(indexes_to_delete):
                NameManager.add_name(PlayManager._bank_of_plays[index].name)
                del PlayManager._bank_of_plays[index]

            PlayManager.fill_zero_gens()

    @staticmethod
    def save_play(play: Play):

        if not PlayManager._initialized:
            PlayManager.init()

        if Settings.game_mode == Mode.Evolution:

            if not exists(f'{PlayManager.PlayPath}/{play.generation}'):
                mkdir(f'{PlayManager.PlayPath}/{play.generation}')

            dump(play, open(f'{PlayManager.PlayPath}/{play.generation}/{play.exemplar}', 'wb'))

    @staticmethod
    def fill_zero_gens():

        if not PlayManager._initialized:
            PlayManager.init()

        if Settings.game_mode == Mode.Evolution:

            zero_plays = [play.exemplar for play in PlayManager._bank_of_plays if play.generation == 0]
            zero_count = len(zero_plays)
            max_exemplar = max(zero_plays) if zero_count > 0 else 0

            to_fill = PlayManager.GenCount - zero_count
            starts_with = max_exemplar + 1

            for curr_ex in range(starts_with, starts_with + to_fill):
                play = Play()
                play.name = NameManager.get_name()
                play.exemplar = curr_ex
                PlayManager._bank_of_plays += [play]
                PlayManager.save_play(play)

    @staticmethod
    def get_play(only_profitable: bool = False) -> Play:

        if not PlayManager._initialized:
            PlayManager.init()

        if not PlayManager._bank_of_plays:
            PlayManager.fill_zero_gens()

        if only_profitable:
            if PlayManager._best_plays is None:
                PlayManager._best_plays = sorted([play for play in PlayManager._bank_of_plays if play.total_plays > 10],
                                                 key=lambda p: p.value(), reverse=True)

            for play in PlayManager._best_plays:
                if not play.busy:
                    play.busy = True
                    return play

        len_plays = len(PlayManager._bank_of_plays)
        start_index = index = randint(0, len_plays - 1)
        while PlayManager._bank_of_plays[index].busy:
            index = (index + 1) % len_plays
            if index == start_index:
                raise OverflowError('There is no plays available')

        PlayManager._bank_of_plays[index].busy = True
        return PlayManager._bank_of_plays[index]

    @staticmethod
    def standings(count: int = -1):

        if not PlayManager._initialized:
            PlayManager.init()

        if count == -1:
            count = len(PlayManager._bank_of_plays)

        Debug.evolution(f'Top {count} exemplars of evolution:')

        for place, play in enumerate(sorted([play for play in PlayManager._bank_of_plays
                                             if len(play.plays_history) > 10 and play.value() > 1],
                                            key=lambda p: p.value(), reverse=True)[:count]):
            Debug.evolution(f'{place + 1:<2}) {play}')

    @staticmethod
    def remove_folder():
        rmtree(PlayManager.PlayPath)
