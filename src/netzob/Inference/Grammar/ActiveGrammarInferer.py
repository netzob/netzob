# -*- coding: utf-8 -*-

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
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <gbossert (a) miskin.fr                           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import time
from threading import Thread
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from pylstar.LSTAR import LSTAR
from pylstar.Letter import Letter
from pylstar.eqtests.RandomWalkMethod import RandomWalkMethod

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Inference.Grammar.GenericMAT import GenericMAT

@NetzobLogger
class ActiveGrammarInferer(Thread):

    def __init__(self, input_symbols, output_symbols, process_wrapper, channel, tmp_path=None):
        Thread.__init__(self)
        self.input_symbols = input_symbols
        self.output_symbols = output_symbols
        self.process_wrapper = process_wrapper
        self.channel = channel
        self.tmp_path = tmp_path

        self.lstar = None
        self.infered_automata = None

    def stop(self):
        """
        This method can be use to halt the current inference process
        """
        self._logger.info("Stopping the inference process")

        if self.lstar is not None:
            self.lstar.stop()
        if self.process_wrapper is not None:
            self.process_wrapper.stop(force=True)
            
    def run(self):
        self._logger.info("Configuring the inference process")

        # creates letters for each input symbols
        input_letters = [Letter(s) for s in self.input_symbols]

        try:
            # creates an abstraction layer on top of the channel to abstract and specialize received and sent messages
            abstraction_layer = AbstractionLayer(
                channel=self.channel,
                symbols=self.input_symbols + self.output_symbols
            )
            # creates a minimal adequat teacher
            mat = GenericMAT(
                abstraction_layer=abstraction_layer,
                process_wrapper=self.process_wrapper,
                cache_file_path=os.path.join(self.tmp_path, "cache.dump"))

            # configures the RandomWalkMethod that will be used as an equivalence query
            eqtests = RandomWalkMethod(
                knowledge_base=mat,
                input_letters=input_letters,
                max_steps=50000,
                restart_probability=0.7)

            # and finally, the LSTAR algorithm
            self.lstar = LSTAR(
                input_vocabulary=self.input_symbols,
                knowledge_base=mat,
                max_states=30,
                eqtests=eqtests)

            # starts the inference process and stores the infered grammar in a dot file (graphviz)
            self._logger.info("Starting the inference process...")
            start_ts = time.time()
            self.infered_automata = self.lstar.learn()
            duration = time.time() - start_ts
            self._logger.info("Inference process finished ({}s)".format(duration))
            
            
        finally:
            try:
                self.process_wrapper.stop(force=True)
            except Exception as e:
                self._logger.info("Encountered the following error while stoping the process wrapper: {}".format(e))

        
