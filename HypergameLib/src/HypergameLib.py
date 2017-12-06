"""
Created on Oct 31, 2015

@author: Christopher Gutierrez
"""
import gambit
import pandas as pd
import texttable as tt
import yaml
import numpy as np
import matplotlib.pyplot as plt
from simpleeval import simple_eval
from scipy.stats import hypergeom, norm
import time
from copy import deepcopy
def slice_list(list, range):
    return list[0:range]

def sample_hg_til_caught(M, n, N):
    count = 0
    for i in range(0, int(N)):
        if hypergeom.rvs(M, n, 1) == 0:
            return count
        else:
            M -= 1
            n -= 1
            count += 1
    return count


class HNF(object):
    class Consts(object):
        # constants found in config file
        SIT_NAMES = "Situation Names"
        ROW_ACT_NAMES = "Row Action Names"
        COL_ACT_NAMES = "Column Action Names"
        NAME = "Name"
        ROW_BELIEF = "Row Belief"
        ROW_ACTION = "Row Action"
        ROW_ACTION_COST = "Row Action Cost"
        COST_COL_ACTIONS = "Cost for Column Actions"
        SIT_NAME = "Situation Name"
        BELIEF_COL_ACTIONS = "Belief for Column Action"
        CUR_BELIEF = "Current Belief"
        ROW_ACT_NAME = "rowActionName"
        ROW_COST = "row_cost"
        COL_COST = "col_cost"
        EU = "EU"
        GLOBAL_CONST_VARS = "Global Const Vars"
        GLOBAL_RAND_VARS = "Global Random Vars"
        GLOBAL_STO_VARS = "Stochastic Column Player"
        GLOBAL_STO_RAND_VARS = "Random Vars"
        GLOBAL_STO_UPDATE_VARS = "Update Vars"
        GLOBAL_STO_RESULT_VARS = "Result Vars"
        GLOBAL_RAND_VARS_TYPE = "type"
        GLOBAL_RAND_VARS_STRING = "string"
        GLOBAL_RAND_VARS_PARAMS = "params"

        SUPPORTED_FUNCS = {"hypergeom_cdf": hypergeom.cdf, "hypergeom_rvs": hypergeom.rvs, "norm_rvs": norm.rvs, \
                           "sum": sum, "slice_list": slice_list, "sample_hg_til_caught": sample_hg_til_caught}
        HYPERSTRATS = ["MO", "PS", "WS", "NEMS"]

    class HNFFactory(object):
        """
        DESC
            Creates an HNFInstance from source
        """

        def __init__(self, settings_file_name):
            """
            DESC
                Creates an HNF object based on the settings file given.
            INPUT
                settings_file_name (str) - A string that points to a file that contains
                   the settings information
            """
            with open(settings_file_name, 'r') as f:
                # load config file
                self.settings = yaml.load(f)
                np.random.seed(seed=int(10000 * time.time() % 100000))
                # get key values
                self.sit_names = self.settings[HNF.Consts.SIT_NAMES]
                self.row_action_names = self.settings[HNF.Consts.ROW_ACT_NAMES]
                self.column_action_names = self.settings[HNF.Consts.COL_ACT_NAMES]
                self.name = self.settings[HNF.Consts.NAME]

                # set the global vars
                if HNF.Consts.GLOBAL_CONST_VARS in self.settings:
                    self.__init_const_vars()
                else:
                    self.const_vars = {}

                if HNF.Consts.GLOBAL_RAND_VARS in self.settings:
                    self.__init_rand_vars()
                else:
                    self.rand_vars = {}

                if HNF.Consts.GLOBAL_STO_VARS in self.settings:
                    # Stochastic column player
                    self.__init_sto_vars()
                else:
                    self.sto_vars = {}

                # init HNG object
                self.HNFOut = HNF.HNFInstance(self.sit_names, self.row_action_names,
                                              self.column_action_names, self.name)

                # set the values found in the settings
                self.__init_from_file()

                # calc the summary and expected utility
                self.HNFOut.init_summary_belief()

                # setup the output stuff
                # self.HNFOut.situation_expected_utility()
                # self.HNFOut.calc_hypergame_expected_utility()
                # self.HNFOut.calc_modeling_opponent_utility()

        def __init_const_vars(self):
            self.const_vars = deepcopy(self.settings[HNF.Consts.GLOBAL_CONST_VARS])
            self.__verify_const_vars()

        def __init_rand_vars(self):
                self.rand_vars = deepcopy(self.settings[HNF.Consts.GLOBAL_RAND_VARS])
                self.__create_const_var_from_random_var(self.rand_vars)

        def __init_sto_vars(self):
            self.sto_vars = deepcopy(self.settings[HNF.Consts.GLOBAL_STO_VARS])
            self.__create_stochastic_column_player_vars()

        def __reset_rand_vars(self):
            self.const_vars.clear()
            self.rand_vars.clear()
            self.sto_vars.clear()

        def sample_vars(self):
            self.__reset_rand_vars()
            self.__init_const_vars()
            self.__init_rand_vars()
            self.__init_sto_vars()
            self.HNFOut = HNF.HNFInstance(self.sit_names, self.row_action_names,
                                          self.column_action_names, self.name)
            self.__init_from_file()
            self.HNFOut.init_summary_belief()

        def get_hnf_instance(self):
            return self.HNFOut

        def __init_from_file(self):
            """
            DESC: extracts all the settings found in the config file and inits
                the HNF object.
            """
            self.__set_costs()
            self.__set_beliefs()
            self.__set_current_belief()

            # Gambit games -- each belief context will be modeled as a sep gambit game
            for situation in self.HNFOut.situationNames:
                self.HNFOut.append_gambit_game(situation)

        def __set_costs(self):
            """
            DESC: extracts cost from settings file and sets the cost in the HNF
            """
            # extract cost info from settings
            cost_rows_row_player = deepcopy(map(lambda r: {HNF.Consts.ROW_ACTION:
                                                      r[HNF.Consts.ROW_ACTION],
                                                  HNF.Consts.COST_COL_ACTIONS:
                                                      r[HNF.Consts.COST_COL_ACTIONS]},
                                       self.settings[HNF.Consts.ROW_ACTION_COST]))

            # set cost values
            for costRow in cost_rows_row_player:
                for action in costRow[HNF.Consts.COST_COL_ACTIONS]:
                    cost = costRow[HNF.Consts.COST_COL_ACTIONS][action][HNF.Consts.ROW_COST]
                    costRow[HNF.Consts.COST_COL_ACTIONS][action][HNF.Consts.ROW_COST] = simple_eval(str(cost),
                                                                                                names=self.const_vars)
                    cost = costRow[HNF.Consts.COST_COL_ACTIONS][action][HNF.Consts.COL_COST]
                    costRow[HNF.Consts.COST_COL_ACTIONS][action][HNF.Consts.COL_COST] = simple_eval(str(cost),
                                                                                                    names=self.const_vars)

                self.HNFOut.set_costs_by_action(costRow[HNF.Consts.ROW_ACTION],
                                                costRow[HNF.Consts.COST_COL_ACTIONS],
                                                actor="row")
                self.HNFOut.set_costs_by_action(costRow[HNF.Consts.ROW_ACTION],
                                                costRow[HNF.Consts.COST_COL_ACTIONS],
                                                actor="column")

        def __set_beliefs(self):
            """
            DESC: extracts the beliefs from settings file and sets the belief in the HNF
            """
            # extract the belief values from settings
            belief_rows = map(lambda r: {HNF.Consts.SIT_NAME: r[HNF.Consts.SIT_NAME],
                                         HNF.Consts.BELIEF_COL_ACTIONS: r[HNF.Consts.BELIEF_COL_ACTIONS]},
                              self.settings[HNF.Consts.ROW_BELIEF])
            # set belief values
            for beliefRow in belief_rows:
                self.HNFOut.set_situational_beliefs(beliefRow[HNF.Consts.SIT_NAME],
                                                    beliefRow[HNF.Consts.BELIEF_COL_ACTIONS])

        def __set_current_belief(self):
            """
            DESC: Extracts the current belief from file and sets the current belief.
            """
            # extract current belief from settings
            current_beliefs = dict(map(lambda r: (r[HNF.Consts.SIT_NAME], r[HNF.Consts.CUR_BELIEF]),
                                       self.settings[HNF.Consts.ROW_BELIEF]))
            # set current beliefs
            self.HNFOut.set_current_belief(current_beliefs)

        def __create_const_var_from_random_var(self, in_dictionary):
            """
            Initialize any random variable and set it in the const_var
            :return:
            """
            for rand_var_key in in_dictionary.keys():
                # make sure that the correct keys are in available
                assert HNF.Consts.GLOBAL_RAND_VARS_TYPE in \
                       in_dictionary[rand_var_key].keys() and \
                       HNF.Consts.GLOBAL_RAND_VARS_PARAMS in \
                       in_dictionary[rand_var_key].keys()

                # verify correct rand type
                assert in_dictionary[rand_var_key][HNF.Consts.GLOBAL_RAND_VARS_TYPE] in \
                       HNF.Consts.SUPPORTED_FUNCS

                # 1. replace the params vals with global constants
                for param in in_dictionary[rand_var_key][HNF.Consts.GLOBAL_RAND_VARS_PARAMS].keys():
                    param_val = in_dictionary[rand_var_key][HNF.Consts.GLOBAL_RAND_VARS_PARAMS][param]
                    in_dictionary[rand_var_key][HNF.Consts.GLOBAL_RAND_VARS_PARAMS][param] \
                        = simple_eval(str(param_val), names=self.const_vars)
                # 2. evaluate the "string" in global random vars
                rand_var_type = in_dictionary[rand_var_key][HNF.Consts.GLOBAL_RAND_VARS_TYPE]
                rand_var_str = in_dictionary[rand_var_key][HNF.Consts.GLOBAL_RAND_VARS_STRING]
                rand_var_params = in_dictionary[rand_var_key][HNF.Consts.GLOBAL_RAND_VARS_PARAMS]

                # 3. store the calculated value into const_vars
                self.const_vars[rand_var_key] = simple_eval(str(rand_var_str),
                                                            names=rand_var_params,
                                                            functions=HNF.Consts.SUPPORTED_FUNCS)
                #print self.const_vars[rand_var_key]

        def __create_stochastic_column_player_vars(self):
            """
            determine the actions of a stochastic column player and generate
            outcomes
            :return:
            """
            # 1. Calc Rand Vars
            for rand_var_key in self.sto_vars[HNF.Consts.GLOBAL_STO_RAND_VARS].keys():
                rand_var_str = self.sto_vars[HNF.Consts.GLOBAL_STO_RAND_VARS][rand_var_key][HNF.Consts.GLOBAL_RAND_VARS_STRING]
                rand_var_params = self.sto_vars[HNF.Consts.GLOBAL_STO_RAND_VARS][rand_var_key][HNF.Consts.GLOBAL_RAND_VARS_PARAMS]
                self.const_vars[rand_var_key] = simple_eval(str(rand_var_str),
                                                            names=rand_var_params,
                                                            functions=HNF.Consts.SUPPORTED_FUNCS)

            # 2. Calc Update Vars
            self.__create_const_var_from_random_var(self.sto_vars[HNF.Consts.GLOBAL_STO_UPDATE_VARS])

            # 3. Calc result vars
            self.__create_const_var_from_random_var(self.sto_vars[HNF.Consts.GLOBAL_STO_RESULT_VARS])

            #print self.const_vars

        def __verify_const_vars(self):
            for const_key in self.const_vars:
                assert type(self.const_vars[const_key]) is float
            pass

    class HNFInstance(object):
        """
        Hypergame Normal Form Class
        Should contain the following
        A belief context matrix
        A payoff matrix
        A situational belief matrix
        """

        # round the the nearest thousandth deceimal place
        ROUND_DEC = 5

        def __init__(self, situationNames, rowActionNames, columnActionNames, \
                     name="", uncertainty=0.0):
            """
            DESC: Create the index names and init the cost and situatational belief mats
            Input:
                   sutiationNames (list) - A list strings. Each item is the name of
                      a situation in the HNF
                   rowActionNames (list) - A list of strings. Each item is the name
                      of the actions that the row player can make
                   columnActionNames (list) - A list of strings. Each item is the
                      name of an action that the column player can make.
            """
            # make sure the inputs are list
            assert type(situationNames) is list and \
                   type(rowActionNames) is list and \
                   type(columnActionNames) is list

            assert len(situationNames) > 0 and len(rowActionNames) > 0 and \
                   len(columnActionNames) > 0

            # make sure that the names of each key is different
            assert len(situationNames) + len(rowActionNames) + \
                   len(columnActionNames) == len(set(situationNames)) + \
                                             len(set(rowActionNames)) + \
                                             len(set(columnActionNames))

            # save the names. To be used as keys in mats and vectors
            self.situationNames = situationNames
            self.rowActionNames = rowActionNames
            self.columnActionNames = columnActionNames

            # init the mats
            self.costs_row = pd.DataFrame(index=rowActionNames,
                                          columns=columnActionNames)

            self.costs_column = pd.DataFrame(index=rowActionNames,
                                             columns=columnActionNames)

            self.situationalBeliefs = pd.DataFrame(index=situationNames,
                                                   columns=columnActionNames)

            # set the current to be uniformly likely
            self.currentBelief = dict.fromkeys(situationNames, 1.0 / float(len(situationNames)))

            # init summary belief to all zeros
            self.summaryBeliefs = dict.fromkeys(columnActionNames, 0.0)

            # set gambit object
            self.gambitGames = dict()

            # init constants
            self.HNFName = name
            self.uncertainty = uncertainty

        def set_current_belief(self, updated_current_belief_dict):
            """
            DESC:
                Set the current belief values.
            INPUT:
                updatedCurrentBeilefDict (dict) - a dictionary with keys equal to
                situation name and values summing up to 1.
                :param updated_current_belief_dict:
            """
            assert type(updated_current_belief_dict) is dict
            assert set(updated_current_belief_dict.keys()) == set(self.situationNames)
            assert 0.99 <= sum(updated_current_belief_dict.values()) <= 1.0

            for key in updated_current_belief_dict.keys():
                self.currentBelief[key] = updated_current_belief_dict[key]

        def set_costs_by_action(self, action_name, updated_dict, actor="row"):
            """
            DESC:
                Set the cost for a given action. The action can be either a row or a
                column action.
            INPUT:
                :param action_name: the action name to be updated.
                :param updated_dict: a dictionary with updated values. The keys must
                                     must be row or column action names and the values
                                     should be the costs
                :param actor : must be either "row" or "column"
            """
            assert type(updated_dict) is dict
            assert action_name in self.rowActionNames or action_name in self.columnActionNames
            assert actor is "row" or actor is "column"
            if action_name in self.rowActionNames:
                # Update a defenders cost row
                for k in updated_dict.keys():
                    if actor == "row":
                        self.costs_row.loc[action_name][k] = updated_dict[k][HNF.Consts.ROW_COST]
                    elif actor == "column":
                        self.costs_column.loc[action_name][k] = updated_dict[k][HNF.Consts.COL_COST]

            elif action_name in self.columnActionNames:
                # Update a column
                for k in updated_dict.keys():
                    if actor == "row":
                        self.costs_row[action_name][k] = updated_dict[k][HNF.Consts.ROW_COST]
                    elif actor == "column":
                        self.costs_column[action_name][k] = updated_dict[k][HNF.Consts.COL_COST]

        def set_situational_beliefs(self, name, updatedDict):
            """
            DESC:
                Set the situational beliefs for a given situation name or column
                action name.
            INPUT:
                name (str) - the name of the situation or the name of the row action
                    to be updated.
                updateDict (dict) - a dictionary with the updated values. The keys
                    must be row situation names or column action names and the values
                    should be the probabilities.
                    :param name:
                    :param updatedDict:
            """
            assert type(updatedDict) is dict
            assert name in self.situationNames or name in self.columnActionNames

            if name in self.situationNames:
                for k in updatedDict.keys():
                    self.situationalBeliefs.loc[name][k] = updatedDict[k]
            elif name in self.columnActionNames:
                for k in updatedDict.keys():
                    self.situationalBeliefs[name][k] = updatedDict[k]

        def set_uncertainty(self, uncertainty):
            """
            DESC
                Set the uncertainty value (duh)
                :param uncertainty:
            """
            self.uncertainty = uncertainty

        def init_summary_belief(self):
            """
            DESC
                Calculate the summary belief from Current Belief and Situational
                Beliefs.
            """
            # asset that all the values are in place
            self.__verify_situational_beliefs()
            self.__verify_current_beliefs()

            for columnActionName in self.columnActionNames:
                tmp_sum = 0.0
                for situationName in self.situationNames:
                    if self.situationalBeliefs[columnActionName][situationName] != "X":
                        tmp_sum += self.currentBelief[situationName] * \
                                   self.situationalBeliefs[columnActionName][situationName]
                self.summaryBeliefs[columnActionName] = round(tmp_sum, self.ROUND_DEC)

            # make the summary belief is valid
            self.__verify_summary_belief()

        def calc_expected_values(self, sit_name=""):
            """
            DESC
                calculate the expected utility. Summary belief, current belief,
                and situational beliefs must all be set before calling this func
            """
            self.__verify_summary_belief()
            self.__verify_current_beliefs()
            self.__verify_situational_beliefs()

            expected_values = dict.fromkeys(self.rowActionNames, 0.0)
            for rowActionName in self.rowActionNames:
                tmp_sum = 0.0
                for columnActionName in self.columnActionNames:
                    if sit_name == "":
                        tmp_sum += self.summaryBeliefs[columnActionName] * \
                                   self.costs_row[columnActionName][rowActionName]
                    else:
                        if self.situationalBeliefs[columnActionName][sit_name] != "X":
                            tmp_sum += self.situationalBeliefs[columnActionName][sit_name] * \
                                       self.costs_row[columnActionName][rowActionName]

                expected_values[rowActionName] = round(tmp_sum, self.ROUND_DEC)
            return expected_values

        def calc_expected_utility(self, expected_values, hyperstrat):
            """
            calculates EU from the expected values.
            :param expected_values:  a dictionary of expected values for each action
            :param hyperstrat: a dictionary containing the prob. using a particular action
            :return:
            """
            out_sum = 0.0
            for rowActionName in self.rowActionNames:
                out_sum += hyperstrat[rowActionName] * expected_values[rowActionName]
            return out_sum

        def calc_g(self, hyperstrat):
            """
            Return the value of the worst action for the given hyperstrategy
            :param hyperstrat: A dictionary for a hyperstrategy
            :return:
            """
            worst = {}
            for rowActionName in self.rowActionNames:
                worst[rowActionName] = hyperstrat[rowActionName] * self.__get_worst_case_action(rowActionName)
            return min(worst.values())

        def calc_heu(self, eu, g):
            """
            Calculate the Hypergame Expected Utility
            :param eu: The expected value
            :param g: The worst action value
            :return: the Hypergame Expected Utility
            """
            return eu - (eu - g) * self.uncertainty

        def calc_hypergame_expected_utilities(self, expected_util):
            """
            Calculates the hypergame expected utility.
            :param expected_util: the expected utility function that will be transformed into a HEU vector
                                  as descrbied in "PLANNING FOR TERRORIST-CAUSED EMERGENCIES"
            :return: the HEU calculated from the expected utility value
            """
            heu = dict.fromkeys(self.rowActionNames, 0.0)
            for rowActionName in self.rowActionNames:
                heu[rowActionName] = (1.0 - self.uncertainty) * \
                                     expected_util[rowActionName] + \
                                     self.uncertainty * \
                                     self.__get_worst_case_action(rowActionName)
            return heu

        def calc_modeling_opponent_utility(self):
            """
            Calculates the modeling oppenent utility value as defined below:
                MO = MAX_k(S_j * u_{j,k} ) for j = 1 to n
                for column j and row k
            as described in "Using Hypergames to Select Plans in Adversarial Environments" by Vane et al
            :return: the modeling opponent expected values for each action
            """
            mo_expected_util = dict.fromkeys(self.rowActionNames, 0.0)
            for rowActionName in self.rowActionNames:
                mo_expected_util[rowActionName] = \
                    max(map(lambda col_action: self.summaryBeliefs[col_action] *
                                               self.costs_row.loc[rowActionName][col_action],
                            self.columnActionNames))

            max_loc = max(mo_expected_util, key=mo_expected_util.get)
            # map the results to a pure strat
            strat_vector = {key: 1 if key == max_loc else 0 for key, value in mo_expected_util.items()}
            return strat_vector

        def calc_pick_subgame_vector(self):
            """
            Calculate the "pick subgame" hyperstrategy
            :return: the value and the name of the action
            """
            best_strat = {}
            for sit in self.situationNames:
                nems = self.calc_nems_expected_util(sit)
                ev = self.calc_expected_values(sit)
                best_strat[sit] = self.calc_expected_utility(ev, nems)
            max_loc = max(best_strat, key=best_strat.get)
            return self.calc_nems_expected_util(max_loc), max_loc

        def calc_weighted_subgame_vector(self):
            """
            Calcualte the "Weighted subgame" hyperstrategy.
            :return: The expected value of the weighted subgame
            """
            out = dict.fromkeys(self.rowActionNames, 0.0)
            for sit in self.situationNames:
                nems = self.calc_nems_expected_util(sit)
                for rowName in self.rowActionNames:
                    out[rowName] += self.currentBelief[sit] * nems[rowName]
            return out

        def print_hnf_table(self, expected_util):
            """
            Prints the Hypergame Normal Form table as seen in R. Vane's work.
            """
            main_tab = tt.Texttable(max_width=160)
            heu_tab = tt.Texttable()

            first_row = ["Current Belief", "Summary Belief"]

            # self.summaryBeliefs.values()]
            first_row.extend([self.summaryBeliefs[name] for name in self.columnActionNames])
            main_out_table = [first_row]

            # top half of table
            for situationName in self.situationNames:
                tmp_row = [self.currentBelief[situationName], situationName]
                tmp_row.extend(self.situationalBeliefs.loc[situationName])
                main_out_table.append(tmp_row)

            middleRow = ["Current EU", " "]
            middleRow.extend(self.columnActionNames)
            main_out_table.append(middleRow)

            # bottom half of table
            for rowActionName in self.rowActionNames:
                tmp_row = [expected_util[rowActionName], rowActionName]
                tmp_row.extend(self.costs_row.loc[rowActionName])
                main_out_table.append(tmp_row)

            main_tab.add_rows(main_out_table, header=False)
            heu_tab.header(["Row Action Name", "HEU"])
            print "Name: " + self.HNFName
            print "Uncertainty: %f" % self.uncertainty
            print main_tab.draw()

            results = self.calc_all_results()
            for name in HNF.Consts.HYPERSTRATS:
                tab = self.__produce_table(name, results)
                print tab.draw()
                # create a new table

        def __produce_table(self, hyperstrat_name, results):
            mo_tab = tt.Texttable()
            first_row = ["Row Actions", hyperstrat_name]
            mo_tab.add_row(first_row)

            for rowActionName in self.rowActionNames:
                tmp_row = [rowActionName, results[hyperstrat_name]["Strategy Vector"][rowActionName]]
                mo_tab.add_row(tmp_row)

            mo_tab.add_row(["EU", results[hyperstrat_name]["Expected Utility"]])
            mo_tab.add_row(["G", results[hyperstrat_name]["Worst Case"]])
            mo_tab.add_row(["HEU", results[hyperstrat_name]["HEU"]])

            return mo_tab

        def display_hnf(self):
            """
            DESC
                Display the HNF table and uncertainty plot
            OUTPUT
                Text to the console showing the table and a matplot
            """
            self.heu_plot_over_uncertainty()
            self.hyperstrat_plot_over_uncertainty()
            self.print_hnf_table(self.calc_expected_values())

        def calc_all_results(self):
            final_results = {}
            for hyperstrat_name in HNF.Consts.HYPERSTRATS:
                results = {}
                if hyperstrat_name == "MO":
                    results["Strategy Vector"] = self.calc_modeling_opponent_utility()
                    results["Expected Values"] = self.calc_expected_values()
                    results["Expected Utility"] = self.calc_expected_utility(results["Expected Values"],
                                                                             results["Strategy Vector"])
                elif hyperstrat_name == "PS":
                    results["Strategy Vector"], _ = self.calc_pick_subgame_vector()
                    results["Expected Values"] = self.calc_expected_values()
                    results["Expected Utility"] = self.calc_expected_utility(results["Expected Values"],
                                                                             results["Strategy Vector"])
                elif hyperstrat_name == "WS":
                    results["Strategy Vector"] = self.calc_weighted_subgame_vector()
                    results["Expected Values"] = self.calc_expected_values()
                    results["Expected Utility"] = self.calc_expected_utility(results["Expected Values"],
                                                                             results["Strategy Vector"])
                elif hyperstrat_name == "NEMS":
                    # find the best sit
                    results["Strategy Vector"], sit = self.calc_pick_subgame_vector()
                    #results["Expected Values"] = self.calc_nems_expected_values(sit)
                    results["Expected Utility"] = self.calc_nems_expected_value(sit)

                results["Worst Case"] = self.calc_g(results["Strategy Vector"])
                results["HEU"] = self.calc_heu(results["Expected Utility"],
                                               results["Worst Case"])
                final_results[hyperstrat_name] = results

            return final_results

        def hyperstrat_plot_over_uncertainty(self, step=0.1):
            """
            DESC: Plot the uncertainty from 0.0 to 1.0 given a step
            :param step:
            """
            # save the current uncertainty and restore it after we plot it
            old_uncertainty = self.uncertainty
            # init hypergame expected utility
            plot_data = {"WS": [], "MO": [], "PS": []}

            # iterate over the uncertainty range. For each step, update the eu
            for uncertainty in np.arange(1.1, 0.0, -1 * step):
                self.set_uncertainty(uncertainty)
                results = self.calc_all_results()
                for hyperstrat_name in plot_data.keys():
                    plot_data[hyperstrat_name] = [results[hyperstrat_name]["HEU"]] + plot_data[hyperstrat_name]

            plot_data["NEMS"] = [results["NEMS"]["Expected Utility"]] * 11
            #print plot_data["NEMS"]

            for hyperstrat_name in plot_data.keys():
                plt.plot(np.arange(0.0, 1.1, step), plot_data[hyperstrat_name], label=hyperstrat_name)

            self.uncertainty = old_uncertainty
            plt.title(self.HNFName + " - HEU for Hyperstrategies over Uncertainty")
            plt.xlabel("Uncertainty")
            plt.ylabel("Hypergame Expected Utility")
            plt.legend()
            plt.show()

        def heu_plot_over_uncertainty(self, step=0.1):
            """
            DESC: Plot the uncertainty from 0.0 to 1.0 given a step
            :param step:
            """
            # save the current uncertainty and restore it after we plot it
            old_uncertainty = self.uncertainty
            # init hypergame expected utility
            heu_over_time = dict.fromkeys(self.rowActionNames, [])
            mo_over_time = dict.fromkeys(self.rowActionNames, [])

            # iterate over the uncertainty range. For each step, update the eu
            for uncertainty in np.arange(0.0, 1.1, step):
                self.set_uncertainty(uncertainty)
                expected_vals = self.calc_expected_values()
                heu = self.calc_hypergame_expected_utilities(expected_vals)
                # save the HEU for each action
                for rowActionName in self.rowActionNames:
                    heu_over_time[rowActionName] = heu_over_time[rowActionName] + \
                                                   [heu[rowActionName]]

            for rowActionName in self.rowActionNames:
                plt.plot(np.arange(0.0, 1.1, step), heu_over_time[rowActionName], label=rowActionName)

            self.uncertainty = old_uncertainty
            plt.title("Hypergame Expected Utility over uncertainty")
            plt.xlabel("Uncertainty")
            plt.ylabel("Hypergame Expected Utility")
            plt.legend()
            plt.show()

        def __verify_all_entries(self):
            """
            DESC: Make sure that all the entries are set before we start to
                  calculate HEU, etc.
            """
            self.__verify_current_beliefs()
            self.__verify_situational_beliefs()
            self.__verify_summary_belief()

        def __verify_summary_belief(self):
            """
            DESC:
                verify that the summary belief adds up to 1.0
            """
            assert 0.99 <= sum(self.summaryBeliefs.values()) <= 1.0

        def __verify_situational_beliefs(self):
            """
            DESC:
                Verify that the situation belief is valid. The rows should always
                add up to 1.
            """
            for situation in self.situationNames:
                filterList = [item for item in self.situationalBeliefs.loc[situation] if item != 'X']
                assert 0.99999 <= sum(filterList) <= 1.00001

        def __verify_current_beliefs(self):
            """
            DESC:
                Verify that the current belief is valid. The sum of current belief
                values should be 1.0.
            """
            assert sum(self.currentBelief.values()) >= 0.99 and sum(self.currentBelief.values()) <= 1.0

        def __get_worst_case_action(self, rowActionName):
            """
            DESC
                get the worst case outcome for a given row action.
            INPUT
                A row action name
            OUTPUT
                A dictionary with the name of the column action and the utility
            """
            # check to see if the row action name is valid
            assert rowActionName in self.rowActionNames
            return min(self.costs_row.loc[rowActionName])

        def __create_gambit_game(self, situation):
            col_len = len([item for item in self.situationalBeliefs.loc[situation] if item != "X"])
            g = gambit.Game.new_table([len(self.rowActionNames), col_len])
            g.title = situation
            g.players[0].label = "Row Player"
            self.__set_gambit_actions(g, 0, situation)
            g.players[1].label = "Column Player"
            col_action_names = self.__set_gambit_actions(g, 1, situation)

            for col_ind, col_name in enumerate(col_action_names):
                for row_ind, row_name in enumerate(self.rowActionNames):
                    #print self.costs_row
                    g[row_ind, col_ind][0] = int(self.costs_row[col_name][row_name])
                    # hack for now
                    g[row_ind, col_ind][1] = int(self.costs_column[col_name][row_name])

            return g

        def __set_gambit_actions(self, g, player_index, situation):
            assert player_index == 0 or player_index == 1
            # row player
            if player_index == 0:
                action_names = self.rowActionNames
            # column player
            else:
                action_names = list()
                for colActionName in self.columnActionNames:
                    if self.situationalBeliefs.loc[situation][colActionName] != "X":
                        action_names.append(colActionName)
                        # action_names = self.columnActionNames

            for i, actionName in enumerate(action_names):
                g.players[player_index].strategies[i].label = actionName
            return action_names

        def append_gambit_game(self, situation):
            """
            For a given situation name (str), append the approrate gambit object
            into self.gambitGames.
            :param situation:
            :return:
            """
            self.gambitGames[situation] = self.__create_gambit_game(situation)

        def calc_nems_expected_util(self, situation, player="Row Player"):
            game = self.gambitGames[situation]
            solver = gambit.nash.ExternalEnumMixedSolver()
            s = solver.solve(game)
            # return the first nash equl.
            return dict(zip(self.rowActionNames, s[0][player]))

        def calc_nems_expected_value(self, situation, player="Row Player"):
            game = self.gambitGames[situation]
            solver = gambit.nash.ExternalEnumMixedSolver()
            s = solver.solve(game)
            return s[0]._profile.payoff(game.players[0])