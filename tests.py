#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Sep. 4 18:29:00 2018
All elements required to play to the game Caylus Magna Carta.
@author: Olivier
"""

# Remark: in order to simplify this code, attributes (e.g. Castle.n_castle_tokens,
# SmallProductionPlayerBuilding.n_cubes_into_area, GameElement.n_all_except_last_neutral_buildings) depending on
# the number of players in the game are created as [None .. None, value(n_min_players) .. value(n_max_players)]
# and so are indexed by player numbers in the game.


import abc
import collections
import itertools
import random
import sys
import xml.etree.ElementTree as ET
from enum import Enum, unique
from os import path
import unittest
import caylusMC

class MyTest(unittest.TestCase):
    def test_is_even(self):
        mr = caylusMC.MoneyResource("Gold", 2)
        m = caylusMC.Money(mr, 1)
        self.assertEqual(m.money, "Gold")

if __name__ == '__main__':
    unittest.main()