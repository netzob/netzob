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



#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.TypeConvertor import TypeConvertor
from netzob.Common.EnvironmentalDependency import EnvironmentalDependency
from lxml import etree
 


#+---------------------------------------------------------------------------+
#| ProjectConfiguration :
#|     Class definition of the configuration of a Project
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class ProjectConfiguration(object):
    
    VOCABULARY_EQUIVALENCE_THRESHOLD = "equivalence_threshold"
    VOCABULARY_ORPHAN_REDUCTION = "orphan_reduction"
    VOCABULARY_NB_ITERATION = "nb_iteration"
    VOCABULARY_DO_INTERNAL_SLICK = "do_internal_slick"
    VOCABULARY_GLOBAL_DISPLAY = "global_display"
    VOCABULARY_ENVIRONMENTAL_DEPENDENCIES = "environmental_dependencies"
    VOCABULARY_ENVIRONMENTAL_DEPENDENCY = "environmental_dependency"
    
    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self) :
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
        self.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_DISPLAY, "BINARY")
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
        
        xmlVocabularyInferenceGlobalDisplay = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_DISPLAY)
        xmlVocabularyInferenceGlobalDisplay.text = str(self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_DISPLAY))
        
        xmlVocabularyInferenceEnvDependencies = etree.SubElement(xmlVocabularyInference, "{" + namespace + "}" + ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES)
        envDependencies = self.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES)
        if envDependencies != None :
            for envDependency in envDependencies :
                envDependency.save(xmlVocabularyInferenceEnvDependencies, namespace)
                
                
        
        
        
        
        
        
    @staticmethod
    def loadDefaultProjectConfiguration():
        projectConfiguration = ProjectConfiguration()
        return projectConfiguration
    
    @staticmethod
    def loadProjectConfiguration(xmlRoot, namespace, version):
        
        projectConfiguration = ProjectConfiguration()

        if version == "0.1" :  
            # Load the configuration of the vocabulary inference
            if xmlRoot.find("{" + namespace + "}vocabulary_inference") != None :
                
                xmlVocabularyInference = xmlRoot.find("{" + namespace + "}vocabulary_inference")
                            
                # Equivalence threshold
                xmlEquivalence = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD)
                if xmlEquivalence != None and xmlEquivalence != None and len(xmlEquivalence) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD, int(xmlEquivalence.text))
                
                # Orphan reduction
                xmlOrphanReduction = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION)
                if xmlOrphanReduction != None and xmlOrphanReduction != None and len(xmlOrphanReduction) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION, TypeConvertor.str2bool(xmlOrphanReduction.text))
                    
                # Nb iteration
                xmlNbIteration = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_NB_ITERATION)
                if xmlNbIteration != None and xmlNbIteration != None and len(xmlNbIteration) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_NB_ITERATION, int(xmlNbIteration.text))
                    
                # Do Internal Slick
                xmlDoInternalSlick = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
                if xmlDoInternalSlick != None and xmlDoInternalSlick != None and len(xmlDoInternalSlick) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK, TypeConvertor.str2bool(xmlDoInternalSlick.text))
                    
                # Global display
                xmlGlobalDisplay = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_GLOBAL_DISPLAY)
                if xmlGlobalDisplay != None and xmlGlobalDisplay != None and len(xmlGlobalDisplay) > 0:
                    projectConfiguration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_DISPLAY, xmlGlobalDisplay.text)
                    
                # Environmental dependencies
                xmlEnvDependencies = xmlVocabularyInference.find("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES)
                if xmlEnvDependencies != None :
                    envDependencies = projectConfiguration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES)
                    for xmlEnvDependency in xmlEnvDependencies.findall("{" + namespace + "}" + ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCY) :
                        envDependencyName = xmlEnvDependency.get("name", "none")
                        envDependencyType = xmlEnvDependency.get("type", "none")
                        envDependencyValue = xmlEnvDependency.text
                        if envDependencyValue == None :
                            envDependencyValue = ""
                        envDependencies.append(EnvironmentalDependency(envDependencyName, envDependencyType, envDependencyValue))
            
            # Load the configuration of the grammar inference
            
            # Load the configuration of the simulation
        
        return projectConfiguration
        
        
    
