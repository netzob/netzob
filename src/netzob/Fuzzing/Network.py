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
from gi.repository import Gtk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import logging
import threading
import nfqueue
import socket

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Fuzzing.TreeViews.TreeSymbolGenerator import TreeSymbolGenerator
from netzob.Fuzzing.TreeViews.TreeTypeStructureGenerator import TreeTypeStructureGenerator


#+---------------------------------------------------------------------------+
#| Network:
#|     This class offers the capability to fuzz network flows in live
#+---------------------------------------------------------------------------+
class Network(object):
    def new(self):
        pass

    def update(self):
        self.treeSymbolGenerator.update()
        self.treeTypeStructureGenerator.update()

    def clear(self):
        pass

    def kill(self):
#        os.popen("sudo iptables -D OUTPUT -p tcp --dport 80  -j NFQUEUE 2>&1 > /dev/null")
#        os.popen("sudo iptables -D OUTPUT -p tcp --sport 80  -j NFQUEUE 2>&1 > /dev/null")
        if self.aFuzzThread is not None and self.aFuzzThread.isAlive():
            self.aFuzzThread._Thread__stop()

    def save(self):
        pass

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main object
    #+----------------------------------------------
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Fuzzing.Network.py')
        self.netzob = netzob
        self.selectedSymbol = None
        self.aFuzzThread = None
        self.packets = []
        self.panel = Gtk.VPaned()
        self.panel.show()

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------
        topPanel = Gtk.HPaned()
        topPanel.show()
        self.panel.add(topPanel)
        vb_left_panel = Gtk.VBox(False, spacing=0)
        topPanel.add(vb_left_panel)
        vb_left_panel.set_size_request(-1, -1)
        vb_left_panel.show()

        # Initialize the treeview generator for the symbols
        self.treeSymbolGenerator = TreeSymbolGenerator(self.netzob)
        self.treeSymbolGenerator.initialization()
        vb_left_panel.pack_start(self.treeSymbolGenerator.getScrollLib(), True, True, 0)
        selection = self.treeSymbolGenerator.getTreeview().get_selection()
        selection.connect("changed", self.symbolSelected)

        #+----------------------------------------------
        #| RIGHT PART OF THE GUI : TYPE STRUCTURE OUTPUT
        #+----------------------------------------------
        vb_right_panel = Gtk.VBox(False, spacing=0)
        vb_right_panel.show()
        # Initialize the treeview for the type structure
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator(self.netzob)
        self.treeTypeStructureGenerator.initialization()
        self.treeTypeStructureGenerator.getTreeview().connect('button-press-event', self.button_press_on_field)
        vb_right_panel.add(self.treeTypeStructureGenerator.getScrollLib())
        topPanel.add(vb_right_panel)

        #+----------------------------------------------
        #| BOTTOM PART OF THE GUI : PACKET CAPTURING
        #+----------------------------------------------
        # Network Capturing Panel
        sniffPanel = Gtk.Table(rows=6, columns=4, homogeneous=False)
        self.panel.add(sniffPanel)
        sniffPanel.show()

        # Filter
        label = Gtk.Label(label=_("Filter"))
        label.show()
        entry_filter = Gtk.Entry()
        entry_filter.set_width_chars(50)
        entry_filter.show()
        entry_filter.set_text("tcp port 80")
        sniffPanel.attach(label, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        sniffPanel.attach(entry_filter, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Sniff launching button
        but = Gtk.Button(label=_("Fuzz traffic"))
        but.show()
        but.connect("clicked", self.launchFuzz_cb, entry_filter)
        sniffPanel.attach(but, 1, 2, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = Gtk.ScrolledWindow()
        self.treestore = Gtk.TreeStore(int, str, str, str, str, str, int)  # pktID, proto (udp/tcp), IP.src, IP.dst, sport, dport, timestamp
        treeview = Gtk.TreeView(self.treestore)
        selection = treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        selection.connect("changed", self.packet_details)
        cell = Gtk.CellRendererText()
        # Col proto
        column = Gtk.TreeViewColumn(_("Proto"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 1)
        treeview.append_column(column)
        # Col IP.src
        column = Gtk.TreeViewColumn(_("IP source"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 2)
        treeview.append_column(column)
        # Col IP.dst
        column = Gtk.TreeViewColumn(_("IP dest"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 3)
        treeview.append_column(column)
        # Col {TCP,UDP}.sport
        column = Gtk.TreeViewColumn(_("sport"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 4)
        treeview.append_column(column)
        # Col {TCP,UDP}.dport
        column = Gtk.TreeViewColumn(_("dport"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 5)
        treeview.append_column(column)
        treeview.show()
        scroll.add(treeview)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sniffPanel.attach(scroll, 0, 2, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # Packet detail
        scroll = Gtk.ScrolledWindow()
        self.textview = Gtk.TextView()
        self.textview.show()
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sniffPanel.attach(scroll, 2, 4, 0, 6, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

    #+----------------------------------------------
    #| update:
    #|   Update the Treestore
    #+----------------------------------------------
    def symbolSelected(self, selection):
        (model, iter) = selection.get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                # Retrieve the selected symbol
                idSymbol = model.get_value(iter, 0)
                self.selectedSymbol = idSymbol
                symbol = None

                for tmp_symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                    if str(tmp_symbol.getID()) == idSymbol:
                        symbol = tmp_symbol

                # Retrieve a random message in order to show a type structure
                message = symbol.getMessages()[-1]
                self.treeTypeStructureGenerator.setSymbol(symbol)
                self.treeTypeStructureGenerator.setMessage(message)
                self.treeTypeStructureGenerator.update()

    #+----------------------------------------------
    #| button_press_on_field:
    #|   Create a menu to display available operations
    #|   on the treeview symbols
    #+----------------------------------------------
    def button_press_on_field(self, button, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # Retrieves the symbol on which the user has clicked on
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = self.treeTypeStructureGenerator.getTreeview().get_path_at_pos(x, y)
            aIter = self.treeTypeStructureGenerator.getTreeview().get_model().get_iter(path)
            field = self.treeTypeStructureGenerator.getTreeview().get_model().get_value(aIter, 0)
            self.menu = Gtk.Menu()
            item = Gtk.MenuItem(_("Fuzz field"))
            item.connect("activate", self.fuzz_field_cb, field)
            item.show()
            self.menu.append(item)
            self.menu.popup(None, None, None, None, event.button, event.time)

    def fuzz_field_cb(self, widget, field):
        self.log.debug(_("Fuzz field: {0}".format(str(field))))

    #+----------------------------------------------
    #| Called when user select a packet for details
    #+----------------------------------------------
    def packet_details(self, selection):
        (model, paths) = selection.get_selected_rows()
        for path in paths[:1]:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                self.textview.get_buffer().set_text(self.packets[packetID].show())

    #+----------------------------------------------
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launchFuzz_cb(self, button, aFilter):
        button.set_sensitive(False)
        self.packets = []
        self.treestore.clear()
        self.textview.get_buffer().set_text("")

        self.aFuzzThread = threading.Thread(None, self.fuzzThread, None, (button, aFilter), {})
        self.aFuzzThread.start()

    #+----------------------------------------------
    #| Thread for fuzzing
    #+----------------------------------------------
    def fuzzThread(self, button, aFilter):
        self.log.info(_("Launching fuzzing process with : filter=\"{0}\"").format(aFilter.get_text()))

        ## Set Netfilter NFQUEUE
#        os.popen("sudo iptables -I OUTPUT -p tcp --dport 80  -j NFQUEUE 2>&1 > /dev/null")
#        os.popen("sudo iptables -I OUTPUT -p tcp --sport 80  -j NFQUEUE 2>&1 > /dev/null")
        q = nfqueue.queue()
        q.open()
        try:
            q.unbind(socket.AF_INET)
        except:
            pass
        q.bind(socket.AF_INET)
        q.set_callback(self.nfqueue_cb)
        q.create_queue(0)
        q.set_queue_maxlen(5000)
        try:
            ## TODO : do it in a dedicated process

            q.try_run()
        except:
            pass
        q.unbind(socket.AF_INET)
        q.close()

#        os.popen("sudo iptables -D OUTPUT -p tcp --dport 80  -j NFQUEUE 2>&1 > /dev/null")
#        os.popen("sudo iptables -D OUTPUT -p tcp --sport 80  -j NFQUEUE 2>&1 > /dev/null")
        GObject.idle_add(button.set_sensitive, True)

    #+----------------------------------------------
    #| Called when we reiceve a corresponding packet to fuzz
    #+----------------------------------------------
    def nfqueue_cb(self, dummy, payload):
        return payload.set_verdict(nfqueue.NF_ACCEPT)
    """
        data = payload.get_data()
        ip_pkt = ip.IP(data)
        if ip_pkt.p == ip.IP_PROTO_TCP:
            proto_pkt = tcp.TCP(str(ip_pkt.data))
            GObject.idle_add(self.treestore.append,
                             None,
                             [len(self.packets),
                              "TCP",
                              str(ip_pkt.src),
                              str(ip_pkt.dst),
                              str(proto_pkt.sport),
                              str(proto_pkt.dport),
                              int(time.time())]
                            )
        elif ip_pkt.p == ip.IP_PROTO_UDP:
            proto_pkt = udp.UDP(str(ip_pkt.data))
            GObject.idle_add(self.treestore.append,
                             None,
                             [len(self.packets),
                              "UDP",
                              str(ip_pkt.src),
                              str(ip_pkt.dst),
                              str(proto_pkt.sport),
                              str(proto_pkt.dport),
                              int(time.time())]
                            )
        self.packets.append(repr(ip_pkt))
        new_ip_pkt = ip_pkt
        new_ip_pkt.data = self.fuzzPacket(ip_pkt.data)
        return payload.set_verdict_modified(nfqueue.NF_ACCEPT, str(new_ip_pkt), len(new_ip_pkt))
    """
    #+----------------------------------------------
    #| Main function to fuzz packets
    #+----------------------------------------------
    def fuzzPacket(self, packet):
        print repr(packet)
        return packet

    """
        res = ""
        for i in range(len(strIN)):
            if i == offset:
                res += value
            else:
                res += strIN[i]
        return res
    """
    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
