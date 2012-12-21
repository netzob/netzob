# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Global Imports                                                            |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from lxml import etree
from netzob.Common.MMSTD.Actors.MMSTDVisitor import MMSTDVisitor
from netzob.Common.MMSTD.Actors.NetworkChannels.NetworkClient import \
    NetworkClient
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import \
    AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import \
    AlternateVariable
from netzob.Common.MMSTD.Dictionary.Variables.ComputedRelationVariable import \
    ComputedRelationVariable
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.Variables.RepeatVariable import \
    RepeatVariable
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Common.MMSTD.Symbols.impl.UnknownSymbol import UnknownSymbol
from netzob.Common.MMSTD.Transitions.impl.CloseChannelTransition import \
    CloseChannelTransition
from netzob.Common.MMSTD.Transitions.impl.OpenChannelTransition import \
    OpenChannelTransition
from netzob.Common.MMSTD.Transitions.impl.SemiStochasticTransition import \
    SemiStochasticTransition
import logging
import string

#+---------------------------------------------------------------------------+
#| Local Imports                                                             |
#+---------------------------------------------------------------------------+


class PeachExport(object):
    """PeachExport:
            Utility for exporting netzob information into Peach pit file.
            Simplify the construction of a fuzzer with Peach.
    """

    UNKNOWNSYMBOL_MAX_SIZE = 1024

    def __init__(self, netzob):
        """Constructor of PeachExport:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.
        """
        self.netzob = netzob
        self.variableOverRegex = True
        self.mutateStaticFields = True
        self.dictSymbol = dict()  # Associate each symbol to a unique simple number.
        self.normSymbols()

    def normSymbols(self):
        """normSymbols:
                Associate a simple number to each symbol of the project.
        """
        project = self.netzob.getCurrentProject()
        vocabulary = project.getVocabulary()
        dataModelid = 1  # 0 is for the initial state.
        for symbol in vocabulary.getSymbols():
            self.dictSymbol[str(symbol.getID())] = dataModelid
            dataModelid += 1
        # An empty symbol leads to the initial state.
        self.dictSymbol["-1"] = dataModelid
        dataModelid += 1
        # An unknown symbol has its own data model.
        self.dictSymbol["-2"] = dataModelid
        dataModelid += 1

    def getPeachDefinition(self, symbolID, level):
        """getXMLDefinition:
                Returns the Peach pit file (XML format) made on the  netzob information.

                @type symbolID: integer
                @param symbolID: a number which identifies the symbol the xml definition of which we need.
                @type level: integer
                @param level:
                    0: one-state fuzzer ;
                    1: randomized state order fuzzer ;
                    2: randomized transitions stateful fuzzer ;
                    3: fully stateful fuzzer.
                @rtype: string
                @return: the string representation of the generated Peach xml pit file.
        """
        logging.debug(_("Targeted symbolID: {0}").format(str(symbolID)))
        xmlRoot = etree.Element("Peach")
        etree.SubElement(xmlRoot, "Include", ns="default", src="file:defaults.xml")
        xmlImport = etree.SubElement(xmlRoot, "Import")
        xmlImport.attrib["import"] = "PeachzobAddons"

        if level == 0:
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
                self.makeDataModel(xmlRoot, symbol)
                self.makeSingleStateModel(xmlRoot, symbol)

        if level == 1:
            self.makeAllDataModels(xmlRoot)
            self.makeBasicStateModel(xmlRoot)

        if level == 2:
            self.makeAllDataModels(xmlRoot)
            self.makeProbaStateModel(xmlRoot)

        if level == 3:  # TODO: implement this.
            self.makeAllDataModels(xmlRoot)
            self.makeBasicStateModel(xmlRoot)

        # Add the supplementary xml info.
        xmlAgent = etree.SubElement(xmlRoot, "Agent", name="DefaultAgent")
        xmlCommentAgent = etree.Comment("Todo: Configure the Agents.")
        xmlAgent.append(xmlCommentAgent)

        xmlTest = etree.SubElement(xmlRoot, "Test", name="DefaultTest")
        xmlCommentTest = etree.Comment('Todo: Enable Agent <Agent ref="TheAgent"/> ')

        xmlTest.append(xmlCommentTest)
        etree.SubElement(xmlTest, "StateModel", ref="stateModel")

        # Create the publisher.
        self.makePublisher(xmlTest)

        xmlRun = etree.SubElement(xmlRoot, "Run", name="DefaultRun")
        xmlCommentRun = etree.Comment("Todo: Configure the run.")
        xmlRun.append(xmlCommentRun)
        xmlLogger = etree.SubElement(xmlRun, "Logger")
        xmlLogger.attrib["class"] = "logger.Filesystem"
        etree.SubElement(xmlLogger, "Param", name="path", value="logs")
        etree.SubElement(xmlRun, "Test", ref="DefaultTest")

        tree = etree.ElementTree(xmlRoot)
        toStringedTree = etree.tostring(tree, pretty_print=True)

        # Remove the first line:
        splittedToStringedTree = toStringedTree.split("\n")
        splittedToStringedTree = splittedToStringedTree[1:]
        toStringedTree = "\n".join(splittedToStringedTree)
        # Add strings not well managed by lxml.
        result = '<?xml version="1.0" encoding="utf-8"?>\n'
        result = result + '<Peach xmlns="http://phed.org/2008/Peach" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://phed.org/2008/Peach /peach/peach.xsd">\n'
        result = result + toStringedTree
        return result

    def makePublisher(self, xmlFather):
        """makePublisher:
                Retrieve information from Netzob simulator. These information as the communication protocol, the targeted IP and port are used to make the Peach publisher.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element
        """
        simulator = self.netzob.getCurrentProject().getSimulator()
        mmstdVisitor = None
        visitorCount = 0
        for actor in simulator.getActors():
            # We search a MMSTDVisitor. Actors might be of other types.
            if actor.getType() == MMSTDVisitor.TYPE:
                try:  # Informations might be false or the communication channel migth not be an AbstractChannel.
                    mmstdVisitor = actor
                    comChannel = mmstdVisitor.getAbstractionLayer().getCommunicationChannel()

                    logging.debug("Communication layer : {0}".format(str(comChannel)))
                    logging.debug("Protocol : {0}".format(str(comChannel.getProtocol())))
                    if comChannel.getProtocol() == "TCP":
                        xmlPublisher = etree.SubElement(xmlFather, "Publisher")
                        xmlPublisher.attrib["class"] = "tcp.Tcp"
                        etree.SubElement(xmlPublisher, "Param", name="host", value="{0}".format(comChannel.getTargetIP()))
                        etree.SubElement(xmlPublisher, "Param", name="port", value="{0}".format(comChannel.getTargetPort()))
                    if comChannel.getProtocol() == "UDP":
                        xmlPublisher = etree.SubElement(xmlFather, "Publisher")
                        xmlPublisher.attrib["class"] = "udp.Udp"
                        etree.SubElement(xmlPublisher, "Param", name="host", value="{0}".format(comChannel.getTargetIP()))
                        etree.SubElement(xmlPublisher, "Param", name="port", value="{0}".format(comChannel.getTargetPort()))
                    visitorCount += 1
                except:
                    pass
        if visitorCount == 0:
                xmlCommentTest = etree.Comment("The Netzob project has no simulator actors, you must create one. Below is a simple example.")
                xmlFather.append(xmlCommentTest)
                xmlPublisher = etree.SubElement(xmlFather, "Publisher")
                xmlPublisher.attrib["class"] = "tcp.Tcp"
                etree.SubElement(xmlPublisher, "Param", name="host", value="0.0.0.0")
                etree.SubElement(xmlPublisher, "Param", name="port", value="0")
        if visitorCount > 1:
                xmlCommentTest = etree.Comment("The Netzob project has several simulator actors, so this file have several publishers. Choose one of them and remove the others.")
                xmlFather.append(xmlCommentTest)

