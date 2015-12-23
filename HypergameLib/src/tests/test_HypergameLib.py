'''
Created on Nov 1, 2015

@author: krix
'''
import unittest
import gambit
from HypergameLib import HNF

class Test(unittest.TestCase):

    def test_HNFCreator_TerroristExample(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        TerroristHNF = HNF.HNFFactory("../../config/configExample")\
                       .getHNFInstance()
        TerroristHNF.display_hnf()
        
        self.assertTrue(TerroristHNF.HNFName == "Terrorist Example",
                                                "Unable to Parse name")
        
    def test_HNFCreator_DesertStorm(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        DesertStormHNF = HNF.HNFFactory("../../config/DesertStormSettings").getHNFInstance()
        DesertStormHNF.display_hnf()
        self.assertTrue(DesertStormHNF.HNFName == "Desert Storm Example",
                        "Unable to Parse name")
        DesertStormHNF.gambitGames

        
    def _test_HNF_constructor(self):
        sitName = ["Lone Actor", "Bomber", "Cland. Cell", "Cbt Cell", "Desp. Cell", "Unspe"]
        rowName = ["FFQ", "FFC", "FFQ + P", "FFC + P", "FFC++"]
        columnName = ["Fire","Fire + A", "Fire + B", "Fire++"]
        hg = HNF.HNFInstance(sitName, rowName, columnName)
        
        ffqCost = dict(zip(columnName,[-1, -5, -5, -5]))
        ffcCost = dict(zip(columnName,[-2, -3, -3, -4]))
        ffqpCost = dict(zip(columnName,[-2, -3, -4, -4]))
        ffcpCost = dict(zip(columnName,[-2, -3, -3, -3]))
        ffcppCost = dict(zip(columnName,[-2, -3, -2, -3]))
        hg.set_costs_by_action("FFQ", ffqCost)
        hg.set_costs_by_action("FFC", ffcCost)
        hg.set_costs_by_action("FFQ + P", ffqpCost)
        hg.set_costs_by_action("FFC + P", ffcpCost)
        hg.set_costs_by_action("FFC++", ffcppCost)

        sbFire = dict(zip(sitName,[0.8, 0.1, 0.9, 0.2, 0.0, 0.0]))
        sbFireA = dict(zip(sitName,[0.0, 0.0, 0.1, 0.7, 0.1, 0.0]))
        sbFireB = dict(zip(sitName,[0.2, 0.9, 0.0, 0.05, 0.5, 0.0]))
        sbFirePP = dict(zip(sitName,[0.0, 0.0, 0.0, 0.05, 0.4, 1.0]))
        hg.set_situational_beliefs("Fire", sbFire)
        hg.set_situational_beliefs("Fire + A", sbFireA)
        hg.set_situational_beliefs("Fire + B", sbFireB)
        hg.set_situational_beliefs("Fire++", sbFirePP)

        tmp =dict(zip(sitName,[0.6, 0.1, 0.2, 0.1, 0.0, 0.0]))
        hg.set_current_belief(tmp)
        hg.init_summary_belief()
        hg.situation_expected_utility()
        hg.print_hnf_table()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()