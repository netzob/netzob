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


#-------------------------------------------------------------------------------
# Global Imports
#-------------------------------------------------------------------------------
from gettext import gettext as _
import logging
from lxml import etree
import string

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------


#-------------------------------------------------------------------------------
# PeachExport:
#    Utility for exporting netzob information
# in Peach pit file.
#-------------------------------------------------------------------------------
class PeachExport:

    #---------------------------------------------------------------------------
    # Constructor:
    #---------------------------------------------------------------------------
    def __init__(self, netzob):
        self.netzob = netzob

    #---------------------------------------------------------------------------
    # getXMLDefinition:
    #     Returns part of the Peach pit file (XML definition)
    #     TODO: Return the entire Peach pit file
    #     @return a string containing the xml def.
    #---------------------------------------------------------------------------
    def getPeachDefinition(self, symbolID, entireProject):
        xmlRoot = etree.Element("root")
        logging.debug(_("Targeted symbolID: {0}").format(str(symbolID)))
        # TODO(stateful fuzzer): take into account the inferred grammar.

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
                #TODO: Code this function
                self.makeADataModel(xmlRoot, symbol, 0)
            self.makeAState(xmlRoot, 0)

        tree = etree.ElementTree(xmlRoot)
        result = etree.tostring(tree, pretty_print=True)
        return result

    #---------------------------------------------------------------------------
    # makeAllDataModels:
    #    Transform every single netzob symbol into Peach data model.
    #    @param xmlFather: xml tree father of the current element.
    #---------------------------------------------------------------------------
    def makeAllDataModels(self, xmlFather):
        project = self.netzob.getCurrentProject()
        vocabulary = project.getVocabulary()

        dataModelid = 0
        for symbol in vocabulary.getSymbols():
            # Each symbol is translated in a Peach data model
            self.makeADataModel(xmlFather, symbol, dataModelid)
            dataModelid = dataModelid + 1

    #---------------------------------------------------------------------------
    # makeADataModel:
    #    Dissect a netzob symbol in order to extract essential data for the
    #    making of Peach fields in its data model.
    #    @param xmlFather: xml tree father of the current element.
    #    @param symbol: the given symbol that will be dissected.
    #    @param dataModelid: A number that identifies the data model.
    #---------------------------------------------------------------------------
    def makeADataModel(self, xmlFather, symbol, dataModelid):
        # TODO: strengthen the regex analysis.

        xmlDataModel = etree.SubElement(xmlFather, "DataModel", name=("dataModel{0}").format(str(dataModelid)))
        for field in symbol.getFields():

            xmlField = None
            peachType = ""
            variable = field.getVariable()
            if variable is not None:
                # Precision on the variable type.
                peachType = self.getPeachFieldType(variable)
            else:
                logging.debug(_("The field {0} has not got any variable.").format(field.getName()))
                peachType = "Blob"

            if field.isStatic():
                # Static fields are not mutated.
                xmlField = etree.SubElement(xmlDataModel, peachType, name=field.getName(), mutable="false", valueType="hex", value=field.getRegex())
            else:
                # Fields not declared static in netzob are assumed to be dynamic, have a random default value and are mutable.
                # By definition of the isStatic() function, they have at least one character "{" in their regex.
                # We assume that the regex is composed of a random number of fixed and dynamic (.{n,p}, .{,n} and .{n}) subfields .
                # We will illustrate our demarch with the following example "(abcd.{m,n}efg.{,o}.{p}hij)"
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
                                # The regex was like (.{,n}) so fieldlength = n
                                fieldLength = int((splittedRegex[i])[1:len(splittedRegex[i])])
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
                    logging.debug(_("The field {0} is empty.").format(field.getName()))

    #---------------------------------------------------------------------------
    # getPeachFieldType
    #    Find the appropriate peach type for a field depending on its variable type.
    #    May be recursive.
    #    @return peachType: the eventual type of the peach field.
    #---------------------------------------------------------------------------
    def getPeachFieldType(self, variable):
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
                peachType = self.getPeachFieldType(variable.getChildren()[0])
            else:
                # An aggregate field with children has the least demanding type of all its children.
                potentialTypes = []
                for child in variable.getChildren():
                    childType = self.getPeachFieldType(child)
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

    #---------------------------------------------------------------------------
    # makeAStateModel
    #    Create one state model by data model and chain it to the previously
    #    created.
    #    @param xmlFather: xml tree father of the current element.
    #---------------------------------------------------------------------------
    def makeAStateModel(self, xmlFather):
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

    #---------------------------------------------------------------------------
    # makeAState
    #    Create one state model that will use the previously created data model.
    #    @param xmlFather: xml tree father of the current element.
    #    @param stateid: A number that identifies the state in the state model.
    #    @return xmlState: An xml-shaped Peach-state aiming to output fuzzed data
    #    of the corresponding data model.
    #---------------------------------------------------------------------------
    def makeAState(self, xmlFather, stateid):
        # We create one state which will output fuzzed data.
        xmlState = etree.SubElement(xmlFather, "State", name=("state{0}").format(str(stateid)))
        xmlAction = etree.SubElement(xmlState, "Action", type="output")

        # xml link to the previously made data model.
        xmlDataModel = etree.SubElement(xmlAction, "DataModel", ref=("dataModel{0}").format(str(stateid)))
        xmlData = etree.SubElement(xmlAction, "Data", name="data")
        return xmlState
