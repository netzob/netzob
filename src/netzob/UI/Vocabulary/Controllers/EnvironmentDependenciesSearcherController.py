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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gettext import gettext as _
from gi.repository import Gtk, Gdk
from gi.repository import Pango
import gi
from gi.repository import GObject
from netzob.UI.Vocabulary.Views.EnvironmentDependenciesSearcherView import EnvironmentDependenciesSearcherView
from netzob.Common.Threads.Tasks.ThreadedTask import TaskError, ThreadedTask
from netzob.Inference.Vocabulary.Searcher import Searcher
from netzob.Common.Threads.Job import Job
from netzob.Common.Type.Format import Format
gi.require_version('Gtk', '3.0')
import logging


#+----------------------------------------------
#| Local Imports
#+----------------------------------------------

#+----------------------------------------------
#| EnvironmentDependenciesSearcherController.py:
#+----------------------------------------------
class EnvironmentDependenciesSearcherController(object):

    def __init__(self, vocabularyController, symbols):
        # create logger with the given configuration
        self.log = logging.getLogger(__name__)
        self.vocabularyController = vocabularyController
        self._view = EnvironmentDependenciesSearcherView(self)
        self.symbols = symbols
        self.flagStop = False
        self.searchTasks = None

    def run(self):
        self.log.debug("Start the Environment Dependencies Searcher")
        self._view.run()

    def cancelButton_clicked_cb(self, event):
        """Callback executed when the users cancel the execution
        of the environment deps searcher"""
        self.flagStop = True
        self._view.destroy()

    def executeButton_clicked_cb(self, event):
        """Callback executed when the user requests to start the execution"""
        self._view.cancelButton.set_sensitive(True)

        self.flagStop = False

        # create a job to execute the partitioning
        Job(self.startEnvDepsSearch())

    def startEnvDepsSearch(self):
        if len(self.symbols) > 0:
            try:
                (yield ThreadedTask(self.envDepsSearch))
            except TaskError, e:
                self.log.error("Error while proceeding to the environmental search dependencies on symbols: {0}".format(str(e)))
        else:
            self.log.debug("No symbol selected")

        #close dialog box
        self._view.destroy()

        if self.searchTasks is not None:
            self.vocabularyController.executeAbritrarySearch(self.searchTasks)

    def envDepsSearch(self):
        """Search within symbol the environmental deps"""

        currentProject = self.vocabularyController.getCurrentProject()
        if currentProject is None:
            return

        # Create the Searcher
        searcher = Searcher(currentProject)

        # Retrieve all the possibles env dependencies (properties of messages And vocabulary env deps)
        envDeps = currentProject.getEnvironmentDependencies()

        # Create the search tasks
        self.searchTasks = []
        for prop in envDeps:
            if prop.getFormat() == Format.STRING:
                self.log.debug("Search for String {0}...".format(prop.getCurrentValue()))
#                self.searchTasks.extend(searcher.getSearchedDataForString(str(prop.getCurrentValue())))
            elif prop.getFormat() == Format.IP:
                self.log.debug("Search for IP {0}...".format(prop.getCurrentValue()))
                self.searchTasks.extend(searcher.getSearchedDataForIP(prop.getCurrentValue()))
            else:
                self.log.warn("A property with format {0} cannot be searched.".format(prop.getFormat()))
