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
from netzob.UI.Import.Controllers.PcapImportController import PcapImportController
from netzob.Import.ThirdPartyImport import ThirdPartyImport
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.Plugins.ImporterPlugin import ImporterPlugin
from netzob.Common.Plugins.Extensions.GlobalMenuExtension import GlobalMenuExtension
from netzob.UI.Common.AboutDialog import AboutDialog
if os.name == 'posix':
    from netzob.Import.IpcImport import IpcImport
#from netzob.UI.Import.Controllers.FileImportController import FileImportController
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

    # Static entries in the menu
    PATH_WORKSPACE = "/" + _("Workspace")
    PATH_WORKSPACE_CREATEPROJECT = "/" + _("Workspace") + "/" + _("Create a project")
    PATH_WORKSPACE_SWITCHPROJECT = "/" + _("Workspace") + "/" + _("Switch project")
    PATH_WORKSPACE_IMPORTPROJECT = "/" + _("Workspace") + "/" + _("Import a project")
    PATH_WORKSPACE_EXPORTPROJECT = "/" + _("Workspace") + "/" + _("Export a project")
    PATH_WORKSPACE_MANAGEPROJECT = "/" + _("Workspace") + "/" + _("Manage project")
    PATH_WORKSPACE_MANAGETRACES = "/" + _("Workspace") + "/" + _("Manage traces")
    PATH_WORKSPACE_OPTIONS = "/" + _("Workspace") + "/" + _("Options")
    PATH_WORKSPACE_SWITCHWORKSPACE = "/" + _("Workspace") + "/" + _("Switch Workspace")
    PATH_WORKSPACE_QUIT = "/" + _("Workspace") + "/Quit"

    PATH_PROJECT = "/_" + _("Project")
    PATH_PROJECT_SAVEPROJECT = "/" + _("Project") + "/" + _("Save project")
    PATH_PROJECT_SESSIONMANAGER = "/" + _("Project") + "/" + _("Session manager")
    PATH_PROJECT_IMPORTTRACES = "/" + _("Project") + "/" + _("Import traces")
    PATH_PROJECT_IMPORTTRACES_CAPTURENETWORKTRACES = PATH_PROJECT_IMPORTTRACES + "/" + _("Capture network traces")
    PATH_PROJECT_IMPORTTRACES_CAPTUREIPCFLOWS = PATH_PROJECT_IMPORTTRACES + "/" + _("Capture IPC flows")
    PATH_PROJECT_IMPORTTRACES_IMPORTPCAP = PATH_PROJECT_IMPORTTRACES + "/" + _("Import from PCAP")
    PATH_PROJECT_IMPORTTRACES_IMPORTXMLFILE = PATH_PROJECT_IMPORTTRACES + "/" + _("Import from XML File")
    PATH_PROJECT_IMPORTTRACES_IMPORTTHIRDPARTIES = PATH_PROJECT_IMPORTTRACES + "/" + _("Import from Third parties")

    PATH_PROJECT_EXPORTPROJECT = "/" + _("Project") + "/" + _("Export project")
    PATH_PROJECT_EXPORTPROJECT_XML = "/" + _("Project") + "/" + _("Export project") + "/" + _("XML")
    PATH_PROJECT_EXPORTPROJECT_TEXT = "/" + _("Project") + "/" + _("Export project") + "/" + _("Text")

    PATH_VIEWS = "/" + _("Views")
    PATH_VIEWS_DISPLAYSYMBOLSTRUCTURE = "/" + _("Views") + "/" + _("Display symbol structure")
    PATH_VIEWS_DISPLAYMESSAGES = "/" + _("Views") + "/" + _("Display messages")
    PATH_VIEWS_DISPLAYSEARCHRESULTS = "/" + _("Views") + "/" + _("Display search results")
    PATH_VIEWS_DISPLAYPROPERTIES = "/" + _("Views") + "/" + _("Display properties")

    PATH_HELP = "/_" + _("Help")
    PATH_HELP_HELPCONTENT = "/" + _("Help") + "/" + _("Help Contents")
    PATH_HELP_ABOUT = "/" + _("Help") + "/" + _("About Netzob")

    #+-----------------------------------------------------------------------+
    #| Constructor
    #|   Creation of the menu
    #+-----------------------------------------------------------------------+
    def __init__(self, netzob):
        self.netzob = netzob

        # This is the structure used to generate new menus.
        # Item 1: The menu path. The letter after the underscore indicates an
        #         accelerator key once the menu is open.
        # Item 2: The accelerator key for the entry
        # Item 3: The callback.
        # Item 4: The callback action.  This changes the parameters with
        #         which the callback is called.  The default is 0.
        # Item 5: The item type, used to define what kind of an item it is.
        #       Here are the possible values:

        #       NULL               -> "<Item>"
        #       ""                 -> "<Item>"
        #       "<Title>"          -> create a title item
        #       "<Item>"           -> create a simple item
        #       "<CheckItem>"      -> create a check item
        #       "<ToggleItem>"     -> create a toggle item
        #       "<RadioItem>"      -> create a radio item
        #       <path>             -> path of a radio item to link against
        #       "<Separator>"      -> create a separator
        #       "<Branch>"         -> create an item to hold sub items (optional)
        #       "<LastBranch>"     -> create a right justified branch
        self.menu_items = [
            # WORKSPACE
            (Menu.PATH_WORKSPACE, None, None, 0, "<Branch>"),
            (Menu.PATH_WORKSPACE_CREATEPROJECT, None, self.createProjectAction, 0, None),
            (Menu.PATH_WORKSPACE_SWITCHPROJECT, None, None, 0, "<Branch>"),
            (Menu.PATH_WORKSPACE_IMPORTPROJECT, None, self.importProjectAction, 0, None),
            (Menu.PATH_WORKSPACE_EXPORTPROJECT, None, self.exportProjectAction, 0, None),
            (Menu.PATH_WORKSPACE_MANAGEPROJECT, None, None, 0, None),
            (Menu.PATH_WORKSPACE_MANAGETRACES, None, self.manageTracesAction, 0, None),
            (Menu.PATH_WORKSPACE_OPTIONS, None, None, 0, None),
            (Menu.PATH_WORKSPACE_SWITCHWORKSPACE, None, None, 0, None),
            (Menu.PATH_WORKSPACE_QUIT, "<control>Q", self.exitAction, 0, None),
            # PROJECT
            (Menu.PATH_PROJECT, None, None, 0, "<Branch>"),
            (Menu.PATH_PROJECT_SAVEPROJECT, None, self.saveProjectAction, 0, None),
            (Menu.PATH_PROJECT_SESSIONMANAGER, None, self.sessionManagerAction, 0, None),
            # PROJECT / IMPORT TRACES
            (Menu.PATH_PROJECT_IMPORTTRACES, None, None, 0, "<Branch>"),
            (Menu.PATH_PROJECT_IMPORTTRACES_CAPTURENETWORKTRACES, None, self.importNetworkTraficAction, 0, None),
            (Menu.PATH_PROJECT_IMPORTTRACES_CAPTUREIPCFLOWS, None, self.importIPCFlowsAction, 0, None),
            (Menu.PATH_PROJECT_IMPORTTRACES_IMPORTPCAP, None, self.importPcapAction, 0, None),
            (Menu.PATH_PROJECT_IMPORTTRACES_IMPORTXMLFILE, None, self.importXMLAction, 0, None),
            (Menu.PATH_PROJECT_IMPORTTRACES_IMPORTTHIRDPARTIES, None, self.importThirdParty, 0, None),
            # PROJECT / EXPORT PROJECT
            (Menu.PATH_PROJECT_EXPORTPROJECT, None, None, 0, "<Branch>"),
            (Menu.PATH_PROJECT_EXPORTPROJECT_XML, None, self.exportXMLAction, 0, None),
            (Menu.PATH_PROJECT_EXPORTPROJECT_TEXT, None, self.exportTextAction, 0, None),
            # VIEW
            (Menu.PATH_VIEWS, None, None, 0, "<Branch>"),
            (Menu.PATH_VIEWS_DISPLAYSYMBOLSTRUCTURE, None, self.displaySymbolStructureAction, 0, "<CheckItem>"),
            (Menu.PATH_VIEWS_DISPLAYMESSAGES, None, self.displayMessagesAction, 0, "<CheckItem>"),
            (Menu.PATH_VIEWS_DISPLAYSEARCHRESULTS, None, self.displaySearchAction, 0, "<CheckItem>"),
            (Menu.PATH_VIEWS_DISPLAYPROPERTIES, None, self.displayPropertiesAction, 0, "<CheckItem>"),

            # HELP
            (Menu.PATH_HELP, None, None, 0, "<LastBranch>"),
            (Menu.PATH_HELP_HELPCONTENT, None, None, 0, None),
            (Menu.PATH_HELP_ABOUT, None, self.aboutDialogAction, 0, None),
            ]
        self.computeMenuBar(self.netzob)

    def update(self):
        self.item_factory.get_widget(Menu.PATH_WORKSPACE_CREATEPROJECT).set_sensitive(True)
        self.item_factory.get_widget(Menu.PATH_WORKSPACE_IMPORTPROJECT).set_sensitive(True)
        self.item_factory.get_widget(Menu.PATH_WORKSPACE_MANAGEPROJECT).set_sensitive(True)
        self.item_factory.get_widget(Menu.PATH_WORKSPACE_MANAGETRACES).set_sensitive(True)
        self.item_factory.get_widget(Menu.PATH_WORKSPACE_OPTIONS).set_sensitive(False)
        self.item_factory.get_widget(Menu.PATH_WORKSPACE_SWITCHWORKSPACE).set_sensitive(False)
        self.item_factory.get_widget(Menu.PATH_WORKSPACE_QUIT).set_sensitive(True)

        if self.netzob.getCurrentProject() == None:
            # Deactivate almost everything
            self.item_factory.get_widget(Menu.PATH_WORKSPACE_SWITCHPROJECT).set_sensitive(False)
            self.item_factory.get_widget(Menu.PATH_PROJECT_SESSIONMANAGER).set_sensitive(False)
            self.item_factory.get_widget(Menu.PATH_PROJECT_IMPORTTRACES).set_sensitive(False)
            self.item_factory.get_widget(Menu.PATH_PROJECT_EXPORTPROJECT).set_sensitive(False)
            self.item_factory.get_widget(Menu.PATH_HELP_HELPCONTENT).set_sensitive(False)
            self.item_factory.get_widget(Menu.PATH_WORKSPACE_EXPORTPROJECT).set_sensitive(False)

            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYMESSAGES).set_sensitive(False)
            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYPROPERTIES).set_sensitive(False)
            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYSEARCHRESULTS).set_sensitive(False)
            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYSYMBOLSTRUCTURE).set_sensitive(False)

        else:
            # Activate everything
            self.item_factory.get_widget(Menu.PATH_PROJECT_SAVEPROJECT).set_sensitive(True)
            self.item_factory.get_widget(Menu.PATH_PROJECT_SESSIONMANAGER).set_sensitive(True)
            self.item_factory.get_widget(Menu.PATH_PROJECT_IMPORTTRACES).set_sensitive(True)
            self.item_factory.get_widget(Menu.PATH_PROJECT_EXPORTPROJECT).set_sensitive(True)
            self.item_factory.get_widget(Menu.PATH_WORKSPACE_EXPORTPROJECT).set_sensitive(True)

            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYMESSAGES).set_sensitive(True)
            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYPROPERTIES).set_sensitive(True)
            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYSEARCHRESULTS).set_sensitive(True)
            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYSYMBOLSTRUCTURE).set_sensitive(True)

