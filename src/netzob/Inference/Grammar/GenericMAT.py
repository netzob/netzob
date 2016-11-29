# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <gbossert (a) miskin.fr>                          |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import time
import logging

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from pylstar.ActiveKnowledgeBase import ActiveKnowledgeBase
from pylstar.Letter import Letter
from pylstar.Word import Word

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Common.Models.Simulator.Channels.AbstractChannel import ChannelDownException
from netzob.Common.Models.Vocabulary.EmptySymbol import EmptySymbol


@NetzobLogger
class GenericMAT(ActiveKnowledgeBase):
    """Generic Minimal Adequat Teacher.    

    >>> import thread
    >>> from netzob.all import *
    >>> from pylstar.Letter import Letter
    >>> from pylstar.Word import Word
    >>> server_channel = TCPServer(localIP="127.0.0.1", localPort=8888)
    >>> id_thread = thread.start_new_thread(server_channel.open, ())
    >>> client_channel = TCPClient(remoteIP="127.0.0.1", remotePort=8888)
    >>> aLayer = AbstractionLayer(client_channel, [])
    >>> mat = GenericMAT(aLayer)
    >>> mat.start_target()
    >>> s_a = Symbol(fields=[Field("a")])
    >>> s_b = Symbol(fields=[Field("b")])
    >>> s_c = Symbol(fields=[Field("c")])
    >>> word = Word([Letter(s_a), Letter(s_b), Letter(s_c)])
    >>> output = mat.submit_word(word)
    >>> mat.stop_target()
    >>> server_channel.close()
    >>> print len(output)
    3
    >>> print str(output.letters[0])
    EmptyLetter
    
    
    """
    

    def __init__(self, abstraction_layer, process_wrapper=None, cache_file_path = None, submitted_word_cb = None):
        super(GenericMAT, self).__init__(cache_file_path = cache_file_path)
        self.abstraction_layer = abstraction_layer
        self.process_wrapper = process_wrapper
        self.submitted_word_cb = submitted_word_cb
        

    def start_target(self):
        """This method opens the channel"""
        
        self.stop_target()

        self.process_wrapper.start()
        
        for nb_attempt in xrange(10):            
            if self.process_wrapper.is_ready():
                break
            time.sleep(1)

        # we also try multiple times to open the channel with the target
        channel_is_open = False
        for nb_attemp in xrange(10):
            try:
                self.abstraction_layer.openChannel()
                channel_is_open = True
                break
            except Exception as e:
                logging.warn("Target is not yet ready (channel cannot be opened): {}".format(e))
                time.sleep(1)

        if not channel_is_open:
            raise Exception("Cannot open a channel with the target")        

    def stop_target(self):
        """This method stops the channel"""
        self.abstraction_layer.closeChannel()
        self.abstraction_layer.reset()

        if self.process_wrapper is not None:
            self.process_wrapper.stop()

    def submit_word(self, word):
        """This method return the Word produced by the target while submited the specified word"""
        output_letters = []
        
        for letter in word.letters:
            symbols = letter.symbols
            try:
                output_symbols = []
                for symbol in symbols:
                    try:
                        self.abstraction_layer.writeSymbol(symbol)
                    except ChannelDownException, e:
                        self._logger.debug("Channel is Down")
                    (curr_output_symbols, data) = self.abstraction_layer.readSymbols()
                    output_symbols.extend(curr_output_symbols)
                output_letters.append(Letter(symbols=output_symbols))
            except Exception, e:            
                self._logger.fatal("An error occurred : {}".format(e))
                output_letters.append(Letter(symbols=[EmptySymbol()]))


        for i in xrange(len(word.letters)):
            input_letter = word.letters[i]
            output_letter = output_letters[i]
            input_str = "None"
            output_str = "None"
            
            if input_letter.symbols is not None:
                input_str = ','.join([s.name for s in input_letter.symbols])

            if output_letter.symbols is not None:
                output_str = ','.join([s.name for s in output_letter.symbols])
                
            self._logger.debug(">>> {}".format(input_str))
            self._logger.debug("<<< {}".format(output_str))

        self.write_cache()

        if self.submitted_word_cb is not None:
            try:
                self.submitted_word_cb(word.letters, output_letters)
            except Exception as e:
                self._logger.error("Error encountered while executed submitted_word_cb: {}".format(e))

    
        return Word(output_letters, normalize=False)


            
    
