from unittest import TestCase

from nintendeals import noe
from nintendeals.commons.enumerates import Platforms, Regions

LIMIT = 20


class TestListing(TestCase):

    def test_list_3ds_games(self):
        for index, game in enumerate(noe.list_3ds_games()):
            if index > LIMIT:
                break

            self.assertEqual(game.platform, Platforms.NINTENDO_3DS)
            self.assertEqual(game.region, Regions.EU)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("500"))

    def test_list_switch_games(self):
        for index, game in enumerate(noe.list_switch_games()):
            if index > LIMIT:
                break

            self.assertEqual(game.platform, Platforms.NINTENDO_SWITCH)
            self.assertEqual(game.region, Regions.EU)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("700"))

    def test_list_wiiu_games(self):
        for index, game in enumerate(noe.list_wiiu_games()):
            if index > LIMIT:
                break

            self.assertEqual(game.platform, Platforms.NINTENDO_WIIU)
            self.assertEqual(game.region, Regions.EU)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("200"))
