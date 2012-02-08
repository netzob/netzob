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
#| Standard library imports
#+----------------------------------------------
import logging

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------


#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.MMSTD.Dictionary import DictionaryEntry
from netzob.Common.MMSTD.Dictionary import MMSTDDictionary

#from netzob.Common.MMSTD.Dictionary.Values import Aggregate
#from netzob.Common.MMSTD.Dictionary.Values import TextValue
#from netzob.Common.MMSTD.Dictionary.Values import EndValue
#from netzob.Common.MMSTD.Dictionary.Values import VarValue
#from netzob.Common.MMSTD.Dictionary.Variables.HexVariable import HexVariable
#from netzob.Common.MMSTD.Dictionary.Variables.IntVariable import IntVariable
#from netzob.Common.MMSTD.Dictionary.Variables.MD5Variable import MD5Variable
#from netzob.Common.MMSTD.Dictionary.Variables.WordVariable import WordVariable
#from netzob.Common.MMSTD.Dictionary.Variables.IPVariable import IPVariable
#from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import AggregateVariable
#from netzob.Common.MMSTD.Dictionary.Variables.DynLenStringVariable import DynLenStringVariable





#+----------------------------------------------
#| DictionaryXmlParser:
#|    Parser for an XML Dictionary
#+----------------------------------------------
class DictionaryXmlParser(object):

    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML:
    #|     Function which parses an XML and extract from it
    #[    the definition of a dictionary
    #| @param rootElement: XML root of the dictionary definition
    #| @return an instance of a dictionary
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, file):
        log = logging.getLogger('netzob.Common.MMSTD.Tools.Parser.DictionaryXmlParser.py')

        if rootElement.tag != "dictionary":
            raise NameError("The parsed XML doesn't represent a dictionary.")

        # First we identify all the variables
        variables = []
        for xmlVariable in rootElement.findall("var"):
            idVar = int(xmlVariable.get("id", "-1"))
            nameVar = xmlVariable.get("name", "none")
            typeVar = xmlVariable.get("type", "none")

            variable = None
            if typeVar == "HEX":
                size = int(xmlVariable.get("size", "-1"))
                min = int(xmlVariable.get("min", "-1"))
                max = int(xmlVariable.get("max", "-1"))
                reset = xmlVariable.get("reset", "normal")
                variable = HexVariable(idVar, nameVar, xmlVariable.text)
                if size != -1:
                    variable.setSize(size)
                if min != -1:
                    variable.setMin(min)
                if max != -1:
                    variable.setMax(max)
                variable.setReset(reset)
            elif typeVar == "INT":
                size = int(xmlVariable.get("size", "-1"))
                min = int(xmlVariable.get("min", "-1"))
                max = int(xmlVariable.get("max", "-1"))
                reset = xmlVariable.get("reset", "normal")
                variable = IntVariable(idVar, nameVar, size, xmlVariable.text)
                if min != -1:
                    variable.setMin(min)
                if max != -1:
                    variable.setMax(max)
                variable.setReset(reset)


            elif typeVar == "MD5":
                initVar = xmlVariable.get("init", "")
                valVar = int(xmlVariable.get("idVariable", "0"))
                variable = MD5Variable(idVar, nameVar, initVar, valVar)
            elif typeVar == "AGGREGATE":
                variable = AggregateVariable(idVar, nameVar, xmlVariable.text.split(';'))
            elif typeVar == "WORD":
                variable = WordVariable(idVar, nameVar, xmlVariable.text)
            elif typeVar == "IP":
                variable = IPVariable(idVar, nameVar, xmlVariable.text)
            elif typeVar == "DYN_LEN_STRING":
                variable = DynLenStringVariable(idVar, nameVar, int(xmlVariable.text))

            if variable != None:
                variables.append(variable)


        # Parse the entries declared in dictionary
        entries = []
        for xmlEntry in rootElement.findall("entry"):
            idEntry = int(xmlEntry.get("id", "-1"))
            nameEntry = xmlEntry.get("name", "none")

            initialValue = Aggregate.Aggregate()

            currentValue = initialValue

            # Let's rock baby !
            # We start the parsing process of the dictionary
            for xmlValue in list(xmlEntry):
                if xmlValue.tag == "text":
                    currentValue.registerValue(DictionaryXmlParser.getTextValue(xmlValue))
                elif xmlValue.tag == "end":
                    currentValue.registerValue(DictionaryXmlParser.getEndValue(xmlValue))
                elif xmlValue.tag == "var":
                    currentValue.registerValue(DictionaryXmlParser.getVarValue(xmlValue, variables))
                else:
                    log.warn("The tag " + xmlValue.tag + " has not been parsed !")





            entry = DictionaryEntry.DictionaryEntry(idEntry, nameEntry, initialValue)

            entries.append(entry)

        # Create a dictionary based on the variables and the entries
        dictionary = MMSTDDictionary.MMSTDDictionary(variables, entries)
        return dictionary


    @staticmethod
    def getTextValue(xmlElement):
        value = None
        if xmlElement.tag == "text" and len(xmlElement.text) > 0:
            value = TextValue.TextValue(xmlElement.text)
        else:
            # create logger with the given configuration
            log = logging.getLogger('netzob.Common.MMSTD.Tools.Parser.DictionaryXmlParser.py')
            log.warn("Error in the XML Dictionary, the xmlElement is not a text value")
        return value

    @staticmethod
    def getEndValue(xmlElement):
        value = None
        if xmlElement.tag == "end":
            value = EndValue.EndValue()
        else:
            # create logger with the given configuration
            log = logging.getLogger('netzob.Common.MMSTD.Tools.Parser.DictionaryXmlParser.py')
            log.warn("Error in the XML Dictionary, the xmlElement is not an end value")
        return value

    @staticmethod
    def getVarValue(xmlElement, variables):
        value = None
        if xmlElement.tag == "var" and xmlElement.get("id", "none") != "none":
            idVariable = int(xmlElement.get("id", "-1"))
            resetCondition = xmlElement.get("reset", "normal")
            variable = None
            for tmp_var in variables:
                if tmp_var.getID() == idVariable:
                    variable = tmp_var

            value = VarValue.VarValue(variable, resetCondition)
        else:
            # create logger with the given configuration
            log = logging.getLogger('netzob.Common.MMSTD.Tools.Parser.DictionaryXmlParser.py')
            log.warn("Error in the XML Dictionary, the xmlElement is not a var value")
        return value
