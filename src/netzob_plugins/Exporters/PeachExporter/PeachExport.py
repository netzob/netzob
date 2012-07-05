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


#-----------------------------------------------------------------------------
# Global Imports
#-----------------------------------------------------------------------------
from gettext import gettext as _
import logging
from lxml import etree
import string


#+----------------------------------------------------------------------------
#| Local Imports
#+----------------------------------------------------------------------------


class PeachExport:
    """
        PeachExport:
            Utility for exporting netzob information into Peach pit file.
            Simplify the construction of a fuzzer with Peach.

    """

    def __init__(self, netzob):
        """
            Constructor of PeachExport:

                @type netzob: netzob.NetzobGUI.netzob
                @param netzob: the main netzob project.

        """
        self.netzob = netzob

    def getPeachDefinition(self, symbolID, entireProject):
        """
            getXMLDefinition:
                Returns part of the Peach pit file (XML format).

                @type symbolID: integer
                @param symbolID: a number which identifies the symbol the xml definition of which we need.
                @type entireProject: boolean
                @param entireProject: true if we want to see the Peach definition of the whole project, false elsewhere.

        """
        xmlRoot = etree.Element("root")
        logging.debug(_("Targeted symbolID: {0}").format(str(symbolID)))

        if entireProject:
            self.makeAllDataModels(xmlRoot)
            self.makeAStateModel(xmlRoot)

        else:
            project = self.netzob.getCurrentProject()
            vocabulary = project.getVocabulary()
            symbols = vocabulary.getSymbols()
            resSymbol = None
            for symbol in symbols:
                if str(symbol.getID()) == symbolID:
                    resSymbol = symbol
                    break
            if resSymbol == None:
                logging.warning(_("Impossible to retrieve the symbol having the id {0}").format(str(symbolID)))
                return None
            else:
                self.makeADataModel(xmlRoot, symbol, 0)
            self.makeAState(xmlRoot, 0)

        tree = etree.ElementTree(xmlRoot)
        result = etree.tostring(tree, pretty_print=True)
        return result

    def makeAllDataModels(self, xmlFather):
        """
            makeAllDataModels:
                Transform every single netzob symbol into Peach data model.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element

        """
        project = self.netzob.getCurrentProject()
        vocabulary = project.getVocabulary()

        dataModelid = 0
        for symbol in vocabulary.getSymbols():
            # Each symbol is translated in a Peach data model
            self.makeADataModel(xmlFather, symbol, dataModelid)
            dataModelid = dataModelid + 1

    def makeADataModel(self, xmlFather, symbol, dataModelid):
        """
            makeADataModel:
                Dissect a netzob symbol in order to extract essential data for the making of Peach fields in its data Model

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
                @type symbol: netzob.common.Symbol.symbol
                @param symbol: the given symbol that will be dissected.
                @type dataModelid: integer
                @param dataModelid: a number that identifies the data model.

        """
        xmlDataModel = etree.SubElement(xmlFather, "DataModel", name=("dataModel{0}").format(str(dataModelid)))
        for field in symbol.getFields():

            xmlField = None
            peachType = ""
            variable = field.getVariable()
            if variable is not None:
                # Precision on the variable type.
                peachType = self.getRecPeachFieldType(variable)
            else:
                logging.debug(_("The field {0} has not got any variable.").format(field.getName()))
                peachType = "Blob"

            if field.isStatic():
                # Static fields are not mutated.
                xmlField = etree.SubElement(xmlDataModel, peachType, name=field.getName(), mutable="false", valueType="hex", value=field.getRegex())

            else:
                # Fields not declared static in netzob are assumed to be dynamic, have a random default value and are mutable.

                # Regex management: #
                #-------------------#

                # We assume that the regex is composed of a random number of fixed and dynamic (.{n,p}, .{,n} and .{n}) subregexs. Each subregex will have its own peach subfield.
                # We will illustrate it with the following example "(abcd.{m,n}efg.{,o}.{p}hij)"
                regex = field.getRegex()
                if (regex != "()"):
                    regex = regex[1:len(regex) - 1]  # regex = "abcd.{m,n}efg.{,o}.{p}hij"

                    splittedRegex = []
                    for lterm in string.split(regex, ".{"):
                            for rterm in string.split(lterm, "}"):
                                splittedRegex.append(rterm)  # splittedRegex = ["abcd", "m,n", "efg", ",o", "", "p", "hij"]
                                logging.debug(_("The field {0} has the splitted Regex = {1}").format(field.getName(), str(splittedRegex)))

                    for i in range(len(splittedRegex)):
                        # splittedRegex will always contain dynamic subfields in even position.
                        if (i % 2) == 1:
                            fieldLength = 0
                            if splittedRegex[i].find(",") == -1:
                                # The regex was like (.{n}) so fieldlength = n
                                fieldLength = int(splittedRegex[i])
                            elif splittedRegex[i].find(",") == 0:
                                # The regex was like (.{,n}) so fieldlength = n/2
                                fieldLength = int((splittedRegex[i])[1:len(splittedRegex[i])])
                                fieldLength = fieldLength / 2
                            else:
                                # The regex was like (.{n,p}) so fieldlength = (n+p)/2
                                fieldLength = int(string.split(splittedRegex[i], ",")[0]) + int(string.split(splittedRegex[i], ",")[1])
                                fieldLength = fieldLength / 2
                            # The given field length is the length in half-bytes.
                            fieldLength = (fieldLength + 1) / 2
                            xmlField = etree.SubElement(xmlDataModel, peachType, name=("{0}_{1}").format(field.getName(), i), length=str(fieldLength))
                            logging.debug(_("The field {0} has a dynamic subfield of size {1}.").format(field.getName(), str(fieldLength)))
                        else:
                            if splittedRegex[i] != "":
                                xmlField = etree.SubElement(xmlDataModel, peachType, name=("{0}_{1}").format(field.getName(), i), mutable="false", valueType="hex", value=splittedRegex[i])
                                logging.debug(_("The field {0} has a static subfield of value {1}.").format(field.getName(), splittedRegex[i]))
                else:
                    # If the field's regex is (), we add a null-length Peach field type.
                    fieldLength = 0
                    xmlField = etree.SubElement(xmlDataModel, "Blob", name=field.getName(), length=str(fieldLength))
                    logging.debug(_("The field {0} is empty.").format(field.getName()))

                # Variable/Defaultvalue Management: #
                #-----------------------------------#
                # TODO: We have a problem if the regex is multiple and if we have a variable. Now we just add values extracted from the variable in the last subfield.

                # If we have a variable, we retrieve its value and use them for fuzzing more precisely.
                if variable is not None:
                    # We retrieve the values of the variable in text format.
                    values = self.getRecVariableValue(variable)
                    logging.debug(_("The field {0} has the value {1}.").format(field.getName(), str(values)))

                    # We add the first value of the variable as the default value of the peach field.
                    xmlField.attrib["valueType"] = "string"
                    xmlField.attrib["value"] = values[0]

                    # We add all other values to the field as potential valid values.
                    values = values[1:]
                    strValue = ""
                    for value in values:
                        strValue = ("{0};{1}").format(strValue, value)  # Each value is separated by a ';' character.
                    strValue = strValue[1:]  # We withdraw the first character which is a ';'.
                    xmlHint = etree.SubElement(xmlField, "Hint", name="ValidValues", value=strValue)

    def getRecVariableValue(self, variable):
        """
            getRecVariableValue:
                Find the value(s) of a variable. May be recursive.

                @type variable: netzob.common.MMSTD.Dictionary.Variable.variable
                @param variable: the given variable which values are searched.
                @return type: string list.
                @return: the list containing all the values of the given variable, each in string format.

        """
        values = []
        if variable.getTypeVariable() == "Aggregate":
            for child in variable.getChildren():
                for value in self.getRecVariableValue(child):
                    values.append(value)
        else:
            values.append(variable.getValue(False, self.netzob.getCurrentProject().getVocabulary(), None)[1])
        return values

    def getRecPeachFieldType(self, variable):
        """
            getRecPeachFieldType:
                Find the appropriate peach type for a field depending on its variable type. May be recursive.

                @type variable: netzob.common.MMSTD.Dictionary.Variable.variable
                @param variable: the given variable which type is searched
                @return type: string
                @return: the eventual Peach type of the variable. It can be String, Number or Blob.

        """
        # TODO: manage all native types of netzob. AlternateVariable and ReferencedVariable remain.
        logging.debug(_("Getting the type of variable {0}.").format(variable.getName()))

        # Default type is Blob. BinaryVariable and HexVariable are transformed in Blob.
        peachType = "Blob"
        if variable.getTypeVariable() == "Word" or variable.getTypeVariable() == "IPv4Variable":
            peachType = "String"
        elif variable.getTypeVariable() == "DecimalWord":
            peachType = "Number"
        elif variable.getTypeVariable() == "Aggregate":
            logging.debug(_("Variable has {0} child(ren).").format(len(variable.getChildren())))
            if len(variable.getChildren()) == 1:
                # An aggregate field with has the type of its child.
                peachType = self.getRecPeachFieldType(variable.getChildren()[0])
            else:
                # An aggregate field with children has the least demanding type of all its children.
                potentialTypes = []
                for child in variable.getChildren():
                    childType = self.getRecPeachFieldType(child)
                    if childType not in potentialTypes:
                        potentialTypes.append(childType)
                # Hierarchy of Peach type is Blob > String > Number.
                if "Blob" in potentialTypes:
                    peachType = "Blob"
                elif "String" in potentialTypes:
                    peachType = "String"
                elif "Number" in potentialTypes:
                    peachType = "Number"
        logging.debug(_("Variable {0} is of type {1}.").format(variable.getName(), peachType))
        return peachType

    def makeAStateModel(self, xmlFather):
        """
            makeAStateModel:
                Create a Peach state model. Create one state by data model and chain it to the previously created one.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.

        """
        # TODO(stateful fuzzer): Make one state model for each state of the protocol.
        xmlStateModel = etree.SubElement(xmlFather, "StateModel", name="simpleStateModel", initialState="state0")
        # There is always at least one state, the first state which is naturally called state0 and is the initial state.

        project = self.netzob.getCurrentProject()
        vocabulary = project.getVocabulary()
        stateid = 0
        xmlState = None
        # We make one state by symbol. So, all symbols will be fuzz-tested sequentially and equally.
        for symbol in vocabulary.getSymbols():
            # If the current state has a precursor, we link them from older to newer.
            if xmlState is not None:
                xmlAction = etree.SubElement(xmlState, "Action", type="changeState", ref=("state{0}").format(stateid))
            xmlState = self.makeAState(xmlStateModel, stateid)
            stateid = stateid + 1

    def makeAState(self, xmlFather, stateid):
        """
            makeAState:
                Create one state which will output data formatted according to a previously created data model.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
                @type stateid: integer
                @param stateid: a number that identifies the state in the state model and links to the proper data model.
                @return type: lxml.etree.element
                @return: a Peach state in xml format.

        """
        # We create one state which will output fuzzed data.
        xmlState = etree.SubElement(xmlFather, "State", name=("state{0}").format(str(stateid)))
        xmlAction = etree.SubElement(xmlState, "Action", type="output")

        # xml link to the previously made data model.
        xmlDataModel = etree.SubElement(xmlAction, "DataModel", ref=("dataModel{0}").format(str(stateid)))
        xmlData = etree.SubElement(xmlAction, "Data", name="data")
        return xmlState
