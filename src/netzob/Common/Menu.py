# -*- coding: utf-8 -*-


#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import gtk
import logging
import os

#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+
from netzob.Common.Project import Project
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Import.NetworkImport import NetworkImport
from netzob.Import.PcapImport import PcapImport
#from netzob.Import.IpcImport import IpcImport
from netzob.Import.FileImport import FileImport
from netzob.Export.ScapyExport import ScapyExport
from netzob.Export.RawExport import RawExport
from netzob.Export.TextExport import TextExport
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.TraceManager import TraceManager
from netzob import release

#+---------------------------------------------------------------------------+
#| Menu:
#|     Class definition of the menu
#+---------------------------------------------------------------------------+
class Menu(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #|   Creation of the menu
    #+-----------------------------------------------------------------------+
    def __init__(self, netzob):
        self.netzob = netzob

        # creation of the menu entries
        self.menuBar = gtk.MenuBar()

        # Creation of the Workspace menu
        self.createWorkspaceMenu()

        # Creation of the Project menu
        self.createProjectMenu()

        # Creation of the View menu
        self.createViewMenu()

        # Creation of the Help menu
        self.createHelpMenu()

        self.menuBar.show_all()

    def createHelpMenu(self):
        self.menuHelp = gtk.Menu()

        menuRootHelp = gtk.MenuItem("Help")
        menuRootHelp.set_submenu(self.menuHelp)

        self.helpContent = gtk.MenuItem("Help Contents")
        self.menuHelp.append(self.helpContent)

        self.about = gtk.MenuItem("About Netzob")
        self.about.connect("activate", self.aboutDialogAction)

        self.menuHelp.append(self.about)

        self.menuBar.append(menuRootHelp)

    def createProjectMenu(self):
        self.menuProject = gtk.Menu()

        menuRootProject = gtk.MenuItem("Project")
        menuRootProject.set_submenu(self.menuProject)

        self.saveProject = gtk.MenuItem("Save project")
        self.saveProject.connect("activate", self.saveProjectAction)
        self.menuProject.append(self.saveProject)

        self.menuImport = gtk.Menu()
        self.importRootMenu = gtk.MenuItem("Import traces")
        self.importRootMenu.set_submenu(self.menuImport)

        captureNetworkTracesEntry = gtk.MenuItem("Capture network traces")
        captureNetworkTracesEntry.connect("activate", self.importNetworkTraficAction)
        self.menuImport.append(captureNetworkTracesEntry)

        captureIPCFlowsEntry = gtk.MenuItem("Capture IPC flows")
        captureIPCFlowsEntry.connect("activate", self.importIPCFlowsAction)
        self.menuImport.append(captureIPCFlowsEntry)

        importPCAPFileEntry = gtk.MenuItem("Import from PCAP")
        importPCAPFileEntry.connect("activate", self.importPcapAction)
        self.menuImport.append(importPCAPFileEntry)

        importFileEntry = gtk.MenuItem("Import from File")
        importFileEntry.connect("activate", self.importFileAction)
        self.menuImport.append(importFileEntry)

        self.menuProject.append(self.importRootMenu)

        self.menuExport = gtk.Menu()
        self.exportRootMenu = gtk.MenuItem("Export project")
        self.exportRootMenu.set_submenu(self.menuExport)

        exportScapyEntry = gtk.MenuItem("Scapy dissector")
        exportScapyEntry.connect("activate", self.exportScapyAction)
#        self.menuExport.append(exportScapyEntry)

        exportWiresharkEntry = gtk.MenuItem("Wireshark dissector")
        exportWiresharkEntry.connect("activate", self.exportWiresharkAction)
#        self.menuExport.append(gtk.MenuItem("Wireshark dissector"))

        exportXMLEntry = gtk.MenuItem("XML")
        exportXMLEntry.connect("activate", self.exportXMLAction)
        self.menuExport.append(exportXMLEntry)

        exportTextEntry = gtk.MenuItem("Text")
        exportTextEntry.connect("activate", self.exportTextAction)
        self.menuExport.append(exportTextEntry)

        self.menuProject.append(self.exportRootMenu)

        self.menuBar.append(menuRootProject)

    def updateProjectMenu(self):
        if self.netzob.getCurrentProject() == None:
            # Deactivate almost everything
            self.saveProject.set_sensitive(False)
            self.importRootMenu.set_sensitive(False)
            self.exportRootMenu.set_sensitive(False)
            self.helpContent.set_sensitive(False)
        else:
            # Activate everything
            self.saveProject.set_sensitive(True)
            self.importRootMenu.set_sensitive(True)
            self.exportRootMenu.set_sensitive(True)
            self.displaySymbolStructure.set_sensitive(True)
            self.displayMessages.set_sensitive(True)
            self.displayConsole.set_sensitive(False)
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE)
            self.displaySymbolStructure.set_active(isActive)
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES)
            self.displayMessages.set_active(isActive)
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_CONSOLE)
            self.displayConsole.set_active(isActive)

    def createViewMenu(self):
        self.menuView = gtk.Menu()

        menuRootView = gtk.MenuItem("View")
        menuRootView.set_submenu(self.menuView)

        self.displaySymbolStructure = gtk.CheckMenuItem("Display symbol structure")
        self.displaySymbolStructure.connect("activate", self.displaySymbolStructureAction)
        self.menuView.append(self.displaySymbolStructure)
        self.displaySymbolStructure.set_sensitive(False)

        self.displayMessages = gtk.CheckMenuItem("Display messages")
        self.displayMessages.connect("activate", self.displayMessagesAction)
        self.menuView.append(self.displayMessages)
        self.displayMessages.set_sensitive(False)

        self.displayConsole = gtk.CheckMenuItem("Display console")
        self.displayConsole.connect("activate", self.displayConsoleAction)
        self.menuView.append(self.displayConsole)
        self.displayConsole.set_sensitive(False)

        self.menuBar.append(menuRootView)

    def createWorkspaceMenu(self):

        self.menuWorkspace = gtk.Menu()

        agr = gtk.AccelGroup()
        self.netzob.add_accel_group(agr)

        menuRootWorkspace = gtk.MenuItem("Workspace")
        menuRootWorkspace.set_submenu(self.menuWorkspace)

        self.createProject = gtk.MenuItem("Create a project")
        self.createProject.connect("activate", self.createProjectAction)
        self.menuWorkspace.append(self.createProject)

        self.selectAProject = gtk.Menu()
        selectAProjectRoot = gtk.MenuItem("Switch project")
        selectAProjectRoot.set_submenu(self.selectAProject)
        self.menuWorkspace.append(selectAProjectRoot)

        self.manageProject = gtk.MenuItem("Manage projects")
        self.menuWorkspace.append(self.manageProject)

        self.manageTraces = gtk.MenuItem("Manage traces")
        self.manageTraces.connect("activate", self.manageTracesAction)
        self.menuWorkspace.append(self.manageTraces)

        self.options = gtk.MenuItem("Options")
        self.menuWorkspace.append(self.options)

        self.switchWorkspace = gtk.MenuItem("Switch workspace")
        self.menuWorkspace.append(self.switchWorkspace)

        self.exit = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
        key, mod = gtk.accelerator_parse("<Control>Q")
        self.exit.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
        self.exit.connect("activate", self.exitAction)

        self.menuWorkspace.append(self.exit)
        self.menuBar.append(menuRootWorkspace)

    def updateWorkspaceMenu(self):
        self.createProject.set_sensitive(True)
        self.manageTraces.set_sensitive(True)
        self.manageProject.set_sensitive(False)
        self.options.set_sensitive(False)
        self.switchWorkspace.set_sensitive(False)
        self.exit.set_sensitive(True)

        # Update the list of project
        for i in self.selectAProject.get_children():
            self.selectAProject.remove(i)
        for project in self.netzob.getCurrentWorkspace().getProjects():
            projectEntry = gtk.MenuItem(project.getName())
            projectEntry.connect("activate", self.switchProjectAction, project)
            self.selectAProject.append(projectEntry)
        self.selectAProject.show_all()

    def update(self):
        self.updateWorkspaceMenu()
        self.updateProjectMenu()

    def getMenuBar(self):
        return self.menuBar

    def exitAction(self, widget):
        self.netzob.destroy(widget)

    #+----------------------------------------------
    #| Called when user wants to manage the traces
    #+----------------------------------------------
    def manageTracesAction(self, widget):
        TraceManager(self.netzob.getCurrentWorkspace(), self.netzob.update)

    def switchProjectAction(self, widget, newProject):
        self.netzob.switchCurrentProject(newProject)
        self.update()

    #+----------------------------------------------
    #| Called when user wants to import network trafic
    #+----------------------------------------------
    def importNetworkTraficAction(self, widget):
        networkImportPanel = NetworkImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import PCAP file
    #+----------------------------------------------
    def importPcapAction(self, widget):
        pcapImportPanel = PcapImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import IPC flow
    #+----------------------------------------------
    def importIPCFlowsAction(self, widget):
        ipcImportPanel = IpcImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import file
    #+----------------------------------------------
    def importFileAction(self, widget):
        fileImportPanel = FileImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to export as Scapy dissector
    #+----------------------------------------------
    def exportScapyAction(self, widget):
        scapyPanel = ScapyExport(self.netzob)

    def exportWiresharkAction(self, widget):
