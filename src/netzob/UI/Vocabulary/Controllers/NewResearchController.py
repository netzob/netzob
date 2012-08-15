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
import logging
import os
import time

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.Common.Threads.Job import Job
from netzob.Common.Threads.Tasks.ThreadedTask import TaskError, ThreadedTask
from netzob.Inference.Vocabulary.SearchTask import SearchTask
from netzob.Common.Type.Format import Format
from netzob.Inference.Vocabulary.Searcher import Searcher
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.NewResearchView import NewResearchView
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class NewResearchController(object):

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self._view = NewResearchView(self)
        self.log = logging.getLogger(__name__)
        self.searchRunning = False
        self.stopFlag = False

    @property
    def view(self):
        return self._view

    def show(self):
        self._view.researchBar.show()

    def hide(self):
        self._view.researchBar.hide()

    def research_entry_changed_cb(self, widget):
        """Callback executed when the user types some
        data in the research entry"""

        if self.vocabularyController.getCurrentProject() is None:
            return

        text = widget.get_text()
        tformat = self._view.research_format.get_active_text()

        # Stop current search process (and wit for it stops)
        self.stopSearch()
        while self.searchRunning:
            time.sleep(0.001)

        # Disallow nav in search results while none are computed
        self._view.research_previous.set_sensitive(False)
        self._view.research_next.set_sensitive(False)

        if len(text) > 0:
            Job(self.startNewSearch(text, tformat))

    def startNewSearch(self, text, format):
        """Start a search process with the provided text and format"""
        try:
            (yield ThreadedTask(self.search, text, format))
        except TaskError, e:
            self.log.error(_("Error while proceeding to the search process: {0}").format(str(e)))

    def search(self, text, format):
        """Execute the search process (to be executed in a dedicated thread)"""
        self.searchRunning = True

        symbols = self.vocabularyController.getCurrentProject().getVocabulary().getSymbols()
        GObject.idle_add(self._view.spinnerSearchProcess.show)
        GObject.idle_add(self._view.spinnerSearchProcess.start)

        # create a task for the text
        searcher = Searcher(self.vocabularyController.getCurrentProject())
        # generate variations for each provided format (see glade file)
        if format == "string":
            searchTasks = searcher.getSearchedDataForString(text)
        elif format == "hexa":
            searchTasks = searcher.getSearchedDataForHexadecimal(text)
        elif format == "decimal":
            searchTasks = searcher.getSearchedDataForDecimal(text)
        elif format == "octal":
            searchTasks = searcher.getSearchedDataForOctal(text)
        elif format == "binary":
            searchTasks = searcher.getSearchedDataForBinary(text)
        elif format == "ipv4":
            searchTasks = searcher.getSearchedDataForIP(text)
        else:
            searchTasks = None
            self.log.error("Cannot search for data if provided with type {0}".format(format))

        if searchTasks is not None:
            searchTasks = searcher.search(searchTasks)
            nbResult = 0
            for searchTask in searchTasks:
                nbResult += len(searchTask.getResults())

            if nbResult == 0:
                GObject.idle_add(self._view.imageWarning.show)
                GObject.idle_add(self._view.numberOfResultLabel.show)
                GObject.idle_add(self._view.numberOfResultLabel.set_label, _("No occurrence found."))
            else:
                GObject.idle_add(self._view.imageWarning.hide)
                GObject.idle_add(self._view.numberOfResultLabel.show)
                if nbResult > 1:
                    GObject.idle_add(self._view.numberOfResultLabel.set_label, _("{0} occurrences found.".format(nbResult)))
                else:
                    GObject.idle_add(self._view.numberOfResultLabel.set_label, _("{0} occurrence found.".format(nbResult)))

            if not self.stopFlag and nbResult > 0:
                # if search has completed (not stopped), nav. is allowed
                GObject.idle_add(self._view.research_previous.set_sensitive, True)
                GObject.idle_add(self._view.research_next.set_sensitive, True)

        self.searchRunning = False
        self.stopFlag = False
        GObject.idle_add(self._view.spinnerSearchProcess.stop)
        GObject.idle_add(self._view.spinnerSearchProcess.hide)

    def stopSearch(self):
        """Stop any current search process"""
        if self.searchRunning:
            self.stopFlag = True

    def research_previous_clicked_cb(self, widget):
        # ++CODE HERE++
        # SEARCH PREVIOUS TEXT IN A MESSAGELIST SYMBOL
        # PRINT IT WITH MODIFIED COLOR
        pass

    def research_next_clicked_cb(self, widget):
        # ++CODE HERE++
        # SEARCH NEXT TEXT IN A MESSAGELIST SYMBOL
        # PRINT IT WITH MODIFIED COLOR
        pass

    def research_close_clicked_cb(self, widget):
        self.hide()

    def research_preferences_clicked_cb(self, widget):
        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui",
            "research_preferences.glade"))
        dialog = builder2.get_object("preferencesResearchDialog")

        # ++CODE HERE++
        # SET THE RIGHT VALUE FOR THE RESEARCH 5 PREFERENCES
        # GO TO THE FILE VocabularyView.glade TO SEE NAME OF WIDGET
        # +exemple+ TO SET THE VALUE OF THE FIRST LINE TOGGLE FOR research_displaySymbol
        # JUST DO THAT :
        # builder2.get_object("research_displaySymbol").set_active(True)
        #button apply
        applybutton = builder2.get_object("apply_preferences")
        dialog.add_action_widget(applybutton, 0)
        #button cancel
        cancelbutton = builder2.get_object("cancel_preferences")
        dialog.add_action_widget(cancelbutton, 1)
        #run the dialog window and wait for the result
        result = dialog.run()

        if (result == 0):
            #apply
            # ++CODE HERE++
            # SET THE RIGHT VALUE FOR THE RESEARCH 5 PREFERENCES TO THE MODEL
            # GO TO THE FILE VocabularyView.glade TO SEE NAME OF WIDGET
            # +exemple+ TO GET THE VALUE OF research_displaySymbol
            # DO THAT :
            # boolean = builder2.get_object("research_displaySymbol").get_active()

            dialog.destroy()
        if (result == 1):
            #cancel
            dialog.destroy()
