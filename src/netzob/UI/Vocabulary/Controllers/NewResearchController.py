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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import os
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

    @property
    def view(self):
        return self._view

    def show(self):
        print "show research bar"
        self._view.researchBar.show()

    def hide(self):
        self._view.researchBar.hide()

    def research_entry_changed_cb(self, widget):
        text = widget.get_text()
        # ++CODE HERE++
        # DO SEARCH WITH PREFERENCES
        # (you can see PREFERENCES in the preferencesResearchDialog at VocabularyView.glade)

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