#+---------------------------------------------------------------------------+
#| Data Models                                                               |
#+---------------------------------------------------------------------------+
    def makeAllDataModels(self, xmlFather):
        """makeAllDataModels:
                Transform every netzob symbol into a Peach data model.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element
        """
        project = self.netzob.getCurrentProject()
        vocabulary = project.getVocabulary()

        for symbol in vocabulary.getSymbols():
            # Each symbol is translated in a Peach data model
            self.makeDataModel(xmlFather, symbol)
        self.makeUnknownSymbolDataModel(xmlFather)

    def makeDataModel(self, xmlFather, symbol):
        """makeDataModel:
                Dissect a netzob symbol in order to extract essential data for the making of Peach fields in its data Model

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
                @type symbol: netzob.common.Symbol.symbol
                @param symbol: the given symbol that will be dissected.
        """
        dataModelid = self.dictSymbol[str(symbol.getID())]
        xmlDataModel = etree.SubElement(xmlFather, "DataModel", name=("dataModel {0}").format(str(dataModelid)))
        for field in symbol.getExtendedFields():
            xmlField = None

            #-----------------------------------#
            # Variable/Defaultvalue Management: #
            #-----------------------------------#
            if self.variableOverRegex:
                logging.debug(_("The fuzzing is based on variables."))
                variable = field.getVariable()
                if variable is None:
                    variable = field.getDefaultVariable(symbol)

                # We retrieve the values of the variable in text format.
                typedValueLists = self.getRecVariableTypedValueLists(variable)
                logging.debug(_("The field {0} has the value {1}.").format(field.getName(), str(typedValueLists)))

                # We count the subfields for the selected field. Aggregate variable can cause multiple subfields.
                subLength = 0
                for typedValueList in typedValueLists:
                    subLength = max(subLength, len(typedValueList))

                logging.debug(_("Sublength : {0}.").format(str(subLength)))
                # We create one Peach subfield for each netzob subfield.
                xmlFields = []
                # For each subfield.
                for i in range(subLength):
                    # We retrieve the peach type of the field for Peach to be as efficient and precise as possible.
                    peachType = self.getPeachFieldType(typedValueLists, i)
                    xmlFields.append(etree.SubElement(xmlDataModel, peachType, valueType="hex", name=("{0}_{1}").format(field.getName(), i)))
                    # We write down all possible values the subfield can have.
                    paramValues = []
                    logging.debug("TypedValueLists : {0}".format(str(typedValueLists)))
                    for typedValueList in typedValueLists:
                        # If we have such a field. (The double list typedValueLists is lacunar)
                        if len(typedValueList) > i:
                            # We add a peach version of the netzob type in order to translate the subfield properly.
                            paramValues.append(self.netzobTypeToPeachType(typedValueList[i][0]) + "," + self.bitarray2hex(typedValueList[i][1]))
                    if len(paramValues) > 1:
                        # If there is several possible values, we use a fixup.
                        xmlOrFixup = etree.SubElement(xmlFields[i], "Fixup")
                        xmlOrFixup.attrib["class"] = "PeachzobAddons.Or"
                        # We transform the bitarray list into an hex string understandable by Peach.
                        formattedValue = ""
                        for paramValue in paramValues:
                            formattedValue = ("{0}; {1}").format(formattedValue, paramValue)
                        formattedValue = formattedValue[2:]  # Remove the '; ' prefix.
                        etree.SubElement(xmlOrFixup, "Param", name="values", value=formattedValue)
                    elif len(paramValues) == 1:
                        # We assume that fields that has only one value are "static".
                        formattedValue = (string.split(paramValues[0], ","))[1]
                        xmlFields[i].attrib["value"] = formattedValue
                        if not self.mutateStaticFields:
                            xmlFields[i].attrib["mutable"] = "false"

            #-------------------#
            # Regex management: #
            #-------------------#
            else:
                logging.debug(_("The fuzzing is based on regexes."))
                peachType = self.getPeachFieldTypeFromNetzobFormat(field)
                regex = field.getRegex()
                if field.isStatic():
                    regex = regex[1:len(regex) - 1]
                    if peachType == "Number":
                        xmlField = etree.SubElement(xmlDataModel, peachType, name=field.getName(), value=str(self.hexstring2int(regex)))
                    else:
                        xmlField = etree.SubElement(xmlDataModel, peachType, name=field.getName(), valueType="hex", value=regex)
                    if not self.mutateStaticFields:
                        xmlField.attrib["mutable"] = "false"
                else:
                    # Fields not declared static in netzob are assumed to be dynamic, have a random default value and are mutable.
                    # We assume that the regex is composed of a random number of fixed and dynamic ((.{n,p}), (.{,n}) and (.{n})) subregexs. Each subregex will have its own peach subfield.
                    # We will illustrate it with the following example "(abcd.{m,n}efg.{,o}.{p}hij)"
                    if (regex != "()"):
                        regex = regex[1:len(regex) - 1]  # regex = "abcd.{m,n}efg.{,o}.{p}hij"

                        splittedRegex = []
                        for lterm in string.split(regex, ".{"):
                                for rterm in string.split(lterm, "}"):
                                    splittedRegex.append(rterm)  # splittedRegex = ["abcd", "m,n", "efg", ",o", "", "p", "hij"]
                                    logging.debug(_("The field {0} has the splitted Regex = {1}").format(field.getName(), str(splittedRegex)))

                        for i in range(len(splittedRegex)):
                            # Dynamic subfield (splittedRegex will always contain dynamic subfields in even position).
                            if (i % 2) == 1:
                                if splittedRegex[i].find(",") == -1:  # regex = {n}
                                    fieldMaxLength = int(splittedRegex[i])
                                    fieldMinLength = fieldMaxLength
                                elif splittedRegex[i].find(",") == 0:  # regex = {,p}
                                    fieldMaxLength = int((splittedRegex[i])[1:len(splittedRegex[i])])
                                    fieldMinLength = 0
                                else:  # regex = {n,p}
                                    fieldMaxLength = int(string.split(splittedRegex[i], ",")[1])
                                    fieldMinLength = int(string.split(splittedRegex[i], ",")[0])
                                # The given field length is the length in half-bytes.
                                fieldMaxLength = (fieldMaxLength + 1) / 2
                                fieldMinLength = fieldMinLength / 2
                                xmlField = etree.SubElement(xmlDataModel, peachType, name=("{0}_{1}").format(field.getName(), i))
                                xmlRanStringFixup = etree.SubElement(xmlField, "Fixup")
                                xmlRanStringFixup.attrib["class"] = "PeachzobAddons.RandomField"
                                etree.SubElement(xmlRanStringFixup, "Param", name="minlen", value=str(fieldMinLength))
                                etree.SubElement(xmlRanStringFixup, "Param", name="maxlen", value=str(fieldMaxLength))
                                etree.SubElement(xmlRanStringFixup, "Param", name="type", value=peachType)
                            else:
                                # Static subfield.
                                if splittedRegex[i] != "":
                                    xmlField = etree.SubElement(xmlDataModel, peachType, name=("{0}_{1}").format(field.getName(), i), valueType="hex", value=splittedRegex[i])
                                    logging.debug(_("The field {0} has a static subfield of value {1}.").format(field.getName(), splittedRegex[i]))
                                    if not self.mutateStaticFields:
                                        xmlField.attrib["mutable"] = "false"
                    else:
                        # If the field's regex is (), we add a null-length Peach field type.
                        xmlField = etree.SubElement(xmlDataModel, "Blob", name=field.getName(), length=0)
                        logging.debug(_("The field {0} is empty.").format(field.getName()))

    def makeUnknownSymbolDataModel(self, xmlFather):
        """makeUnknownSymbolDataModel:
                Make a data model for unknown symbols.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element
        """
        dataModelid = self.dictSymbol["-2"]
        xmlDataModel = etree.SubElement(xmlFather, "DataModel", name=("dataModel {0}").format(str(dataModelid)))
        xmlField = etree.SubElement(xmlDataModel, "Blob", name="Field 0")
        xmlRanStringFixup = etree.SubElement(xmlField, "Fixup")
        xmlRanStringFixup.attrib["class"] = "PeachzobAddons.RandomField"
        etree.SubElement(xmlRanStringFixup, "Param", name="minlen", value=str(0))
        etree.SubElement(xmlRanStringFixup, "Param", name="maxlen", value=str(PeachExport.UNKNOWNSYMBOL_MAX_SIZE))
        etree.SubElement(xmlRanStringFixup, "Param", name="type", value="Blob")

    def netzobTypeToPeachType(self, netzobType):
        """netzobTypeToPeachType:
                Transform a netzob variable type (Word, IPv4Variable, Decimal Word ...) in a Peach field type (Number, String, Blob).

                @type netzobType: string
                @param netzobType: a netzob type.
                @rtype: string
                @return: the associated peach type.
        """
        peachType = ""
        if netzobType == "DecimalWord":
            peachType = "Number"
        elif netzobType == "Word" or netzobType == "IPv4Variable":
            peachType = "String"
        else:
            peachType = "Blob"
        return peachType

    def getRecVariableTypedValueLists(self, variable):
        """getRecVariableTypedValueLists:
                Find the value(s) and its(their) type of a variable. May be recursive.

                @type variable: netzob.common.MMSTD.Dictionary.Variable.variable
                @param variable: the given variable which values are searched.
                @rtype: (string, bitarray.bitarray) list list.
                @return: the list, representing aggregations, of lists, representing alternations, of couple (type of a leaf variable, value (in bitarray) of leaf variable).
        """
        logging.debug(_("<[ variable  : {0}.").format(str(variable.getName())))
        variableType = variable.getVariableType()
        typedValueLists = []  # List of list of couple type-value.
        if variableType == AggregateVariable.TYPE:
            for child in variable.getChildren():
                # We concatenate the double lists at the lower level (inner list).
                logging.debug(_("fatherValueLists : {0}.").format(str(typedValueLists)))
                typedValueLists = self.concatVariableValues(typedValueLists, self.getRecVariableTypedValueLists(child))

        elif variableType == AlternateVariable.TYPE:
            for child in variable.getChildren():
                # We simply concatenate the two double lists as simple list.
                for value in self.getRecVariableTypedValueLists(child):
                    typedValueLists.append(value)

        elif variableType == ComputedRelationVariable.TYPE:
