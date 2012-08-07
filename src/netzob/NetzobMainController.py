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
import locale
import gettext
import uuid
import shutil
from lxml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk
import gi
from netzob.Common.Project import Project
from netzob.UI.Common.AboutDialog import AboutDialog
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.DepCheck import DepCheck
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Workspace import Workspace
from netzob.Common.CommandLine import CommandLine
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.LoggingConfiguration import LoggingConfiguration
from netzob.NetzobMainView import NetzobMainView


class NetzobMainController(object):
    """"Netzob main window controller"""

    def __init__(self):
        # Parse command line arguments
        cmdLine = CommandLine()
        cmdLine.parse()
        opts = cmdLine.getOptions()
        # Initialize everything
        self._loadWorkspace(opts)
        self._initLogging()
        self._initResourcesAndLocales()

        # Check dependencies
        if not DepCheck.checkRequiredDependency():
            self.log.fatal("Netzob could not start because some of its required dependencies were not found.")
            sys.exit()

        # Initialize main view
        self.view = None    # small hack since the attribute need to exists when the main glade is loaded
        self.view = NetzobMainView(self)

        # Load all available plugins
        NetzobPlugin.loadPlugins(self)

        # Refresh list of available projects
        self.updateListOfAvailableProjects()

    def _loadWorkspace(self, opts):
        if opts.workspace == None:
            workspace = str(ResourcesConfiguration.getWorkspaceFile())
        else:
            workspace = opts.workspace

        logging.debug("The workspace: {0}".format(str(workspace)))

        # Load workspace
        self.currentWorkspace = (Workspace.loadWorkspace(workspace))

        # the semi-automatic loading of the workspace has failed (second attempt)
        if self.currentWorkspace == None:
            # we force the creation (or specification) of the workspace
            if not ResourcesConfiguration.initializeResources(True):
                logging.fatal("Error while configuring the resources of Netzob")
                sys.exit()
            workspace = str(ResourcesConfiguration.getWorkspaceFile())
            logging.debug("The workspace: {0}".format(str(workspace)))
            # loading the workspace
            self.currentWorkspace = (Workspace.loadWorkspace(workspace))
            if self.currentWorkspace == None:
                logging.fatal("Stopping the execution (no workspace computed)!")
                sys.exit()

        self.currentProject = self.currentWorkspace.getLastProject()

    def _initResourcesAndLocales(self):
        # Initialiaze gettext
        gettext.bindtextdomain("netzob", ResourcesConfiguration.getLocaleLocation())
        gettext.textdomain("netzob")
        try:
            locale.getlocale()
        except:
            logging.exception("setlocale failed, resetting to C")
            locale.setlocale(locale.LC_ALL, "C")

        # Initialize and verify all resources
        if not ResourcesConfiguration.initializeResources():
            logging.fatal("Error while configuring the resources of Netzob")
            sys.exit()

    def _initLogging(self):
        # Create the logging infrastructure
        LoggingConfiguration().initializeLogging(self.currentWorkspace)
        self.log = logging.getLogger(__name__)
        self.log.info(_("Starting netzob"))

    def run(self):
        self.view.run()
        Gtk.main()

    def close(self):
        currentProject = self.getCurrentProject()
        # Close the current project
        if currentProject is not None:
            if currentProject.hasPendingModifications(self.getCurrentWorkspace()) and self.view.offerToSaveCurrentProject():
                self.getCurrentProject().saveConfigFile(self.getCurrentWorkspace())
        # Close the controller
        Gtk.main_quit()

    def getCurrentProject(self):
        return self.currentProject

    def getCurrentWorkspace(self):
        return self.currentWorkspace

    def updateListOfAvailableProjects(self):
        """Fetch the list of available projects in the
        current workspace, and provide them to its associated view"""
        listOfProjectsNameAndPath = self.currentWorkspace.getNameOfProjects()
        self.view.updateSwitchProjectMenu(listOfProjectsNameAndPath)

    def perspectiveComboBox_changed_cb(self, comboBox):
        iter = comboBox.get_active_iter()
        if iter is not None and self.view is not None:
            model = comboBox.get_model()
            newPerspectiveCode = model[iter][0]
            self.view.switchPerspective(newPerspectiveCode)

    def mainWindow_destroy_cb(self, window):
        self.close()

    def entry_disableButtonIfEmpty_cb(self, widget, button):
        if(len(widget.get_text()) > 0):
            button.set_sensitive(True)
        else:
            button.set_sensitive(False)

    def newProject_activate_cb(self, action):
        """Display the dialog in order
        to create a new project when the user request it
        through the menu."""
        finish = False
        errorMessage = None
        while not finish:
            #open dialogbox
            builder2 = Gtk.Builder()
            builder2.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "dialogbox.glade"))
            dialog = builder2.get_object("newProject")
            #button apply
            applybutton = builder2.get_object("newProjectApplyButton")
            applybutton.set_sensitive(False)
            dialog.add_action_widget(applybutton, 0)
            #button cancel
            cancelbutton = builder2.get_object("newProjectCancelButton")
            dialog.add_action_widget(cancelbutton, 1)
            #disable apply button if no text
            entry = builder2.get_object("entry4")
            entry.connect("changed", self.entry_disableButtonIfEmpty_cb, applybutton)
            if errorMessage is not None:
                # Display a warning message on the dialog box
                warnLabel = builder2.get_object("NewProjectWarnLabel")
                warnLabel.set_text(errorMessage)
                warnBox = builder2.get_object("newProjectWarnBox")
                warnBox.show_all()

            #run the dialog window and wait for the result
            result = dialog.run()
            if result == 0:
                newProjectName = entry.get_text()
                dialog.destroy()
                self.log.debug("Verify the uniqueness of project name : {0}".format(newProjectName))
                found = False
                for (projectName, projectPath) in self.currentWorkspace.getNameOfProjects():
                    if projectName == newProjectName:
                        found = True
                        break
                if found:
                    self.log.info(_("A project with the same name already exists ({0}, {1}), please change it.".format(projectName, projectPath)))
                    errorMessage = _("A project with this name exists")
                else:
                    self.log.debug(_("Create new project {0}").format(newProjectName))
                    newProject = Project.createProject(self.getCurrentWorkspace(), newProjectName)
                    self.switchProject(newProject.getPath())
                    finish = True
                    errorMessage = None
            else:
                dialog.destroy()
                finish = True
        if (result == 1):
            #cancel
            dialog.destroy()

    def saveProject_activate_cb(self, action):
        # ++CODE HERE++
        # SAVE THE CURRENT PROJECT
        pass

    def fileSetFileChooser_importProject_cb(self, widget, applyButton):
        """Callback executed when the user
        selects a file in the file chooser of
        the import project dialog box"""
        selectedFile = widget.get_filename()
        if selectedFile is not None:
            applyButton.set_sensitive(True)
        else:
            applyButton.set_sensitive(False)

    def importProject_activate_cb(self, action):
        """Display the dialog in order
        to import a project when the user request it
        through the menu."""
        logging.debug("Import project")
        finish = False
        errorMessage = None
        while not finish:
            #open dialogbox
            builder2 = Gtk.Builder()
            builder2.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "dialogbox.glade"))
            dialog = builder2.get_object("importProject")
            #button apply
            applybutton = builder2.get_object("importProjectApplyButton")
            applybutton.set_sensitive(False)
            dialog.add_action_widget(applybutton, 0)
            #button cancel
            cancelbutton = builder2.get_object("importProjectCancelButton")
            dialog.add_action_widget(cancelbutton, 1)
            #disable apply button if no file is provided
            fileChooserButton = builder2.get_object("importProjectFileChooserButton")
            fileChooserButton.connect("file-set", self.fileSetFileChooser_importProject_cb, applybutton)
            if errorMessage is not None:
                # Display a warning message on the dialog box
                warnLabel = builder2.get_object("importProjectWarnLabel")
                warnLabel.set_text(errorMessage)
                warnBox = builder2.get_object("importProjectWarnBox")
                warnBox.show_all()

            #run the dialog window and wait for the result
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
                        # Retrieving and storing of the config file
                        try:
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
                            logging.warn("Error when importing project: " + str(e))
            else:
                dialog.destroy()
                finish = True
        if (result == 1):
            #cancel
            dialog.destroy()

    def fileSetFileChooserOrFilenamEntry_exportProject_cb(self, widget, fileChooser, fileEntry, applyButton):
        """Callback executed when the user
        selects a file in the file chooser of
        the export project dialog box"""
        currentFolder = fileChooser.get_current_folder()
        currentFile = fileEntry.get_text()
        if currentFolder is not None and len(currentFolder) > 0 and currentFile is not None and len(currentFile) > 0:
            applyButton.set_sensitive(True)
        else:
            applyButton.set_sensitive(False)

    def exportProject_activate_cb(self, action):
        """Display the dialog in order
        to export the current project when the user request it
        through the menu."""
        logging.debug("Export project")
        finish = False
        errorMessage = None
        while not finish:
            #open dialogbox
            builder2 = Gtk.Builder()
            builder2.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "dialogbox.glade"))
            dialog = builder2.get_object("exportProject")
            #button apply
            applybutton = builder2.get_object("exportProjectApplyButton")
            applybutton.set_sensitive(False)
            dialog.add_action_widget(applybutton, 0)
            #button cancel
            cancelbutton = builder2.get_object("exportProjectCancelButton")
            dialog.add_action_widget(cancelbutton, 1)
            #disable apply button if no directory and filename is provided
            fileChooserButton = builder2.get_object("exportProjectFileChooserButton")
            filenameEntry = builder2.get_object("exportProjectFilenameEntry")

            # set the default filename based on current project
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
            #run the dialog window and wait for the result
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
                            logging.debug("Output filename : {0}".format(outputFilename))
                            xmlDefinitionOfProject = self.getCurrentProject().generateXMLConfigFile()
                            tree = ElementTree(xmlDefinitionOfProject)
                            tree.write(outputFilename)
                            finish = True
                            errorMessage = None
                        except IOError, e:
                            errorMessage = _("An error occurred while exporting the project.")
                            logging.warn("Error when importing project: " + str(e))
            else:
                dialog.destroy()
                finish = True
        if (result == 1):
            #cancel
            dialog.destroy()

    def switchWorkspace_activate_cb(self, action):
        #open dialogbox
        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "dialogbox.glade"))
        dialog = builder2.get_object("switchWorkspace")
        #button apply
        applybutton = builder2.get_object("button23")
        dialog.add_action_widget(applybutton, 0)
        #button cancel
        cancelbutton = builder2.get_object("button22")
        dialog.add_action_widget(cancelbutton, 1)
        #run the dialog window and wait for the result
        result = dialog.run()

        if (result == 0):
            #apply
            newWorkspacePath = dialog.get_current_folder()
            self.log.debug(_("Switch to the workspace {0}").format(newWorkspacePath))
            # ++CODE HERE++
            # SWITCH/CREATE THE WORKSPACE FOR newWorkspacePath
            # SWITCH TO THE LAST PROJECT OPEN IN THE WORKSPACE
            # UPDATE VIEW/PROJECT
            dialog.destroy()
        if (result == 1):
            #cancel
            dialog.destroy()

    def quit_activate_cb(self, action):
        """Callback executed when the user
        request to close Netzob"""
        self.close()

    def aboutNetzob_activate_cb(self, action):
        """Displays the about dialog
        when the user click on the associate
        menu entry."""
        AboutDialog.display()

    def switchProject_cb(self, widget, projectPath):
        """Callback for the GTK view in order to
        switch to another project.
        @param projectPath: the path to the project to load
        @type projectPath: str
        """
        self.switchProject(projectPath)

    def switchProject(self, projectPath):
        """Change the current project with the project
        declared in file projectPath. If the loading is successful
        the view is updated
        @param projectPath: the path to the project to load
        @type projectPath: str
        """
        if projectPath is not None:
            logging.debug("Switch to the project declared in {0}".format(projectPath))

            newProject = Project.loadProject(self.currentWorkspace, projectPath)
            if newProject is not None:
                self.currentProject = newProject
                self.view.currentProjectHasChanged()
            else:
                logging.warning("Impossible to load the requested project.")
