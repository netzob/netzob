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
import time

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk, GObject
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Pango

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.SplitFieldView import SplitFieldView
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.UI.NetzobWidgets import NetzobErrorMessage


class SplitFieldController(object):
    """Split a field in two fields"""

    def __init__(self, vocabularyController, field):
        self.vocabularyController = vocabularyController
        self._view = SplitFieldView(self)
        self.log = logging.getLogger(__name__)
        self.field = field

    @property
    def view(self):
        return self._view

    def run(self):
        if self.initBuffer() == False:
            return
        self._view.run()

    #+----------------------------------------------
    #|  rightClickToSplitColumn:
    #|   Callback to split a column
    #+----------------------------------------------
    def initBuffer(self):
        self.split_position = 1
        self.split_min_len = 999999
        self.split_max_len = 0
        self.split_align = "left"

        # Find the size of the shortest/longest message
        cells = self.field.getCells()
        for m in cells:
            if len(m) > self.split_max_len:
                self.split_max_len = len(m)
            if len(m) < self.split_min_len:
                self.split_min_len = len(m)

        if self.split_min_len == 0:
            self.view.splitFieldDialog.destroy()
            NetzobErrorMessage(_("Can't split field with empty cell(s)."))
            return False

        self.view.buffer.get_buffer().create_tag("redTag", weight=Pango.Weight.BOLD, foreground="red", family="Courier")
        self.view.buffer.get_buffer().create_tag("greenTag", weight=Pango.Weight.BOLD, foreground="#006400", family="Courier")

        for m in cells:
            self.view.buffer.get_buffer().insert_with_tags_by_name(self.view.buffer.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:self.split_position], self.field.getFormat()) + "  ", "redTag")
            self.view.buffer.get_buffer().insert_with_tags_by_name(self.view.buffer.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[self.split_position:], self.field.getFormat()) + "\n", "greenTag")

    def cancel_clicked_cb(self, widget):
        self.view.splitFieldDialog.destroy()
        self.vocabularyController.view.updateSymbolList()

    def doSplit_clicked_cb(self, widget):
        if self.split_max_len <= 1:
            self.view.splitFieldDialog.destroy()
            return

        if self.split_align == "right":
            split_index = -self.split_position
        else:
            split_index = self.split_position
        self.field.splitField(split_index, self.split_align)
        self.view.splitFieldDialog.destroy()
        self.vocabularyController.view.updateSelectedMessageTable()

    def adjustSplitLeft_clicked_cb(self, widget):
        self.adjustSplit_clicked("left")

    def adjustSplitRight_clicked_cb(self, widget):
        self.adjustSplit_clicked("right")

    def adjustSplit_clicked(self, direction):
        if self.split_max_len <= 1:
            return
        messages = self.field.getCells()

        # Bounds checking
        if self.split_align == "left":
            if direction == "left":
                self.split_position -= 1
                if self.split_position < 1:
                    self.split_position = 1
            else:
                self.split_position += 1
                if self.split_position > self.split_min_len - 1:
                    self.split_position = self.split_min_len - 1
                    if self.split_position == 0:
                        self.split_position = 1
        else:
            if direction == "left":
                self.split_position += 1
                if self.split_position > self.split_min_len - 1:
                    self.split_position = self.split_min_len - 1
                    if self.split_position == 0:
                        self.split_position = 1
            else:
                self.split_position -= 1
                if self.split_position < 1:
                    self.split_position = 1

        # Colorize text according to position
        self.view.buffer.get_buffer().set_text("")
        for m in messages:
            # Crate padding in case of right alignment
            if self.split_align == "right":
                padding = ""
                messageLen = len(m)
                for i in range(self.split_max_len - messageLen):
                    padding += " "
                self.view.buffer.get_buffer().insert_with_tags_by_name(self.view.buffer.get_buffer().get_end_iter(), padding, "greenTag")
                split_index = -self.split_position
            else:
                split_index = self.split_position
            self.view.buffer.get_buffer().insert_with_tags_by_name(self.view.buffer.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:split_index], self.field.getFormat()) + "  ", "redTag")
            self.view.buffer.get_buffer().insert_with_tags_by_name(self.view.buffer.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[split_index:], self.field.getFormat()) + "\n", "greenTag")

    def changeAlignment_clicked_cb(self, widget):
        if self.split_align == "left":
            self.split_align = "right"
        else:
            self.split_align = "left"

        messages = self.field.getCells()

        # Adapt alignment
        self.view.buffer.get_buffer().set_text("")
        for m in messages:
            # Crate padding in case of right alignment
            if self.split_align == "right":
                padding = ""
                messageLen = len(m)
                for i in range(self.split_max_len - messageLen):
                    padding += " "
                self.view.buffer.get_buffer().insert_with_tags_by_name(self.view.buffer.get_buffer().get_end_iter(), padding, "greenTag")
                split_index = -self.split_position
            else:
                split_index = self.split_position
            self.view.buffer.get_buffer().insert_with_tags_by_name(self.view.buffer.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:split_index], self.field.getFormat()) + "  ", "redTag")
            self.view.buffer.get_buffer().insert_with_tags_by_name(self.view.buffer.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[split_index:], self.field.getFormat()) + "\n", "greenTag")
