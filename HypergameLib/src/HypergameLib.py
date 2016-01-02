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
        EU = "EU"

    class HNFFactory(object):
        """
        DESC
            Creates an HNFInstance
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

                # get key values
                sit_names = self.settings[HNF.Consts.SIT_NAMES]
                row_action_names = self.settings[HNF.Consts.ROW_ACT_NAMES]
                column_action_names = self.settings[HNF.Consts.COL_ACT_NAMES]
                name = self.settings[HNF.Consts.NAME]

                # init HNG object
                self.HNFOut = HNF.HNFInstance(sit_names, row_action_names, column_action_names, name)

                # set the values found in the settings
                self.__initFromFile()

                # calc the summary and expected utility
                self.HNFOut.init_summary_belief()

                # setup the output stuff
                #self.HNFOut.situation_expected_utility()
                #self.HNFOut.calc_hypergame_expected_utility()
                #self.HNFOut.calc_modeling_opponent_utility()

        def getHNFInstance(self):
            return self.HNFOut

        def __initFromFile(self):
            """
            DESC: extracts all the settings found in the config file and inits
                the HNF object.
            """
            self.__setCosts()
            self.__setBeliefs()
            self.__setCurrentBelief()

            # Gambit games -- each belief context will be modeled as a sep gambit game
            for situation in self.HNFOut.situationNames:
                self.HNFOut.append_gambit_game(situation)

        def __setCosts(self):
            """
            DESC: extracts cost from settings file and sets the cost in the HNF
            """
            # extract cost info from settings
            costRows = map(lambda r: {HNF.Consts.ROW_ACTION: r[HNF.Consts.ROW_ACTION],
                                      HNF.Consts.COST_COL_ACTIONS: r[HNF.Consts.COST_COL_ACTIONS]},
                           self.settings[HNF.Consts.ROW_ACTION_COST])
            # set cost values
            for costRow in costRows:
                self.HNFOut.set_costs_by_action(costRow[HNF.Consts.ROW_ACTION],
                                                costRow[HNF.Consts.COST_COL_ACTIONS])


        def __setBeliefs(self):
            """
            DESC: extracts the beliefs from settings file and sets the belief in the HNF
            """
            # extract the belief values from settings
            beliefRows = map(lambda r: {HNF.Consts.SIT_NAME: r[HNF.Consts.SIT_NAME],
                                        HNF.Consts.BELIEF_COL_ACTIONS: r[HNF.Consts.BELIEF_COL_ACTIONS]},
                             self.settings[HNF.Consts.ROW_BELIEF])
            # set belief values
            for beliefRow in beliefRows:
                self.HNFOut.set_situational_beliefs(beliefRow[HNF.Consts.SIT_NAME],
                                                    beliefRow[HNF.Consts.BELIEF_COL_ACTIONS])

        def __setCurrentBelief(self):
            """
            DESC: Extracts the current belief from file and sets the current belief.
            """
            # extract current belief from settings
            currentBeliefs = dict(map(lambda r: (r[HNF.Consts.SIT_NAME], r[HNF.Consts.CUR_BELIEF]),
                                      self.settings[HNF.Consts.ROW_BELIEF]))
            # set current beliefs
            self.HNFOut.set_current_belief(currentBeliefs)

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
            self.costs = pd.DataFrame(index=rowActionNames,
                                      columns=columnActionNames)
            self.situationalBeliefs = pd.DataFrame(index=situationNames,
                                                   columns=columnActionNames)

            # set the current to be uniformly likely
            self.currentBelief = dict.fromkeys(situationNames, 1.0 / float(len(situationNames)))

            # init summary belief to all zeros
            self.summaryBeliefs = dict.fromkeys(columnActionNames, 0.0)

            # init expected utility
            # self.expectedUtility = dict.fromkeys(rowActionNames, 0.0)

            # init hypergame expected utility
            # self.hypergameExpectedUtility = dict.fromkeys(rowActionNames, 0.0)

            # init MO utility
            # self.modelingOpponentUtility = dict.fromkeys(rowActionNames, 0.0)

            # set gambit object
            self.gambitGames = dict()

            # init constants
            self.HNFName = name
            self.uncertainty = uncertainty

        def set_current_belief(self, updatedCurrentBeilefDict):
            """
            DESC:
                Set the current belief values.
            INPUT:
                updatedCurrentBeilefDict (dict) - a dictionary with keys equal to
                situation name and values summing up to 1.
                :param updatedCurrentBeilefDict:
            """
            assert type(updatedCurrentBeilefDict) is dict
            assert set(updatedCurrentBeilefDict.keys()) == set(self.situationNames)
            assert 0.99 <= sum(updatedCurrentBeilefDict.values()) <= 1.0

            for key in updatedCurrentBeilefDict.keys():
                self.currentBelief[key] = updatedCurrentBeilefDict[key]

        def set_costs_by_action(self, actionName, updatedDict):
            """
            DESC:
                Set the cost for a given action. The action can be either a row or a
                column action.
            INPUT:
                :param actionName: the action name to be updated.
                :param updatedDict: a dictionary with updated values. The keys must
                    must be row or column action names and the values should be the
                    costs
            """
            assert type(updatedDict) is dict
            assert actionName in self.rowActionNames or \
                   actionName in self.columnActionNames

            if actionName in self.rowActionNames:
                # Update a defenders cost row
                for k in updatedDict.keys():
                    self.costs.loc[actionName][k] = updatedDict[k]
            elif actionName in self.columnActionNames:
                # Update a column
                for k in updatedDict.keys():
                    self.costs[actionName][k] = updatedDict[k]

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
            assert name in self.situationNames or \
                   name in self.columnActionNames

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
                tmpSum = 0.0
                for situationName in self.situationNames:
                    if self.situationalBeliefs[columnActionName][situationName] != "X":
                        tmpSum += self.currentBelief[situationName] * \
                                  self.situationalBeliefs[columnActionName][situationName]
                self.summaryBeliefs[columnActionName] = round(tmpSum, self.ROUND_DEC)

            # make the summary belief is valid
            self.__verify_summary_belief()

        def situation_expected_utility(self, situation=""):
            """
            DESC
                calculate the expected utility. Summary belief, current belief,
                and situational beliefs must all be set before calling this func
            """
            self.__verify_summary_belief()
            self.__verify_current_beliefs()
            self.__verify_situational_beliefs()

            expected_utility = dict.fromkeys(self.rowActionNames, 0.0)
            for rowActionName in self.rowActionNames:
                tmp_sum = 0.0
                for columnActionName in self.columnActionNames:
                    tmp_sum += self.summaryBeliefs[columnActionName] * \
                               self.costs[columnActionName][rowActionName]
                expected_utility[rowActionName] = round(tmp_sum, self.ROUND_DEC)
            return expected_utility

        def calc_hypergame_expected_utility(self, expected_util):
            """
            Calculates the hypergame expected utility.
            :param expected_util: the expected utility function that will be transformed into a HEU vector
                                  as descrbied in "PLANNING FOR TERRORIST-CAUSED EMERGENCIES"
            :return: the HEU calculated from the expected utility value
            """
            heu = dict.fromkeys(self.rowActionNames, 0.0)
            for rowActionName in self.rowActionNames:
                heu[rowActionName] = (1.0 - self.uncertainty) *\
                                     expected_util[rowActionName] +\
                                     self.uncertainty *\
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
                    max(map(lambda i: self.summaryBeliefs[i] *
                            self.costs.loc[rowActionName][i],
                            self.columnActionNames))
            return mo_expected_util

        # The following is need:
        #    1. HEU for ALL row actions
        #    2. MO for ALL row actions
        #    3. Best HEU for

        def print_hnf_table(self, expected_util):
            """
            Prints the Hypergame Normal Form table as seen in R. Vane's work.
            """
            main_tab = tt.Texttable(max_width=160)
            heu_tab = tt.Texttable()

            first_row = ["Current Belief", "Summary Belief"]
            first_row.extend(self.summaryBeliefs.values())
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
                tmp_row.extend(self.costs.loc[rowActionName])
                main_out_table.append(tmp_row)

            main_tab.add_rows(main_out_table, header=False)
            heu_tab.header(["Row Action Name", "HEU"])
            print "Name: " + self.HNFName
            print "Uncertainty: %f" % self.uncertainty
            print main_tab.draw()
            # print "Best expected utility: (%s, %0.2f)" % \
            #    (self.bestCaseEU[HNF.Consts.ROW_ACT_NAME], \
            #            self.bestCaseEU[HNF.Consts.EU])
            # print "Worst expected utility: (%s, %0.2f)" %\
            #    (self.worstCaseEU[HNF.Consts.ROW_ACT_NAME], \
            #        self.worstCaseEU[HNF.Consts.EU])

        def display_hnf(self):
            """
            DESC
                Display the HNF table and uncertainty plot
            OUTPUT
                Text to the console showing the table and a matplot
            """
            self.heu_plot_over_uncertainty()
            self.print_hnf_table(self.situation_expected_utility())

        def calculate_results(self):

            pass

        def heu_plot_over_uncertainty(self, situation="", step=0.1):
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
                eu = self.situation_expected_utility(situation)
                heu = self.calc_hypergame_expected_utility(eu)
                # save the HEU for each action
                for rowActionName in self.rowActionNames:
                    heu_over_time[rowActionName] = heu_over_time[rowActionName] + \
                                                 [heu[rowActionName]]

            for rowActionName in self.rowActionNames:
                plt.plot(np.arange(0.0, 1.1, step), heu_over_time[rowActionName], label=rowActionName)

            plt.title("Hypergame Expected Utility over uncertainty")
            plt.xlabel("Uncertainty")
            plt.ylabel("Hypergame Expected Utility")
            plt.legend()
            plt.show()
            self.uncertainty = old_uncertainty

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
            assert sum(self.currentBelief.values()) >= 0.99 \
                   and sum(self.currentBelief.values()) <= 1.0

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
            return min(self.costs.loc[rowActionName])

        def create_gambit_game(self, situation):
            colLen = len([item for item in self.situationalBeliefs.loc[situation] if item != "X"])
            g = gambit.Game.new_table([len(self.rowActionNames), colLen])
            g.title = situation
            g.players[0].label = "Row Player"
            self.__set_gambit_actions(g, 0, situation)
            g.players[1].label = "Column Player"
            colActionNames = self.__set_gambit_actions(g, 1, situation)

            for col_ind, col_name in enumerate(colActionNames):
                for row_ind, row_name in enumerate(self.rowActionNames):
                    g[row_ind, col_ind][0] = int(self.costs[col_name][row_name])
                    # hack for now
                    g[row_ind, col_ind][1] = int(-1 * self.costs[col_name][row_name])

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
                #action_names = self.columnActionNames

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
            self.gambitGames[situation] = self.create_gambit_game(situation)

        def calc_nems_expected_util(self, situation):
            game = self.gambitGames[situation]
            solver = gambit.nash.ExternalLogitSolver()
            s = solver.solve(game)
            nems_eu = s[:len(self.rowActionNames)]
            return nems_eu

        def calc_nems_expected_value(self, expected_util):

            pass
