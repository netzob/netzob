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
#| Global Imports
#+---------------------------------------------------------------------------+
import gtk
import pango
import pygtk
pygtk.require('2.0')

#+---------------------------------------------------------------------------+
#| NetzobLabel:
#| @param text: the string of the label
#+---------------------------------------------------------------------------+
def NetzobLabel(text):
    label = gtk.Label(text)
    label.show()
    label.modify_font(pango.FontDescription("sans 9"))
    return label

#+---------------------------------------------------------------------------+
#| NetzobButton:
#| @param text: the string of the button
#+---------------------------------------------------------------------------+
def NetzobButton(text):
    but = gtk.Button(gtk.STOCK_OK)
    but.set_label(text)
    but.show()
    if but.get_use_stock():
        label = but.child.get_children()[1]
        label.modify_font(pango.FontDescription("sans 9"))
    elif isinstance(but.child, gtk.Label):
        label = but.child
        label.modify_font(pango.FontDescription("sans 9"))
    return but

#+---------------------------------------------------------------------------+
#| NetzobFrame:
#| @param text: the string of the frame
#+---------------------------------------------------------------------------+
def NetzobFrame(text):
    frame = gtk.Frame()
    frame.set_label(text)
    frame.show()
    label = frame.get_label_widget()
    label.modify_font(pango.FontDescription("sans 9"))
    return frame

#+---------------------------------------------------------------------------+
#| NetzobComboBoxEntry:
#+---------------------------------------------------------------------------+
def NetzobComboBoxEntry():
    combo = gtk.combo_box_entry_new_text()
    combo.show()
    combo.set_model(gtk.ListStore(str))
    cell = combo.get_cells()[0]  # Get the cellrenderer
    cell.set_property("size-points", 9)
    return combo

#+---------------------------------------------------------------------------+
#| NetzobProgressBar:
#+---------------------------------------------------------------------------+
def NetzobProgressBar(text=None):
    pb = gtk.ProgressBar(adjustment=None)
    if text != None:
        pb.set_text(text)

    pb.show()
    return pb
