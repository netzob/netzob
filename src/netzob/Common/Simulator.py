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
import logging
from lxml.etree import ElementTree
from lxml import etree
from netzob.Common.MMSTD.Actors.MMSTDVisitor import MMSTDVisitor


#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
#+---------------------------------------------------------------------------+
#| Simulator:
#|     Class definition of the simulator attached to a project
#+---------------------------------------------------------------------------+
class Simulator(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self):
        self.actors = []

    def getActorByID(self, actorID):
        """Computes and retrieves the actor which's ID is
        provided (None if unfound)"""
        for actor in self.actors:
            if str(actor.getID()) == str(actorID):
                return actor
        return None

    #+-----------------------------------------------------------------------+
    #| Save & Load
    #+-----------------------------------------------------------------------+
    def save(self, root, namespace):
        """Save in the XML tree the simulator definition"""
        xmlSimulator = etree.SubElement(root, "{" + namespace + "}simulator")

        if len(self.actors) > 0:
            xmlActors = etree.SubElement(xmlSimulator, "{" + namespace + "}actors")
            for actor in self.actors:
                actor.save(xmlActors, namespace)

    @staticmethod
    def loadSimulator(xmlRoot, namespace, version, automata, vocabulary):
        if version == "0.1":
            simulator = None
            actors = []

            if xmlRoot.find("{" + namespace + "}actors") is not None:
                xmlActors = xmlRoot.find("{" + namespace + "}actors")
                for xmlActor in xmlActors.findall("{" + namespace + "}actor"):
                    actor = MMSTDVisitor.loadFromXML(xmlActor, namespace, version, automata, vocabulary)
                    if actor is None:
                        logging.warn("An error occurred and prevented to load the actor.")
                    else:
                        actors.append(actor)

            simulator = Simulator()
            simulator.setActors(actors)
            return simulator
        return None

    #+-----------------------------------------------------------------------+
    #| Getters & Setters
    #+-----------------------------------------------------------------------+
    def getActors(self):
        return self.actors

    def setActors(self, actors):
        self.actors = actors

    def addActor(self, actor):
        self.actors.append(actor)

    def removeActor(self, actor):
        self.actors.remove(actor)
