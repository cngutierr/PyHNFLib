import unittest
import gambit

from HypergameLib import HNF


class MyTestCase(unittest.TestCase):
    def test_DesertStorm_hardcoded(self):
        """
        Hand crafted test for Desert Storm Example.
        :return:
        """
        print "DESERT STORM EXAMPLE"
        g = gambit.Game.new_table([6, 6])
        g.title = "Desert Storm Hypergame"
        g.players[0].label = "Attacker"
        g.players[1].label = "Defender"
        g.players[0].strategies[0].label = "Attack"
        g.players[0].strategies[1].label = "Attack Right"
        g.players[0].strategies[2].label = "Attack Left"
        g.players[0].strategies[3].label = "Env. Left"
        g.players[0].strategies[4].label = "Inv. Beach"
        g.players[0].strategies[5].label = "Env. Vert"

        g.players[1].strategies[0].label = "Defend"
        g.players[1].strategies[1].label = "Defend Left"
        g.players[1].strategies[2].label = "Defend Right"
        g.players[1].strategies[3].label = "W/ Res"
        g.players[1].strategies[4].label = "Screen"
        g.players[1].strategies[5].label = "Counter Attack"

        g[0, 0][0] = -1
        g[1, 0][0] = -1
        g[2, 0][0] = -1
        g[3, 0][0] = 3
        g[4, 0][0] = 1
        g[5, 0][0] = 2

        g[0, 0][1] = 1
        g[1, 0][1] = 1
        g[2, 0][1] = 1
        g[3, 0][1] = -3
        g[4, 0][1] = -1
        g[5, 0][1] = -2

        g[0, 1][0] = -1
        g[1, 1][0] = -3
        g[2, 1][0] = 0
        g[3, 1][0] = 5
        g[4, 1][0] = -3
        g[5, 1][0] = 0

        g[0, 1][1] = 1
        g[1, 1][1] = 3
        g[2, 1][1] = 0
        g[3, 1][1] = -5
        g[4, 1][1] = 3
        g[5, 1][1] = 0

        g[0, 2][0] = -1
        g[1, 2][0] = 0
        g[2, 2][0] = -3
        g[3, 2][0] = 1
        g[4, 2][0] = 2
        g[5, 2][0] = 0

        g[0, 2][1] = 1
        g[1, 2][1] = 0
        g[2, 2][1] = 3
        g[3, 2][1] = -1
        g[4, 2][1] = -2
        g[5, 2][1] = 0

        g[0, 3][0] = 1
        g[1, 3][0] = 1
        g[2, 3][0] = 1
        g[3, 3][0] = 2
        g[4, 3][0] = -1
        g[5, 3][0] = -3

        g[0, 3][1] = -1
        g[1, 3][1] = -1
        g[2, 3][1] = -1
        g[3, 3][1] = -2
        g[4, 3][1] = 1
        g[5, 3][1] = 3

        g[0, 4][0] = 1
        g[1, 4][0] = 1
        g[2, 4][0] = 1
        g[3, 4][0] = -1
        g[4, 4][0] = -1
        g[5, 4][0] = -2

        g[0, 4][1] = -1
        g[1, 4][1] = -1
        g[2, 4][1] = -1
        g[3, 4][1] = 1
        g[4, 4][1] = 1
        g[5, 4][1] = 2

        g[0, 5][0] = 4
        g[1, 5][0] = 1
        g[2, 5][0] = 1
        g[3, 5][0] = -2
        g[4, 5][0] = -2
        g[5, 5][0] = -1

        g[0, 5][1] = -4
        g[1, 5][1] = -1
        g[2, 5][1] = -1
        g[3, 5][1] = 2
        g[4, 5][1] = 2
        g[5, 5][1] = 1
        print "solver"
        solver = gambit.nash.ExternalLogitSolver()
        s = solver.solve(g)
        print s
        self.assertAlmostEqual(s[0][0], 0.1250004426696509, places=20, msg="NEMS did not match")
        self.assertAlmostEqual(s[0][1], 0.49999948506171976, places=20, msg="NEMS did not match")
        self.assertAlmostEqual(s[0][3], 0.37500007226862936, places=20, msg="NEMS did not match")

    def test_simpleOPM(self):
        """
        DESC
            Display the HNF info created from file
        """
        simple_opm = HNF.HNFFactory("../../config/SimpleOPM").getHNFInstance()
        simple_opm.display_hnf()
        for i, game in enumerate(simple_opm.gambitGames.values()):
            self.assertEqual(game.players[0].label, "Row Player", "Labels are incorrect")
            self.assertEqual(game.players[1].label, "Column Player", "Labels are incorrect")

            # get all the names of the strategies/actions
            actions_in_gambit = [i.label for i in game.strategies]

            # check that the actions in HNF and gambit match
            for rowAction in simple_opm.rowActionNames:
                self.assertTrue(rowAction in actions_in_gambit,
                                "Row action not found in gambit game")
            #for columnAction in simple_opm.columnActionNames:
            #    self.assertTrue(columnAction in actions_in_gambit,
            #                    "Column action not found in gambit game")

            #for col_ind, colName in enumerate(simple_opm.columnActionNames):
            #    for row_ind, rowName in enumerate(simple_opm.rowActionNames):
            #        self.assertEqual(float(game[row_ind, col_ind][0]), simple_opm.costs[colName][rowName])

            print "Calc the NEMS"
            solver = gambit.nash.ExternalLogitSolver()
            s = solver.solve(game)
            print s
            pass

    def test_DesertStorm(self):
        """
        DESC
            Display the HNF info created from file
        """
        DesertStormHNF = HNF.HNFFactory("../../config/DesertStormSettings").getHNFInstance()
        DesertStormHNF.display_hnf()
        for i, game in enumerate(DesertStormHNF.gambitGames.values()):
            self.assertEqual(game.players[0].label, "Row Player", "Labels are incorrect")
            self.assertEqual(game.players[1].label, "Column Player", "Labels are incorrect")

            # get all the names of the strategies/actions
            actions_in_gambit = [i.label for i in game.strategies]

            # check that the actions in HNF and gambit match
            for rowAction in DesertStormHNF.rowActionNames:
                self.assertTrue(rowAction in actions_in_gambit,
                                "Row action not found in gambit game")
            for columnAction in DesertStormHNF.columnActionNames:
                self.assertTrue(columnAction in actions_in_gambit,
                                "Column action not found in gambit game")

            for col_ind, colName in enumerate(DesertStormHNF.columnActionNames):
                for row_ind, rowName in enumerate(DesertStormHNF.rowActionNames):
                    self.assertEqual(float(game[row_ind, col_ind][0]), DesertStormHNF.costs_row[colName][rowName])

            print "Calc the NEMS"
            solver = gambit.nash.ExternalLogitSolver()
            s = solver.solve(game)
            self.assertAlmostEqual(s[0][0], 0.125, 3, msg="NEMS does not match expectation")
            self.assertAlmostEqual(s[0][1], 0.5, 1, msg="NEMS does not match expectation")
            self.assertAlmostEqual(s[0][2], 0.0, 1, msg="NEMS does not match expectation")
            self.assertAlmostEqual(s[0][3], 0.375, 3, msg="NEMS does not match expectation")
            pass

if __name__ == '__main__':
    unittest.main()
