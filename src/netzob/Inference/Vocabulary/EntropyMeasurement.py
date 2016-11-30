# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
import math

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger


@NetzobLogger
class EntropyMeasurement(object):
    """This utility class exposes various methods related
    to Entropy. This measure can be usefull to identify
    encrypted and compressed chunk of data accross various messages.
    By entropy we refer to the Shanon's one.

    >>> import binascii
    >>> from netzob.all import *
    >>> fake_random_values = [b"00000906", b"00110906", b"00560902", b"00ff0901"]
    >>> messages = [RawMessage(binascii.unhexlify(val)) for val in fake_random_values]
    >>> [byte_entropy for byte_entropy in EntropyMeasurement.measure_entropy(messages)]
    [0.0, 2.0, 0.0, 1.5]

    
    In the following example, 1000 messages are generated under a simple specification.
    In the specification, 5 bytes are randomly generated. This specificity can easily be spoited by
    the entropy measurement as illustred below.
    
    
    >>> f1 = Field(b"hello ")
    >>> f2 = Field(Raw(nbBytes=5))
    >>> f3 = Field(b", welcome !")
    >>> s = Symbol(fields=[f1, f2, f3])
    >>> messages = [RawMessage(s.specialize()) for x in range(1000)]
    >>> bytes_entropy = [byte_entropy for byte_entropy in EntropyMeasurement.measure_entropy(messages)]
    >>> min(bytes_entropy[6:11]) > 7
    True


    You can also measure the entropy of the data that are accepeted by a specific field.

    >>> f1 = Field(Raw(nbBytes=2))
    >>> f2 = Field(Raw(nbBytes=(10, 20)))
    >>> f3 = Field(Raw(nbBytes=2))
    >>> s = Symbol(fields=[f1, f2, f3])
    >>> s.messages = [RawMessage(s.specialize()) for x in range(1000)]
    >>> bytes_entropy = [byte_entropy for byte_entropy in EntropyMeasurement.measure_values_entropy(f2.getValues())]
    >>> print(min(bytes_entropy[:10]) > 7)
    True
    
    
    """

    def __init__(self):
        pass

    @staticmethod
    def measure_entropy(messages):
        """This method returns the entropy of bytes found at each position of
        the messages.
        
        >>> [x for x in EntropyMeasurement.measure_entropy(messages=None)]
        Traceback (most recent call last):
        ...
        Exception: Messages cannot be None

        >>> from netzob.all import *
        >>> [x for x in EntropyMeasurement.measure_entropy(messages=[RawMessage()])]
        Traceback (most recent call last):
        ...
        Exception: At least two messages must be provided

        
        """
        if messages is None:
            raise Exception("Messages cannot be None")
        if len(messages) < 2:
            raise Exception("At least two messages must be provided")
    
        values = [m.data for m in messages]
        return EntropyMeasurement.measure_values_entropy(values)
            
    @staticmethod
    def measure_values_entropy(values):
        """This method returns the entropy of bytes found at each position of
        the specified values.
        
        >>> [x for x in EntropyMeasurement.measure_values_entropy(values=None)]
        Traceback (most recent call last):
        ...
        Exception: values cannot be None

        >>> from netzob.all import *
        >>> [x for x in EntropyMeasurement.measure_values_entropy(values=[])]
        Traceback (most recent call last):
        ...
        Exception: At least one value must be provided
        """

        if values is None:
            raise Exception("values cannot be None")
        if len(values) < 1 :
            raise Exception("At least one value must be provided")

        # computes longuest message
        longuest = max([len(value) for value in values])

        for i_byte in range(longuest):            

            dataset = []
            for value in values:
                try:
                    dataset.append(value[i_byte])
                except Exception:
                    pass

            yield EntropyMeasurement.__measure_entropy(dataset)
            
            
    @staticmethod
    def __measure_entropy(values):
        if values is None:
            raise Exception("values cannot be None")
        if len(values) < 1 :
            raise Exception("At least one value must be provided")

        entropy = 0
        for x in range(256):            
            p_x = float(values.count(x))/len(values)
            if p_x > 0:
                entropy += - p_x*math.log(p_x, 2)
                
        return entropy
                    
