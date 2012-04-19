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
#| Global Imports
#+---------------------------------------------------------------------------+
import logging
import gtk
import pygtk
import gobject
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.MMSTD.Transitions.impl.OpenChannelTransition import OpenChannelTransition

pygtk.require('2.0')

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| AutomaticGrammarAbstractionView:
#|     Class to show the wizard and to abstract the current gramar
#+---------------------------------------------------------------------------+
class AutomaticGrammarAbstractionView(object):

    #+-----------------------------------------------------------------------+
    #| Constructor:
    #+-----------------------------------------------------------------------+
    def __init__(self, project):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.AutomaticGrammarAbstractionView.py')
        self.project = project

    def display(self):
        # Display the form for the creation of a word variable
        self.dialog = gtk.Dialog(title="Automatic abstraction of the current grammar", flags=0, buttons=None)

        mainTable = gtk.Table(rows=2, columns=2, homogeneous=False)
        # Insert the Save button
        self.startButton = gtk.Button("Start the abstraction")
        self.startButton.show()
        self.startButton.connect("clicked", self.startAbstraction)
        mainTable.attach(self.startButton, 0, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.dialog.vbox.pack_end(mainTable, True, True, 0)
        self.dialog.show_all()

    def startAbstraction(self, button):
        self.log.debug("Start the abstraction")

        # Retrieve available sequences
        sessions = self.project.getVocabulary().getSessions()
        self.log.debug("A number of %d sessions will be injected in the grammar" % (len(sessions)))

        for session in sessions:
            self.log.debug("Search for a difference with a new session")

            # We apply the session on current automata and find an output symbol to include
            difference = self.applySession(session)
            while difference != None:
                (transition, outputSymbol) = difference
                self.log.debug("A difference has been found, symbol %s must be added to transition %s" % (outputSymbol.getName(), transition.getName()))
                self.addOutputSymbolOnTransition(outputSymbol, transition)
#                return
                difference = self.applySession(session)

            self.log.debug("The current session does not introduce other differences")
        self.log.debug("All the sessions have been applied on current automata")

    def addOutputSymbolOnTransition(self, symbol, transition):
        self.log.debug("Adding symbol %s as an output transition %s." % (symbol.getName(), transition.getName()))
        # Adding symbol as an output symbol of the provided transition
        # to do so, we have to ;
        #   - find out all current existing symbols in the transition
        #   - add the current symbol
        #   - put a static probability (will be computed in another step)

        outputSymbolDefs = transition.getOutputSymbols()
        numberOfExistingSymbols = len(outputSymbolDefs) + 1
        new_probability = 100.0 / numberOfExistingSymbols
        transition.addOutputSymbol(symbol, 0, 100)

        # Update probabilities
        for (symbol, proba, time) in transition.getOutputSymbols():
            transition.setProbabilityForOutputSymbol(symbol, new_probability)

    def applySession(self, session):
        # retrieve the automata
        automata = self.project.getGrammar().getAutomata()

        self.log.debug("automata : %s" % automata.getDotCode())

        if automata == None:
            self.log.warn("Cannot apply a session on the current automata because it doesn't exist")
            return None

        difference = None

        # Configure the role-play environment
        # with :
        #  - a memory
        memory = Memory(None)
        #  - an abstraction layer
        abstractionLayer = AbstractionLayer(None, self.project.getVocabulary(), memory, None, None)

        currentState = automata.getInitialState()
        # We execute the opening transition
        if len(currentState.getTransitions()) == 1 and currentState.getTransitions()[0].getType() == OpenChannelTransition.TYPE:
            currentState = currentState.getTransitions()[0].getOutputState()

        isInput = True
        for message in session.getMessages():
            self.log.debug("Inject message : %s" % (message.getData()))
            # we abstract the message
            symbol = abstractionLayer.abstract(TypeConvertor.netzobRawToBitArray(str(message.getData())))
            if isInput:
                # We simulate the reception of the message
                #  - verify its a valid input symbol
                #  - find out the associated transition
                currentTransition = None
                for transition in currentState.getTransitions():
                    if transition.getInputSymbol() == symbol:
                        currentTransition = transition
                        break
                if currentTransition == None:
                    self.log.warn("Input symbol %s doesn't match any existing transition in current state %s" % (symbol.getName(), currentState.getName()))
                    self.log.warn("We forget this message.")
                else:
                    self.log.debug("Input symbol %s matchs the transition %s from state %s" % (symbol.getName(), currentTransition.getName(), currentState.getName()))
                    isInput = False
            else:
                # We simulate emiting the message
                #  - we just verify the symbol matches available output message in current transition
                found = False
                for (outputSymbol, probability, time) in currentTransition.getOutputSymbols():
                    if symbol.getID() == outputSymbol.getID():
                        found = True
                        isInput = True
                        currentState = currentTransition.getOutputState()
                        break

                if not found:
                    self.log.info("A difference has been found, symbol %s is not an output symbol of transition %s " % (symbol.getName(), currentTransition.getName()))
                    return (currentTransition, symbol)
        return difference

    def displaySession(self, session):
        memory = Memory(None)
        #  - an abstraction layer
        abstractionLayer = AbstractionLayer(None, self.project.getVocabulary(), memory, None, None)
        symbols = []
        for message in session.getMessages():
            symbols.append(abstractionLayer.abstract(TypeConvertor.netzobRawToBitArray(str(message.getData()))))

        for symbol in symbols:
            self.log.debug("- %s" % symbol.getName())
