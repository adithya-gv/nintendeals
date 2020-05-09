import logging
import re
from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.constants import NA, SWITCH, N3DS
from nintendeals.noa.external import algolia

log = logging.getLogger(__name__)


def _list_games(platform: str, **kwargs) -> Iterator[Game]:
    for data in algolia.search_games(platform=platform, **kwargs):
        game = Game(
            title=data["title"],
            region=NA,
            platform=platform,
            nsuid=data.get("nsuid"),
        )

        game.na_slug = data["slug"]
        game.genres = data.get("categories", [])

        try:
            release_date = data["releaseDateMask"].split("T")[0]
            game.release_date = datetime.strptime(release_date, '%Y-%m-%d')
        except ValueError:
            pass

        try:
            game.players = int(re.sub(r"[^\d]*", "", data["players"]))
        except ValueError:
            game.players = 0

        game.description = data.get("description")
        game.free_to_play = data.get("msrp") == 0.0
        game.publisher = data.get("publishers", [None])[0]
        game.developer = data.get("developers", [None])[0]

        game.virtual_console = data.get("virtualConsole", "na") != "na"

        yield game


def list_switch_games(**kwargs) -> Iterator[Game]:
    """
        List all the Switch games in Nintendo of America. The following subset
    of data will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (Unavailable)
        * platform: str = "Nintendo Switch"
        * region: str = "NA"
        * na_slug: str

        * description: str
        * developer: str
        * genres: List[str]
        * publisher: str
        * release_date: datetime

        # Common Features
        * free_to_play: bool

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Iterator of Switch games from Nintendo of America.
    """
    log.info("Fetching list of Nintendo Switch games")

    yield from _list_games(SWITCH, **kwargs)


def list_3ds_games(**kwargs) -> Iterator[Game]:
    """
        List all the 3DS games in Nintendo of America. The following subset
    of data will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (Unavailable)
        * platform: str = "Nintendo 3DS"
        * region: str = "NA"
        * na_slug: str

        * description: str
        * developer: str
        * genres: List[str]
        * publisher: str
        * release_date: datetime

        # Common Features
        * free_to_play: bool

        # 3DS Features
        * virtual_console: bool

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Iterator of 3DS games from Nintendo of America.
    """
    log.info("Fetching list of Nintendo 3DS games")

    yield from _list_games(N3DS, **kwargs)
