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
import logging
#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.UI.Vocabulary.Views.MessagesDistributionView import MessagesDistributionView
import cairo
import math


#+----------------------------------------------
#| MessagesDistributionController:
#+----------------------------------------------
class MessagesDistributionController(object):
    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, vocabularyController, symbolList):
        self.vocabularyController = vocabularyController
        self._view = MessagesDistributionView(self)
        self.log = logging.getLogger(__name__)
        self.symbols = symbolList
        # Create buffer
        self.double_buffer = None

        colors = ["FF0000", "00FF00", "0000FF", "FFFF00", "FF00FF", "00FFFF", "000000",
                  "800000", "008000", "000080", "808000", "800080", "008080", "808080",
                  "C00000", "00C000", "0000C0", "C0C000", "C000C0", "00C0C0", "C0C0C0",
                  "400000", "004000", "000040", "404000", "400040", "004040", "404040",
                  "200000", "002000", "000020", "202000", "200020", "002020", "202020",
                  "600000", "006000", "000060", "606000", "600060", "006060", "606060",
                  "A00000", "00A000", "0000A0", "A0A000", "A000A0", "00A0A0", "A0A0A0",
                  "E00000", "00E000", "0000E0", "E0E000", "E000E0", "00E0E0", "E0E0E0"]

        self.colorBySymbol = dict()
        for i in range(0, len(self.symbols)):
            s = self.symbols[i]
            self.colorBySymbol[s.getID()] = colors[i]

        self.dataPointBySymbol = dict()
        self.scalesBySymbol = dict()
        self.axisByFieldBySymbol = dict()
        self.axisBySymbol = dict()
        self.heightPerSymbol = 15

        currentAxisForSymbol = 5

        for symbol in self.symbols:
            self.axisBySymbol[symbol.getID()] = currentAxisForSymbol
            currentAxisForSymbol += self.heightPerSymbol
            i = 0
            resX = []
            resY = []

            maxX = 0
            maxY = 0

            current_i = 0
            fieldAxis = []
            for field in symbol.getExtendedFields():
                cellsField = field.getUniqValuesByField()

                maxField = 0
                for cell in cellsField:
                    sizeCell = len(cell) / 2
                    if maxField is None or maxField < sizeCell:
                        maxField = sizeCell
                current_i += maxField
                fieldAxis.append(current_i)
            self.axisByFieldBySymbol[symbol.getID()] = fieldAxis

            for field in symbol.getExtendedFields():
                maxCell = -1
                for cell in field.getUniqValuesByField():
                    for j in range(len(cell) / 2):
                        if (i + j) > maxX:
                            maxX = (i + j)
                        resX.append(i + j)

                        valY = int(cell[j * 2:j * 2 + 2], 16)
                        if valY > maxY:
                            maxY = valY
                        resY.append(valY)
                    if len(cell) / 2 > maxCell:
                        maxCell = len(cell) / 2
                i += maxCell
            self.dataPointBySymbol[symbol.getID()] = ([resX, resY])

            scaleX = float(100) / float(maxX)
            scaleY = float(100) / float(maxY)
            self.scalesBySymbol[symbol.getID()] = (scaleX, scaleY)
        self.low_y = currentAxisForSymbol

    @property
    def view(self):
        return self._view

    def run(self):
        if self.vocabularyController.getCurrentProject() is None:
            logging.info("Open a project before...")
            return
        self._view.show()

    def closeButton_clicked_cb(self, widget):
        self._view.destroy()

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

        # Draw a white background
        cc.set_source_rgb(1, 1, 1)

        # Draw the symbols
        for symbol in self.symbols:
            self.draw_symbol(symbol, cc)

        # Draw interface (grids and scales)
        self.draw_interface(cc)

        self.double_buffer.flush()

    def draw_interface(self, cc):
        """Draw the interface on the initialized cairo context
            @var cc: the initialized Cairo Context"""

        line_width = 1.0
        line_width, notused = cc.device_to_user(line_width, 0.0)
        cc.select_font_face('Sans')
        cc.set_font_size(15)
        cc.set_source_rgb(0, 0, 0)

        cc.move_to(80, 20)
        cc.set_line_width(line_width)
        cc.line_to(self.double_buffer.get_width() - 20, 20)
        cc.line_to(self.double_buffer.get_width() - 20, self.double_buffer.get_height() - self.low_y)
        cc.line_to(self.double_buffer.get_width() - 20, self.double_buffer.get_height() - self.low_y)
        cc.line_to(80, self.double_buffer.get_height() - self.low_y)
        cc.line_to(80, 20)

        # Show different values 0 and 255
        cc.set_font_size(8)
        cc.move_to(60, 25)
        cc.show_text("255")
        cc.move_to(70, self.double_buffer.get_height() - self.low_y)
        cc.show_text("0")
        cc.stroke()

        cc.move_to(20, (self.double_buffer.get_height() - self.low_y) / 2 + 10)
        cc.show_text("Bytes values")

        # Show percent (0%, 100%)
        cc.move_to(75, self.double_buffer.get_height() - self.low_y + 8)
        cc.show_text("0%")

        cc.move_to(self.double_buffer.get_width() - 35, self.double_buffer.get_height() - self.low_y + 8)
        cc.show_text("100%")

        cc.move_to((self.double_buffer.get_width() - 20) / 2, self.double_buffer.get_height() - self.low_y + 8)
        cc.show_text("Bytes")

    def draw_symbol(self, symbol, cc):
        i = 0
        hexColor = self.colorBySymbol[symbol.getID()]
        dec1Color = int(hexColor[0:2], 16)
        dec2Color = int(hexColor[2:4], 16)
        dec3Color = int(hexColor[4:6], 16)

        x_mul = float(self.double_buffer.get_width() - 100) / 100
        y_mul = float(self.double_buffer.get_height() - 20 - self.low_y) / 100

        (x_scale, y_scale) = self.scalesBySymbol[symbol.getID()]

        y_axis_symbol = self.double_buffer.get_height() - self.axisBySymbol[symbol.getID()]
        symbolShortName = symbol.getName()
        if len(symbolShortName) > 15:
            symbolShortName = symbolShortName[:12] + "..."
        cc.set_source_rgb(dec1Color, dec2Color, dec3Color)
        cc.move_to(2, y_axis_symbol + 5)
        cc.show_text(symbolShortName)

        # Draw symbol names and fields info
        fieldsAxis = self.axisByFieldBySymbol[symbol.getID()]
        x = 80
        cc.move_to(x, y_axis_symbol)
        for axis in fieldsAxis:
            cc.move_to(x, y_axis_symbol)
            x = 80 + (axis * x_scale * x_mul)
            cc.line_to(x, y_axis_symbol)
            cc.move_to(x, y_axis_symbol - 5)
            cc.line_to(x, y_axis_symbol + 5)
            cc.move_to(x, y_axis_symbol)
            cc.set_source_rgb(dec1Color, dec2Color, dec3Color)
            cc.stroke()

        (xval, yval) = self.dataPointBySymbol[symbol.getID()]
        for i in range(0, len(xval)):
            x = 80 + (xval[i] * x_scale * x_mul)
            y = 20 + ((255 - yval[i]) * y_scale * y_mul)

            cc.arc(x, y, 1, 0, 2 * math.pi)
            cc.set_source_rgb(1, 1, 1)
            cc.fill_preserve()

            cc.set_source_rgb(dec1Color, dec2Color, dec3Color)
            cc.stroke()

    def on_draw(self, widget, cr):
        """Throw double buffer into widget drawable"""

        if self.double_buffer is not None:
            cr.set_source_surface(self.double_buffer, 0.0, 0.0)
            cr.paint()
        else:
            print('Invalid double buffer')

        return True
