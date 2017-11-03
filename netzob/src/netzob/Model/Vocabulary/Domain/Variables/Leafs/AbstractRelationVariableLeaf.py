#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import  uuid
#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from lxml import etree
from lxml.etree import ElementTree
#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS


@NetzobLogger
class AbstractRelationVariableLeaf(AbstractVariableLeaf):
    """Represents a relation relation between variables, one being updated with the others.

    """

    def __init__(self, varType, fieldDependencies=None, name=None):
        super(AbstractRelationVariableLeaf, self).__init__(
            varType, name, svas=SVAS.VOLATILE)
        if fieldDependencies is None:
            fieldDependencies = []
        self.fieldDependencies = fieldDependencies

    @property
    def fieldDependencies(self):
        """A list of fields that are required before computing the value of this relation

        :type: a list of :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        """
        return self.__fieldDependencies

    @fieldDependencies.setter
    @typeCheck(list)
    def fieldDependencies(self, fields):
        if fields is None:
            fields = []
        for field in fields:
            if not isinstance(field, AbstractField):
                raise TypeError("At least one specified field is not a Field.")
        self.__fieldDependencies = []
        for f in fields:
            self.__fieldDependencies.extend(f.getLeafFields())

    def XMLProperties(currentNode, xmlAbsRelLeaf, symbol_namespace, common_namespace):
        AbstractVariableLeaf.XMLProperties(currentNode, xmlAbsRelLeaf, symbol_namespace, common_namespace)

        # Save fieldDependencies: Problem is it is a List of References to an Objekt.
        # Bypass it with the uuid to search for later in the Loading Process
        if currentNode.fieldDependencies is not None and len(currentNode.fieldDependencies) > 0:
            xmlfieldDependencies = etree.SubElement(xmlAbsRelLeaf, "{" + symbol_namespace + "}fieldDependencies")
            for field in currentNode.fieldDependencies:
                xmlFieldRef = etree.SubElement(xmlfieldDependencies, "{" + symbol_namespace + "}field-reference")
                xmlFieldRef.set("id", str(field.id.hex))

    def saveToXML(self, xmlroot, symbol_namespace, common_namespace):
        xmlAbsRelLeaf = etree.SubElement(xmlroot, "{" + symbol_namespace + "}abstractRelationVariableLeaf")

        AbstractRelationVariableLeaf.XMLProperties(self, xmlAbsRelLeaf, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):

        fieldDependencies = []
        if xmlroot.find("{" + symbol_namespace + "}fieldDependencies") is not None:
            xmlDependencies = xmlroot.find("{" + symbol_namespace + "}fieldDependencies")
            for xmlRef in xmlDependencies.findall("{" + symbol_namespace + "}field-reference"):
                ref = uuid.UUID(hex=str(xmlRef.get('id')))
                if ref is not None:
                    fieldDependencies.append(ref)
        attributes['fieldDependencies'] = fieldDependencies

        AbstractVariableLeaf.restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes)

        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):

        a = AbstractRelationVariableLeaf.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        absRelVarLeaf = None

        if 'varType' in a.keys():
            absRelVarLeaf = AbstractRelationVariableLeaf(varType=a['varType'], name=a['name'],
                                                         fieldDependencies=list())
            if 'id' in a.keys():
                absRelVarLeaf.id = a['id']
            if 'svas' in a.keys():
                absRelVarLeaf.svas = a['svas']
            if 'fieldDependencies' in a.keys():
                from netzob.Export.XMLHandler.XMLHandler import XMLHandler
                unresolved = dict()
                for ref in a['fieldDependencies']:
                    unresolved[ref] = absRelVarLeaf
                XMLHandler.add_to_unresolved_dict('fieldDependencies', unresolved)
        return absRelVarLeaf
