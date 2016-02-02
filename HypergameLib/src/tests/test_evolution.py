'''
Created on Nov 1, 2015

@author: krix
'''
import unittest
from scipy.stats import norm
from HypergameLib import HNF
import matplotlib.pyplot as plt
import numpy as np
class Test(unittest.TestCase):


    def test_HNFCreator_CreditCard(self):
        '''
        DESC
            Display the HNF info created from file
        '''
        CreditCardHNF = HNF.HNFFactory("../../config/SimpleCreditCard")
        utils = list()
        exfil_rate_history = list()
        cost_exfil_history = list()

        for i in range(0, 100):
            print i
            #1. save results
            utils.append(-1.0*CreditCardHNF.const_vars["total_cost"])
            exfil_rate_history.append(CreditCardHNF.const_vars["round_exfil_rate"])
            cost_exfil_history.extend(list(CreditCardHNF.const_vars["round_cost_exfil"]))
            CreditCardHNF.settings["Global Const Vars"]["exfil_rate"] = float(norm.fit(exfil_rate_history)[0])
            CreditCardHNF.settings["Global Const Vars"]["cost_exfil"] = float(norm.fit(cost_exfil_history)[0])
            if CreditCardHNF.settings["Global Const Vars"]["dec_rate"] < 0.75:
                CreditCardHNF.settings["Global Const Vars"]["dec_rate"] *= 1.10
            #2. recalc the vars
            CreditCardHNF.sample_vars()
        print utils
        plt.plot(np.arange(0, 100, 1), utils)
        plt.show()
        print norm.fit(exfil_rate_history)
        print norm.fit(cost_exfil_history)
        CreditCardHNF.sample_vars()
        inst = CreditCardHNF.get_hnf_instance()
        inst.set_uncertainty(0.2)
        inst.display_hnf()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()