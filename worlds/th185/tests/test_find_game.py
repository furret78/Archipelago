import unittest

import pymem

from worlds.th185.variables.meta_data import FILE_NAME


class FindGameTest(unittest.TestCase):
    pymemprocess = None

    def test_find_game(self):

        while self.pymemprocess is None:
            try:
                self.pymemprocess = pymem.Pymem(process_name=FILE_NAME)
            except Exception as e:
                print(e)
                print("Failed test! Cannot find game. Trying again...")