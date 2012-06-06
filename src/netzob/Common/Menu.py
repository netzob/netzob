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
from lxml.etree import ElementTree
import uuid
import shutil

#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+
from netzob.Common.Project import Project
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.SessionManager import SessionManager
from netzob.Import.NetworkImport import NetworkImport
from netzob.Import.PcapImport import PcapImport
from netzob.Import.ThirdPartyImport import ThirdPartyImport
if os.name == 'posix':
    from netzob.Import.IpcImport import IpcImport
from netzob.Import.FileImport import FileImport
from netzob.Import.XMLImport import XMLImport
from netzob.Export.ScapyExport import ScapyExport
from netzob.Export.RawExport import RawExport
from netzob.Export.TextExport import TextExport
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.TraceManager import TraceManager
from netzob.UI.NetzobWidgets import NetzobInfoMessage, NetzobErrorMessage
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

        self.sessionManager = gtk.MenuItem("Session manager")
        self.sessionManager.connect("activate", self.sessionManagerAction)
        # TODO
        # self.menuProject.append(self.sessionManager)

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

        importXMLEntry = gtk.MenuItem("Import from XML File")
        importXMLEntry.connect("activate", self.importXMLAction)
        self.menuImport.append(importXMLEntry)

        importThirdPartyEntry = gtk.MenuItem("Import from Third parties")
        importThirdPartyEntry.connect("activate", self.importThirdParty)
        self.menuImport.append(importThirdPartyEntry)

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
            self.sessionManager.set_sensitive(False)
            self.importRootMenu.set_sensitive(False)
            self.exportRootMenu.set_sensitive(False)
            self.helpContent.set_sensitive(False)
        else:
            # Activate everything
            self.saveProject.set_sensitive(True)
            self.sessionManager.set_sensitive(True)
            self.importRootMenu.set_sensitive(True)
            self.exportRootMenu.set_sensitive(True)
            self.displaySymbolStructure.set_sensitive(True)
            self.displayMessages.set_sensitive(True)
            self.displaySearchView.set_sensitive(True)
            self.displayPropertiesView.set_sensitive(True)
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE)
            self.displaySymbolStructure.set_active(isActive)
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES)
            self.displayMessages.set_active(isActive)
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH)
            self.displaySearchView.set_active(isActive)
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES)
            self.displayPropertiesView.set_active(isActive)

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

        self.displaySearchView = gtk.CheckMenuItem("Display search results")
        self.displaySearchView.connect("activate", self.displaySearchAction)
        self.menuView.append(self.displaySearchView)
        self.displaySearchView.set_sensitive(False)

        self.displayPropertiesView = gtk.CheckMenuItem("Display properties")
        self.displayPropertiesView.connect("activate", self.displayPropertiesAction)
        self.menuView.append(self.displayPropertiesView)
        self.displayPropertiesView.set_sensitive(False)

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
        self.selectAProjectRoot = gtk.MenuItem("Switch project")
        self.selectAProjectRoot.set_submenu(self.selectAProject)
        self.menuWorkspace.append(self.selectAProjectRoot)

        self.importProject = gtk.MenuItem("Import a project")
        self.importProject.connect("activate", self.importProjectAction)
        self.menuWorkspace.append(self.importProject)

        self.exportProject = gtk.MenuItem("Export a project")
        self.exportProject.connect("activate", self.exportProjectAction)
        self.menuWorkspace.append(self.exportProject)

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
        self.importProject.set_sensitive(True)
        self.manageTraces.set_sensitive(True)
        self.manageProject.set_sensitive(False)
        self.options.set_sensitive(False)
        self.switchWorkspace.set_sensitive(False)
        self.exit.set_sensitive(True)
        if self.netzob.getCurrentProject() == None:
            self.exportProject.set_sensitive(False)
        else:
            self.exportProject.set_sensitive(True)

        # Update the list of project
        for i in self.selectAProject.get_children():
            self.selectAProject.remove(i)

        availableProjectsName = self.netzob.getCurrentWorkspace().getNameOfProjects()
        for (projectName, projectFile) in availableProjectsName:
            projectEntry = gtk.MenuItem(projectName)
            projectEntry.connect("activate", self.switchProjectAction, projectFile)
            self.selectAProject.append(projectEntry)
        self.selectAProject.show_all()

        # Deactivate the global 'switch menu' if no project is available
        if len(availableProjectsName) == 0:
            self.selectAProjectRoot.set_sensitive(False)
        else:
            self.selectAProjectRoot.set_sensitive(True)

    def update(self):
        self.updateWorkspaceMenu()
        self.updateProjectMenu()

    def getMenuBar(self):
        return self.menuBar

    def exitAction(self, widget):
        self.netzob.destroy(widget)

    def setDisplaySearchViewActiveStatus(self, status):
        self.displaySearchView.set_active(status)

    #+----------------------------------------------
    #| Called when user wants to manage the traces
    #+----------------------------------------------
    def manageTracesAction(self, widget):
        TraceManager(self.netzob.getCurrentWorkspace(), self.netzob.update)

    def switchProjectAction(self, widget, projectPath):
        newProject = Project.loadProject(self.netzob.getCurrentWorkspace(), projectPath)
        if newProject == None:
            logging.error("Impossible to switch to requested project due to an error in the loading process.")
            return

        # Loading the project based on its name
        self.netzob.switchCurrentProject(newProject)
        self.update()

    #+----------------------------------------------
    #| Called when user wants to export a project
    #+----------------------------------------------
    def importProjectAction(self, widget):
        chooser = gtk.FileChooserDialog(title="Export as", action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            fileName = chooser.get_filename()
        chooser.destroy()

        if os.path.isfile(fileName):
            idProject = str(uuid.uuid4())
            # First we verify and create if necessary the directory of the project
            projectPath = "projects/" + idProject + "/"
            destPath = os.path.join(os.path.join(self.netzob.getCurrentWorkspace().getPath(), projectPath))
            if not os.path.exists(destPath):
                logging.info("Creation of the directory " + destPath)
                os.mkdir(destPath)
            # Retrieving and storing of the config file
            try:
                destFile = os.path.join(destPath, Project.CONFIGURATION_FILENAME)
                shutil.copy(fileName, destFile)
            except IOError, e:
                logging.warn("Error when importing project: " + str(e))
                return None

            project = Project.loadProject(self.netzob.getCurrentWorkspace(), destPath)
            project.setID(idProject)
            project.setName("Copy of " + project.getName())
            project.setPath(projectPath)
            project.saveConfigFile(self.netzob.getCurrentWorkspace())
            self.netzob.getCurrentWorkspace().referenceProject(project.getPath())
            self.netzob.getCurrentWorkspace().saveConfigFile()
            NetzobInfoMessage("Project '" + project.getName() + "' correctly imported")
            self.update()

    #+----------------------------------------------
    #| Called when user wants to export a project
    #+----------------------------------------------
    def exportProjectAction(self, widget):
        chooser = gtk.FileChooserDialog(title="Export as (XML)", action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            fileName = chooser.get_filename()
        chooser.destroy()

        doCreateFile = False
        isFile = os.path.isfile(fileName)
        if not isFile:
            doCreateFile = True
        else:
            md = gtk.MessageDialog(None,
                                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_OK_CANCEL, "Are you sure to override the file '" + fileName + "' ?")
            resp = md.run()
            md.destroy()
            if resp == gtk.RESPONSE_OK:
                doCreateFile = True

        if doCreateFile:
            root = self.netzob.getCurrentProject().generateXMLConfigFile()
            tree = ElementTree(root)
            tree.write(fileName)
            NetzobInfoMessage("Project correctly exported to '" + fileName + "'")

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
    #| Called when user wants to import file
    #+----------------------------------------------
    def importXMLAction(self, widget):
        xmlImportPanel = XMLImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import from third parties
    #+----------------------------------------------
    def importThirdParty(self, widget):
        thirdPartyImportPanel = ThirdPartyImport(self.netzob)

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

    #+----------------------------------------------
    #| Called when user wants to display search results panel
    #+----------------------------------------------
    def displaySearchAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH, self.displaySearchView.get_active())
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display properties results panel
    #+----------------------------------------------
    def displayPropertiesAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES, self.displayPropertiesView.get_active())
        self.netzob.updateCurrentPanel()

    def aboutDialogAction(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name(release.appname)
        about.set_version(release.version)
        about.set_copyright(release.copyright)
        if release.versionName != None:
            about.set_comments("--{0}--\n{1}".format(release.versionName, release.description))
        else:
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

    def sessionManagerAction(self, widget):
        logging.info("Starting the session manager")
        sessionManagerPanel = SessionManager(self.netzob)

    def createProjectAction(self, widget):
        dialog = gtk.Dialog(title="Create a new project", flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()
        label = gtk.Label("New project name")
        label.show()
        entry = gtk.Entry()
        but = gtk.Button("Create project")
        but.connect("clicked", self.createProjectAction_cb, entry, dialog)
        but.set_flags(gtk.CAN_DEFAULT)
        but.show()
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        dialog.set_default(but)
        dialog.action_area.pack_start(table, True, True, 0)
        # Grab focus must be called after adding the widget to the top level element
        entry.set_flags(gtk.CAN_FOCUS)
        entry.show()
        entry.grab_focus()

    #+----------------------------------------------
    #| Creation of a new project from
    #+----------------------------------------------
    def createProjectAction_cb(self, button, entry, dialog):
        projectName = entry.get_text()

        # we verify a name has been provided
        if projectName == None or projectName == "":
            logging.warn("Impossible to create a project with an empty name.")
            errorDialog = NetzobErrorMessage("Impossible to create a project with an empty name.")
            return

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
