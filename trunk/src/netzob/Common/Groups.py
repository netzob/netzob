# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging
import time
import gtk
import pygtk
pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.ProjectParser import ProjectParser
from netzob.Inference.Vocabulary.Clusterer import Clusterer

#+---------------------------------------------- 
#| Groups :
#|     definition of the groups of messages
#+---------------------------------------------- 
class Groups(object):
    
    #+----------------------------------------------
    #| Fields in a group message definition :
    #|     - groups
    #+----------------------------------------------
    
    #+---------------------------------------------- 
    #| Constructor :
    #+----------------------------------------------   
    def __init__(self, netzob):
        self.log = logging.getLogger('netzob.Common.Groups.py') # Create logger with the given configuration
        self.netzob = netzob
        self.groups = []

    def clear(self):
        del self.groups[:] # Just clean the object without deleting it

    def initGroupsWithTraces(self):
        projectParser = ProjectParser(self.netzob)
        self.setGroups(projectParser.parse())
        for g in self.groups :
            g.buildInitRegex()

    

    #+---------------------------------------------- 
    #| alignWithDelimiter:
    #|  Align each messages of each group with a specific delimiter
    #+----------------------------------------------
    def alignWithDelimiter(self, delimiter):
        # Use the default protocol type for representation
        configParser = ConfigurationParser()
        valID = configParser.getInt("clustering", "protocol_type")
        if valID == 0:
            aType = "ascii"
        else:
            aType = "binary"

        for group in self.groups :
            columns = []
            i = -1
            doBreak = False
            while True:
                i += 1
                maxSize = 0
                minSize = 999999
                for message in group.getMessages():
                    try: # A carambar to the one who finds this awsome try/except code !
                        maxSize = max(maxSize, len(message.getStringData().split(delimiter)[i]))
                        minSize = min(minSize, len(message.getStringData().split(delimiter)[i]))
                    except IndexError:
                        doBreak = True
                if doBreak == True:
                    break
                columns.append({'name' : "Name",
                                'regex' : "(.{" + str(minSize) + "," + str(maxSize) + "})",
                                'selectedType' : aType,
                                'tabulation' : 0,
                                'description' : "",
                                'color' : ""
                                })
                columns.append({'name' : "Sep",
                                'regex' : delimiter,
                                'selectedType' : aType,
                                'tabulation' : 0,
                                'description' : "",
                                'color' : ""
                                })
            del columns[-1]
            del columns[-1]
            columns.append({'name' : "Name",
                            'regex' : "(.{,})",
                            'selectedType' : aType,
                            'tabulation' : 0,
                            'description' : "",
                            'color' : ""
                            })
            group.setColumns(columns)

    #+---------------------------------------------- 
    #| slickRegexes:
    #|  try to make smooth the regexes, by deleting tiny static
    #|  sequences that are between big dynamic sequences
    #+----------------------------------------------
    def slickRegexes(self, button, ui):
        for group in self.getGroups():
            group.slickRegex()
        ui.update()

    #+---------------------------------------------- 
    #| mergeCommonRegexes:
    #|  try to merge identical regexes
    #+----------------------------------------------
    def mergeCommonRegexes(self, button, ui):
        self.log.info("Merging not implemented yet")

    #+---------------------------------------------- 
    #| findSizeField:
    #|  try to find the size field of each regex
    #+----------------------------------------------    
    def findSizeFields(self, store):
        for group in self.getGroups():
            group.findSizeFields(store)


    #+---------------------------------------------- 
    #| search_cb:
    #|  launch the search
    #+----------------------------------------------    
    def search_cb(self, but, entry, notebook):
        if entry.get_text() == "":
            return

        # Clear the notebook
        for i in range(notebook.get_n_pages()):
            notebook.remove_page(i)

        # Fill the notebook
        for group in self.getGroups():
            vbox = group.search(entry.get_text())
            if vbox != None:
                notebook.append_page(vbox, gtk.Label(group.getName()))

    #+---------------------------------------------- 
    #| Groups management :
    #+----------------------------------------------    
    def addGroup(self, group):
        self.groups.append(group)

    def removeGroup(self, group):
        self.groups.remove(group)
    #+---------------------------------------------- 
    #| getMessageByID:
    #|     Retrieves the message given its ID
    #| @param id_message the id of the message to retrieve
    #| @return the message or None if not found
    #+----------------------------------------------    
    def getMessageByID(self, id_message):
        for group in self.getGroups() :
            for msg in group.getMessages() :
                if str(msg.getID()) == id_message :
                    return msg
        return None
    #+---------------------------------------------- 
    #| getMessages:
    #|     Retrieves all the messages
    #| @param id_message the id of the message to retrieve
    #| @return the message or None if not found
    #+----------------------------------------------                   
    def getMessages(self):
        messages = []
        for group in self.getGroups() :
            for msg in group.getMessages() :
                messages.append(msg)
        
        return messages


    #+---------------------------------------------- 
    #| GETTERS :
    #+----------------------------------------------    
    def getGroups(self):
        return self.groups

    #+---------------------------------------------- 
    #| SETTERS :
    #+----------------------------------------------    
    def setGroups(self, groups):
        self.groups = groups