#            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE)
#            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYSYMBOLSTRUCTURE).set_active(True)
#
#            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES)
#            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYSEARCHRESULTS).set_active(True)
#
#            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH)
#            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYSEARCHRESULTS).set_active(True)
#
#            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES)
#            self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYPROPERTIES).set_active(True)

        switchProject = self.item_factory.get_widget(Menu.PATH_WORKSPACE_SWITCHPROJECT)
        # Update the list of project
        for i in switchProject.get_children():
            switchProject.remove(i)

        availableProjectsName = self.netzob.getCurrentWorkspace().getNameOfProjects()
        for (projectName, projectFile) in availableProjectsName:
            projectEntry = gtk.MenuItem(projectName)
            projectEntry.connect("activate", self.switchProjectAction, projectFile)
            switchProject.append(projectEntry)
        switchProject.show_all()

        # Deactivate the global 'switch menu' if no project is available
        if len(availableProjectsName) == 0:
            self.item_factory.get_widget(Menu.PATH_WORKSPACE_SWITCHPROJECT).set_sensitive(False)
        else:
            self.item_factory.get_widget(Menu.PATH_WORKSPACE_SWITCHPROJECT).set_sensitive(True)

        # Retrieve and activate the menu entries associated with plugins
        self.updateMenuWithPlugins()

    def updateMenuWithPlugins(self):
        # Show plugins
        logging.debug("Retrieve plugins for Menu")
        for pluginExtension in NetzobPlugin.getLoadedPluginsExtension(GlobalMenuExtension):
            try:
                logging.debug("Menu available : {0}".format(pluginExtension))
                for menuEntry in pluginExtension.getMenuEntries():
                    if not menuEntry in self.menu_items:
                        self.item_factory.create_items([menuEntry])
                        self.menu_items.append(menuEntry)
            except Exception, e:
                logging.warning("An error occurred when computing menu entry for plugin {0} ({1})".format(pluginExtension, e))

    def getMenuBar(self, window):
        self.computeMenuBar(window)
        return self.item_factory.get_widget("<main>")

    def computeMenuBar(self, window):
        accel_group = gtk.AccelGroup()
        item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)
        item_factory.create_items(self.menu_items)
        window.add_accel_group(accel_group)
        self.item_factory = item_factory

    def aboutDialogAction(self, widget, data):
        AboutDialog()

    #+----------------------------------------------
    #| Called when user save the current project
    #+----------------------------------------------
    def saveProjectAction(self, widget, data):
        logging.info(_("Starting the saving of the current project: %s") % str(self.netzob.getCurrentProject().getName()))
        self.netzob.getCurrentProject().saveConfigFile(self.netzob.getCurrentWorkspace())

    def sessionManagerAction(self, widget, data):
        logging.info("Starting the session manager")
        sessionManagerPanel = SessionManager(self.netzob)

    def exitAction(self, widget, data):
        self.netzob.destroy(widget)

    def setDisplaySearchViewActiveStatus(self, status, data):
        self.displaySearchView.set_active(status)

    #+----------------------------------------------
    #| Called when user wants to manage the traces
    #+----------------------------------------------
    def manageTracesAction(self, widget, data):
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
    def importProjectAction(self, widget, data):
        chooser = gtk.FileChooserDialog(title=_("Export as"), action=gtk.FILE_CHOOSER_ACTION_OPEN,
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
    def exportProjectAction(self, widget, data):
        chooser = gtk.FileChooserDialog(title=_("Export as (XML)"), action=gtk.FILE_CHOOSER_ACTION_SAVE,
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
                                   gtk.BUTTONS_OK_CANCEL, _("Are you sure to override the file '{0}'?").format(fileName))
            resp = md.run()
            md.destroy()
            if resp == gtk.RESPONSE_OK:
                doCreateFile = True

        if doCreateFile:
            root = self.netzob.getCurrentProject().generateXMLConfigFile()
            tree = ElementTree(root)
            tree.write(fileName)
            NetzobInfoMessage(_("Project correctly exported to '{0}'").format(fileName))

    #+----------------------------------------------
    #| Called when user wants to import network trafic
    #+----------------------------------------------
    def importNetworkTraficAction(self, widget, data):
        networkImportPanel = NetworkImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import PCAP file
    #+----------------------------------------------
    def importPcapAction(self, widget, data):
        pcapImportPanel = PcapImportController(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import IPC flow
    #+----------------------------------------------
    def importIPCFlowsAction(self, widget, data):
        ipcImportPanel = IpcImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import file
    #+----------------------------------------------
    def importFileAction(self, widget, data):
        fileImportPanel = FileImportController(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import file
    #+----------------------------------------------
    def importXMLAction(self, widget, data):
        xmlImportPanel = XMLImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to import from third parties
    #+----------------------------------------------
    def importThirdParty(self, widget, data):
        thirdPartyImportPanel = ThirdPartyImport(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to export as Scapy dissector
    #+----------------------------------------------
    def exportScapyAction(self, widget, data):
        scapyPanel = ScapyExport(self.netzob)

    def exportWiresharkAction(self, widget, data):
#        wiresharkPanel = WireS(self.netzob)
        pass

    #+----------------------------------------------
    #| Called when user wants to export as raw XML
    #+----------------------------------------------
    def exportXMLAction(self, action, data):
        rawExportPanel = RawExportController(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to export as text
    #+----------------------------------------------
    def exportTextAction(self, action, data):
        textExportPanel = TextExportController(self.netzob)

    #+----------------------------------------------
    #| Called when user wants to display symbol structure panel
    #+----------------------------------------------
    def displaySymbolStructureAction(self, widget, data):
        if self.netzob.getCurrentProject() != None:
            isActive = self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYSYMBOLSTRUCTURE).get_active()
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE, isActive)
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display messages panel
    #+----------------------------------------------
    def displayMessagesAction(self, widget, data):
        if self.netzob.getCurrentProject() != None:
            isActive = self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYMESSAGES).get_active()
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES, isActive)
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display the console
    #+----------------------------------------------
    def displayConsoleAction(self, widget, data):
        if self.netzob.getCurrentProject() != None:
            pass
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display search results panel
    #+----------------------------------------------
    def displaySearchAction(self, widget, data):
        if self.netzob.getCurrentProject() != None:
            isActive = self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYSEARCHRESULTS).get_active()
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH, isActive)
        self.netzob.updateCurrentPanel()

    #+----------------------------------------------
    #| Called when user wants to display properties results panel
    #+----------------------------------------------
    def displayPropertiesAction(self, widget, data):
        if self.netzob.getCurrentProject() != None:
            isActive = self.item_factory.get_widget(Menu.PATH_VIEWS_DISPLAYPROPERTIES).get_active()
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES, isActive)
        self.netzob.updateCurrentPanel()

    def createProjectAction(self, widget, data):
        dialog = gtk.Dialog(title=_("Create a new project"), flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()
        label = gtk.Label(_("New project name"))
        label.show()
        entry = gtk.Entry()
        but = gtk.Button(_("Create project"))
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
            logging.warn(_("Unable to create a project with an empty name."))
            errorDialog = NetzobErrorMessage(_("Unable to create a project with an empty name."))
            return

        # We verify the project name doesn't already exist
        found = False
        for project in  self.netzob.getCurrentWorkspace().getProjects():
            if project.getName() == projectName:
                found = True
        if found:
            dialogBis = gtk.Dialog(title=_("Error"), flags=0, buttons=None)
            label = gtk.Label(_("This project name already exists"))
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
