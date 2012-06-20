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
from gettext import gettext as _
from gi.repository import Gtk
from gi.repository import Pango
import gi
gi.require_version('Gtk', '3.0')


#+---------------------------------------------------------------------------+
#| NetzobLabel:
#| @param text: the string of the label
#+---------------------------------------------------------------------------+
def NetzobLabel(text):
    label = Gtk.Label(label=text)
    label.show()
    label.modify_font(Pango.FontDescription("sans 9"))
    return label


#+---------------------------------------------------------------------------+
#| NetzobButton:
#| @param text: the string of the button
#+---------------------------------------------------------------------------+
def NetzobButton(text):
    but = Gtk.Button(Gtk.STOCK_OK)
    but.set_label(text)
    but.show()
    if but.get_use_stock():
        label = but.get_child().get_children()[1]
        label.modify_font(Pango.FontDescription("sans 9"))
    elif isinstance(but.get_child(), Gtk.Label):
        label = but.get_child()
        label.modify_font(Pango.FontDescription("sans 9"))
    return but


#+---------------------------------------------------------------------------+
#| NetzobFrame:
#| @param text: the string of the frame
#+---------------------------------------------------------------------------+
def NetzobFrame(text):
    frame = Gtk.Frame()
    frame.set_label(text)
    frame.show()
    label = frame.get_label_widget()
    label.modify_font(Pango.FontDescription("sans 9"))
    return frame


#+---------------------------------------------------------------------------+
#| NetzobComboBoxEntry:
#+---------------------------------------------------------------------------+
def NetzobComboBoxEntry():
    combo = Gtk.combo_box_entry_new_text()
    combo.show()
    combo.set_model(Gtk.ListStore(str))
    cell = combo.get_cells()[0]  # Get the cellrenderer
    cell.set_property("size-points", 9)
    return combo


#+---------------------------------------------------------------------------+
#| NetzobProgressBar:
#+---------------------------------------------------------------------------+
def NetzobProgressBar(text=None):
    pb = Gtk.ProgressBar(adjustment=None)
    if text != None:
        pb.set_text(text)

    pb.show()
    return pb


#+---------------------------------------------------------------------------+
#| NetzobErrorMessage:
#+---------------------------------------------------------------------------+
def NetzobErrorMessage(text):
    md = Gtk.MessageDialog(None,
                           Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                           Gtk.MessageType.ERROR,
                           Gtk.ButtonsType.CLOSE,
                           text)
    md.run()
    md.destroy()


#+---------------------------------------------------------------------------+
#| NetzobInfoMessage:
#+---------------------------------------------------------------------------+
def NetzobInfoMessage(text):
    md = Gtk.MessageDialog(None,
                           Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                           Gtk.MessageType.INFO,
                           Gtk.ButtonsType.CLOSE,
                           text)
    md.run()
    md.destroy()
