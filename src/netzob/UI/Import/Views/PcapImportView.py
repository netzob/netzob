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
from gi.repository import Gtk
import gi
from bitarray import bitarray
gi.require_version('Gtk', '3.0')


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

        self.dialog = Gtk.Dialog(title=_("Import file"), flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(panel, True, True, 0)
        self.dialog.set_size_request(1000, 500)

    def buildPanel(self):
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        panel = Gtk.Table(rows=5, columns=4)
        panel.show()

        # FIle selection
        self.butSelectFile = Gtk.Button(_("Import PCAP"))
        self.butSelectFile.show()
        self.labelFile = Gtk.Label(label="...")
        self.labelFile.show()
        panel.attach(self.butSelectFile, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(self.labelFile, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Scapy filter
        label = Gtk.Label(label=_("Scapy filter"))
#        label.show()  # TODO : implement the filter
        self.entryScapyFilter = Gtk.Entry()
        self.entryScapyFilter.set_width_chars(50)
        self.entryScapyFilter.show()
        self.entryScapyFilter.set_text("tcp or udp")
        panel.attach(label, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(self.entryScapyFilter, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Sniff launching button
        self.butLaunchSniff = Gtk.Button(label=_("Import traffic"))
        self.butLaunchSniff.show()
        panel.attach(self.butLaunchSniff, 1, 2, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = Gtk.ScrolledWindow()
        self.treestore = Gtk.TreeStore(int, str, str, str, str, str, int)  # pktID, proto (udp/tcp), IP.src, IP.dst, sport, dport, timestamp
        self.treeviewPackets = Gtk.TreeView(self.treestore)
        self.treeviewPackets.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.treeviewPackets.set_size_request(500, -1)
        cell = Gtk.CellRendererText()
        # Col proto
        column = Gtk.TreeViewColumn(_("Proto"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.treeviewPackets.append_column(column)
        # Col IP.src
        column = Gtk.TreeViewColumn(_("IP source"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        self.treeviewPackets.append_column(column)
        # Col IP.dst
        column = Gtk.TreeViewColumn(_("IP dest"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=3)
        self.treeviewPackets.append_column(column)
        # Col {TCP,UDP}.sport
        column = Gtk.TreeViewColumn(_("sport"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=4)
        self.treeviewPackets.append_column(column)
        # Col {TCP,UDP}.dport
        column = Gtk.TreeViewColumn(_("dport"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=5)
        self.treeviewPackets.append_column(column)
        self.treeviewPackets.show()
        scroll.add(self.treeviewPackets)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        panel.attach(scroll, 0, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)
        # Button select packets for further analysis
        self.butSaveSelectedPackets = Gtk.Button(label=_("Save selected packets"))
        self.butSaveSelectedPackets.show()
        panel.attach(self.butSaveSelectedPackets, 1, 2, 4, 5, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet detail
        scroll = Gtk.ScrolledWindow()
        self.textview = Gtk.TextView()
        self.textview.show()
        self.textview.get_buffer().create_tag("normalTag", family="Courier")
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        panel.attach(scroll, 2, 4, 0, 5, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        return panel
