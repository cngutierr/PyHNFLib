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
                       .get_hnf_instance()
        TerroristHNF.display_hnf()
        
        self.assertTrue(TerroristHNF.HNFName == "Terrorist Example",
                                                "Unable to Parse name")

        
    def __test_HNFCreator_DesertStorm(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        DesertStormHNF = HNF.HNFFactory("../../config/DesertStormSettings").get_hnf_instance()
        DesertStormHNF.display_hnf()
        self.assertTrue(DesertStormHNF.HNFName == "Desert Storm Example",
                        "Unable to Parse name")
        print DesertStormHNF.calc_nems_expected_util("3x3 Subgame")
        print DesertStormHNF.calc_nems_expected_util("6x6 Subgame")

    def __test_HNFCreator_exp9(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        exp9HNF = HNF.HNFFactory("../../config/exp9").get_hnf_instance()
        exp9HNF.display_hnf()

        print exp9HNF.calc_nems_expected_util("C1")
        print exp9HNF.calc_nems_expected_util("C0")



    def __test_HNFCreator_exp512(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        exp512HNF = HNF.HNFFactory("../../config/exp512").get_hnf_instance()
        exp512HNF.set_uncertainty(0.2)
        exp512HNF.display_hnf()



    def __test_HNFCreator_SimpleOPM(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        DesertStormHNF = HNF.HNFFactory("../../config/SimpleOPM").get_hnf_instance()
        DesertStormHNF.display_hnf()
        self.assertTrue(DesertStormHNF.HNFName == "Simple OPM Example",
                        "Unable to Parse name")
        DesertStormHNF.gambitGames

    def test_HNFCreator_CreditCard(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        CreditCardHNF = HNF.HNFFactory("../../config/SimpleCreditCard").get_hnf_instance()
        CreditCardHNF.set_uncertainty(0.1)

        CreditCardHNF.display_hnf()
        self.assertTrue(CreditCardHNF.HNFName == "Simple Credit Card Example",
                        "Unable to Parse name")
        print CreditCardHNF.calc_nems_expected_util("Naive Attacker")
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()