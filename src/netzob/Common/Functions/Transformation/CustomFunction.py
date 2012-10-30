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
from netzob.Common.Functions.TransformationFunction import TransformationFunction
from code import InteractiveInterpreter


#+---------------------------------------------------------------------------+
#| CustomFunction:
#|     Definition of a Custom function (provided by user)
#+---------------------------------------------------------------------------+
class CustomFunction(TransformationFunction):
    """Definition of a Custom function (provided by user)"""

    TYPE = "CustomFunction"

    def __init__(self, name, sourceCode, sourceCodeReverse):
        TransformationFunction.__init__(self, CustomFunction.TYPE, name)
        self.sourceCode = sourceCode + '\n'
        self.sourceCodeReverse = sourceCodeReverse + '\n'

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
                logging.warning("Error while applying function on a message : " + str(e))
        return output

    def reverse(self, message):
        output = "00"
        compiledCode = None
        toCompile = self.sourceCodeReverse
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
                logging.warning("Error while appying function on a message : " + str(e))
        return output

    def save(self, root, namespace_common):
        xmlFunction = etree.SubElement(root, "{" + namespace_common + "}function")
        xmlFunction.set("type", self.getType())
        xmlFunction.set("name", self.getName())
        xmlFunction.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:CustomFunction")
        xmlSourceCode = etree.SubElement(xmlFunction, "{" + namespace_common + "}source-code")
        xmlSourceCode.text = self.getSourceCode()
        xmlSourceCodeReverse = etree.SubElement(xmlFunction, "{" + namespace_common + "}source-code_reverse")
        xmlSourceCodeReverse.text = self.getSourceCodeReverse()

    @staticmethod
    def loadFromXML(rootElement, namespace, version):
        """loadFromXML:
           Function which parses an XML and extract from it
           the definition of a rendering function
           @param rootElement: XML root of the function
           @return an instance of a function
           @throw NameError if XML invalid"""

        nameFunction = rootElement.get("name")
        sourceCode = rootElement.find("{" + namespace + "}source-code").text
        if rootElement.find("{" + namespace + "}source-code_reverse") is not None:
            sourceCodeReverse = rootElement.find("{" + namespace + "}source-code_reverse").text
        else:
            sourceCodeReverse = sourceCode
        function = CustomFunction(nameFunction, sourceCode, sourceCodeReverse)
        return function

    def compileSourceCode(self):
        errorMessage = None
        try:
            compiledCode = code.compile_command(self.sourceCode, "string", "exec")
        except SyntaxError:
            errorMessage = traceback.format_exc().rstrip()

        return errorMessage

    def compileReverseSourceCode(self):
        errorMessage = None
        try:
            compiledCode = code.compile_command(self.sourceCodeReverse, "string", "exec")
        except SyntaxError:
            errorMessage = traceback.format_exc().rstrip()

        return errorMessage

    def getSourceCode(self):
        return self.sourceCode

    def getSourceCodeReverse(self):
        return self.sourceCode
