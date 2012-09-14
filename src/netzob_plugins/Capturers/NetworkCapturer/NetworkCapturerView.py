# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import pcapy

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Pango

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobWidgets import NetzobLabel, NetzobComboBoxEntry
from netzob.Common.Plugins.Capturers.AbstractCapturerView import AbstractCapturerView


class NetworkCapturerView(AbstractCapturerView):
    """NetworkCapturerView:
            GUI for viewing network capturer.
    """

    def __init__(self):
        """Constructor of NetworkCapturerView:
        """
        self.buildPanel()

        self.dialog = Gtk.Dialog(title=_("Network capturer"), flags=0, buttons=None)
        self.dialog.vbox.pack_start(self.panel, True, True, 0)
        self.dialog.set_size_request(600, 400)

    def buildPanel(self):
        """buildPanel:
                Build and display the main panel.
        """
        # Network Capturing Panel
        self.panel = Gtk.Table(rows=7, columns=4, homogeneous=False)
        self.panel.show()

        # Network devices
        label = Gtk.Label(label=_("Network devices"))
        label.show()
        self.listNetworkDevice = Gtk.ComboBoxText.new_with_entry()
        self.listNetworkDevice.show()
        self.listNetworkDevice.set_size_request(300, -1)
        self.listNetworkDevice.set_model(Gtk.ListStore(str))
        self.listNetworkDevice.get_model().clear()

        # list of interfaces
        try:
            interfaces = pcapy.findalldevs()
        except:
            logging.warn(_("You don't have enough permissions to open any network interface on this system."))
            interfaces = []

        for interface in interfaces:
            self.listNetworkDevice.append_text(str(interface))

        self.panel.attach(label, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.listNetworkDevice, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # BPF filter
        label = Gtk.Label(label=_("BPF filter"))
        label.show()
        self.entry_filter = Gtk.Entry()
        self.entry_filter.set_width_chars(50)
        self.entry_filter.show()
        self.entry_filter.set_text("tcp port 80")
        self.panel.attach(label, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.entry_filter, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Count capturing limit
        label = Gtk.Label(label=_("Count limit"))
        label.show()
        self.entry_count = Gtk.Entry()
        self.entry_count.show()
        self.entry_count.set_text("10")
        self.panel.attach(label, 0, 1, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.entry_count, 1, 2, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Time capturing limit
        label = Gtk.Label(label=_("Timeout"))
        label.show()
        self.entry_time = Gtk.Entry()
        self.entry_time.show()
        self.entry_time.set_text("10")
        self.panel.attach(label, 0, 1, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.entry_time, 1, 2, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Sniff launching button
        self.butLaunchSniff = Gtk.Button(label=_("Sniff traffic"))
        self.butLaunchSniff.show()
        self.panel.attach(self.butLaunchSniff, 1, 2, 5, 6, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = Gtk.ScrolledWindow()
        self.treestore = Gtk.TreeStore(int, str, str, str, int, int, int)  # pktID, proto (udp/tcp), IP.src, IP.dst, sport, dport, timestamp
        self.treeview = Gtk.TreeView(self.treestore)
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.selection = self.treeview.get_selection()
        cell = Gtk.CellRendererText()
        # Col proto
        column = Gtk.TreeViewColumn(_("Proto"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 1)
        self.treeview.append_column(column)
        # Col IP.src
        column = Gtk.TreeViewColumn(_("IP source"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 2)
        self.treeview.append_column(column)
        # Col IP.dst
        column = Gtk.TreeViewColumn(_("IP dest"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 3)
        self.treeview.append_column(column)
        # Col {TCP,UDP}.sport
        column = Gtk.TreeViewColumn(_("sport"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 4)
        self.treeview.append_column(column)
        # Col {TCP,UDP}.dport
        column = Gtk.TreeViewColumn(_("dport"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 5)
        self.treeview.append_column(column)
        self.treeview.show()
        scroll.add(self.treeview)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.panel.attach(scroll, 0, 2, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)
        # Button select packets for further analysis
        self.butSaveSelectedPackets = Gtk.Button(label=_("Save selected packets"))
        self.butSaveSelectedPackets.show()
        self.panel.attach(self.butSaveSelectedPackets, 1, 2, 6, 7, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet detail
        scroll = Gtk.ScrolledWindow()
        self.textview = Gtk.TextView()
        self.textview.show()
        self.textview.get_buffer().create_tag("normalTag", family="Courier")
        self.textview.set_size_request(300, -1)
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.panel.attach(scroll, 2, 4, 0, 7, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)
