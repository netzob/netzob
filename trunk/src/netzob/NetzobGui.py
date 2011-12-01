#!/usr/bin/env python
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

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import gtk
import gobject
import os
import threading
import sys
import logging
from time import sleep



#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
sys.path.append('lib/')
sys.path.append('lib/libNeedleman/')
from xml.etree import ElementTree
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Inference.Vocabulary.UImodelization import UImodelization
from netzob.Inference.Grammar.UIGrammarInference import UIGrammarInference
from netzob.Export.UIexport import UIexport
from netzob.Import.UIimport import UIimport
from netzob.Fuzzing.UIfuzzing import UIfuzzing

from netzob.Common.LoggingConfiguration import LoggingConfiguration
from netzob.Simulator.UISimulator import UISimulator
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.StateParser import StateParser
from netzob.Common.Groups import Groups
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.MMSTD.Tools.Parsers.MMSTDParser.MMSTDXmlParser import MMSTDXmlParser
#+---------------------------------------------- 
#| NetzobGUI :
#|     Graphical runtime class
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class NetzobGui():

    #+---------------------------------------------- 
    #| Constructor :
    #| @param path: path of the directory containing traces to parse 
    #+----------------------------------------------   
    def __init__(self):
        
        # First we initialize and verify all the resources
        if not ResourcesConfiguration.initializeResources() :
            logging.fatal("Error while configuring the resources of Netzob")
            sys.exit()
           
#        splashScreen = SplashScreen.SplashScreen()
#        while gtk.events_pending():
#            gtk.main_iteration()
#        sleep(3) 
#        splashScreen.window.destroy() 
        
        # Second we create the logging infrastructure
        LoggingConfiguration().initializeLogging()
                
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.py')
        
        self.log.info("Starting netzob")
        self.tracePath = ""

        # Groups of messages are handled with the following object
        self.groups = Groups(self)

        # Main window definition
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Netzob : NETwork protocol modeliZatiOn By reverse engineering")
        
        window.set_icon_from_file(("%s/logo.png" % 
                                   ResourcesConfiguration.getStaticResources()))
        window.connect("delete_event", self.evnmtDelete)
        window.connect("destroy", self.destroy)
        main_vbox = gtk.VBox(False, spacing=0)
        
        # Main menu
        menubar = self.get_main_menu(window)
        main_vbox.pack_start(menubar, False, True, 0)
        
        ## UI Header definition
        toolbar = gtk.HBox(False, spacing=0)
        main_vbox.pack_start(toolbar, False, False, 2)

        label = gtk.Label("Select trace : ")
#        menu = gtk.Menu()
#        gtk.MenuItem("")

        liststore = gtk.ListStore(str, str)
        self.entry = gtk.ComboBox(liststore)
        cellText = gtk.CellRendererText()
        self.entry.pack_start(cellText, True)
        self.entry.add_attribute(cellText, 'text', 0)
        cellImage = gtk.CellRendererPixbuf()
        self.entry.pack_start(cellImage, False)
        self.entry.add_attribute(cellImage, 'stock_id', 1)

