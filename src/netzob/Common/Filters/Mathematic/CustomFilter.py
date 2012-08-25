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
import gzip
import StringIO
import code
import string
import traceback
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Filters.MathematicFilter import MathematicFilter
from code import InteractiveInterpreter


#+---------------------------------------------------------------------------+
#| CustomFilter:
#|     Definition of a Custom filter (provided by user)
#+---------------------------------------------------------------------------+
class CustomFilter(MathematicFilter):
    """Definition of a Custom filter (provided by user)"""

    TYPE = "CustomFilter"

    def __init__(self, name, sourceCode):
        MathematicFilter.__init__(self, CustomFilter.TYPE, name)
        self.sourceCode = sourceCode + '\n'

    def apply(self, message):
        output = "00"
        compiledCode = None
        toCompile = self.sourceCode
        try:
            compiledCode = code.compile_command(toCompile, "string", "exec")
        except SyntaxError:
            errorMessage = traceback.format_exc().rstrip()

        if compiledCode is not None:
            try:
                # Initialize locals with the message
                locals = {'message': message}
                interpreter = InteractiveInterpreter(locals)
                # Run the compiled code
                interpreter.runcode(compiledCode)
                # Fetch the new value of message
                output = interpreter.locals['message']
            except Exception, e:
                logging.warning("Error while appying filter on a message : " + str(e))

        return output

    def compileSourceCode(self):
        errorMessage = None
        try:
            compiledCode = code.compile_command(self.sourceCode, "string", "exec")
        except SyntaxError:
            errorMessage = traceback.format_exc().rstrip()

        return errorMessage

    def save(self, root, namespace_common):
        xmlFilter = etree.SubElement(root, "{" + namespace_common + "}filter")
        xmlFilter.set("type", self.getType())
        xmlFilter.set("name", self.getName())
        xmlFilter.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:CustomFilter")
        xmlSourceCode = etree.SubElement(xmlFilter, "{" + namespace_common + "}source-code")
        xmlSourceCode.text = self.getSourceCode()

    @staticmethod
    def loadFromXML(rootElement, namespace, version):
        """loadFromXML:
           Function which parses an XML and extract from it
           the definition of a rendering filter
           @param rootElement: XML root of the filter
           @return an instance of a filter
           @throw NameError if XML invalid"""

        nameFilter = rootElement.get("name")
        sourceCode = rootElement.find("{" + namespace + "}source-code").text

        filter = CustomFilter(nameFilter, sourceCode)
        return filter

    def getSourceCode(self):
        return self.sourceCode
