import lzma
import pickle

import click

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance


# D:\proj\SC2MapAnalysis\MapAnalyzer\pickle_gameinfo\SubmarineLE.xz
@click.group(
        help="Commands marked with (LIVE) require SC launch and windows environment."
)  # pragma: no cover
def cli():  # pragma: no cover
    pass


@cli.command(help="Save map plot as png")  # pragma: no cover
@click.option("-mp", default=".", help="map file path")  # pragma: no cover
def save_plot(mp):  # pragma: no cover
    with lzma.open(f"{mp}", "rb") as f:
        raw_game_data, raw_game_info, raw_observation = pickle.load(f)

    bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
    map_data = MapData(bot=bot)
    map_data.save_plot()
    print("Saved.")
