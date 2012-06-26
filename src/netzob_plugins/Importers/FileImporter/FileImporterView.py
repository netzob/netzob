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
from gi.repository import Gtk
import gi
from bitarray import bitarray
gi.require_version('Gtk', '3.0')
from gettext import gettext as _

#+----------------------------------------------
#| FileImporterView:
#|     GUI for capturing messages from files
#+----------------------------------------------
class FileImporterView(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self):
        panel = self.buildPanel()

        self.dialog = Gtk.Dialog(title=_("Import file"), flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(panel, True, True, 0)
        self.dialog.set_size_request(1000, 600)

    def buildPanel(self):
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        panel = Gtk.Table(rows=10, columns=8, homogeneous=True)
        panel.show()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Select a file
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.butSelectFiles = Gtk.Button(_("Select file(s)"))
        self.butSelectFiles.show()
        self.entryFilepath = Gtk.Entry()
        self.entryFilepath.set_text("")
        self.entryFilepath.show()
        panel.attach(self.butSelectFiles, 0, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)
        panel.attach(self.entryFilepath, 2, 6, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Separator
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        label_separator = Gtk.Label(label=_("HEX line-separator (ex: 0a) :"))
        label_separator.show()
        self.entrySeparator = Gtk.Entry()
        self.entrySeparator.set_text("")
        self.entrySeparator.show()

        panel.attach(label_separator, 0, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)
        panel.attach(self.entrySeparator, 2, 6, 1, 2, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # File details
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll = Gtk.ScrolledWindow()
        self.textview = Gtk.TextView()
        self.textview.show()
        self.textview.get_buffer().create_tag("normalTag", family="Courier")

        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        panel.attach(scroll, 0, 6, 2, 10, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Extracted data
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll2 = Gtk.ScrolledWindow()
        self.lineView = Gtk.TreeView(Gtk.TreeStore(str, str))  # line number, content
        self.lineView.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        cell = Gtk.CellRendererText()
        # Col file descriptor
        column = Gtk.TreeViewColumn(_("Message ID"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 0)
        self.lineView.append_column(column)
        self.lineView.show()

        scroll2.add(self.lineView)
        scroll2.show()
        scroll2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        panel.attach(scroll2, 6, 8, 0, 10, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # Button select packets for further analysis
        self.butValidateMessages = Gtk.Button(label=_("Import"))
        self.butValidateMessages.show()
        panel.attach(self.butValidateMessages, 2, 3, 10, 11, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        return panel
