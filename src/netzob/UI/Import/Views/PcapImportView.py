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
import gtk
import pygtk
from bitarray import bitarray
pygtk.require('2.0')


#+----------------------------------------------
#| PcapImportView:
#|     GUI for capturing messages from PCAP
#+----------------------------------------------
class PcapImportView():

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self):
        panel = self.buildPanel()

        self.dialog = gtk.Dialog(title=_("Import file"), flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(panel, True, True, 0)
        self.dialog.set_size_request(1000, 500)

    def buildPanel(self):
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        panel = gtk.Table(rows=5, columns=4)
        panel.show()

        # FIle selection
        self.butSelectFile = gtk.Button(_("Import PCAP"))
        self.butSelectFile.show()
        self.labelFile = gtk.Label("...")
        self.labelFile.show()
        panel.attach(self.butSelectFile, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(self.labelFile, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Scapy filter
        label = gtk.Label(_("Scapy filter"))
#        label.show()  # TODO : implement the filter
        self.entryScapyFilter = gtk.Entry()
        self.entryScapyFilter.set_width_chars(50)
        self.entryScapyFilter.show()
        self.entryScapyFilter.set_text("tcp or udp")
        panel.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(self.entryScapyFilter, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Sniff launching button
        self.butLaunchSniff = gtk.Button(label=_("Import traffic"))
        self.butLaunchSniff.show()
        panel.attach(self.butLaunchSniff, 1, 2, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = gtk.ScrolledWindow()
        self.treestore = gtk.TreeStore(int, str, str, str, str, str, int)  # pktID, proto (udp/tcp), IP.src, IP.dst, sport, dport, timestamp
        self.treeviewPackets = gtk.TreeView(self.treestore)
        self.treeviewPackets.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.treeviewPackets.set_size_request(500, -1)
        cell = gtk.CellRendererText()
        # Col proto
        column = gtk.TreeViewColumn(_("Proto"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.treeviewPackets.append_column(column)
        # Col IP.src
        column = gtk.TreeViewColumn(_("IP source"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        self.treeviewPackets.append_column(column)
        # Col IP.dst
        column = gtk.TreeViewColumn(_("IP dest"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=3)
        self.treeviewPackets.append_column(column)
        # Col {TCP,UDP}.sport
        column = gtk.TreeViewColumn(_("sport"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=4)
        self.treeviewPackets.append_column(column)
        # Col {TCP,UDP}.dport
        column = gtk.TreeViewColumn(_("dport"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=5)
        self.treeviewPackets.append_column(column)
        self.treeviewPackets.show()
        scroll.add(self.treeviewPackets)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        panel.attach(scroll, 0, 2, 3, 4, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)
        # Button select packets for further analysis
        self.butSaveSelectedPackets = gtk.Button(label=_("Save selected packets"))
        self.butSaveSelectedPackets.show()
        panel.attach(self.butSaveSelectedPackets, 1, 2, 4, 5, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet detail
        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        self.textview.show()
        self.textview.get_buffer().create_tag("normalTag", family="Courier")
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        panel.attach(scroll, 2, 4, 0, 5, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        return panel
