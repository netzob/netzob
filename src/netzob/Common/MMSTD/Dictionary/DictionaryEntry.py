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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| DictionaryEntry:
#|     Definition of an entry in a dictionary
#+---------------------------------------------------------------------------+
class DictionaryEntry():

    def __init__(self, id, name, value):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.DictionaryEntry.py')
        self.id = id
        self.name = name
        self.value = value

    #+---------------------------------------------------------------------------+
    #| generate:
    #|     Generate the value of the entry
    #+---------------------------------------------------------------------------+
    def generate(self):
        self.log.debug("Generate ...")
        self.value.generate()

    #+---------------------------------------------------------------------------+
    #| forget:
    #|     Forgets the value of the entry
    #| @param temporary flag indicated the forget operation must be temporary
    #+---------------------------------------------------------------------------+
    def forget(self, temporary):
        self.log.debug("Forget ...")
        self.value.forget(temporary)

    #+---------------------------------------------------------------------------+
    #| undoForget:
    #|     Since a forget operation can be temporary, this method allows to
    #|     reverse it
    #+---------------------------------------------------------------------------+
    def undoForget(self):
        self.log.debug("Undo forget ...")
        self.value.undoForget()

    #+---------------------------------------------------------------------------+
    #| send:
    #|     Prepare to send this entry
    #| @param negative a flag which indicates if we send or not the negative
    #|        value of the entry
    #| @param current dictionnary
    #| @return the result to send (ValueResult)
    #+---------------------------------------------------------------------------+
    def send(self, negative, dictionary):
        self.log.debug("Send (negative=" + str(negative) + " ...")
        return self.value.send(negative, dictionary)

    #+---------------------------------------------------------------------------+
    #| compare:
    #|     Compare this entry with a specific value
    #| @param val the string value to which we must compare
    #| @param indice position in the value of the analysis
    #| @param negative a flag which indicates if we compare or not the negative
    #|        value of the entry
    #| @return the result of the comparaison
    #+---------------------------------------------------------------------------+
    def compare(self, val, indice, negative, dictionary):
        self.log.debug("Compare (val=" + str(val) + ", i=" + str(indice) + " neg=" + str(negative) + "...")
        return self.value.compare(val, indice, negative, dictionary)

    #+---------------------------------------------------------------------------+
    #| learn:
    #|     Learn the following value
    #| @param val the string value to learn
    #| @param indice position in the value of the analysis
    #| @return the result of the learning process
    #+---------------------------------------------------------------------------+
    def learn(self, val, indice):
        self.log.debug("Learn (val=" + val + ", i=" + str(indice) + "...")
        return self.value.learn(val, indice)

    def restore(self):
        self.value.restore()

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def isActive(self):
        return self.active

    def getValue(self):
        return self.value

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def __str__(self):
        return self.name
