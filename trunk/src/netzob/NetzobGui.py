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
from netzob.Common.Project import Project


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
        
#        splashScreen = SplashScreen.SplashScreen()
#        while gtk.events_pending():
#            gtk.main_iteration()
#        sleep(3) 
#        splashScreen.window.destroy() 
        
        # loading the workspace
        self.currentWorkspace = Workspace.loadWorkspace(ResourcesConfiguration.getWorkspaceFile())
        self.currentProject = None
        
        # Second we create the logging infrastructure
        LoggingConfiguration().initializeLogging(self.currentWorkspace)
                
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
        
    def getCurrentProject(self):
        return self.currentProject
    def getCurrentWorkspace(self):
        return self.currentWorkspace
        
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
                                        ('CreateProject', None, '_Create project', None,
                                         None, self.createProject_cb),
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
    #+------------------------------------------------------------------------
    def updateListOfAvailableProjects(self):
        # retrieves all the project references in current workspace
        projects = self.getCurrentWorkspace().getProjects()
        
        # Sort and add to the menu
        if len(projects) == 0:
            self.uiId = self.uiManager.add_ui(self.uiId, "/Menu/Workspace/SelectProject", "EmptyProject", "EmptyProject", gtk.UI_MANAGER_MENUITEM, False)
            self.uiId = self.uiManager.new_merge_id()
            self.uiActionGroup.add_actions([('EmptyProject', None, '...', None, None, self.projectSelected_cb)])
        else:
            for (project) in sorted(projects) :
                self.uiManager.add_ui(self.uiId, "/Menu/Workspace/SelectProject", project.getName(), project.getName(), gtk.UI_MANAGER_MENUITEM, False)
                self.uiId = self.uiManager.new_merge_id()
                
                # If an action for the current project entry exist with delete it
                aAction = self.uiActionGroup.get_action(project.getName())
                if aAction != None:
                    self.uiActionGroup.remove_action(aAction)
                    
                # Specify an action for current project through the callback (project is the use data)   
                self.uiActionGroup.add_actions([(project.getName(), "", project.getName(), None, None, self.projectSelected_cb)], project)

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

    #+---------------------------------------------- 
    #| Called when user create a new project
    #+----------------------------------------------
    def createProject_cb(self, action):
        dialog = gtk.Dialog(title="Create a new project", flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()
        label = gtk.Label("New project name")
        label.show()
        entry = gtk.Entry()
        entry.show()
        but = gtk.Button("Create project")
        but.connect("clicked", self.createProject_cb_cb, entry, dialog)
        but.show()
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        dialog.action_area.pack_start(table, True, True, 0)
        

    #+---------------------------------------------- 
    #| Creation of a new project from
    #+----------------------------------------------
    def createProject_cb_cb(self, button, entry, dialog):
        
        projectName = entry.get_text()
        
        # We verify the project name doesn't already exist
        found = False
        for project in  self.getCurrentWorkspace().getProjects() :
            if project.getName() == projectName :
                found = True
        if found :
            dialogBis = gtk.Dialog(title="Error", flags=0, buttons=None)
            label = gtk.Label("This project name already exists")
            label.show()
            dialogBis.action_area.pack_start(label, True, True, 0)
            dialogBis.set_size_request(250, 50)
            dialogBis.show()
            
            return
        
        # Creation of the project
        project = Project.createProject(self.getCurrentWorkspace(), projectName)
        
        self.updateListOfAvailableProjects()

    #+---------------------------------------------- 
    #| Called when user save the current project
    #+----------------------------------------------                
    def saveProject_cb(self, null):
        self.log.info("Starting the saving of the current project : " + str(self.currentProject))
        
        # Verify that there is a current project
        if self.getCurrentProject() == None:
            self.log.info("No project selected")
            return
        
        self.getCurrentProject().saveConfigFile(self.getCurrentWorkspace())
#
#        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
#        projectConfigPath = projectsDirectoryPath + os.sep + self.currentProject + os.sep + "config.xml"
#        
#        for page in self.pageList:
#            page[1].save(projectConfigPath)

    #+---------------------------------------------- 
    #| Called when user select a new project for analysis
    #+----------------------------------------------
    def projectSelected_cb(self, action, project):
        self.log.debug("The current project is : " + project.getName())
        self.currentProject = project
        
        # We update all the pages of the gui
        for page in self.pageList:
            page[1].clear()
            page[1].update()
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
        

    #+---------------------------------------------- 
    #| Called when user wants to import PCAP file
    #+----------------------------------------------
    def importPcapFile_cb(self, action):
        pcapImportPanel = PcapImport(self)
        
    #+---------------------------------------------- 
    #| Called when user wants to import IPC flow
    #+----------------------------------------------
    def importIpcFlow_cb(self, action):
        ipcImportPanel = IpcImport(self)
        

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
        
        
