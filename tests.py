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
from unittest import mock
from unittest.mock import patch
import unittest
import caylusMC
import module_Player

class MyTest(unittest.TestCase):
    #FAIL
    def test_Money_singleton(self):
        mr = caylusMC.module_Resource.MoneyResource("Gold", 2)
        m = caylusMC.module_Resource.Money(mr, 1)
        self.assertEqual(m.money, "Gold")

    def test_ordinal_number(self):
        self.assertEqual(caylusMC.ordinal_number(1), "1st")
        self.assertEqual(caylusMC.ordinal_number(2), "2nd")
        self.assertEqual(caylusMC.ordinal_number(3), "3rd")
        self.assertEqual(caylusMC.ordinal_number(4), "4th")
        self.assertEqual(caylusMC.ordinal_number(11), "11st")
        self.assertEqual(caylusMC.ordinal_number(12), "12nd")
        self.assertEqual(caylusMC.ordinal_number(13), "13rd")
        self.assertEqual(caylusMC.ordinal_number(14), "14th")
        with self.assertRaises(Exception) as context:
            caylusMC.ordinal_number(0)
        self.assertTrue('The ordinal number is not defined for non-positive integers.' in str(context.exception))
        with self.assertRaises(Exception) as context:
            caylusMC.ordinal_number(-1)
        self.assertTrue('The ordinal number is not defined for non-positive integers.' in str(context.exception))

    #ERROR
    def test_resource_all_payments(self):
        # E.g.: current_money_resources = 3F,2W,3S,3G and resource_costs = -1F,-3W,(S),-1G requires resource_payments = -1F,-2W,-0S,-1G-1G.
        resource_costs = list()
        resource_all_payments = list()
        #resource_costs.keys()
        self.assertEqual(module_Player.Player.resource_all_payments(resource_costs,resource_costs), resource_all_payments)
        # E.g.: current_money_resources = 3F,2W,3S,3G and resource_costs = -1any,(F),-1W,(S),(G) requires resource_payments = -1F,-1W,-0S,-0G or -0F,-2W,-0S,-0G or -0F,-1W,-1S,-0G (but not -0F,-1W,-0S,-1G).
        resource_costs = list()
        resource_all_payments = list()
        self.assertEqual(module_Player.Player.resource_all_payments(resource_costs), resource_all_payments)

    #ERROR
    def test_remove_tokens_castle(self):
        players = list("red","blue=basic")
        caylusMC.__init__(GameElement.gm, Version.v, players)
        caylusMC.setup()
        self.assertEqual(caylusMC.Game.remove_tokens_castle(0,2))
        self.assertEqual(caylusMC.Game.remove_tokens_castle(1,3))
        self.assertEqual(caylusMC.Game.remove_tokens_castle(4,4))

    def test_choose_n_provost_movement(self):
        mock.builtins.input = lambda _: "-1"
        original_input = mock.builtins.input
        self.assertEqual(module_Player.HumanPlayer.choose_n_provost_movement(module_Player.HumanPlayer,0, 3), TRUE)
        mock.builtins.input = original_input
        self.assertEqual(mock_stdout.getvalue(),'Please:')
        mock.builtins.input = lambda _: "4"
        self.assertEqual(mock_stdout.getvalue(), 'Please:')
        mock.builtins.input = lambda _: "2"
        self.assertEqual(module_Player.HumanPlayer.choose_n_provost_movement(module_Player.HumanPlayer, 0, 3), TRUE)

if __name__ == '__main__':
    print("hello")
    unittest.main()