#            TODO: Integrate Pointing Variable & Repeat Variable.
#            # We retrieve the typedValueLists of the pointed variable. Referenced variable are variable pointing to another variable.
#            vocabulary = self.netzob.getCurrentProject().getVocabulary()
#            pointedVariable = variable.getPointedVariable(vocabulary)
#            typedValueLists = self.getRecVariableTypedValueLists(pointedVariable)
            pass

        elif variableType == DataVariable.TYPE:
            # We add the variable type and its binary value as a singleton list in the higher list.
            # We are only interested in current values.
            value = variable.getCurrentValue()
            if value is not None:
                typedValueLists.append([(variableType, value)])
        elif variableType == RepeatVariable.TYPE:
            # TODO : implement this.
            pass

        # typedValueLists = [[("Word", "a")], [("Word", "b"), ("Word", "c"), ("Word", "e")], [("Word", "d"), ("Word", "e")]]
        # <=> variable = a + bce + de
        logging.debug(_("typedValueLists  : {0}.").format(str(typedValueLists)))
        logging.debug(_("variable  : {0}. ]>").format(str(variable.getName())))
        return typedValueLists

    def concatVariableValues(self, fatherValueLists, sonValueLists):
        """concatVariableValues:
                Insert the values of a son to its father's in such a way that the global form (aggregation of alternation) is respected.
                From an aerial point of view, we concatenate both father and son's inner list in a double list. This concatenation stays in the inner list.

                @type fatherValueLists: (string, bitarray.bitarray) list list.
                @param fatherValueLists: the preexisting father double list.
                @type fatherValueLists: (string, bitarray.bitarray) list list.
                @param fatherValueLists: the son double list to be inserted.
                @rtype: (string, bitarray.bitarray) list list.
                @return: the double list resulting of the concatenation.
        """
        finalValueLists = []
        if len(fatherValueLists) == 0:
            #initialization
            finalValueLists = sonValueLists
        for fvl in fatherValueLists:
            for svl in sonValueLists:
                midvl = fvl + svl
                logging.debug(_("concatVariableValues : midvl before : {0}.").format(str(midvl)))
                finalValueLists.append(midvl)
                logging.debug(_("concatVariableValues : midvl after : {0}.").format(str(finalValueLists)))

        return finalValueLists

    def getPeachFieldType(self, typedValueLists, index):
        """getPeachFieldType:
                Get the peach type (Blob, String or Number) of the current field. This type is determined through the majority of the type of an alternation.

                @type typedValueLists: (string, bitarray.bitarray) list list.
                @param typedValueLists: a double list composed of aggregation of alternation, we search transversely among an alternation the majority type.
                @type index: integer
                @param index: an index pointing to the targeted alternation.
                @rtype: string
                @return: the majority type of the targeted alternation.
        """
        peachType = ""
        for typedValueList in typedValueLists:
            # The hierarchy is Blob > String > Number
            if typedValueList[index][0] == "DecimalWord":
                if peachType != "Blob" and peachType != "String" and peachType != "Number":
                    peachType = "Number"
            elif typedValueList[index][0] == "Word" or typedValueList[index][0] == "IPv4Variable":
                if peachType != "Blob" and peachType != "String":
                    peachType = "String"
            else:
                if peachType != "Blob":
                    peachType = "Blob"
                    break
        if peachType == "":
            # Eventual default value.
            peachType = "Blob"
        return peachType

    def getPeachFieldTypeFromNetzobFormat(self, field):
        """getPeachFieldTypeFromNetzobFormat:
                Get the peach type (Blob, String or Number) of the current field from the netzob visualization format (string, decimal, octal, hex or binary).

                @type field: netzob.Common.Field.Field
                @param field: the given field which peach type is being searched.
                @rtype: string
                @return: the peach field type.
        """
        peachType = ""
        formt = field.getFormat()
        logging.debug(_("Format of the field {0} is {1}.").format(field.getName(), formt))
        if formt == "string":
            peachType = "String"
        elif formt == "decimal":
            peachType = "Number"
        else:
            peachType = "Blob"
        return peachType

