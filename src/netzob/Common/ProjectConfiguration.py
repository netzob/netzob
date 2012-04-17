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
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.EnvironmentalDependency import EnvironmentalDependency
from netzob.Common.Type.Format import Format
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess


#+---------------------------------------------------------------------------+
#| ProjectConfiguration:
#|     Class definition of the configuration of a Project
#+---------------------------------------------------------------------------+
class ProjectConfiguration(object):

    VOCABULARY_EQUIVALENCE_THRESHOLD = "equivalence_threshold"
    VOCABULARY_ORPHAN_REDUCTION = "orphan_reduction"
    VOCABULARY_NB_ITERATION = "nb_iteration"
    VOCABULARY_DO_INTERNAL_SLICK = "do_internal_slick"
    VOCABULARY_GLOBAL_FORMAT = "global_format"
    VOCABULARY_GLOBAL_UNITSIZE = "global_unitsize"
    VOCABULARY_GLOBAL_SIGN = "global_sign"
    VOCABULARY_GLOBAL_ENDIANESS = "global_endianess"
    VOCABULARY_DISPLAY_MESSAGES = "display_messages"
    VOCABULARY_DISPLAY_SYMBOL_STRUCTURE = "display_symbol_structure"
    VOCABULARY_DISPLAY_CONSOLE = "display_console"
    VOCABULARY_DISPLAY_SEARCH = "display_search"
    VOCABULARY_DISPLAY_PROPERTIES = "display_properties"
    VOCABULARY_ENVIRONMENTAL_DEPENDENCIES = "environmental_dependencies"
    VOCABULARY_ENVIRONMENTAL_DEPENDENCY = "environmental_dependency"

    SIMULATION_ACTORS = "actors"
    SIMULATION_ACTOR = "actor"

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self):
        self.vocabularyInference = dict()
        self.grammarInference = dict()
        self.simulation = dict()
        self.resetParameters()

    def resetParameters(self):
        # Vocabulary
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD, 60)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION, False)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_NB_ITERATION, 100)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK, False)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT, Format.HEX)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE, UnitSize.NONE)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN, Sign.UNSIGNED)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS, Endianess.BIG)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES, True)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE, False)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_CONSOLE, False)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH, False)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES, False)
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES, [])

        # Grammar
    def setVocabularyInferenceParameter(self, name, value):
        self.vocabularyInference[name] = value

    def getVocabularyInferenceParameter(self, name):
        return self.vocabularyInference[name]

    def setGrammarInferenceParameter(self, name, value):
        self.grammarInference[name] = value

    def getGrammarInferenceParameter(self, name):
        return self.grammarInference[name]

    def setSimulationParameter(self, name, value):
        self.simulation[name] = value

    def getSimulationParameter(self, name):
        return self.simulation[name]

    def save(self, root, namespace):
        xmlConfiguration = etree.SubElement(root, "{" + namespace + "}configuration")
        xmlVocabularyInference = etree.SubElement(xmlConfiguration, "{" + namespace + "}vocabulary_inference")

        xmlVocabularyInferenceEquivalenceThreshold = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD)
        xmlVocabularyInferenceEquivalenceThreshold.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD))

        xmlVocabularyInferenceOrphanReduction = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION)
        xmlVocabularyInferenceOrphanReduction.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION)).lower()

        xmlVocabularyInferenceNbIteration = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_NB_ITERATION)
        xmlVocabularyInferenceNbIteration.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_NB_ITERATION))

        xmlVocabularyInferenceDoInternalSlick = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
        xmlVocabularyInferenceDoInternalSlick.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)).lower()

        xmlVocabularyInferenceDisplayMessages = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES)
        xmlVocabularyInferenceDisplayMessages.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES)).lower()

        xmlVocabularyInferenceDisplaySymbolStructure = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE)
        xmlVocabularyInferenceDisplaySymbolStructure.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE)).lower()

        xmlVocabularyInferenceDisplayConsole = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_CONSOLE)
        xmlVocabularyInferenceDisplayConsole.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_CONSOLE)).lower()

        xmlVocabularyInferenceDisplaySearch = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH)
        xmlVocabularyInferenceDisplaySearch.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH)).lower()

        xmlVocabularyInferenceDisplayProperties = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES)
        xmlVocabularyInferenceDisplayProperties.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES)).lower()

        xmlVocabularyInferenceGlobalFormat = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        xmlVocabularyInferenceGlobalFormat.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT))

        xmlVocabularyInferenceGlobalUnitSize = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
        xmlVocabularyInferenceGlobalUnitSize.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE))

        xmlVocabularyInferenceGlobalSign = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_SIGN)
        xmlVocabularyInferenceGlobalSign.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN))

        xmlVocabularyInferenceGlobalEndianess = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS)
        xmlVocabularyInferenceGlobalEndianess.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS))

        xmlVocabularyInferenceEnvDependencies = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES)
        envDependencies = self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES)
        if envDependencies != None:
            for envDependency in envDependencies:
                envDependency.save(xmlVocabularyInferenceEnvDependencies, namespace)

    #+-----------------------------------------------------------------------+
    #| Static methods
    #+-----------------------------------------------------------------------+
    @staticmethod
    def loadDefaultProjectConfiguration():
        projectConfiguration = ProjectConfiguration()
        return projectConfiguration

    @staticmethod
    def loadProjectConfiguration(xmlRoot, namespace, version):

        projectConfiguration = ProjectConfiguration()

        if version == "0.1":
            # Load the configuration of the vocabulary inference
            if xmlRoot.find("{" + namespace + "}vocabulary_inference") != None:

                xmlVocabularyInference = xmlRoot.find("{" + namespace + "}vocabulary_inference")

                # Equivalence threshold
                xmlEquivalence = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD)
                if xmlEquivalence != None and xmlEquivalence.text != None and len(xmlEquivalence.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD, int(xmlEquivalence.text))

                # Orphan reduction
                xmlOrphanReduction = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION)
                if xmlOrphanReduction != None and xmlOrphanReduction.text != None and len(xmlOrphanReduction.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION, TypeConvertor.str2bool(xmlOrphanReduction.text))

                # Nb iteration
                xmlNbIteration = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_NB_ITERATION)
                if xmlNbIteration != None and xmlNbIteration.text != None and len(xmlNbIteration.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_NB_ITERATION, int(xmlNbIteration.text))

                # Do Internal Slick
                xmlDoInternalSlick = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
                if xmlDoInternalSlick != None and xmlDoInternalSlick.text != None and len(xmlDoInternalSlick.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK, TypeConvertor.str2bool(xmlDoInternalSlick.text))

                # Display Messages
                xmlDisplayMessages = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES)
                if xmlDisplayMessages != None and xmlDisplayMessages.text != None and len(xmlDisplayMessages.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES, TypeConvertor.str2bool(xmlDisplayMessages.text))

                # Display Symbol Structure
                xmlDisplaySymbolStructure = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE)
                if xmlDisplaySymbolStructure != None and xmlDisplaySymbolStructure.text != None and len(xmlDisplaySymbolStructure.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE, TypeConvertor.str2bool(xmlDisplaySymbolStructure.text))

                # Display Console
                xmlDisplayConsole = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_CONSOLE)
                if xmlDisplayConsole != None and xmlDisplayConsole.text != None and len(xmlDisplayConsole.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_CONSOLE, TypeConvertor.str2bool(xmlDisplayConsole.text))

                # Display Search
                xmlDisplaySearch = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH)
                if xmlDisplaySearch != None and xmlDisplaySearch.text != None and len(xmlDisplaySearch.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH, TypeConvertor.str2bool(xmlDisplaySearch.text))

                # Display Properties
                xmlDisplayProperties = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES)
                if xmlDisplayProperties != None and xmlDisplayProperties.text != None and len(xmlDisplayProperties.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES, TypeConvertor.str2bool(xmlDisplayProperties.text))

                # Global format
                xmlGlobalFormat = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
                if xmlGlobalFormat != None and xmlGlobalFormat.text != None and len(xmlGlobalFormat.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT, xmlGlobalFormat.text)

                # Global unitsize
                xmlGlobalUnitSize = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
                if xmlGlobalUnitSize != None and xmlGlobalUnitSize.text != None and len(xmlGlobalUnitSize.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE, xmlGlobalUnitSize.text)

                # Global sign
                xmlGlobalSign = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_SIGN)
                if xmlGlobalSign != None and xmlGlobalSign.text != None and len(xmlGlobalSign.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN, xmlGlobalSign.text)

                # Global endianess
                xmlGlobalEndianess = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS)
                if xmlGlobalEndianess != None and xmlGlobalEndianess.text != None and len(xmlGlobalEndianess.text) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS, xmlGlobalEndianess.text)

                # Environmental dependencies
                xmlEnvDependencies = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES)
                if xmlEnvDependencies != None:
                    envDependencies = projectConfiguration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES)
                    for xmlEnvDependency in xmlEnvDependencies.findall("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCY):
                        envDependencyName = xmlEnvDependency.get("name", "none")
                        envDependencyType = xmlEnvDependency.get("type", "none")
                        envDependencyValue = xmlEnvDependency.text
                        if envDependencyValue == None:
                            envDependencyValue = ""
                        envDependencies.append(EnvironmentalDependency(envDependencyName, envDependencyType, envDependencyValue))

            # Load the configuration of the grammar inference

            # Load the configuration of the simulation

        return projectConfiguration
