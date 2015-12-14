'''
Created on Oct 31, 2015

@author: Christopher Gutierrez
'''
import pandas as pd
import texttable as tt
import yaml
import numpy as np
import matplotlib.pyplot as plt

class HNF(object):
    
    class Consts(object):
        #constants found in config file
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
        '''
        DESC
            Creates an HNFInstance
        '''
        def __init__(self, settingsFileName):
            '''
            DESC
                Creates an HNF object based on the settings file given.
            INPUT
                settingsFileName (str) - A string that points to a file that contains
                   the settings information
            '''
            with open(settingsFileName, 'r') as f:
                #load config file
                self.settings = yaml.load(f)
                
                #get key values
                sitNames = self.settings[HNF.Consts.SIT_NAMES]
                rowActionNames = self.settings[HNF.Consts.ROW_ACT_NAMES]
                columnActionNames = self.settings[HNF.Consts.COL_ACT_NAMES]
                name = self.settings[HNF.Consts.NAME]
                
                #init HNG object
                self.HNFOut = HNF.HNFInstance(sitNames, rowActionNames, columnActionNames, name)
                
                #set the values found in the settings
                self.__initFromFile()
                
                #calc the summary and expected utility
                self.HNFOut.initSummaryBelief()
                self.HNFOut.initExpectedUtility()
                self.HNFOut.calcHypergameExpectedUtility()
                self.HNFOut.calcModelingOpponentUtility()
                
                
        def getHNFInstance(self):
            return self.HNFOut
        
        def __initFromFile(self):
            '''
            DESC: extracts all the settings found in the config file and inits 
                the HNF object.
            '''
            self.__setCosts()
            self.__setBeliefs()
            self.__setCurrentBelief()
        
        def __setCosts(self):
            '''
            DESC: extracts cost from settings file and sets the cost in the HNF
            '''
            #extract cost info from setttings
            costRows =  map(lambda r: {HNF.Consts.ROW_ACTION:r[HNF.Consts.ROW_ACTION],\
                            HNF.Consts.COST_COL_ACTIONS:r[HNF.Consts.COST_COL_ACTIONS]},\
                            self.settings[HNF.Consts.ROW_ACTION_COST])
            #set cost values
            for costRow in costRows:
                self.HNFOut.setCosts(costRow[HNF.Consts.ROW_ACTION],\
                                    costRow[HNF.Consts.COST_COL_ACTIONS])
                
        def __setBeliefs(self):
            '''
            DESC: extracts the beliefs from settings file and sets the belief in the HNF
            '''
            #extract the belief values from settings
            beliefRows = map(lambda r: {HNF.Consts.SIT_NAME:r[HNF.Consts.SIT_NAME],\
                        HNF.Consts.BELIEF_COL_ACTIONS:r[HNF.Consts.BELIEF_COL_ACTIONS]},\
                        self.settings[HNF.Consts.ROW_BELIEF])
            #set belief values 
            for beliefRow in beliefRows:
                self.HNFOut.setSituationalBeliefs(beliefRow[HNF.Consts.SIT_NAME],\
                                        beliefRow[HNF.Consts.BELIEF_COL_ACTIONS])
        def __setCurrentBelief(self):
            '''
            DESC: Extracts the current belief from file and sets the current belief.
            '''
            #extract current belief from settings
            currentBeliefs = dict(map(lambda r: (r[HNF.Consts.SIT_NAME],r[HNF.Consts.CUR_BELIEF]),\
                        self.settings[HNF.Consts.ROW_BELIEF]))
            #set current beliefs
            self.HNFOut.setCurrentBelief(currentBeliefs)
            
    class HNFInstance(object):
        '''
        Hypergame Normal Form Class
        Should contain the following
        A belief context matrix
        A payoff matrix
        A situational belief matrix
        '''
        
        #round the the nearest thousandth deceimal place
        ROUND_DEC = 5
        
        def __init__(self, situationNames, rowActionNames, columnActionNames,\
                     name="", uncertainty=0.0):
            '''
            DESC: Create the index names and init the cost and situatational belief mats
            Input: 
                   sutiationNames (list) - A list strings. Each item is the name of 
                      a situation in the HNF
                   rowActionNames (list) - A list of strings. Each item is the name
                      of the actions that the row player can make
                   columnActionNames (list) - A list of strings. Each item is the
                      name of an action that the column player can make.
            '''
            #make sure the inputs are list
            assert type(situationNames) is list and \
                   type(rowActionNames) is list and\
                   type(columnActionNames) is list 
            
            assert len(situationNames) > 0 and len(rowActionNames) > 0 and\
                   len(columnActionNames) > 0
            
            #make sure that the names of each key is different  
            assert len(situationNames) + len(rowActionNames) +\
                   len(columnActionNames) == len(set(situationNames)) + \
                                            len(set(rowActionNames)) +\
                                            len(set(columnActionNames))
            
            #save the names. To be used as keys in mats and vectors
            self.situationNames = situationNames
            self.rowActionNames = rowActionNames
            self.columnActionNames = columnActionNames
            
            #init the mats 
            self.costs = pd.DataFrame(index = rowActionNames,\
                                       columns = columnActionNames)
            self.situationalBeliefs = pd.DataFrame(index=situationNames,\
                                                    columns=columnActionNames)
        
            #set the current to be uniformly likely
            self.currentBelief = dict.fromkeys(situationNames, 1.0/float(len(situationNames)))
    
            #init summary belief to all zeros
            self.summaryBeliefs = dict.fromkeys(columnActionNames, 0.0)
            
            #init expected utility
            self.expectedUtility = dict.fromkeys(rowActionNames, 0.0)
            
            #init hypergame expected utility
            self.hypergameExpectedUtility = dict.fromkeys(rowActionNames, 0.0)
            
            #init MO utility
            self.modelingOpponentUtility = dict.fromkeys(rowActionNames, 0.0)
            #init constants
            self.HNFName = name
            self.uncertainty = uncertainty
            self.bestCaseEU = None
            self.worstCaseEU = None
        
        def setCurrentBelief(self, updatedCurrentBeilefDict):
            '''
            DESC: 
                Set the current belief values.
            INPUT:
                updatedCurrentBeilefDict (dict) - a dictionary with keys equal to 
                situation name and values summing up to 1.
            '''
            assert type(updatedCurrentBeilefDict) is dict
            assert set(updatedCurrentBeilefDict.keys()) == set(self.situationNames)
            assert sum(updatedCurrentBeilefDict.values()) >= 0.99\
                   and sum(updatedCurrentBeilefDict.values())  <= 1.0
            
            for key in updatedCurrentBeilefDict.keys():
                self.currentBelief[key] = updatedCurrentBeilefDict[key]
        
        def setCosts(self, actionName, updatedDict):
            '''
            DESC:
                Set the cost for a given action. The action can be either a row or a
                column action.
            INPUT:
                actionName (str) - the action name to be updated.
                updatedDict (dict) - a dictionary with updated values. The keys must
                    must be row or column action names and the values should be the 
                    costs
            '''
            assert type(updatedDict) is dict
            assert actionName in self.rowActionNames or\
                   actionName in self.columnActionNames
            
            if actionName in self.rowActionNames:
                #Update a defenders cost row
                for k in updatedDict.keys():
                    self.costs.loc[actionName][k] = updatedDict[k]
            elif actionName in self.columnActionNames:
                #Update a column
                for k in updatedDict.keys():
                    self.costs[actionName][k] = updatedDict[k]
        
        def setSituationalBeliefs(self, name, updatedDict):
            '''
            DESC:
                Set the situational beliefs for a given situation name or column 
                action name.
            INPUT:
                name (str) - the name of the situation or the name of the row action
                    to be updated.
                updateDict (dict) - a dictionary with the updated values. The keys
                    must be row situation names or column action names and the values
                    should be the probabilities.  
            '''
            assert type(updatedDict) is dict
            assert name in self.situationNames or\
                   name in self.columnActionNames
            
            if name in self.situationNames:
                
                for k in updatedDict.keys():
                    self.situationalBeliefs.loc[name][k] = updatedDict[k]
            elif name in self.columnActionNames:
                for k in updatedDict.keys():
                    self.situationalBeliefs[name][k] = updatedDict[k]
    
        def setUncertainty(self, uncertainty):
            '''
            DESC
                Set the uncertainty value (duh)
            '''
            self.uncertainty = uncertainty    
            
        def initSummaryBelief(self):
            '''
            DESC
                Calculate the summary belief from Current Belief and Situational
                Beliefs.
            '''
            #asset that all the values are in place
            self.__verifySituationalBeliefs()
            self.__verifyCurrentBeliefs()
            
            for columnActionName in self.columnActionNames:
                tmpSum = 0.0
                for situationName in self.situationNames:
                    tmpSum += self.currentBelief[situationName] * \
                        self.situationalBeliefs[columnActionName][situationName]
                self.summaryBeliefs[columnActionName] = round(tmpSum,self.ROUND_DEC)
            
            #make the summary belief is valid
            self.__verifySummaryBelief()
        
        def initExpectedUtility(self):
            '''
            DESC
                calculate the expected utility. Summary belief, current belief,
                and situational beliefs must all be set before calling this func
            '''
            self.__verifySummaryBelief()
            self.__verifyCurrentBeliefs()
            self.__verifySituationalBeliefs()
            for rowActionName in self.rowActionNames:
                tmpSum = 0.0
                for columnActionName in self.columnActionNames:
                    tmpSum += self.summaryBeliefs[columnActionName] * \
                            self.costs[columnActionName][rowActionName]
                self.expectedUtility[rowActionName] = round(tmpSum,self.ROUND_DEC)
            
            #now that we have EUs, update the best and worst EU vars
            self.__setBestWorstEU()
    
        def calcHypergameExpectedUtility(self):
            '''
            DESC: Calculates the hypergame expected utility.
            '''
            for rowActionName in self.rowActionNames:
                self.hypergameExpectedUtility[rowActionName]=(1.0-self.uncertainty)\
                        * self.expectedUtility[rowActionName] + self.uncertainty\
                        * self.__getWorstCaseAction(rowActionName)
                              
        def calcModelingOpponentUtility(self):
            '''
            DESC
                Calculating the MO
                MO = MAX_k(S_j * u_{j,k} ) for j = 1 to n
                for column j and row k
            '''
            for rowActionName in self.rowActionNames:
                self.modelingOpponentUtility[rowActionName] = \
                    max(map(lambda i: self.summaryBeliefs[i] * \
                            self.costs.loc[rowActionName][i], self.columnActionNames))
            print self.modelingOpponentUtility
            
    

