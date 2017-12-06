'''
Created on Nov 1, 2015

@author: krix
'''
import unittest
from scipy.stats import norm
from HypergameLib import HNF, slice_list
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
        round_cost = list()
        utils_wo_dec = list()
        mo_history = list()
        ws_history = list()
        ps_history = list()
        CreditCardHNF.get_hnf_instance().set_uncertainty(0.5)
        max_range = 100
        for i in range(0, max_range):

            round_num_exfil_suc = CreditCardHNF.const_vars["round_num_exfil_suc"]
            round_cost_exfil = CreditCardHNF.const_vars["round_cost_exfil"]
            #sum(slice_list(round_cost_exfil, round_num_exfil_suc))/round_num_exfil_suc

            print "iter %i, dec_rate = %f, " % (i, CreditCardHNF.settings["Global Const Vars"]["dec_rate"] )
            results = CreditCardHNF.get_hnf_instance().calc_all_results()
            #1. save results
            utils.append(-1.0*CreditCardHNF.const_vars["total_cost"])
            #print results['MO']["Strategy Vector"]
            #print results['WS']["Strategy Vector"]
            #print results['PS']["Strategy Vector"]

            mo_history.append(results['MO']["HEU"])
            ws_history.append(results['WS']["HEU"])
            ps_history.append(results['PS']["HEU"])

            max_heu = max(results['MO']["HEU"], results['WS']["HEU"], results['PS']["HEU"])

            round_cost.append(CreditCardHNF.const_vars["use_dec_cost"])
            utils_wo_dec.append(CreditCardHNF.const_vars["wo_dec_cost"])


            exfil_rate_history.append(CreditCardHNF.const_vars["round_exfil_rate"])
            cost_exfil_history.extend(list(CreditCardHNF.const_vars["round_cost_exfil"]))
            CreditCardHNF.settings["Global Const Vars"]["exfil_rate"] = float(norm.fit(exfil_rate_history)[0])
            CreditCardHNF.settings["Global Const Vars"]["cost_exfil"] = float(norm.fit(cost_exfil_history)[0])

            #if CreditCardHNF.settings["Global Const Vars"]["dec_rate"] < 0.1:
            #    CreditCardHNF.settings["Global Const Vars"]["dec_rate"] *= 1.1

            #if utils_wo_dec[-1] > round_cost[-1]:
            #    update_val = float(utils_wo_dec[-1]/round_cost[-1])

            if np.median(utils_wo_dec) > np.median(round_cost):
                update_val = float(np.median(utils_wo_dec)/np.median(round_cost))

                CreditCardHNF.settings["Global Const Vars"]["dec_rate"] *= update_val + 1.0
                if CreditCardHNF.settings["Global Const Vars"]["dec_rate"] > 0.3:
                    CreditCardHNF.settings["Global Const Vars"]["dec_rate"] = 0.3
                print CreditCardHNF.settings["Global Const Vars"]["dec_rate"]
            #2. recalc the vars
            CreditCardHNF.sample_vars()


        CreditCardHNF.sample_vars()
        inst = CreditCardHNF.get_hnf_instance()
        inst.display_hnf()

        plt.plot(np.arange(0, max_range, 1), utils, label="Round Result")
        plt.plot(np.arange(0.0, max_range, 1), mo_history, label="MO")
        plt.plot(np.arange(0.0, max_range, 1), ws_history, label="WS")
        plt.plot(np.arange(0.0, max_range, 1), ps_history, label="PS")
        plt.plot(np.arange(0.0, max_range, 1), ps_history, label="PS")
        plt.plot( np.arange(0.0, max_range, 1), round_cost, label="RC")
        plt.title("Utility over time")
        plt.xlabel("Round")
        plt.ylabel("Utility")
        plt.legend()
        plt.show()

        plt.plot(np.arange(0, max_range, 1), utils, label="True Damage")
        plt.plot(np.arange(0, max_range, 1), utils_wo_dec, label="Damage WO Deception")
        plt.plot(np.arange(0, max_range, 1), round_cost, label="Damage W Deception")
        plt.title("Utility over time")
        plt.xlabel("Round")
        plt.ylabel("Utility")
        plt.legend()
        plt.show()


        dif = [round_cost[i] - utils_wo_dec[i] for i in range(0, max_range)]
        plt.plot(np.arange(0, max_range, 1), dif, label="Savings Damage")
        plt.title("Savings Per Round")
        plt.xlabel("Round")
        plt.ylabel("Utility")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()