#+---------------------------------------------------------------------------+
#| Sate Models                                                               |
#+---------------------------------------------------------------------------+
    def makeSingleStateModel(self, xmlFather, symbol):
        """makeSingleStateModel:
                Make just one state model that emits fuzzed data according to the given symbol.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
        """
        xmlStateModel = etree.SubElement(xmlFather, "StateModel", name="stateModel", initialState="state 0")
        xmlState = etree.SubElement(xmlStateModel, "State", name="state 0")
        # We create one action which will output fuzzed data.
        xmlAction = etree.SubElement(xmlState, "Action", type="output")
        etree.SubElement(xmlAction, "DataModel", ref=("dataModel {0}").format(str(self.dictSymbol[symbol.getID()])))
        etree.SubElement(xmlAction, "Data", name="data")

    def makeBasicStateModel(self, xmlFather):
        """makeBasicStateModel:
                Create a basic Peach state model. One state per sybmol, all these states are accessed randomly.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
        """
        xmlStateModel = etree.SubElement(xmlFather, "StateModel", name="stateModel", initialState="state 0")
        # There is always at least one state, the first state which is naturally called state0 and is the initial state.
        xmlFirstState = etree.SubElement(xmlStateModel, "State", name="state 0")

        # Count symbols in the current project.
        vocabulary = self.netzob.getCurrentProject().getVocabulary()
        nbSymbols = 1  # 1 for the unknown symbol, we do not care of the empty symbol which is useless in outputs.
        for symbol in vocabulary.getSymbols():
            nbSymbols += 1

        # We make one state by symbol. So, all symbols will be fuzz-tested sequentially and equally.
        i = 0
        for symbol in vocabulary.getSymbols():
            # If the current state has a precursor, we link them from older to newer.
            xmlState = etree.SubElement(xmlStateModel, "State", name=("state {0}").format(str(self.dictSymbol[symbol.getID()])))
            # We create one action which will output fuzzed data.
            xmlAction = etree.SubElement(xmlState, "Action", type="output")
            etree.SubElement(xmlAction, "DataModel", ref=("dataModel {0}").format(str(self.dictSymbol[symbol.getID()])))
            etree.SubElement(xmlAction, "Data", name="data")

            # Create a transition between the first state and this state.
            etree.SubElement(xmlFirstState, "Action", type="changeState", ref="state {0}".format(str(self.dictSymbol[symbol.getID()])),
                             when="random.randint(1,{0})==1".format(str(nbSymbols - i)))
            i += 1

            # Create a reverse transition between this state and the first state.
            #etree.SubElement(xmlState, "Action", type="changeState", ref="state 0")

        # Unknown symbol.
        xmlState = etree.SubElement(xmlStateModel, "State", name=("state {0}").format(str(self.dictSymbol["-2"])))
        # We create one action which will output fuzzed data.
        xmlAction = etree.SubElement(xmlState, "Action", type="output")
        etree.SubElement(xmlAction, "DataModel", ref=("dataModel {0}").format(str(self.dictSymbol["-2"])))
        etree.SubElement(xmlAction, "Data", name="data")
        # Last transition.
        etree.SubElement(xmlFirstState, "Action", type="changeState", ref="state {0}".format(str(self.dictSymbol["-2"])))
        #etree.SubElement(xmlState, "Action", type="changeState", ref="state 0")

    def makeProbaStateModel(self, xmlFather):
        """makeProbaStateModel:
                Return a state model based on the transitions and states inferred from Netzob. At each state, a transition is chosen according to a dice throw among all
                transitions allowed by netzob. One symbol is created for every *different* symbols. So if a symbol is used in different states, it will create instant transition
                bewteen these state. That is assumed and part of the state fuzzing of this model.
                Inputs are not managed.
                There is a structural difference between Peach and Netzob state models. Globally, states of the first are transitions of the second.

                @type xmlFather: lxml.etree.element
                @param xmlFather: the xml tree father of the current element.
        """
        mmstd = None
        try:
            # If mmstd is None, these few lines should raise an alert.
            mmstd = self.netzob.getCurrentProject().getGrammar().getAutomata()
            initialState = mmstd.getInitialState()
            transitions = mmstd.getTransitions()
            states = mmstd.getAllStates()
        except:
            logging.info(_("No state model defined in Netzob."))
            etree.SubElement(xmlFather, "StateModel", name="No state model defined in Netzob.")
            return

        # A simple dictionary of all the xml states.
        xmlStatesDict = dict()

        # Associate the ID of a symbol to the sum of the probabilities of all the transitions that leads to the state it comes from.
        probaDict = dict()

        # List of transitions formed like [startStateID, endStateID, weighting (probability), isTheTransitionFinal]
        transList = []

        xmlStateModel = etree.SubElement(xmlFather, "StateModel", name="stateModel", initialState="state 0")

        # Create the initial state.
        for transition in transitions:
            # We search the very first transition.
            if transition.getType() == OpenChannelTransition.TYPE:
                if transition.getInputState() == initialState:
                    xmlState = etree.SubElement(xmlStateModel, "State", name="state 0")
                    xmlStatesDict[0] = xmlState
                    # Determine the upper bound of probability.
                    outputState = transition.getOutputState()
                    probaDict[0] = 0
                    for outTrans in mmstd.getTransitionsStartingFromState(outputState):
                        if outTrans.getType() == SemiStochasticTransition.TYPE:
                            for outSymbol in outTrans.getOutputSymbols():
                                probaDict[0] += outSymbol[1]
                    # Create probabilistic transitions.
                    for outTrans in mmstd.getTransitionsStartingFromState(outputState):
                        if outTrans.getType() == SemiStochasticTransition.TYPE:
                            for outSymbol in outTrans.getOutputSymbols():
                                    transList.append([0, self.getSymbolID(outSymbol[0]), outSymbol[1]])
                    break

        # Create all other states.
        for transition in transitions:
            if transition.getType() == SemiStochasticTransition.TYPE:
                # Output Symbols : [[Symbol, Probability, Time], [Symbol, Probability, Time], ...]
                outputSymbols = transition.getOutputSymbols()

                # Create one Peach state per output symbol.
                for symbol in outputSymbols:
                    if not self.getSymbolID(symbol[0]) in xmlStatesDict.keys():
                        if self.getSymbolID(symbol[0]) == "-1":  # Empty symbol.
                            # We create an empty state with no actions.
                            xmlState = etree.SubElement(xmlStateModel, "State", name=("state {0}").format(self.dictSymbol[self.getSymbolID(symbol[0])]))
                            xmlStatesDict[self.getSymbolID(symbol[0])] = xmlState
                        else:
                            xmlState = etree.SubElement(xmlStateModel, "State", name=("state {0}").format(self.dictSymbol[self.getSymbolID(symbol[0])]))
                            # We create one action which will output fuzzed data.
                            xmlAction = etree.SubElement(xmlState, "Action", type="output")
                            etree.SubElement(xmlAction, "DataModel", ref=("dataModel {0}").format(self.dictSymbol[self.getSymbolID(symbol[0])]))
                            etree.SubElement(xmlAction, "Data", name="data")
                            xmlStatesDict[self.getSymbolID(symbol[0])] = xmlState

                    probaDict[self.getSymbolID(symbol[0])] = 0

        # Determine the upper bound.
        for state in states:
            for inTrans in mmstd.getTransitionsLeadingToState(state):
                if inTrans.getType() == SemiStochasticTransition.TYPE:
                    for inSymbol in inTrans.getOutputSymbols():
                        for outTrans in mmstd.getTransitionsStartingFromState(state):
                            if outTrans.getType() == SemiStochasticTransition.TYPE:
                                for outSymbol in outTrans.getOutputSymbols():
                                    probaDict[self.getSymbolID(inSymbol[0])] += outSymbol[1]
                            if outTrans.getType() == CloseChannelTransition.TYPE:
                                    probaDict[self.getSymbolID(inSymbol[0])] += 100

        # Create probabilistic transitions.
        for state in states:
            for inTrans in mmstd.getTransitionsLeadingToState(state):
                if inTrans.getType() == SemiStochasticTransition.TYPE:
                    for inSymbol in inTrans.getOutputSymbols():
                        for outTrans in mmstd.getTransitionsStartingFromState(state):
                            if outTrans.getType() == SemiStochasticTransition.TYPE:
                                for outSymbol in outTrans.getOutputSymbols():
                                    transList.append([self.getSymbolID(inSymbol[0]), self.getSymbolID(outSymbol[0]), outSymbol[1]])
                            #if outTrans.getType() == CloseChannelTransition.TYPE:
                                # Eventual transition to the end and the first state above.
                                #transList.append([self.getSymbolID(inSymbol[0]), 0, 100])

        # Normalize transitions: pack transitions which go from the same state and to the same state.
        normTransList = []
        for transition in transList:
            found = False
            for normTransition in normTransList:
                if transition[0] == normTransition[0] and transition[1] == normTransition[1]:
                    # Similar transitions, we sum their weightings.
                    normTransition[2] += transition[2]
                    found = True
                    break
            if not found:
                # New transitions, we add it.
                normTransList.append(transition)

        # Add transitions to the xml file.
        for normTransition in normTransList:
            toStateName = ""
            if normTransition[1] == 0:  # First state.
                toStateName = "state 0"
            else:
                toStateName = ("state {0}").format(str(self.dictSymbol[normTransition[1]]))

            if probaDict[normTransition[0]] == normTransition[2]:  # Last transition.
                etree.SubElement(xmlStatesDict[normTransition[0]], "Action", type="changeState", ref=toStateName)
            else:
                etree.SubElement(xmlStatesDict[normTransition[0]], "Action", type="changeState", ref=toStateName,
                                 when="random.randint(1,{0})<={1}".format(str(int(probaDict[normTransition[0]])), str(int(normTransition[2]))))
                # Reduce probability. The tests will be successive, for instance: test1: 20%, test2: 30%, test3: 40% test4: 10% of a single dice is equivalent to:
                # test1 20/100, test2 (if not test1) 30/80 (30/100 = 30/80*80/100), test3 (if neither test1 nor test2) 40/50 ...
                probaDict[normTransition[0]] -= normTransition[2]

