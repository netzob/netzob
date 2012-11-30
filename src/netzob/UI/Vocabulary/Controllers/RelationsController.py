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
import cairo
from gi.repository import Gtk, Gdk
import gi
from netzob.UI.Vocabulary.Views.RelationsView import RelationsView
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import os
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class RelationsController(object):

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self._view = RelationsView(self)
        self.log = logging.getLogger(__name__)
        # Create buffer
        self.double_buffer = None
        # position of fields
        self.fieldsPositions = dict()  # {symbol1_ID:{field1_obj:(x1, y1, x2, y2), ...}}

    @property
    def view(self):
        return self._view

    def show(self):
        if self.vocabularyController.getCurrentProject() is None:
            logging.info("Open a project before...")
            return
        self._view.relationsDialog.show()

    def hide(self):
        self._view.relationsDialog.hide()

    def destroy(self):
        self._view.relationsDialog.destroy()

    def on_configure(self, widget, event, data=None):
        """Configure the double buffer based on size of the widget"""

        # Destroy previous buffer
        if self.double_buffer is not None:
            self.double_buffer.finish()
            self.double_buffer = None

        # Create a new buffer
        self.double_buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                widget.get_allocated_width(),
                                                widget.get_allocated_height())

        # Initialize the buffer
        self.draw()

        return False

    def draw(self):
        if self.double_buffer is None:
            self.log.error("Impossible to draw relations since the buffer is invalid (set to None).")

        cc = cairo.Context(self.double_buffer)
#        # Scale to device coordenates
#        cc.scale(self.double_buffer.get_width(), self.double_buffer.get_height())

        # Draw a white background
        cc.set_source_rgb(1, 1, 1)

        # Draw the symbols
        self.draw_symbols(cc)

        self.drawFieldsRelations()

        self.double_buffer.flush()

    def draw_symbols(self, cc):
        """Draw the symbols on a initialized cairo context
        @var cc: the initialized Cairo Context"""

        if self.vocabularyController.getCurrentProject() is None:
            logging.info("Open a project before.")
            return

        currentProject = self.vocabularyController.getCurrentProject()
        symbols = currentProject.getVocabulary().getSymbols()

        rows = len(symbols)
        symbol_vertical_size = 30
        line_width = 1.0
        line_width, notused = cc.device_to_user(line_width, 0.0)

        cc.select_font_face('Sans')
        cc.set_font_size(15)
        cc.set_source_rgb(0, 0, 0)

        max_symbol_name_width = 0

        for i in range(1, len(symbols) + 1):
            symbol = symbols[i - 1]

            # Draw symbol line separators
            cc.move_to(0, i * symbol_vertical_size)
            cc.line_to(self.double_buffer.get_width(), i * symbol_vertical_size)
            cc.set_line_width(line_width)
            cc.stroke()

            xbearing, ybearing, width, height, xadvance, yadvance = (cc.text_extents(symbol.getName()))
            cc.move_to(10, i * symbol_vertical_size - symbol_vertical_size / 2 + height / 2)
            if 10 + width > max_symbol_name_width:
                max_symbol_name_width = 10 + width
            cc.show_text(symbol.getName())
            cc.stroke()

        cc.move_to(max_symbol_name_width + 10, 0)
        cc.line_to(max_symbol_name_width + 10, i * symbol_vertical_size)
        cc.stroke()

        # Draw vertical bytes lines
        initial = max_symbol_name_width + 10
        for nbByte in range(10, self.double_buffer.get_width(), 10):
            cc.move_to(initial + nbByte, 0)
            cc.line_to(initial + nbByte, len(symbols) * symbol_vertical_size)
            cc.set_source_rgb(0.94, 0.94, 0.94)
            cc.stroke()

        # Draw fields
        for i in range(1, len(symbols) + 1):
            symbol = symbols[i - 1]
            y_symbol = i * symbol_vertical_size - symbol_vertical_size / 2
            current_x = max_symbol_name_width + 30
            fieldsPositions = dict()
            for field in symbol.getExtendedFields():
                cc.rectangle(current_x, y_symbol - 10, 30, 20)
                fieldsPositions[field] = [current_x, y_symbol - 10, current_x + 30, y_symbol + 10]
                cc.set_source_rgb(1, 0.86, 0.45)
                cc.fill()

                current_x = current_x + 40
            print fieldsPositions
            self.fieldsPositions[symbol.getID()] = fieldsPositions

    def drawFieldsRelations(self):
        symbols = self.vocabularyController.getCurrentProject().getVocabulary().getSymbols()
        for symbol in symbols:
            for field in symbol.getExtendedFields():
                self.drawFieldRelations(symbol, field)

    def drawFieldRelations(self, symbol, field):
        variable = field.getVariable()
        if variable is None:
            variable = field.getDefaultVariable(symbol)
        # we retrieve all the relations declared in the variable
        relationVariables = self.getRelationsInVariable(variable)

        print relationVariables

    def getRelationsInVariable(self, variable):
        logging.debug("Get relations for variable {0}".format(variable))
        relations = []
        if variable.getTypeVariable() == "AggregateVariable" or variable.getTypeVariable() == "AlternateVariable":
            for v in variable.getChildren():
                relations.extend(self.getRelationsInVariable(v))
        elif variable.getTypeVariable() == "ReferencedVariable":
            relations.append(variable)
        return relations

    def on_motion_notify_event(self, widget, event):
        logging.debug("YESS")

    def on_button_press_event(self, widget, event):
        """Callback executed when the clicks with his
        mouse"""

        if event.button == 1:
            print event.x
            print event.y
            # fetch which field has been clicked on
            clickedField = self.getFieldAtPosition(event.x, event.y)

            if clickedField is not None:
                self.log.debug("Field {0} has been selected.".format(clickedField.getName()))
            else:
                self.log.debug("No field has been selected.")

    def getFieldAtPosition(self, x, y):
        for s in self.fieldsPositions.keys():
            fields = self.fieldsPositions[s]
            for f in fields.keys():
                f_x1 = fields[f][0]
                f_y1 = fields[f][1]
                f_x2 = fields[f][2]
                f_y2 = fields[f][3]
                print "({0}, {1}; {2}, {3})".format(f_x1, f_y1, f_x2, f_y2)
                if f_x1 <= x and f_x2 >= x and f_y1 <= y and f_y2 >= y:
                    return f
        return None

    def on_draw(self, widget, cr):
        """Throw double buffer into widget drawable"""

        if self.double_buffer is not None:
            cr.set_source_surface(self.double_buffer, 0.0, 0.0)
            cr.paint()
        else:
            print('Invalid double buffer')

        return True

    def relationOkButton_clicked_cb(self, widget):
        self.destroy()
