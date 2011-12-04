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
        
    def get_main_menu(self, window):
        ui = '''
<ui>
  <menubar name="Menu">
    <menu action="Workspace">
      <menuitem action="CreateProject"/>
      <menu action="SelectProject">
      </menu>
      <menuitem action="ManageProjects"/>
      <menuitem action="Options"/>
      <menuitem action="Exit"/>
    </menu>
    <menu action="Project">
      <menuitem action="SaveProject"/>
      <menuitem action="ManageTraces"/>
      <menu action="Import">
        <menuitem action="CaptureNetworkTrafic"/>
        <menuitem action="ImportPcapFile"/>
        <menuitem action="CaptureIpcFlow"/>
        <menuitem action="CaptureApiFlow"/>
        <menuitem action="ImportFile"/>
      </menu>
      <menu action="ExportProject">
        <menuitem action="ExportScapy"/>
        <menuitem action="ExportWireshark"/>
        <menuitem action="ExportXML"/>
      </menu>
    </menu>
    <menu action="Help">
      <menuitem action="NetzobHelp"/>
      <menuitem action="About"/>
    </menu>
  </menubar>
</ui>
'''
        self.uiManager = gtk.UIManager()
        groupAcc = self.uiManager.get_accel_group()
        window.add_accel_group(groupAcc)
        self.uiActionGroup = gtk.ActionGroup('UImanager')
        self.uiActionGroup.add_actions([('Workspace', None, '_Workspace'),
                                        ('CreateProject', None, '_Create project (todo)', None,
                                         None, self.print_hello),
                                        ('SelectProject', None, '_Select existing project'),
                                        ('ManageProjects', None, '_Manage projects (todo)', None,
                                         None, self.print_hello),
                                        ('Options', None, '_Options (todo)', None,
                                         None, self.print_hello),
                                        ('Exit', gtk.STOCK_QUIT, '_Exit', None,
                                         'Exit the program', self.destroy)])
        self.uiActionGroup.add_actions([('Project', None, '_Project'),
                                        ('SaveProject', None, '_Save project', None,
                                         None, self.saveProject_cb),
                                        ('ManageTraces', None, '_Manage traces (todo)', None,
                                         None, self.print_hello),
                                        ('Import', None, '_Import', None),
                                        ('CaptureNetworkTrafic', None, '_Capture network trafic', None,
                                         None, self.importNetworkTrafic_cb),
                                        ('ImportPcapFile', None, '_Import PCAP file', None,
                                         None, self.importPcapFile_cb),
                                        ('CaptureIpcFlow', None, '_Capture IPC flow', None,
                                         None, self.importIpcFlow_cb),
                                        ('CaptureApiFlow', None, '_Capture API flow', None,
                                         None, self.importApiFlow_cb),
                                        ('ImportFile', None, '_Import file', None,
                                         None, self.importFile_cb),
                                        ('ExportProject', None, '_Export'),
                                        ('ExportScapy', None, '_Export as Scapy dissector', None,
                                         None, self.exportScapyDissector_cb),
                                        ('ExportWireshark', None, '_Export as Wireshark dissector', None,
                                         None, self.print_hello),
                                        ('ExportXML', None, '_Export in XML', None,
                                         None, self.exportRaw_cb)])
        self.uiActionGroup.add_actions([('Help', None, '_Help'),
                                        ('NetzobHelp', None, '_Netzob help (todo)', None,
                                         None, self.print_hello),
                                        ('About', None, '_About Netzob', None,
                                         None, self.aboutDialog)])
        self.uiActionGroup.get_action('Exit').set_property('short-label', '_Exit')
        self.uiManager.insert_action_group(self.uiActionGroup, 0)
        self.uiId = self.uiManager.add_ui_from_string(ui)
        self.updateListOfAvailableProjects()
        menu = self.uiManager.get_widget('/Menu')
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
        about.set_logo(gtk.gdk.pixbuf_new_from_file(logoPath))
        about.run()
        about.destroy()
        
    #+------------------------------------------------------------------------ 
    #| updateListOfAvailableProjects :
    #| @param entry the GTK entry in which the name of the available projects
    #|              will be added
    #+------------------------------------------------------------------------
    def updateListOfAvailableProjects(self):
        # retrieves the workspace directory path
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        if projectsDirectoryPath == "" :
            self.log.warn("No available projects directory found.")
            return 
               
        # A temporary list in which all the projects will be stored and then sorted
        tmpListOfProjects = []
         
        # List all the projects (except .svn)
        for tmpProject in os.listdir(projectsDirectoryPath):
            stateSaved = False
            if os.path.isfile(projectsDirectoryPath + os.sep + tmpProject) or tmpProject == '.svn':
                continue
            for aFile in os.listdir(projectsDirectoryPath + os.sep + tmpProject):
                if aFile == "config.xml":
                    stateSaved = True
                    continue
            if stateSaved == True:
                tmpListOfProjects.append([tmpProject, gtk.STOCK_INFO])
            else:
                tmpListOfProjects.append([tmpProject, ''])
        
        # Sort and add to the menu
        if len(tmpListOfProjects) == 0:
            self.uiId = self.uiManager.add_ui(self.uiId, "/Menu/Workspace/SelectProject", "EmptyProject", "EmptyProject", gtk.UI_MANAGER_MENUITEM, False)
            self.uiId = self.uiManager.new_merge_id()
            self.uiActionGroup.add_actions([('EmptyProject', None, '...', None, None, self.projectSelected_cb)])
        else:
            for (project, stock_id) in sorted(tmpListOfProjects) :
                self.uiManager.add_ui(self.uiId, "/Menu/Workspace/SelectProject", project, project, gtk.UI_MANAGER_MENUITEM, False)
                self.uiId = self.uiManager.new_merge_id()
                self.uiActionGroup.add_actions([(project, stock_id, project, None, None, self.projectSelected_cb)])

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
                
    def saveProject_cb(self, null):
        self.log.info("Starting the saving of the current project : " + str(self.currentProject))
        
        # Verify that there is a current project
        if self.currentProject == "" or self.currentProject == "..." or self.currentProject == None:
            self.log.info("No project selected")
            return

        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        projectConfigPath = projectsDirectoryPath + os.sep + self.currentProject + os.sep + "config.xml"
        
        for page in self.pageList:
            page[1].save(projectConfigPath)

    #+---------------------------------------------- 
    #| Called when user select a new project for analysis
    #+----------------------------------------------
    def projectSelected_cb(self, action):
        # retrieve the new project path
        project = action.get_name()
        if project == "" or project == None:
            return
        self.currentProject = project
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        projectPath = projectsDirectoryPath + os.sep + project

        # If a state saving exists, loads it
        for file in os.listdir(projectPath):
            filePath = projectPath + os.sep + file
            if file == "config.xml":
                self.log.info("A configuration file has been found, so we analyze and load it")
                stateParser = StateParser(projectPath + "/config.xml")
                stateParser.loadConfiguration()
                self.groups.setGroups(stateParser.getGroups())
        
        # clear past analysis and initialize the each notebook
        self.groups.clear()
        for page in self.pageList:
            page[1].clear()
            page[1].new()
            
        self.update()

    #+---------------------------------------------- 
    #| Called when user wants to export as Scapy dissector
    #+----------------------------------------------
    def exportScapyDissector_cb(self, action):
        scapyPanel = ScapyExport(self)
        dialog = gtk.Dialog(title="Export project as Scapy dissector", flags=0, buttons=None)
        dialog.show()
        dialog.vbox.pack_start(scapyPanel.getPanel(), True, True, 0)
        dialog.set_size_request(800, 700)
        scapyPanel.update()

    #+---------------------------------------------- 
    #| Called when user wants to export as raw XML
    #+----------------------------------------------
    def exportRaw_cb(self, action):
        rawExportPanel = RawExport(self)
        dialog = gtk.Dialog(title="Export project as raw XML", flags=0, buttons=None)
        dialog.show()
        dialog.vbox.pack_start(rawExportPanel.getPanel(), True, True, 0)
        dialog.set_size_request(800, 700)
        rawExportPanel.update()

    #+---------------------------------------------- 
    #| Called when user wants to import network trafic
    #+----------------------------------------------
    def importNetworkTrafic_cb(self, action):
        networkImportPanel = NetworkImport(self)
        dialog = gtk.Dialog(title="Capture network trafic", flags=0, buttons=None)
        dialog.show()
        dialog.vbox.pack_start(networkImportPanel.getPanel(), True, True, 0)
        dialog.set_size_request(900, 700)

    #+---------------------------------------------- 
    #| Called when user wants to import PCAP file
    #+----------------------------------------------
    def importPcapFile_cb(self, action):
        pcapImportPanel = PcapImport(self)
        dialog = gtk.Dialog(title="Import PCAP file", flags=0, buttons=None)
        dialog.show()
        dialog.vbox.pack_start(pcapImportPanel.getPanel(), True, True, 0)
        dialog.set_size_request(900, 700)

    #+---------------------------------------------- 
    #| Called when user wants to import IPC flow
    #+----------------------------------------------
    def importIpcFlow_cb(self, action):
        ipcImportPanel = IpcImport(self)
        dialog = gtk.Dialog(title="Capture IPC flow", flags=0, buttons=None)
        dialog.show()
        dialog.vbox.pack_start(ipcImportPanel.getPanel(), True, True, 0)
        dialog.set_size_request(900, 700)

    #+---------------------------------------------- 
    #| Called when user wants to import API flow
    #+----------------------------------------------
    def importApiFlow_cb(self, action):
        apiImportPanel = ApiImport(self)
        dialog = gtk.Dialog(title="Capture API flow", flags=0, buttons=None)
        dialog.show()
        dialog.vbox.pack_start(apiImportPanel.getPanel(), True, True, 0)
        dialog.set_size_request(900, 700)

    #+---------------------------------------------- 
    #| Called when user wants to import file
    #+----------------------------------------------
    def importFile_cb(self, action):
        fileImportPanel = FileImport(self)
        dialog = gtk.Dialog(title="Import file", flags=0, buttons=None)
        dialog.show()
        dialog.vbox.pack_start(fileImportPanel.getPanel(), True, True, 0)
        dialog.set_size_request(900, 700)

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
        
        
