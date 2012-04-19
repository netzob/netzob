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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Memory:
#|     Definition of an memory
#+---------------------------------------------------------------------------+
class Memory():

    def __init__(self, variables):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Memory.py')
        self.memory = dict()
        self.temporaryMemory = dict()
        self.variables = variables

    def createMemory(self):
        # We create a temporary memory
        self.temporaryMemory = dict()
        for key in self.memory.keys():
            self.temporaryMemory[key] = self.memory[key]

    def persistMemory(self):
        self.memory = dict()
        for key in self.temporaryMemory.keys():
            self.memory[key] = self.temporaryMemory[key]

    def hasMemorized(self, variable):
        self.log.debug("Has Memorized ?")
        for id in self.temporaryMemory.keys():
            self.log.debug("> " + str(id) + " = " + str(self.temporaryMemory.get(id)))

        return variable.getID() in self.temporaryMemory.keys()

    def memorize(self, variable, binValue):
        self.log.debug("We MEMORIZE !!! " + str(variable) + " with " + str(binValue))
        self.temporaryMemory[variable.getID()] = binValue

    def recall(self, variable):
        return self.temporaryMemory[variable.getID()]

    def recallAll(self):
        return self.temporaryMemory

    def restore(self, variable):
        if variable.getID() in self.memory.keys():
            self.temporaryMemory[variable.getID()] = self.memory[variable.getID()]

    def cleanMemory(self):
        self.memory = dict()
        self.temporaryMemory = dict()