#        wiresharkPanel = WireS(self.netzob)
        pass

    #+----------------------------------------------
    #| Called when user wants to export as raw XML
    #+----------------------------------------------
    def exportXMLAction(self, action):
        rawExportPanel = RawExport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to export as text
    #+----------------------------------------------
    def exportTextAction(self, action):
        textExportPanel = TextExport(self.netzob)

#    #+----------------------------------------------
#    #| Called when user wants to import API flow
#    #+----------------------------------------------
#    def importApiFlow_cb(self, action):
#        apiImportPanel = ApiImport(self)
#        dialog = gtk.Dialog(title="Capture API flow", flags=0, buttons=None)
#        dialog.show()
#        dialog.vbox.pack_start(apiImportPanel.getPanel(), True, True, 0)
#        dialog.set_size_request(900, 700)

    #+----------------------------------------------
    #| Called when user wants to display symbol structure panel
    #+----------------------------------------------
    def displaySymbolStructureAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE, self.displaySymbolStructure.get_active())
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display messages panel
    #+----------------------------------------------
    def displayMessagesAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES, self.displayMessages.get_active())
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display the console
    #+----------------------------------------------
    def displayConsoleAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_CONSOLE, self.displayConsole.get_active())
        self.netzob.updateCurrentPanel()

    def aboutDialogAction(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name(release.appname)
        about.set_version(release.version)
        about.set_copyright(release.copyright)
        about.set_comments(release.description)
        about.set_website(release.url)
        logoPath = os.path.join(ResourcesConfiguration.getStaticResources(), "logo.png")
        about.set_logo(gtk.gdk.pixbuf_new_from_file(logoPath))
        about.run()
        about.destroy()

    #+----------------------------------------------
    #| Called when user save the current project
    #+----------------------------------------------
    def saveProjectAction(self, widget):
        logging.info("Starting the saving of the current project : " + str(self.netzob.getCurrentProject().getName()))
        self.netzob.getCurrentProject().saveConfigFile(self.netzob.getCurrentWorkspace())

    def createProjectAction(self, widget):
        dialog = gtk.Dialog(title="Create a new project", flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()
        label = gtk.Label("New project name")
        label.show()
        entry = gtk.Entry()
        entry.show()
        but = gtk.Button("Create project")
        but.connect("clicked", self.createProjectAction_cb, entry, dialog)
        but.show()
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        dialog.action_area.pack_start(table, True, True, 0)

    #+----------------------------------------------
    #| Creation of a new project from
    #+----------------------------------------------
    def createProjectAction_cb(self, button, entry, dialog):
        projectName = entry.get_text()

        # We verify the project name doesn't already exist
        found = False
        for project in  self.netzob.getCurrentWorkspace().getProjects():
            if project.getName() == projectName:
                found = True
        if found:
            dialogBis = gtk.Dialog(title="Error", flags=0, buttons=None)
            label = gtk.Label("This project name already exists")
            label.show()
            dialogBis.action_area.pack_start(label, True, True, 0)
            dialogBis.set_size_request(250, 50)
            dialogBis.show()
            dialog.destroy()
            return

        # Creation of the project
        project = Project.createProject(self.netzob.getCurrentWorkspace(), projectName)
        self.netzob.switchCurrentProject(project)

        # Refresh menu
        self.update()
        dialog.destroy()
