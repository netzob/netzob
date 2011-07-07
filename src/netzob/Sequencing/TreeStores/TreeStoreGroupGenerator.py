#!/usr/bin/python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ...Common import ConfigurationParser
from ..NeedlemanWunsch import NeedlemanWunsch

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| TreeStoreGroupGenerator :
#|     update and generates the treestore 
#|     dedicated to the groups
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TreeStoreGroupGenerator():
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups : the groups of messages
    #| @param treestore : the treestore to update
    #+---------------------------------------------- 
    def __init__(self, groups, treestore):
        self.groups = groups
        self.treestore = treestore
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.TreeStores.TreeStoreGroupGenerator.py')
    
    #+---------------------------------------------- 
    #| default :
    #|         Update the treestore in normal mode
    #+---------------------------------------------- 
    def default(self):
        self.log.debug("Updating the treestore of the group in default mode")        
        self.treestore.clear()
        for group in self.groups :
            iter = self.treestore.append(None, ["Group","{0}".format(group.getName()),"{0}".format(group.getScore()), '#000000', '#FF00FF'])
            for message in group.getMessages() :
                self.treestore.append(iter, ["Message", message.getID(), "0", '#000000', '#FF00FF'])

    #+---------------------------------------------- 
    #| messageSelected :
    #|         Update the treestore when a message
    #|         is a selected
    #| @param selectedMessage the selected message
    #+---------------------------------------------- 
    def messageSelected(self, selectedMessage):
        self.log.debug("Updating the treestore of the group with a selected message")
        self.treestore.clear()
        for group in self.groups :
            tmp_sequences = []
            if (len(group.getRegex())>0) :
                    tmp_sequences.append(group.getRegex())

            tmp_sequences.append(self.selectedMessage.getStringData())
            tmp_alignator = NeedlemanWunsch()

            tmp_score = group.getScore()
            if (len(tmp_sequences)>=2) :
                tmp_regex = tmp_alignator.getRegex(tmp_sequences)
                tmp_score = tmp_alignator.computeScore(tmp_regex)
            if (tmp_score >= group.getScore()):
                color = '#66FF00'
            else :
                color = '#FF0000'
                iter = self.treestore.append(None, ["Group","{0}".format(group.getName()),"{0}".format(group.getScore()), '#000000', color])
            for message in group.getMessages() :
                self.treestore.append(iter, ["Message", message.getID(), "0", '#000000', '#FF00FF'])
    
    
    
        