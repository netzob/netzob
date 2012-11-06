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
import os
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class ImportFileChooserDialog(object):

    GLADE_FILENAME = "importFileChooserDialog.glade"
    RESPONSE_OK = 0
    RESPONSE_CANCEL = 1

    def __init__(self, pluginList):
        self.pluginDict = {}
        for plugin in pluginList:
            self.pluginDict[plugin.getFileTypeDescription()] = plugin
        self.builder = Gtk.Builder()
        gladeFilePath = os.path.join(
            ResourcesConfiguration.getStaticResources(), "ui", "import",
            ImportFileChooserDialog.GLADE_FILENAME)
        self.builder.add_from_file(gladeFilePath)
        self.builder.connect_signals(self)
        self._getObjects(["importFileChooserDialog", "importTypeComboBox"])
        self.log = logging.getLogger(__name__)
        self.log.debug("Create import FileChooserDialog with plugins: "
                       + ", ".join([plugin.getFileTypeDescription()
                                    for plugin in self.pluginDict.itervalues()]))
        importTypeAlign = self.builder.get_object("importTypeAlign")
        styleContext = importTypeAlign.get_style_context()
        styleContext.add_class("primary-toolbar")
        self.importTypeUserChoice = None
        self.pluginWithPriorityList = []

    def run(self):
        return self.importFileChooserDialog.run()

    def destroy(self):
        return self.importFileChooserDialog.destroy()

    def getFilenameListAndPlugin(self):
        filenameList = self.importFileChooserDialog.get_filenames()
        pluginText = self.importTypeComboBox.get_active_text()
        plugin = self.pluginDict[pluginText]
        return (filenameList, plugin)

    def importFileChooserDialog_selection_changed_cb(self, widget):
        filenameList = self.importFileChooserDialog.get_filenames()
        self.log.debug("Selected files: " + ", ".join(filenameList))
        # Only keep plugins that can handle all selected
        # files
        self.pluginWithPriorityList = []
        selectionIndex = -1
        for plugin in self.pluginDict.itervalues():
            canHandleAllFiles = True
            for filename in filenameList:
                if not plugin.canHandleFile(filename):
                    canHandleAllFiles = False
                    break
            if canHandleAllFiles:
                pluginDesc = plugin.getFileTypeDescription()
                if self.importTypeUserChoice == pluginDesc:
                    print pluginDesc
                    selectionIndex = len(self.pluginWithPriorityList)
                self.pluginWithPriorityList.append((plugin.PLUGIN_PRIORITY,
                                                    pluginDesc))
        self.log.debug("Filtered plugins: " + ", ".join(["{0}:{1}".format(*p)
                                                         for p in self.pluginWithPriorityList]))
        # Sort plugin list by priority
        self.pluginWithPriorityList = sorted(self.pluginWithPriorityList,
                                             key=lambda t: t[0])
        self.importTypeComboBox.remove_all()
        for pluginWithPrio in self.pluginWithPriorityList:
            self.importTypeComboBox.prepend_text(pluginWithPrio[1])
        # If a specific import plugin was selected by the user
        # previously, keep it as default if possible.
        # Otherwise, use the plugin with the highest priority
        # as default
        if selectionIndex != -1:
            self.importTypeComboBox.set_active(selectionIndex)
            self.log.debug("Default selection: {0}".format(selectionIndex))
        else:
            self.importTypeUserChoice = None
            self.importTypeComboBox.set_active(0)

    def importTypeComboBox_changed_cb(self, widget):
        pluginText = self.importTypeComboBox.get_active_text()
        # Memorize user choice if it is not the default choice
        if pluginText is not None and \
                ((pluginText != self.importTypeUserChoice and
                 self.importTypeUserChoice is not None) or
                 (pluginText != self.pluginWithPriorityList[len(self.pluginWithPriorityList) - 1][1] and
                 self.importTypeUserChoice is None)):
            self.log.debug("Setting {0} as user choice".format(pluginText))
            self.importTypeUserChoice = pluginText

    def _getObjects(self, objectsList):
        for object in objectsList:
            setattr(self, object, self.builder.get_object(object))
