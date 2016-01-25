'''
Created on Nov 1, 2015

@author: krix
'''
import unittest
import gambit
from HypergameLib import HNF

class Test(unittest.TestCase):

    def __test_HNFCreator_TerroristExample(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        TerroristHNF = HNF.HNFFactory("../../config/terroristSettings")\
                       .getHNFInstance()
        TerroristHNF.display_hnf()
        
        self.assertTrue(TerroristHNF.HNFName == "Terrorist Example",
                                                "Unable to Parse name")
        
    def __test_HNFCreator_DesertStorm(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        DesertStormHNF = HNF.HNFFactory("../../config/DesertStormSettings").getHNFInstance()
        DesertStormHNF.display_hnf()
        self.assertTrue(DesertStormHNF.HNFName == "Desert Storm Example",
                        "Unable to Parse name")
        DesertStormHNF.gambitGames

    def __test_HNFCreator_SimpleOPM(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        DesertStormHNF = HNF.HNFFactory("../../config/SimpleOPM").getHNFInstance()
        DesertStormHNF.display_hnf()
        self.assertTrue(DesertStormHNF.HNFName == "Simple OPM Example",
                        "Unable to Parse name")
        DesertStormHNF.gambitGames

    def test_HNFCreator_CreditCard(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        CreditCardHNF = HNF.HNFFactory("../../config/SimpleCreditCard").getHNFInstance()
        CreditCardHNF.display_hnf()
        self.assertTrue(CreditCardHNF.HNFName == "Simple Credit Card Example",
                        "Unable to Parse name")
        CreditCardHNF.gambitGames
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()