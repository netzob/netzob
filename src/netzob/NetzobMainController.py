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
import sys
import os
import logging
import gettext
import locale
import uuid
import shutil
from lxml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.DepCheck import DepCheck
from netzob.Common.SignalsManager import SignalsManager
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Workspace import Workspace
from netzob.Common.CommandLine import CommandLine
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.LoggingConfiguration import LoggingConfiguration
from netzob.NetzobMainView import NetzobMainView
from netzob.Common.Project import Project
from netzob.UI.Common.AboutDialog import AboutDialog
from netzob.UI.Common.Controllers.BugReporterController import BugReporterController
from netzob.UI.NetzobWidgets import NetzobErrorMessage
from netzob.UI.WorkspaceSelector import WorkspaceSelector
from netzob.Common.Plugins.Extensions.ExportMenuExtension import ExportMenuExtension
from netzob.UI.Common.Controllers.AvailablePluginsController import AvailablePluginsController
from netzob.UI.Export.Controllers.RawExportController import RawExportController


class NetzobMainController(object):
    """"Netzob main window controller"""

    def __init__(self):
        # Parse command line arguments
        cmdLine = CommandLine()
        cmdLine.parse()
        opts = cmdLine.getOptions()

        # Initialize everything
        self._loadBugReporter(opts)
        self.currentWorkspace = self._loadWorkspace(opts)
        self._initLogging(opts)
        self._initResourcesAndLocales()

        # Intialize signals manager
        self.signalsManager = SignalsManager()

        # Loading the last project
        self.currentProject = self.currentWorkspace.getLastProject()

        # Initialize a clipboard object
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        # Check dependencies
        if not DepCheck.checkRequiredDependency():
            self.log.fatal("Netzob could not start because some of its required dependencies were not found.")
            sys.exit()

        # Initialize main view
        self.log.info("Starting netzob UI")
        self.view = None    # small hack since the attribute need to exists when the main glade is loaded
        self.view = NetzobMainView(self)

        # Load all available plugins
        NetzobPlugin.loadPlugins(self)

        self.view.registerPerspectives()

        # Refresh list of available exporter plugins
        self.updateListOfExporterPlugins()

        # Refresh list of available projects
        self.updateListOfAvailableProjects()

    def _loadBugReporter(self, opts):
        """Activate the bug reporter if the command line options
        requests it"""

        if opts.bugReport:
            logging.debug("Activate the bug reporter")

            def log_uncaught_exceptions(exceptionClass, exceptionInstance, traceback):
                bugReporterController = BugReporterController(self,
                                                              exceptionClass,
                                                              exceptionInstance,
                                                              traceback)
                bugReporterController.run()

            sys.excepthook = log_uncaught_exceptions
        else:
            logging.debug("Bug reporter not requested.")

    def _loadWorkspace(self, opts):
        logging.debug("+ Load workspace...")
        if opts.workspace is None:
            workspaceDir = ResourcesConfiguration.getWorkspaceDir()
        else:
            workspaceDir = opts.workspace

        # Loading the workspace
        workspace = (Workspace.loadWorkspace(workspaceDir))
        if workspace is None:
            # We force the creation (or specification) of the workspace
            logging.info("Workspace not found: we ask to the user its new Netzob home directory")
            workspaceDir = self.askForWorkspaceDir()
            if workspaceDir is None:
                logging.fatal("Stopping the execution (no workspace computed)!")
                sys.exit()
            else:
                ResourcesConfiguration.generateUserFile(workspaceDir)
                workspace = (Workspace.loadWorkspace(workspaceDir))
        return workspace

    def askForWorkspaceDir(self):
        workspaceSelector = WorkspaceSelector()
        workspaceSelector.run()
        workspacePath = workspaceSelector.selectedWorkspace
        if workspacePath is not None:
            ResourcesConfiguration.createWorkspace(workspacePath)
        return workspacePath

    def _initResourcesAndLocales(self):
        # Initialize resources
        logging.debug("+ Initialize resources...")
        if not ResourcesConfiguration.initializeResources():
            logging.fatal("Error while configuring the resources of Netzob")
            sys.exit()

        # Initialiaze gettext
        gettext.bindtextdomain("netzob", ResourcesConfiguration.getLocaleLocation())
        gettext.textdomain("netzob")
        locale.bindtextdomain("netzob", ResourcesConfiguration.getLocaleLocation())
        locale.textdomain("netzob")
        try:
            locale.getlocale()
        except:
            logging.exception("setlocale failed, resetting to C")
            locale.setlocale(locale.LC_ALL, "C")

    def _initLogging(self, opts):
        # Create the logging infrastructure
        LoggingConfiguration().initializeLogging(self.currentWorkspace, opts)
        self.log = logging.getLogger(__name__)

    def run(self):
        self.view.run()
        Gtk.main()

    def close(self):
        """The method which closes the current project and the
        workspace before stopping the GTK"""

        result = self.closeCurrentProject()
        if result == True:
            # Save the workspace
            self.getCurrentWorkspace().saveConfigFile()

            # Close the controller
            Gtk.main_quit()
            return False  # We inform Gtk that we want to emit destroy signal
        else:
            return True  # We inform Gtk that we don't want to emit destroy signal

    def closeCurrentProject(self):
        """Close and offers to save the pending modifications in the
        current project."""

        currentProject = self.getCurrentProject()

        # Close the current project
        if currentProject is not None and currentProject.hasPendingModifications(self.getCurrentWorkspace()):
            resp = self.view.offerToSaveCurrentProject()

            if resp == Gtk.ResponseType.YES:
                logging.debug("Saving the current project")
                self.getCurrentProject().saveConfigFile(self.getCurrentWorkspace())
                return True

            elif resp == Gtk.ResponseType.CANCEL:
                logging.debug("Abort quitting")
                return False

        # Emit a signal for toolbar upgrade
        self.getSignalsManager().emitSignal(SignalsManager.SIG_PROJECT_CLOSE)

        self.currentProjet = None
        return True

    def getCurrentProject(self):
        return self.currentProject

    def getCurrentWorkspace(self):
        return self.currentWorkspace

    def updateListOfAvailableProjects(self):
        """Fetch the list of available projects in the current
        workspace, and provide them to its associated view"""
        listOfProjectsNameAndPath = self.currentWorkspace.getNameOfProjects()
        self.view.updateSwitchProjectMenu(listOfProjectsNameAndPath)

    def updateListOfExporterPlugins(self):
        """Fetch the list of available exporter plugins, and provide
        them to its associated view"""
        pluginExtensions = NetzobPlugin.getLoadedPluginsExtension(ExportMenuExtension)
        self.view.updateListExporterPlugins(pluginExtensions)

    def getPerspectiveController(self, perspectiveCode):
        """Fetch the requested perspective (given its code).
        Returns None if it cannot be found"""
        persCodes = self.view.getRegisteredPerspectives().keys()
        if not perspectiveCode in persCodes:
            self.log.warning("The requested perspective ({0}) canot be found.".format(perspectiveCode))
            return None
        (perspectiveDescription, instance) = self.view.getRegisteredPerspectives()[perspectiveCode]
        return instance

    def perspectiveComboBox_changed_cb(self, comboBox):
        iter = comboBox.get_active_iter()
        if iter is not None and self.view is not None:
            model = comboBox.get_model()
            newPerspectiveCode = model[iter][0]
            self.view.switchPerspective(newPerspectiveCode)

    def mainWindow_delete_event_cb(self, window, data):
        return self.close()

    def mainWindow_destroy_cb(self, window):
        Gtk.main_quit()

    def entry_disableButtonIfEmpty_cb(self, widget, button):
        if(len(widget.get_text()) > 0):
            button.set_sensitive(True)
        else:
            button.set_sensitive(False)

    def newProject_activate_cb(self, action):
        """Display the dialog in order to create a new project when
        the user request it through the menu."""

        finish = False
        errorMessage = None

        while not finish:
            # open Dialogbox
            builder2 = Gtk.Builder()
            builder2.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "dialogbox.glade"))
            dialog = builder2.get_object("newProject")
            dialog.set_transient_for(self.view.mainWindow)

            applybutton = builder2.get_object("newProjectApplyButton")
            entry = builder2.get_object("entry4")
            entry.connect("changed", self.entry_disableButtonIfEmpty_cb, applybutton)

            if errorMessage is not None:
                # Display a warning message on the dialog box
                warnLabel = builder2.get_object("NewProjectWarnLabel")
                warnLabel.set_text(errorMessage)
                warnBox = builder2.get_object("newProjectWarnBox")
                warnBox.show_all()

            # Run the dialog window and wait for the result
            result = dialog.run()

            if result == 0:
                newProjectName = entry.get_text()
                dialog.destroy()
                self.log.debug("Verify the uniqueness of project name: {0}".format(newProjectName))
                found = False
                for (projectName, projectPath) in self.currentWorkspace.getNameOfProjects():
                    if projectName == newProjectName:
                        found = True
                        break
                if found:
                    self.log.info("A project with the same name already exists ({0}, {1}), please change it.".format(projectName, projectPath))
                    errorMessage = _("A project with this name exists")
                else:
                    self.log.debug("Create new project {0}".format(newProjectName))
                    newProject = Project.createProject(self.getCurrentWorkspace(), newProjectName)
                    self.switchProject(newProject.getPath())
                    finish = True
                    errorMessage = None
            else:
                dialog.destroy()
                finish = True

    def saveProject_activate_cb(self, action):
        """Save the current project"""

        if self.getCurrentProject() == None:
            NetzobErrorMessage(_("No project selected."), self.view.mainWindow)
            return
        self.getCurrentProject().saveConfigFile(self.getCurrentWorkspace())

    def fileSetFileChooser_importProject_cb(self, widget, applyButton):
        """Callback executed when the user selects a file in the file
        chooser of the import project dialog box"""

        selectedFile = widget.get_filename()
        if selectedFile is not None:
            applyButton.set_sensitive(True)
        else:
            applyButton.set_sensitive(False)

    def importProject_activate_cb(self, action):
        """Display the dialog in order to import a project when the
        user request it through the menu."""

        logging.debug("Import project")
        finish = False
        errorMessage = None

        while not finish:
            # Open Dialogbox
            builder2 = Gtk.Builder()
            builder2.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "dialogbox.glade"))
            dialog = builder2.get_object("importProject")
            dialog.set_transient_for(self.view.mainWindow)

            # Disable the apply button if no file is provided
            applybutton = builder2.get_object("importProjectApplyButton")
            fileChooserButton = builder2.get_object("importProjectFileChooserButton")
            fileChooserButton.connect("file-set", self.fileSetFileChooser_importProject_cb, applybutton)

            if errorMessage is not None:
                # Display a warning message on the dialog box
                warnLabel = builder2.get_object("importProjectWarnLabel")
                warnLabel.set_text(errorMessage)
                warnBox = builder2.get_object("importProjectWarnBox")
                warnBox.show_all()

            # Run the dialog window and wait for the result
            result = dialog.run()

            if result == 0:
                selectedFile = fileChooserButton.get_filename()
                dialog.destroy()

                if selectedFile is None:
                    errorMessage = _("No file selected")
                else:
                    # Verify the file is a valid definition of a project
                    if Project.loadProjectFromFile(selectedFile) is None:
                        errorMessage = _("The file doesn't define a valid project.")
                    else:
                        # Generate the Unique ID of the imported project
                        idProject = str(uuid.uuid4())

                        # First we verify and create if necessary the directory of the project
                        projectPath = "projects/" + idProject + "/"
                        destPath = os.path.join(os.path.join(self.getCurrentWorkspace().getPath(), projectPath))
                        if not os.path.exists(destPath):
                            logging.info("Creation of the directory " + destPath)
                            os.mkdir(destPath)
                        try:
                            # Retrieving and storing of the config file
                            destFile = os.path.join(destPath, Project.CONFIGURATION_FILENAME)
                            shutil.copy(selectedFile, destFile)

                            project = Project.loadProject(self.getCurrentWorkspace(), destPath)
                            project.setID(idProject)
                            project.setName(_("Copy of {0}").format(project.getName()))
                            project.setPath(projectPath)
                            project.saveConfigFile(self.getCurrentWorkspace())
                            self.getCurrentWorkspace().referenceProject(project.getPath())
                            self.getCurrentWorkspace().saveConfigFile()
                            self.updateListOfAvailableProjects()
                            finish = True
                            errorMessage = None
                        except IOError, e:
                            errorMessage = _("An error occurred while copying the file")
                            logging.warn("Error when importing project: {0}".format(e))
            else:
                dialog.destroy()
                finish = True

    def fileSetFileChooserOrFilenamEntry_exportProject_cb(self, widget, fileChooser, fileEntry, applyButton):
        """Callback executed when the user selects a file in the file
        chooser of the export project dialog box"""

        currentFolder = fileChooser.get_current_folder()
        currentFile = fileEntry.get_text()

        if currentFolder is not None and len(currentFolder) > 0 and currentFile is not None and len(currentFile) > 0:
            applyButton.set_sensitive(True)
        else:
            applyButton.set_sensitive(False)

    def xmlExportProject_activate_cb(self, action):
        """Display the dialog in order to export the current project
        when the user request it through the menu."""

        if self.getCurrentProject() == None:
            NetzobErrorMessage(_("No project selected."), self.view.mainWindow)
            return

        logging.debug("Export project")

        finish = False
        errorMessage = None
        while not finish:
            #open dialogbox
            builder2 = Gtk.Builder()
            builder2.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "dialogbox.glade"))
            dialog = builder2.get_object("exportProject")
            dialog.set_transient_for(self.view.mainWindow)

            applybutton = builder2.get_object("exportProjectApplyButton")
            filenameEntry = builder2.get_object("exportProjectFilenameEntry")
            fileChooserButton = builder2.get_object("exportProjectFileChooserButton")

            # Set the default filename based on current project
            if self.getCurrentProject() is not None:
                filenameEntry.set_text("{0}.xml".format(self.getCurrentProject().getName()))
            else:
                errorMessage = _("Please open a project before exporting it.")

            fileChooserButton.connect("current-folder-changed", self.fileSetFileChooserOrFilenamEntry_exportProject_cb, fileChooserButton, filenameEntry, applybutton)
            filenameEntry.connect("changed", self.fileSetFileChooserOrFilenamEntry_exportProject_cb, fileChooserButton, filenameEntry, applybutton)

            # Execute the CB in case default case is functionnal
            self.fileSetFileChooserOrFilenamEntry_exportProject_cb(fileChooserButton, fileChooserButton, filenameEntry, applybutton)

            if errorMessage is not None:
                # Display a warning message on the dialog box
                warnLabel = builder2.get_object("exportProjectWarnLabel")
                warnLabel.set_text(errorMessage)
                warnBox = builder2.get_object("exportProjectWarnBox")
                warnBox.show_all()

            result = dialog.run()

            if result == 0:
                selectedFolder = fileChooserButton.get_current_folder()
                filename = filenameEntry.get_text()
                dialog.destroy()

                if selectedFolder is None:
                    errorMessage = _("No directory selected")
                elif filename is None or len(filename) == 0:
                    errorMessage = _("No filename provided")
                else:
                    if self.getCurrentProject() is None:
                        errorMessage = _("Please open a project before exporting it.")
                    else:
                        try:
                            outputFilename = os.path.join(selectedFolder, filename)
                            logging.debug("Output filename: {0}".format(outputFilename))
                            xmlDefinitionOfProject = self.getCurrentProject().generateXMLConfigFile()
                            tree = ElementTree(xmlDefinitionOfProject)
                            tree.write(outputFilename)
                            finish = True
                            errorMessage = None
                        except IOError, e:
                            errorMessage = _("An error occurred while exporting the project.")
                            logging.warn("Error when importing project: {0}".format(e))
            else:
                dialog.destroy()
                finish = True

    def rawExportProject_activate_cb(self, action):
        """Display the dialog in order to export the symbols when the
        user request it through the menu."""

        if self.getCurrentProject() == None:
            NetzobErrorMessage(_("No project selected."), self.view.mainWindow)
            return
        logging.debug("Export raw symbols")
        controller = RawExportController(self)

    def fileSetFileChooser_switchWorkspace_cb(self, widget, applyButton):
        """Callback executed when the user selects a directory in the
        file chooser"""

        currentFolder = widget.get_current_folder()
        if currentFolder is not None and len(currentFolder) > 0:
            applyButton.set_sensitive(True)
        else:
            applyButton.set_sensitive(False)

    def switchWorkspace_activate_cb(self, action):
        """Callback executed when the user requests to switch to
        another workspace"""

        finish = False
        errorMessage = None
        while not finish:
            #open dialogbox
            builder2 = Gtk.Builder()
            builder2.add_from_file(os.path.join(
                ResourcesConfiguration.getStaticResources(),
                "ui",
                "dialogbox.glade"))

            dialog = builder2.get_object("switchWorkspace")
            dialog.set_transient_for(self.view.mainWindow)

            applybutton = builder2.get_object("switchWorkspaceApplyButton")
            fileChooserButton = builder2.get_object("switchWorkspaceFileChooserButton")
            fileChooserButton.connect("current-folder-changed", self.fileSetFileChooser_switchWorkspace_cb, applybutton)

            if errorMessage is not None:
                # Display a warning message on the dialog box
                warnLabel = builder2.get_object("switchWorkspaceWarnLabel")
                warnLabel.set_text(errorMessage)
                warnBox = builder2.get_object("switchWorkspaceWarnBox")
                warnBox.show_all()

            result = dialog.run()

            if result == 0:
                selectedFolder = fileChooserButton.get_current_folder()
                dialog.destroy()

                if selectedFolder is None:
                    errorMessage = _("No directory selected")
                else:
                    # we verify if its an empty directory
                    if len(os.listdir(selectedFolder)) > 0:
                        # is a valid workspace directory
                        errorMessage = Workspace.isFolderAValidWorkspace(selectedFolder)
                        if errorMessage is None:
                            try:
                                self.currentWorkspace = (Workspace.loadWorkspace(selectedFolder))
                                self.currentProject = self.currentWorkspace.getLastProject()
                                finish = True
                                errorMessage = None
                                self.view.currentWorkspaceHasChanged()
                            except Exception, e:
                                errorMessage = _("An error occurred while loading workspace.")
                                logging.warn("Error while loading workspace declared in folder {0}: {1}".format(selectedFolder, e))
                    else:
                        # create a new workspace
                        try:
                            self.currentWorkspace = ResourcesConfiguration.createWorkspace(selectedFolder)
                            finish = True
                            errorMessage = None
                            self.view.currentWorkspaceHasChanged()
                        except Exception, e:
                                errorMessage = _("An error occurred while creating workspace.")
                                logging.warn("Error while creating workspace declared in folder {0}: {1}".format(selectedFolder, e))
            else:
                dialog.destroy()
                finish = True
        if (result == 1):
            #cancel
            dialog.destroy()

    def quit_activate_cb(self, action):
        """Callback executed when the user request to close Netzob"""

        self.close()

    def aboutNetzob_activate_cb(self, action):
        """Displays the about dialog when the user click on the
        associate menu entry."""

        AboutDialog.display(self.view.mainWindow)

    def availablePlugins_activate_cb(self, action):
        """Displays the list of available plugins"""

        controller = AvailablePluginsController(self)
        controller.run()

    def switchProject_cb(self, widget, projectPath):
        """Callback for the GTK view in order to switch to another
        project.

        @param projectPath: the path to the project to load
        @type projectPath: str
        """

        self.switchProject(projectPath)

    def switchProject(self, projectPath):
        """Change the current project with the project declared in
        file projectPath. If the loading is successful the view is
        updated.

        If a current project is already loaded, it offers to save
        pending modifications before changing.

        @param projectPath: the path to the project to load
        @type projectPath: str
        """

        if projectPath is not None:
            logging.debug("Switch to the project declared in {0}".format(projectPath))
            newProject = Project.loadProject(self.currentWorkspace, projectPath)
            if newProject is not None and self.closeCurrentProject():
                self.currentProject = newProject
                # Emit a signal for toolbar upgrade
                self.getSignalsManager().emitSignal(SignalsManager.SIG_PROJECT_OPEN)
                self.view.currentProjectHasChanged()
            else:
                self.view.currentProjectHasChanged()

    def getSignalsManager(self):
        """returns the signals manager"""
        return self.signalsManager