#        self.entry = gtk.combo_box_entry_new_text()
#        self.entry.set_size_request(200, -1)
        self.entry.connect("changed", self.traceSelected)
        self.updateListOfAvailableTraces()       
      
        label_text = gtk.Label("     Current trace : ")
        self.label_analyse = gtk.Label("...")

        button_save = gtk.Button(gtk.STOCK_OK)
        button_save.set_label("Save trace")
        button_save.connect("clicked", self.saveTrace)

        # Progress Bar handling inside UI Header
        progressBox = gtk.VBox(False, 0)
        progressBox.set_border_width(0)
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        progressBox.pack_start(align, False, False, 5)
        self.progressBar = gtk.ProgressBar()
        align.add(self.progressBar)

        toolbar.pack_start(label, False, False, 5)
        toolbar.pack_start(self.entry, False, False, 5)
        toolbar.pack_start(label_text, False, False, 5)
        toolbar.pack_start(self.label_analyse, False, False, 5)
        toolbar.pack_start(button_save, False, False, 5)
        toolbar.pack_start(progressBox, False, False, 5)

        # Notebook definition
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.connect("switch-page", self.notebookFocus)
        main_vbox.pack_start(self.notebook, True, True, 0)

        self.pageList = []
        # Adding the different notebook
        self.Import = UIimport(self)
        self.modelization = UImodelization(self)
        self.grammarInference = UIGrammarInference(self)
        self.export = UIexport(self)
        self.fuzzing = UIfuzzing(self)
        self.simulator = UISimulator(self)

        self.pageList.append(["Import", self.Import])
        self.pageList.append(["Vocabulary inference", self.modelization])
        self.pageList.append(["Grammar inference", self.grammarInference])
        self.pageList.append(["Fuzzing", self.fuzzing])
        self.pageList.append(["Export", self.export])
        self.pageList.append(["Simulator", self.simulator])
        
        for page in self.pageList:
                self.notebook.append_page(page[1].panel, gtk.Label(page[0]))

        # Show every widgets
        toolbar.show()
        self.entry.show()
        label.show()
        label_text.show()
        self.label_analyse.show()
        button_save.show()
        self.notebook.show()
        progressBox.show()
        align.show()
        self.progressBar.show()
        main_vbox.show()
        window.add(main_vbox)
        window.show()
        
    def get_main_menu(self, window):
        ui = '''<ui>
    <menubar name="Menu">
      <menu action="Workspace">
        <menuitem action="CreateProject"/>
        <menuitem action="SelectProject"/>
        <menuitem action="Options"/>
        <menuitem action="Exit"/>
      </menu>
      <menu action="Project">
        <menuitem action="ImportTrace"/>
        <menuitem action="ExportScapy"/>
        <menuitem action="ExportWireshark"/>
        <menuitem action="ExportXML"/>
      </menu>
      <menu action="Help">
        <menuitem action="NetzobHelp"/>
        <menuitem action="About"/>
      </menu>
    </menubar>
    </ui>'''
        gestionui = gtk.UIManager()
        grouperacc = gestionui.get_accel_group()
        window.add_accel_group(grouperacc)
        groupeactions = gtk.ActionGroup('ExempleUIGestion')
        groupeactions.add_actions([('Workspace', None, '_Workspace'),
                                   ('CreateProject', None, '_Create project', None,
                                    None, self.print_hello),
                                   ('SelectProject', None, '_Select existing project', None,
                                    None, self.print_hello),
                                   ('Options', None, '_Options', None,
                                    None, self.print_hello),
                                   ('Exit', gtk.STOCK_QUIT, '_Exit', None,
                                    'Exit the program', self.destroy)])
        groupeactions.add_actions([('Project', None, '_Project'),
                                   ('ImportTrace', None, '_Import trace', None,
                                    None, self.print_hello),
                                   ('ExportScapy', None, '_Export as Scapy dissector', None,
                                    None, self.print_hello),
                                   ('ExportWireshark', None, '_Export as Wireshark dissector', None,
                                    None, self.print_hello),
                                   ('ExportXML', None, '_Export in XML', None,
                                    None, self.print_hello)])
        groupeactions.add_actions([('Help', None, '_Help'),
                                   ('NetzobHelp', None, '_Netzob help', None,
                                    None, self.print_hello),
                                   ('About', None, '_About Netzob', None,
                                    None, self.aboutDialog)])
        groupeactions.get_action('Exit').set_property('short-label', '_Exit')
        gestionui.insert_action_group(groupeactions, 0)
        gestionui.add_ui_from_string(ui)

        menu = gestionui.get_widget('/Menu')
        return menu

    def print_hello(self):
        pass

    def aboutDialog(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name("Netzob")
        about.set_version("0.3")
        about.set_copyright("(c) Georges Bossert & Frédéric Guihéry")
        about.set_comments("Communication protocol modelization by reverse engineering")
        about.set_website("http://www.netzob.org")
        logoPath = os.path.join(ResourcesConfiguration.getStaticResources(), "logo.png")
        about.set_logo(gtk.gdk.pixbuf_new_from_file(logoPath)) # TODO: find the good path
        about.run()
        about.destroy()
        
    #+------------------------------------------------------------------------ 
    #| updateListOfAvailableTraces :
    #| @param entry the GTK entry in which the name of the available traces
    #|              will be added
    #+------------------------------------------------------------------------
    def updateListOfAvailableTraces(self):
        self.entry.get_model().clear()
        # retrieves the trace directory path
        tracesDirectoryPath = ConfigurationParser().get("traces", "path")
        if tracesDirectoryPath == "" :
            self.log.warn("No available traces directory was found.")
            return 
               
        # a temporary list in which all the folders will be stored and after sorted
        temporaryListOfFolders = []
         
        # list all the directories (except .svn)
        for tmpDir in os.listdir(tracesDirectoryPath):
            stateSaved = False
            pathOfTrace = tracesDirectoryPath + "/" + tmpDir
            
            if os.path.isfile(pathOfTrace) or tmpDir == '.svn':
                continue
            
            
            for aFile in os.listdir(pathOfTrace):
                if aFile == "config.xml":
                    stateSaved = True
                    continue
            if stateSaved == True:
                temporaryListOfFolders.append([tmpDir, gtk.STOCK_INFO])
            else:
                temporaryListOfFolders.append([tmpDir, ''])
        
        # Sort and add to the entry
        for folder in sorted(temporaryListOfFolders) :
            self.entry.get_model().append(folder)

    def startGui(self):
        # UI thread launching
        self.uiThread = threading.Thread(None, self.guiThread, None, (), {})
        self.uiThread.start()

    def evnmtDelete(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
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
                
    def saveTrace(self, null):
        self.log.info("Starting the saving process of all the application")
        
        # retrieve the new trace path
        target = self.entry.get_active_text()
        if target == "" or target == "..." or target == None:
            self.log.info("No trace selected")
            return

        tracesDirectoryPath = ConfigurationParser().get("traces", "path")
        configPath = tracesDirectoryPath + os.sep + target + os.sep + "config.xml"
        
        for page in self.pageList:
            page[1].save(configPath)

    #+---------------------------------------------- 
    #| Called when user select a new trace for analysis
    #+----------------------------------------------
    def traceSelected(self, null):
        # retrieve the new trace path
        target = self.entry.get_active_text()
        if target == "" or target == None:
            return
        tracesDirectoryPath = ConfigurationParser().get("traces", "path")
        self.label_analyse.set_text(target)
        self.tracePath = tracesDirectoryPath + os.sep + target

        # If a state saving exists, loads it
        for file in os.listdir(self.tracePath):
            filePath = self.tracePath + "/" + file
            if file == "config.xml":
                self.log.info("A configuration file has been found, so we analyze and load it")
                stateParser = StateParser(self.tracePath + "/config.xml")
                stateParser.loadConfiguration()
                self.groups.setGroups(stateParser.getGroups())
        
        # clear past analysis and initialize the each notebook
        self.groups.clear()
        for page in self.pageList:
            page[1].clear()
            #nameTab = self.notebook.get_tab_label_text(self.notebook.get_nth_page(self.notebook.get_current_page()))
            #if page[0] == nameTab:
            page[1].new()
            
        self.update()

    #+---------------------------------------------- 
    #| Update each panels
    #+----------------------------------------------
    def update(self):
        for page in self.pageList:
            page[1].update()
            
    def getDictionary(self):
        actorGrammar = "example_learning.xml"
        grammar_directory = ConfigurationParser().get("automata", "path") 
        xmlFile = os.path.join(grammar_directory, actorGrammar)
        tree = ElementTree.ElementTree()
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
        
        
