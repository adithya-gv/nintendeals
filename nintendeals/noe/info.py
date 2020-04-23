from datetime import datetime

import requests
from bs4 import BeautifulSoup

from nintendeals.classes.games import Game
from nintendeals.constants import EU, PLATFORMS

DETAIL_URL = "https://ec.nintendo.com/GB/en/titles/{nsuid}"


def _sibling(soup: BeautifulSoup, string: str, tag: str = "p") -> str:
    p = soup.find(tag, class_="game_info_title", string=string)

    if not p:
        return ""

    sib = p.find_next_sibling("p")

    if not sib:
        return ""

    return sib.text


def _scrap(url: str) -> Game:
    response = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(response.text, features="html.parser")

    script = next(filter(lambda s: "var nsuids = [" in str(s), soup.find_all('script')))
    lines = [line.strip().replace("\",", "") for line in str(script).split("\n") if ':' in line]
    data = {}

    for line in lines:
        split = line.split(": \"")

        if len(split) != 2:
            continue

        data[split[0].replace("\"", "")] = split[1].replace("\"", "")

    platform = data["systemTypeMasterSystem"]

    game = Game(
        nsuid=data["nsuid"],
        product_code=data["productCode"],
        title=soup.find("h1").text,
        region=EU,
        platform=PLATFORMS[platform],
    )

    # Genres
    game.genres = list(map(lambda g: g.strip(), _sibling(soup, string="Categories").split(",")))
    game.genres.sort()

    # Languages
    game.languages = _sibling(soup, string="Languages").split(",")
    game.languages.sort()

    # Players
    try:
        text = _sibling(soup, "Players")
        game.players = max(map(int, text.split(" - ")))
    except ValueError:
        game.players = 0

    # Release date
    try:
        release_date = data["releaseDate"]
        game.release_date = datetime.strptime(release_date, '%d/%m/%Y')
    except ValueError:
        pass

    # Game size (in MBs)
    game.size, unit = _sibling(soup, "Download size").split(" ")
    game.size = round(float(game.size))

    # Other properties
    features = _sibling(soup, string="Features")

    game.amiibo = "amiibo" in features
    game.demo = "Demo available" in features
    game.description = soup.find("div", class_="col-xs-12 content").text.strip()
    game.developer = _sibling(soup, "Developer")
    game.dlc = "Downloadable content" in features
    game.free_to_play = "\"offdeviceProductPrice\": \"0.0\"" in response.text
    game.iaps = "Offers in-game purchases" in response.text
    game.local_multiplayer = "Local multiplayer" in features
    game.online_play = "Paid online membership service" in features
    game.publisher = _sibling(soup, "Publisher")
    game.save_data_cloud = "Save Data Cloud" in features
    game.voice_chat = "Voice Chat" in features

    # Unknown
    game.game_vouchers = None

    return game


def game_info(nsuid: str) -> Game:
    url = DETAIL_URL.format(nsuid=nsuid)

    print(f"Getting info of game from {url}")
    return _scrap(url)