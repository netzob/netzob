#!/usr/bin/env python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| Netzob : communication protocol modelization by reverse engineering                     |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frédéric Guihéry                      |
#| @url          : http://www.netzob.org                                     |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @contact      : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#|                 Supelec, http://www.rennes.supelec.fr/ren/rd/ssir/        |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import gtk
import pygtk
pygtk.require('2.0')
import gobject
import os
import threading
import sys
import logging
from lxml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Project import Project
from netzob.Common.Menu import Menu
from netzob.Inference.Vocabulary.UImodelization import UImodelization
from netzob.Inference.Grammar.UIGrammarInference import UIGrammarInference
from netzob.Export.ScapyExport import ScapyExport
from netzob.Export.RawExport import RawExport
from netzob.Import.ApiImport import ApiImport
from netzob.Import.FileImport import FileImport
from netzob.Import.IpcImport import IpcImport
from netzob.Import.NetworkImport import NetworkImport
from netzob.Import.PcapImport import PcapImport
from netzob.Fuzzing.UIfuzzing import UIfuzzing

from netzob.Common.LoggingConfiguration import LoggingConfiguration
from netzob.Simulator.UISimulator import UISimulator
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.StateParser import StateParser
from netzob.Common.Groups import Groups
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.MMSTD.Tools.Parsers.MMSTDParser.MMSTDXmlParser import MMSTDXmlParser
from netzob.Common.Workspace import Workspace

#+---------------------------------------------- 
#| NetzobGUI :
#|     Graphical runtime class
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class NetzobGui():

    #+---------------------------------------------- 
    #| Constructor :
    #+----------------------------------------------   
    def __init__(self):
        
        # First we initialize and verify all the resources
        if not ResourcesConfiguration.initializeResources() :
            logging.fatal("Error while configuring the resources of Netzob")
            sys.exit()

        # loading the workspace
        self.currentWorkspace = Workspace.loadWorkspace(ResourcesConfiguration.getWorkspaceFile())
        self.currentProject = self.currentWorkspace.getLastProject()
        
        # Second we create the logging infrastructure
        LoggingConfiguration().initializeLogging(self.currentWorkspace)
                
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.py')
        self.log.info("Starting netzob")

        # Groups of messages are handled with the following object
        self.groups = Groups(self)

        # Main window definition
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_default_size(800, 600)
        window.set_title("Netzob : NETwork protocol modeliZatiOn By reverse engineering")
        
        window.set_icon_from_file(("%s/logo.png" % 
                                   ResourcesConfiguration.getStaticResources()))
        window.connect("delete_event", self.evnmtDelete)
        window.connect("destroy", self.destroy)
        main_vbox = gtk.VBox(False, spacing=0)
        
        # Main menu
#        menubar = self.get_main_menu(window)
        self.menu = Menu(self)
        menubar = self.menu.getMenuBar()
        main_vbox.pack_start(menubar, False, True, 0)
        
        self.menu.update()
        
        # Progress Bar handling inside UI Header
#        progressBox = gtk.VBox(False, 0)
#        progressBox.set_border_width(0)
#        align = gtk.Alignment(0.5, 0.5, 0, 0)
#        progressBox.pack_start(align, False, False, 5)
#        self.progressBar = gtk.ProgressBar()
#        align.add(self.progressBar)

        # Notebook definition
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.connect("switch-page", self.notebookFocus)
        main_vbox.pack_start(self.notebook, True, True, 0)

        self.pageList = []
        # Adding the different notebook
        self.modelization = UImodelization(self)
        self.grammarInference = UIGrammarInference(self)
        self.fuzzing = UIfuzzing(self)
        self.simulator = UISimulator(self)

        self.pageList.append(["Vocabulary inference", self.modelization])
        self.pageList.append(["Grammar inference", self.grammarInference])
        self.pageList.append(["Fuzzing", self.fuzzing])
        self.pageList.append(["Simulator", self.simulator])
        
        for page in self.pageList:
                self.notebook.append_page(page[1].panel, gtk.Label(page[0]))

        # Show every widgets
        self.notebook.show()
        main_vbox.show()
        window.add(main_vbox)
        window.show()
        
    def switchCurrentProject(self, project):        
        self.log.debug("The current project is : " + project.getName())
        self.currentProject = project
        for page in self.pageList:
            page[1].clear()
            page[1].update()
            page[1].new()            
        self.update()

    def getCurrentProject(self):
        return self.currentProject
    def getCurrentWorkspace(self):
        return self.currentWorkspace
        
    def offerToSaveCurrentProject(self):
        questionMsg = "Do you want to save the current project (" + self.getCurrentProject().getName() + ")"
        md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == gtk.RESPONSE_YES:
            logging.info("Saving the current project")
            self.getCurrentProject().saveConfigFile(self.getCurrentWorkspace())
        
    def startGui(self):
        # UI thread launching
        self.uiThread = threading.Thread(None, self.guiThread, None, (), {})
        self.uiThread.start()

    def evnmtDelete(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        
        # Before exiting, we compute if its necessary to save
        # it means we simulate a save and compare the XML with the current one
        if self.getCurrentProject() != None and self.getCurrentProject().hasPendingModifications() :
            self.offerToSaveCurrentProject()
        
        
        for page in self.pageList:
            page[1].kill()
        gtk.main_quit()

    def guiThread(self):
        gtk.main()

    #+---------------------------------------------- 
    #| Called when user select a notebook
    #+----------------------------------------------
    def notebookFocus(self, notebook, page, pagenum):
        nameTab = notebook.get_tab_label_text(notebook.get_nth_page(pagenum))
        for page in self.pageList:
            if page[0] == nameTab:
                page[1].update()

    

   
    #+---------------------------------------------- 
    #| Update each panels
    #+----------------------------------------------
    def update(self):
        for page in self.pageList:
            page[1].clear()
            page[1].update()
            
    def getDictionary(self):
        actorGrammar = "example_learning.xml"
        grammar_directory = ConfigurationParser().get("automata", "path") 
        xmlFile = os.path.join(grammar_directory, actorGrammar)
        tree = ElementTree()
        tree.parse(xmlFile)
        # Load the automata based on its XML definition
        serverAutomata = MMSTDXmlParser.loadFromXML(tree.getroot())
        return serverAutomata.getDictionary()
        

#+---------------------------------------------- 
#| RUNTIME
#+----------------------------------------------
if __name__ == "__main__":
    # for handling GUI access from threads
    gobject.threads_init()
        
    netZobGUI = NetzobGui()
    netZobGUI.startGui()
        
        
