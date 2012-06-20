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
import gtk
import pygtk
from bitarray import bitarray
pygtk.require('2.0')


#+----------------------------------------------
#| FileImportView:
#|     GUI for capturing messages from files
#+----------------------------------------------
class FileImportView():

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self):
        panel = self.buildPanel()

        self.dialog = gtk.Dialog(title=_("Import file"), flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(panel, True, True, 0)
        self.dialog.set_size_request(1000, 600)

    def buildPanel(self):
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        panel = gtk.Table(rows=10, columns=8, homogeneous=True)
        panel.show()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Select a file
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.butSelectFiles = gtk.Button(_("Select file(s)"))
        self.butSelectFiles.show()
        self.entryFilepath = gtk.Entry()
        self.entryFilepath.set_text("")
        self.entryFilepath.show()
        panel.attach(self.butSelectFiles, 0, 2, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)
        panel.attach(self.entryFilepath, 2, 6, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Separator
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        label_separator = gtk.Label(_("HEX line-separator (ex: 0a) :"))
        label_separator.show()
        self.entrySeparator = gtk.Entry()
        self.entrySeparator.set_text("")
        self.entrySeparator.show()

        panel.attach(label_separator, 0, 2, 1, 2, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)
        panel.attach(self.entrySeparator, 2, 6, 1, 2, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # File details
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        self.textview.show()
        self.textview.get_buffer().create_tag("normalTag", family="Courier")

        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        panel.attach(scroll, 0, 6, 2, 10, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Extracted data
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll2 = gtk.ScrolledWindow()
        self.lineView = gtk.TreeView(gtk.TreeStore(str, str))  # line number, content
        self.lineView.get_selection().set_mode(gtk.SELECTION_SINGLE)
        cell = gtk.CellRendererText()
        # Col file descriptor
        column = gtk.TreeViewColumn(_("Message ID"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        self.lineView.append_column(column)
        self.lineView.show()

        scroll2.add(self.lineView)
        scroll2.show()
        scroll2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        panel.attach(scroll2, 6, 8, 0, 10, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # Button select packets for further analysis
        self.butValidateMessages = gtk.Button(label=_("Import"))
        self.butValidateMessages.show()
        panel.attach(self.butValidateMessages, 2, 3, 10, 11, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        return panel
