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
from gettext import gettext as _
from gi.repository import Gtk
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
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.Plugins.ImporterPlugin import ImporterPlugin
from netzob.Common.Plugins.Extensions.GlobalMenuExtension import GlobalMenuExtension
from netzob.UI.Common.AboutDialog import AboutDialog
if os.name == 'posix':
    from netzob.Import.IpcImport import IpcImport
#from netzob.UI.Import.Controllers.FileImporterController import FileImporterController
from netzob.Import.XMLImport import XMLImport
from netzob.Export.ScapyExport import ScapyExport
from netzob.UI.Export.Controllers.RawExportController import RawExportController
from netzob.UI.Export.Controllers.TextExportController import TextExportController
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.TraceManager import TraceManager
from netzob.UI.NetzobWidgets import NetzobInfoMessage, NetzobErrorMessage


#+---------------------------------------------------------------------------+
#| Menu:
#|     Class definition of the menu
#+---------------------------------------------------------------------------+
class Menu(object):

    ui_desc = """
<ui>
  <menubar name='MenuBar'>
    <menu action='Workspace'>
      <menuitem action='Create' />
      <menu action='SwitchProject'/>
      <menuitem action='ImportProject' />
      <menuitem action='ExportProject' />
      <menuitem action='ManageProject' />
    <separator/>
      <menuitem action='ManageTraces' />
      <menuitem action='Options' />
      <menuitem action='SwitchWorkspace'/>
      <menuitem action='Quit' />

    </menu>
    <menu action='Project'>
      <menuitem action='Save' />
      <menuitem action='SessionManager' />
      <menu action='ImportTraces'>
    	<menuitem action='ImportNetwork' />
    	<menuitem action='ImportIPCFlows' />
    	<menuitem action='ImportXML' />
      </menu>
      <menu action='Export'>
        <menuitem action='ExportXML' />
        <menuitem action='ExportText' />
      </menu>
    </menu>
    <menu action='View'>
      <menuitem action='DisplaySymbolStructure'/>
      <menuitem action='DisplayMessages'/>
      <menuitem action='DisplaySearchResults'/>
      <menuitem action='DisplayProperties'/>
    </menu>
    <menu action='Help'>
      <menuitem action='Content'/>
      <menuitem action='About'/>
    </menu>
  </menubar>
</ui>"""

    #+-----------------------------------------------------------------------+
    #| Constructor
    #|   Creation of the menu
    #+-----------------------------------------------------------------------+
    def __init__(self, netzob):
        self.netzob = netzob

        self.actiongroup = Gtk.ActionGroup("MenuAction")
        self.actiongroup.add_actions([
            ("Workspace", None, _("Workspace")),
            ("Create", Gtk.STOCK_NEW, _("Create a project"), None, None, self.createProjectAction),
            ("ImportProject", None, _("Import a project"), None, None, self.importProjectAction),
            ("ExportProject", None, _("Export a project"), None, None, self.exportProjectAction),
            ("ManageProject", None, _("Manage projects")),
            ("ManageTraces", None, _("Manage traces"), None, None, self.manageTracesAction),
            ("Options", None, _("Options")),
            ("SwitchWorkspace", None, _("Switch workspace")),
            ("Quit", Gtk.STOCK_QUIT, _("Quit"), "<control>Q", None, self.exitAction),
            ("Project", None, _("Project")),
            ("Save", Gtk.STOCK_SAVE, _("Save project"), None, None, self.saveProjectAction),
            ("SessionManager", None, _("Session manager"), None, None, self.sessionManagerAction),
            ("ImportTraces", None, _("Import traces")),
            ("ImportNetwork", None, _("Capture network traces"), None, None, self.importNetworkTraficAction),
            ("ImportIPCFlows", None, _("Capture IPC flows"), None, None, self.importIPCFlowsAction),
            ("ImportXML", None, _("Import from XML File"), None, None, self.importXMLAction),
            ("Export", None, _("Export project")),
            ("ExportXML", None, _("XML"), None, None, self.exportXMLAction),
            ("ExportText", None, _("Text"), None, None, self.exportTextAction),
            ("View", None, _("View")),
            ("Help", None, _("Help")),
            ("Content", Gtk.STOCK_HELP, _("Help Contents"), None, None, None),
            ("About", Gtk.STOCK_ABOUT, _("About Netzob"), None, None, self.aboutDialogAction)
        ])

        item = Gtk.Action("SwitchProject", _("Switch project"), None, None)
        item.set_property('hide-if-empty', False)
        self.actiongroup.add_action(item)

        self.actiongroup.add_toggle_actions([
            ("DisplaySymbolStructure", None, _("Display symbol structure"), None, None, self.displaySymbolStructureAction),
            ("DisplayMessages", None, _("Display messages"), None, None, self.displayMessagesAction),
            ("DisplaySearchResults", None, _("Display search results"), None, None, self.displaySearchAction),
            ("DisplayProperties", None, _("Display properties"), None, None, self.displayPropertiesAction),
        ])

        self.uimanager = Gtk.UIManager()
        self.uimanager.insert_action_group(self.actiongroup, 0)
        self.uimanager.add_ui_from_string(self.ui_desc)

    def update(self):
        self.uimanager.get_widget("/MenuBar/Workspace/Create").set_sensitive(True)
        self.uimanager.get_widget("/MenuBar/Workspace/ImportProject").set_sensitive(True)
        self.uimanager.get_widget("/MenuBar/Workspace/ManageProject").set_sensitive(True)
        self.uimanager.get_widget("/MenuBar/Workspace/ManageTraces").set_sensitive(True)
        self.uimanager.get_widget("/MenuBar/Workspace/Options").set_sensitive(False)
        self.uimanager.get_widget("/MenuBar/Workspace/SwitchWorkspace").set_sensitive(False)
        self.uimanager.get_widget("/MenuBar/Workspace/SwitchProject").set_sensitive(True)
        self.uimanager.get_widget("/MenuBar/Workspace/Quit").set_sensitive(True)

        if self.netzob.getCurrentProject() == None:
            # Deactivate almost everything
            self.uimanager.get_widget("/MenuBar/Workspace/SwitchWorkspace").set_sensitive(False)
            self.uimanager.get_widget("/MenuBar/Project/SessionManager").set_sensitive(False)
            self.uimanager.get_widget("/MenuBar/Project/ImportTraces").set_sensitive(False)
            self.uimanager.get_widget("/MenuBar/Project/Export").set_sensitive(False)
            self.uimanager.get_widget("/MenuBar/Help/Content").set_sensitive(False)
            self.uimanager.get_widget("/MenuBar/Workspace/ExportProject").set_sensitive(False)

            self.uimanager.get_widget("/MenuBar/View/DisplayMessages").set_sensitive(False)
            self.uimanager.get_widget("/MenuBar/View/DisplayProperties").set_sensitive(False)
            self.uimanager.get_widget("/MenuBar/View/DisplaySearchResults").set_sensitive(False)
            self.uimanager.get_widget("/MenuBar/View/DisplaySymbolStructure").set_sensitive(False)

        else:
            # Activate everything
            self.uimanager.get_widget("/MenuBar/Project/Save").set_sensitive(True)
            self.uimanager.get_widget("/MenuBar/Project/SessionManager").set_sensitive(True)
            self.uimanager.get_widget("/MenuBar/Project/ImportTraces").set_sensitive(True)
            self.uimanager.get_widget("/MenuBar/Project/Export").set_sensitive(True)
            self.uimanager.get_widget("/MenuBar/Workspace/ExportProject").set_sensitive(True)

            self.uimanager.get_widget("/MenuBar/View/DisplayMessages").set_sensitive(True)
            self.uimanager.get_widget("/MenuBar/View/DisplayProperties").set_sensitive(True)
            self.uimanager.get_widget("/MenuBar/View/DisplaySearchResults").set_sensitive(True)
            self.uimanager.get_widget("/MenuBar/View/DisplaySymbolStructure").set_sensitive(True)

        switchProject = self.uimanager.get_widget("/MenuBar/Workspace/SwitchProject").get_submenu()

        # Update the list of project
        for i in switchProject.get_children():
            switchProject.remove(i)

        availableProjectsName = self.netzob.getCurrentWorkspace().getNameOfProjects()
        for (projectName, projectFile) in availableProjectsName:
            projectEntry = Gtk.MenuItem(projectName)
            projectEntry.connect("activate", self.switchProjectAction, projectFile)
            switchProject.append(projectEntry)
        switchProject.show_all()

        self.uimanager.get_widget("/MenuBar/Workspace/SwitchProject").set_sensitive(True)

        # Deactivate the global 'switch menu' if no project is available
        if len(availableProjectsName) == 0:
            self.uimanager.get_widget("/MenuBar/Workspace/SwitchProject").set_sensitive(False)
        else:
            self.uimanager.get_widget("/MenuBar/Workspace/SwitchProject").set_sensitive(True)

        # Retrieve and activate the menu entries associated with plugins
        self.updateMenuWithPlugins()

    """
    TODO: Port to UIManager!
    """
    def updateMenuWithPlugins(self):
        # Show plugins
        logging.debug("Retrieve plugins for Menu")
        for pluginExtension in NetzobPlugin.getLoadedPluginsExtension(GlobalMenuExtension):
            try:
                logging.debug("Menu available : {0}".format(pluginExtension))
                uiDefinition = pluginExtension.getUIDefinition()
                actions = pluginExtension.getActions()
                logging.debug("Adding actions {0}".format(actions))
                self.actiongroup.add_actions(actions)
                self.uimanager.add_ui_from_string(uiDefinition)
            except Exception, e:
                logging.exception("An error occurred when computing menu entry for plugin {0} : {1}".format(pluginExtension, e))

    def getMenuBar(self, window):
        return self.uimanager.get_widget("/MenuBar")

    def aboutDialogAction(self, widget):
        AboutDialog()

    #+----------------------------------------------
    #| Called when user save the current project
    #+----------------------------------------------
    def saveProjectAction(self, widget):
        logging.info(_("Starting the saving of the current project: %s") % str(self.netzob.getCurrentProject().getName()))
        self.netzob.getCurrentProject().saveConfigFile(self.netzob.getCurrentWorkspace())

    def sessionManagerAction(self, widget):
        logging.info("Starting the session manager")
        sessionManagerPanel = SessionManager(self.netzob)

    def exitAction(self, widget):
        self.netzob.destroy(widget)

    def setDisplaySearchViewActiveStatus(self, status):
        self.uimanager.get_widget("/MenuBar/View/DisplaySearchResults").\
            set_active(True)

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
        chooser = Gtk.FileChooserDialog(title=_("Export as"), action=Gtk.FileChooserAction.OPEN,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        res = chooser.run()
        if res == Gtk.ResponseType.OK:
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
            project.setName(_("Copy of {0}").format(project.getName()))
            project.setPath(projectPath)
            project.saveConfigFile(self.netzob.getCurrentWorkspace())
            self.netzob.getCurrentWorkspace().referenceProject(project.getPath())
            self.netzob.getCurrentWorkspace().saveConfigFile()
            NetzobInfoMessage(_("Project '{0}' correctly imported").format(project.getName()))
            self.update()

    #+----------------------------------------------
    #| Called when user wants to export a project
    #+----------------------------------------------
    def exportProjectAction(self, widget):
        chooser = Gtk.FileChooserDialog(title=_("Export as (XML)"), action=Gtk.FileChooserAction.SAVE,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        res = chooser.run()
        if res == Gtk.ResponseType.OK:
            fileName = chooser.get_filename()
        chooser.destroy()

        doCreateFile = False
        isFile = os.path.isfile(fileName)
        if not isFile:
            doCreateFile = True
        else:
            md = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.OK_CANCEL, _("Are you sure to override the file '{0}'?").format(fileName))
            resp = md.run()
            md.destroy()
            if resp == Gtk.ResponseType.OK:
                doCreateFile = True

        if doCreateFile:
            root = self.netzob.getCurrentProject().generateXMLConfigFile()
            tree = ElementTree(root)
            tree.write(fileName)
            NetzobInfoMessage(_("Project correctly exported to '{0}'").format(fileName))

    #+----------------------------------------------
    #| Called when user wants to import network trafic
    #+----------------------------------------------
    def importNetworkTraficAction(self, widget):
        networkImportPanel = NetworkImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import IPC flow
    #+----------------------------------------------
    def importIPCFlowsAction(self, widget):
        ipcImportPanel = IpcImport(self.netzob)

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
        rawExportPanel = RawExportController(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to export as text
    #+----------------------------------------------
    def exportTextAction(self, action):
        textExportPanel = TextExportController(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to display symbol structure panel
    #+----------------------------------------------
    def displaySymbolStructureAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            isActive = self.uimanager.get_widget("/MenuBar/View/DisplaySymbolStructure").get_active()
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE, isActive)
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display messages panel
    #+----------------------------------------------
    def displayMessagesAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            isActive = self.uimanager.get_widget("/MenuBar/View/DisplayMessages").get_active()
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES, isActive)
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display the console
    #+----------------------------------------------
    def displayConsoleAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            pass
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display search results panel
    #+----------------------------------------------
    def displaySearchAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            isActive = self.uimanager.get_widget("/MenuBar/View/DisplaySearchResults").get_active()
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH, isActive)
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display properties results panel
    #+----------------------------------------------
    def displayPropertiesAction(self, widget):
        if self.netzob.getCurrentProject() != None:
            isActive = self.uimanager.get_widget("/MenuBar/View/DisplayProperties").get_active()
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES, isActive)
        self.netzob.updateCurrentPanel()

    def createProjectAction(self, widget):
        dialog = Gtk.Dialog(title=_("Create a new project"), flags=0, buttons=None)
        dialog.show()
        table = Gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()
        label = Gtk.Label(label=_("New project name"))
        label.show()
        entry = Gtk.Entry()
        but = Gtk.Button(_("Create project"))
        but.connect("clicked", self.createProjectAction_cb, entry, dialog)
        but.set_can_default(True)
        but.show()
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        dialog.set_default(but)
        dialog.action_area.pack_start(table, True, True, 0)
        # Grab focus must be called after adding the widget to the top level element
        entry.set_can_focus(True)
        entry.show()
        entry.grab_focus()

    #+----------------------------------------------
    #| Creation of a new project from
    #+----------------------------------------------
    def createProjectAction_cb(self, button, entry, dialog):
        projectName = entry.get_text()

        # we verify a name has been provided
        if projectName == None or projectName == "":
            logging.warn(_("Unable to create a project with an empty name."))
            errorDialog = NetzobErrorMessage(_("Unable to create a project with an empty name."))
            return

        # We verify the project name doesn't already exist
        found = False
        for project in self.netzob.getCurrentWorkspace().getProjects():
            if project.getName() == projectName:
                found = True
        if found:
            dialogBis = Gtk.Dialog(title=_("Error"), flags=0, buttons=None)
            label = Gtk.Label(label=_("This project name already exists"))
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
