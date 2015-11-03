'''
Created on Nov 1, 2015

@author: krix
'''
import unittest
import HypergameLib

class Test(unittest.TestCase):

    def test_HNFCreator_(self):
        HNFCreator = HypergameLib.HNFCreator("../../config/configExample")
        self.assertTrue(HNFCreator.settings["Name"] == "Terrorist Example", "Unable to Parse Name")
    
    def test_HNFCreator_DesertStorm(self):
        HNFCreator = HypergameLib.HNFCreator("../../config/DesertStormSettings")
        self.assertTrue(HNFCreator.settings["Name"] == "Desert Storm Example", "Unable to Parse Name")
    def test_HNF_constructor(self):
        sitName = ["Lone Actor", "Bomber", "Cland. Cell", "Cbt Cell", "Desp. Cell", "Unspe"]
        rowName = ["FFQ", "FFC", "FFQ + P", "FFC + P", "FFC++"]
        columnName = ["Fire","Fire + A", "Fire + B", "Fire++"]
        hg = HypergameLib.HNF(sitName, rowName, columnName)
        
        ffqCost = dict(zip(columnName,[-1, -5, -5, -5]))
        ffcCost = dict(zip(columnName,[-2, -3, -3, -4]))
        ffqpCost = dict(zip(columnName,[-2, -3, -4, -4]))
        ffcpCost = dict(zip(columnName,[-2, -3, -3, -3]))
        ffcppCost = dict(zip(columnName,[-2, -3, -2, -3]))
        hg.setCosts("FFQ", ffqCost)
        hg.setCosts("FFC", ffcCost)
        hg.setCosts("FFQ + P", ffqpCost)
        hg.setCosts("FFC + P", ffcpCost)
        hg.setCosts("FFC++", ffcppCost)

        sbFire = dict(zip(sitName,[0.8, 0.1, 0.9, 0.2, 0.0, 0.0]))
        sbFireA = dict(zip(sitName,[0.0, 0.0, 0.1, 0.7, 0.1, 0.0]))
        sbFireB = dict(zip(sitName,[0.2, 0.9, 0.0, 0.05, 0.5, 0.0]))
        sbFirePP = dict(zip(sitName,[0.0, 0.0, 0.0, 0.05, 0.4, 1.0]))
        hg.setSituationalBeliefs("Fire", sbFire)
        hg.setSituationalBeliefs("Fire + A", sbFireA)
        hg.setSituationalBeliefs("Fire + B", sbFireB)
        hg.setSituationalBeliefs("Fire++", sbFirePP)
        
        tmp =dict(zip(sitName,[0.6, 0.1, 0.2, 0.1, 0.0, 0.0]))
        hg.setCurrentBelief(tmp)
        hg.calcSummaryBelief()
        hg.calcExpectedUtility()
        hg.printHNFTable()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()