#+---------------------------------------------------------------------------+
#| Utils                                                                     |
#+---------------------------------------------------------------------------+
    def bitarray2hex(self, abitarray):
        """bitarray2hex:
                Transform a bitarray in a pure hex string.

                @type abitarray: bitarray.bitarray
                @param abitarray: the given bitarray which is transformed.
                @rtype: string
                @return: the hex translation of the bitarray.
        """
        return (abitarray.tobytes()).encode('hex')

    def bitarray2str(self, abitarray):
        """bitarray2str:
                Transform a bitarray in a 'u string.

                @type abitarray: bitarray.bitarray
                @param abitarray: the given bitarray which is transformed.
                @rtype: string
                @return: the 'u string translation of the bitarray.
        """
        return (abitarray.tobytes())

    def hexstring2int(self, hexstring):
        """hexstring2int:
            Transform a hexstring in an int. A hexstring is like "1234deadbeef"

            @type hexstring: string
            @param hextring: the given hexstring which is trasnformed in int.
            @rtype: integer
            @return: the integer extracted from the hex string 'hexstring'
        """
        return int('0x' + hexstring, 16)

    def getSymbolID(self, symbol):
        """getSymbolID:
                Custom function to retrieve a symbol ID even if he does not have one. (this is the case for EmptySymbol and UnknownSymbol).
        """
        if symbol.getType() == EmptySymbol.TYPE:
            return "-1"
        elif symbol.getType() == UnknownSymbol.TYPE:
            return "-2"
        else:
            return str(symbol.getID())

#+---------------------------------------------------------------------------+
#| Getters And Setters                                                       |
#+---------------------------------------------------------------------------+
    def setVariableOverRegex(self, value):
        """setVariableOverRegex:
                Setter for variableOverRegex.

            @type value: boolean
            @param value: the new value of variableOverRegex.
        """
        self.variableOverRegex = value

    def setMutateStaticFields(self, value):
        """setMutateStaticFields:
                Setter for mutateStaticFields.

            @type value: boolean
            @param value: the new value of mutateStaticFields.
        """
        self.mutateStaticFields = value
