#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Common.Models.Vocabulary.Domain.Specializer.VariableSpecializerPath import VariableSpecializerPath

@NetzobLogger
class VariableSpecializer():
    """Computes the specialization of a token-tree and returns a raw data
    """


    def __init__(self, variable, memory = None):
        self.variable = variable
        if memory is not None:
            self.memory = memory
        else:
            self.memory = Memory()

    def specialize(self):
        """Execute the specialize operation"""

        if self.variable is None:
            raise Exception("No definition domain specified.")

        self._logger.debug("Specialize variable {0}".format(self.variable))
            
        self.__clearResults()

        # we create the initial parser path
        variableSpecializerPath = self._createVariableSpecializerPath(None)

        self.variableSpecializerPaths = self.variable.specialize(variableSpecializerPath)
        self._logger.debug("Specializing variable '{0}' generated '{1}' valid paths".format(self.variable, len(self.variableSpecializerPaths)))
        
        return self.isOk()

        
    def _createVariableSpecializerPath(self, generatedContent, originalVariableSpecializerPath=None):
        self._logger.debug("Generated content of the path = {0}".format(generatedContent))
        copy_generatedContent = None

        if generatedContent is not None:
            copy_generatedContent = generatedContent.copy()
        
        varPath = VariableSpecializerPath(self, copy_generatedContent, originalVariableSpecializerPath)
        return varPath

        
    
    def isOk(self):
        """Returns True if at least one valid VariableSpecializerResult is available"""
        return len(self.variableSpecializerPaths)>0
    
    def __clearResults(self):
        """Prepare for a new specializing by cleaning any previously results"""
        self.variableSpecializerResults = []
        self.variableSpecializerPaths = []        

    

