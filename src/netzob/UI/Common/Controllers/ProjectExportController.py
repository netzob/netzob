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
from locale import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import os
import os.path
from lxml.etree import ElementTree
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Common.Views.ProjectExportView import ProjectExportView


class ProjectExportController(object):
    """Manage export of an existing project."""

    def __init__(self, mainController, parent=None, project=None):
        self.mainController = mainController
        self.log = logging.getLogger(__name__)
        self.workspace = mainController.getCurrentWorkspace()

        if project:
            self.project = project
        else:
            self.project = self.mainController.getCurrentProject()

        if not parent:
            parent = mainController.view.mainWindow
        self._view = ProjectExportView(self, parent=parent)

    @property
    def view(self):
        if hasattr(self, "_view"):
            return self._view
        return False

    def run(self):
        self.view.run()

    def closebutton_clicked_cb(self, widget):
        self.view.destroy()

    def exportProjectFileChooserButton_current_folder_changed_cb(self, widget, fileChooser, fileEntry, applyButton):
        pass

    def exportProjectFileChooserButton_current_folder_changed_cb(self, fileChooser):
        """Callback executed when the user selects a file in the file
        chooser of the export project dialog box"""
        self._refreshButtonsSensitivity()

    def exportProjectFilenameEntry_changed_cb(self, entry):
        self._refreshButtonsSensitivity()

    def _refreshButtonsSensitivity(self):
        currentFolder = self.view.exportProjectFileChooserButton.get_current_folder()
        currentFile = self.view.exportProjectFilenameEntry.get_text()
        applyButton = self.view.exportProjectApplyButton

        if currentFolder is not None and len(currentFolder) > 0 and currentFile is not None and len(currentFile) > 0:
            applyButton.set_sensitive(True)
        else:
            applyButton.set_sensitive(False)

    def exportProjectApplyButton_clicked_cb(self, button):
        """Display the dialog in order to export the current project
        when the user request it through the menu."""

        logging.debug("Export project")

        try:
            selectedFolder = self.view.exportProjectFileChooserButton.get_current_folder()
            filename = self.view.exportProjectFilenameEntry.get_text()

            if selectedFolder is None:
                raise Exception(_("No directory selected"))
            elif filename is None or len(filename) == 0:
                raise Exception(_("No filename provided"))
            else:
                outputFilename = os.path.join(selectedFolder, filename)
                logging.debug("Output filename: {0}".format(outputFilename))
                overwrite = True

                if os.path.exists(outputFilename):
                    questionMsg = _("A file named \"{0}\" already exists. Do you want to replace it?").format(filename)

                    dialog = Gtk.MessageDialog(self.view.exportProject,
                                               Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                               Gtk.MessageType.WARNING,
                                               Gtk.ButtonsType.NONE,
                                               questionMsg)

                    dialog.format_secondary_text(_("The file already exists in \"{0}\". Replacing it will overwrite its contents.").format(selectedFolder))

                    dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
                    dialog.add_button(_("Replace"), Gtk.ResponseType.YES)
                    dialog.set_default_response(Gtk.ResponseType.YES)

                    response = dialog.run()
                    dialog.destroy()

                    if response == Gtk.ResponseType.CANCEL:
                        self.view.destroy()
                        self.log.info("Export was cancelled")
                        return

                xmlDefinitionOfProject = self.project.generateXMLConfigFile()
                tree = ElementTree(xmlDefinitionOfProject)
                tree.write(outputFilename, pretty_print=True)
                self.view.destroy()

        except Exception, e:
            self.view.showErrorMessage(_("An error occurred while exporting the project."))
            logging.warn("Error when exporting project: {0}".format(e))
