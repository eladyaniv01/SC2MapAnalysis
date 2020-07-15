import lzma
import pickle

import click

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance


# D:\proj\SC2MapAnalysis\MapAnalyzer\pickle_gameinfo\SubmarineLE.xz
@click.group(help='Commands marked with (LIVE) require SC launch and windows environment.')
def cli():
    pass


@cli.command(help='Save map plot as png')
@click.option('-mp', default='.', help='map file path')
def save_plot(mp):
    with lzma.open(f"{mp}", "rb") as f:
        raw_game_data, raw_game_info, raw_observation = pickle.load(f)

    bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
    map_data = MapData(bot=bot)
    map_data.save_plot()
    print("Saved.")
