from typing import Optional
from os import listdir, makedirs, remove
from os.path import exists
from data.poker_game import PokerGame
from data.parsing.poker_stars_parsing import PokerStars, PokerStarsParsing
from data.parsing.party_poker_parsing import PartyPoker, PartyPokerParsing
from data.parsing.poker_888_parsing import Poker888, Poker888Parsing
from special.debug import Debug


class GameParser:

    @staticmethod
    def get_parser(text, game):
        match = PokerStars.identifier.search(text)
        if match is not None:
            Debug.parser('Found PokerStars game')
            return PokerStarsParsing(game)

        match = Poker888.identifier.search(text)
        if match is not None:
            Debug.parser('Found Poker888 game')
            return Poker888Parsing(game)

        match = Poker888.identifier_snap.search(text)
        if match is not None:
            Debug.parser('Found Poker888 Snap Poker game')
            return Poker888Parsing(game)

        match = PartyPoker.identifier.search(text)
        if match is not None:
            Debug.parser('Found PartyPoker game')
            return PartyPokerParsing(game)

        return None

    @staticmethod
    def parse_dir(path: str) -> None:
        games = listdir(PokerGame.path_to_raw_games + path)
        if not exists(PokerGame.path_to_parsed_games + path):
            makedirs(PokerGame.path_to_parsed_games + path)
        for game_path in games:
            game = GameParser.parse_game(f'{path}/{game_path}')
            if game is not None:
                game.save()
                # game.convert()
                remove(PokerGame.path_to_raw_games + path + '/' + game_path)

    @staticmethod
    def parse_game(path: str) -> Optional[PokerGame]:
        game = PokerGame()
        text_game = open(PokerGame.path_to_raw_games + path, 'r', encoding='utf-8').read().strip()
        game.source = path

        Debug.parser('\nStarting to analyse ' + path)

        parser = GameParser.get_parser(text_game, game)

        if parser is None:
            Debug.parser('Cannot parse game - can not identify')
            return None

        parser.process_game(text_game)

        game.approximate_players_left()
        game.add_final_table_marks()
        return game