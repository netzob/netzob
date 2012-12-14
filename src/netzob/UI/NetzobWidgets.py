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
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk, Pango
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


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
    combo = Gtk.ComboBoxText.new_with_entry()
    combo.show()
    combo.set_model(Gtk.ListStore(str))
    cell = combo.get_cells()[0]  # Get the cellrenderer
    cell.set_property("size-points", 9)
    return combo


#+---------------------------------------------------------------------------+
#| NetzobProgressBar:
#+---------------------------------------------------------------------------+
def NetzobProgressBar(text=None):
    pb = Gtk.ProgressBar()
    if text is not None:
        pb.set_text(text)

    pb.show()
    return pb


#+---------------------------------------------------------------------------+
#| NetzobErrorMessage:
#+---------------------------------------------------------------------------+
def NetzobErrorMessage(text, parent=None):
    md = Gtk.MessageDialog(parent,
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


#+---------------------------------------------------------------------------+
#| NetzobQuestionMessage:
#+---------------------------------------------------------------------------+
def NetzobQuestionMessage(text):
    md = Gtk.MessageDialog(None,
                           Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                           Gtk.MessageType.QUESTION,
                           Gtk.ButtonsType.YES_NO,
                           text)
    result = md.run()
    md.destroy()
    return result


def addNetzobIconsToDefaultFactory():
    def addIconToFactory(iconStockID, iconFilename):
        iconSet = Gtk.IconSet()
        iconSource = Gtk.IconSource()
        iconPath = os.path.abspath(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "icons",
            "24x24",
            iconFilename))
        iconSource.set_filename(iconPath)
        iconSource.set_size(Gtk.IconSize.LARGE_TOOLBAR)
        iconSet.add_source(iconSource)
        netzobIconFactory.add(iconStockID, iconSet)
    netzobIconFactory = Gtk.IconFactory()
    addIconToFactory("netzob-import-messages", "import-messages.png")
    addIconToFactory("netzob-capture-messages", "capture-messages.png")
    addIconToFactory("netzob-partitioning-sequence", "partitioning-sequence.png")
    addIconToFactory("netzob-partitioning-simple", "partitioning-simple.png")
    addIconToFactory("netzob-partitioning-force", "partitioning-force.png")
    addIconToFactory("netzob-partitioning-smooth", "partitioning-smooth.png")
    addIconToFactory("netzob-partitioning-reset", "partitioning-reset.png")
    addIconToFactory("netzob-partitioning-freeze", "partitioning-freeze.png")
    addIconToFactory("netzob-concat-field", "concat-field.png")
    addIconToFactory("netzob-concat-symbol", "concat-symbol.png")
    addIconToFactory("netzob-edit-cut-left", "split-field.png")
    addIconToFactory("netzob-edit-cut-right", "edit-cut-right.png")
    addIconToFactory("netzob-create-variable", "create-variable.png")
    addIconToFactory("netzob-move-to-symbol", "move-to-symbol.png")
    addIconToFactory("netzob-search-environment-dep", "search-environment-dep.png")
    addIconToFactory("netzob-messages-distribution", "messages-distribution.png")
    addIconToFactory("netzob-filter-messages", "filter-messages.png")
    addIconToFactory("netzob-variable-table", "variable-table.png")
    addIconToFactory("netzob-field-limit", "field-limit.png")
    addIconToFactory("netzob-select-all", "select-all.png")
    addIconToFactory("netzob-unselect-all", "unselect-all.png")
    addIconToFactory("netzob-concat-symbol", "concat-symbol.png")
    addIconToFactory("netzob-rename", "rename.png")
    addIconToFactory("netzob-new-window", "new-window.png")
    addIconToFactory("grammar-add-state", "grammar-add-state.png")
    addIconToFactory("grammar-add-open", "grammar-add-open.png")
    addIconToFactory("grammar-add-stochastic", "grammar-add-stochastic.png")
    addIconToFactory("grammar-add-close", "grammar-add-close.png")
    Gtk.IconFactory.add_default(netzobIconFactory)
