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
from netzob.UI.Common.Views.CustomMathFilterView import CustomMathFilterView
from netzob.Common.Filters.Mathematic.CustomFilter import CustomFilter
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
class CustomMathFilterController(object):
    """Manage the creation of a custom math filter"""

    def __init__(self, vocabularyController, symbol):
        self.vocabularyController = vocabularyController
        self.log = logging.getLogger(__name__)
        self._view = CustomMathFilterView(self)
        self.symbol = symbol
        self.sourceCode = ""
        self.reverseSourceCode = ""
        self.filterName = ""
        self.filter = None

    @property
    def view(self):
        return self._view

    def run(self):
        self.initSourceCode()
        self.initReverseSourceCode()
        self.updateMessages()
        self._view.run()

    def cancelButton_clicked_cb(self, widget):
        """Callback executed when the user clicks
        on the cancel button"""
        self._view.customMathFilterDialog.destroy()

    def applyButton_clicked_cb(self, widget):
        """Callback executed when the user clicks
        on the apply button."""
        self._view.customMathFilterDialog.destroy()

        if self.filter is not None:
            # Create the filter add it to the workspace set of available filters
            workspace = self.vocabularyController.getCurrentWorkspace()
            workspace.addCustomMathFilter(self.filter)

    def testYourFilterButton_clicked_cb(self, widget):
        self.dataUpdated()

    def sourceCodeIsTheSameForReverseCheckButton_toggled_cb(self, widget):
        if self._view.sourceCodeIsTheSameForReverseCheckButton.get_active():
            self._view.filterReverseTextView.set_editable(False)
        else:
            self._view.filterReverseTextView.set_editable(True)

    def initSourceCode(self):
        initialSource = """# Type below the Python source code of your filter.
# The source code must edit the content of a 'message' variable. This variable
# contains an hexastring value (eg. '0b1c3489') you can 'filter'.
# An example of a source code would be :
#
# ! This source code is for abstracting messages (decrypt, decompress received messages...)
#
# An example of a source code would be :
#
# message = '00'+message+'00'
"""
        self._view.filterTextView.get_buffer().set_text(initialSource)

    def initReverseSourceCode(self):
        initialSource = """# Type below the Python source code of your filter.
# The source code must edit the content of a 'message' variable. This variable
# contains an hexastring value (eg. '0b1c3489') you can 'filter'.
#
# ! This source code is for specifying messages (encrypt, compress sent messages...)
#
# An example of a source code would be :
#
# message = '00'+message+'00'
"""
        self._view.filterReverseTextView.get_buffer().set_text(initialSource)

    def dataUpdated(self):
        # retrieve the source code
        self.sourceCode = self._view.filterTextView.get_buffer().get_text(self._view.filterTextView.get_buffer().get_start_iter(), self._view.filterTextView.get_buffer().get_end_iter(), True)

        if self._view.sourceCodeIsTheSameForReverseCheckButton.get_active():
            self.reverseSourceCode = self.sourceCode
        else:
            self.reverseSourceCode = self._view.filterReverseTextView.get_buffer().get_text(self._view.filterReverseTextView.get_buffer().get_start_iter(), self._view.filterReverseTextView.get_buffer().get_end_iter(), True)

        # retrieve the name of the filter
        self.filterName = self._view.nameOfFilterEntry.get_text()

        if self.filterName is not None and len(self.filterName) > 0 and self.sourceCode is not None and len(self.sourceCode) > 0 and self.reverseSourceCode is not None and len(self.reverseSourceCode) > 0:
            self.filter = CustomFilter(self.filterName, self.sourceCode, self.reverseSourceCode)
            errorMessage = self.filter.compileSourceCode()

            if errorMessage is None:
                self._view.applyButton.set_sensitive(True)
                self.updateMessages()
                self._view.imageValid.show()
                self._view.imageError.hide()
                self._view.scrolledwindow3.show_all()
                self._view.labelMessage.set_label(_("Verify below the filtered messages"))
                self._view.labelMessage.show()
            else:
                self.filter = None
                self._view.applyButton.set_sensitive(False)
                self.updateMessages()
                self._view.imageValid.hide()
                self._view.imageError.show()
                self._view.scrolledwindow3.show_all()
                self._view.labelMessage.set_label("{0}".format(errorMessage))
                self._view.labelMessage.show()

            errorMessage = self.filter.compileReverseSourceCode()

            if errorMessage is None:
                self._view.applyButton.set_sensitive(True)
                self._view.imageValid.show()
                self._view.imageError.hide()
                self._view.scrolledwindow3.show_all()
            else:
                self.filter = None
                self._view.applyButton.set_sensitive(False)
                self.updateMessages()
                self._view.imageValid.hide()
                self._view.imageError.show()
                self._view.scrolledwindow3.show_all()
                self._view.labelMessage.set_label("Error with the reverse source code {0}".format(errorMessage))
                self._view.labelMessage.show()

        else:
            self._view.applyButton.set_sensitive(False)
            self._view.imageValid.hide()
            self._view.imageError.show()
            self._view.scrolledwindow3.show_all()
            self._view.labelMessage.set_label(_("Specify the name and the source code of your Filter"))
            self._view.labelMessage.show()

    def updateMessages(self):
        self._view.messagesListStore.clear()

        for message in self.symbol.getMessages():
            original = message.getStringData()
            if self.filter is not None:
                filtered = self.filter.apply(original)
            else:
                filtered = ""
            self.addMessage(original, filtered)

    def addMessage(self, original, filtered):
        i = self._view.messagesListStore.append()
        self._view.messagesListStore.set(i, 0, original)
        self._view.messagesListStore.set(i, 1, filtered)