#The following is need:
#    1. HEU for ALL row actions
#    2. MO for ALL row actions
#    3. Best HEU for

            
        def printHNFTable(self):
            '''
            DESC: Prints the Hypergame Normal Form table as seen in R. Vane's work.
            '''
            mainTab = tt.Texttable(max_width=160)
            heuTab = tt.Texttable()
            
            firstRow = ["Current Belief", "Summary Belief"]
            firstRow.extend(self.summaryBeliefs.values())
            mainOutTable = [firstRow]
    
            #top half of table
            for situationName in self.situationNames:
                tmpRow = [self.currentBelief[situationName], situationName]
                tmpRow.extend(self.situationalBeliefs.loc[situationName])
                mainOutTable.append(tmpRow)
            
            middleRow = ["Current EU", " "]
            middleRow.extend(self.columnActionNames)
            mainOutTable.append(middleRow)
    
            #bottom half of table 
            for rowActionName in self.rowActionNames:
                tmpRow = [self.expectedUtility[rowActionName], rowActionName]
                tmpRow.extend(self.costs.loc[rowActionName])
                mainOutTable.append(tmpRow)

            mainTab.add_rows(mainOutTable, header=False)
            heuTab.header(["Row Action Name", "HEU"])
            print "Name: " + self.HNFName
            print "Uncertainty: %f" % self.uncertainty 
            print mainTab.draw()
            #print "Best expected utility: (%s, %0.2f)" % \
            #    (self.bestCaseEU[HNF.Consts.ROW_ACT_NAME], \
            #            self.bestCaseEU[HNF.Consts.EU])
            #print "Worst expected utility: (%s, %0.2f)" %\
            #    (self.worstCaseEU[HNF.Consts.ROW_ACT_NAME], \
            #        self.worstCaseEU[HNF.Consts.EU])
      
                    
        def displayHNF(self):
            '''
            DESC
                Display the HNF table and uncertainty plot
            OUTPUT
                Text to the console showing the table and a matplot
            '''
            self.heuPlotOverUncertainty()
            self.printHNFTable()
        
        def heuPlotOverUncertainty(self, step=0.1):
            '''
            DESC: Plot the uncertainty from 0.0 to 1.0 given a step
            '''
            #save the current uncertainty and restore it after we plot it
            oldUncertainty = self.uncertainty
            #init hypergame expected utility
            heuOverTime = dict.fromkeys(self.rowActionNames, [])
            moOverTime = dict.fromkeys(self.rowActionNames, [])
            for uncertainty in np.arange(0.0, 1.1, step):
                self.setUncertainty(uncertainty)
                self.calcHypergameExpectedUtility()
                #save the HEU for each action 
                for rowActionName in self.rowActionNames:
                    heuOverTime[rowActionName] = heuOverTime[rowActionName] + \
                                    [self.hypergameExpectedUtility[rowActionName]]
                    
            for rowActionName in self.rowActionNames:
                plt.plot(np.arange(0.0, 1.1, step), heuOverTime[rowActionName], label=rowActionName)
            
            plt.title("Hypergame Expected Utility over uncertainty")
            plt.xlabel("Uncertainty")
            plt.ylabel("Hypergame Expected Utility")
            plt.legend()
            plt.show()
            self.uncertainty = oldUncertainty
            
        def __verifyAllEntries(self):
            '''
            DESC: Make sure that all the entries are set before we start to
                  calculate HEU, etc.
            '''
            self.__verifyCurrentBeliefs()
            self.__verifySituationalBeliefs()
            self.__verifySummaryBelief()
            
        def __verifySummaryBelief(self):
            '''
            DESC: 
                verify that the summary belief adds up to 1.0
            '''
            assert sum(self.summaryBeliefs.values()) >= 0.99 \
                   and sum(self.summaryBeliefs.values()) <= 1.0
            
        def __verifySituationalBeliefs(self):
            '''
            DESC:
                Verify that the situation belief is valid. The rows should always
                add up to 1. 
            '''
            for situation in self.situationNames:
                assert sum(self.situationalBeliefs.loc[situation]) == 1.0
            
        def __verifyCurrentBeliefs(self):
            '''
            DESC:
                Verify that the current belief is valid. The sum of current belief 
                values should be 1.0.
            '''
            assert sum(self.currentBelief.values()) >= 0.99\
                  and sum(self.currentBelief.values()) <= 1.0
    
        def __setBestWorstEU(self):
            '''
            DESC: Set the best expected utility and the worst expected utility
            '''
            #set the worst case expected util
            worstCaseEUKey = min(self.expectedUtility, key=self.expectedUtility.get)
            self.worstCaseEU = {HNF.Consts.ROW_ACT_NAME: worstCaseEUKey,\
                                HNF.Consts.EU:self.expectedUtility[worstCaseEUKey]}
            
            #set the best case expected util
            bestCaseEUKey = max(self.expectedUtility, key=self.expectedUtility.get)
            self.bestCaseEU = {"rowActionName": bestCaseEUKey,\
                               HNF.Consts.EU:self.expectedUtility[bestCaseEUKey]}
    
        def __getWorstCaseAction(self, rowActionName):
            '''
            DESC
                get the worst case outcome for a given row action.
            INPUT
                A row action name
            OUTPUT
                A dictionary with the name of the column action and the utility
            '''
            #check to see if the row action name is valid
            assert rowActionName in self.rowActionNames
            return min(self.costs.loc[rowActionName])
            