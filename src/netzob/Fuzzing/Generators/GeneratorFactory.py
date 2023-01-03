# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
# |             ANSSI,   https://www.ssi.gouv.fr                              |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# |       - Rémy Delion <remy.delion (a) amossys.fr>                          |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
#import randomstate
import pkgutil
from typing import Iterable
try:
    import typing
except ImportError:
    pass
from itertools import repeat, starmap

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.WrapperGenerator import WrapperGenerator


class GeneratorFactory(object):
    """The :class:`GeneratorFactory` is a factory that creates specific
    instances of the class :class:`Generator`.

    >>> g = GeneratorFactory.buildGenerator(seed=1, minValue=0, maxValue=255, bitsize=8)
    >>> type(g)
    <class 'netzob.Fuzzing.Generators.XorShiftGenerator.XorShiftGenerator'>
    >>> next(g)
    0
    >>> next(g)
    173

    >>> g = GeneratorFactory.buildGenerator('xorshift', minValue=0, maxValue=1<<16, seed=1)
    >>> type(g)
    <class 'netzob.Fuzzing.Generators.XorShiftGenerator.XorShiftGenerator'>
    >>> next(g)
    0

    >>> g = GeneratorFactory.buildGenerator('determinist', seed=0, minValue=10, maxValue=20, bitsize=8, signed=True)
    >>> type(g)
    <class 'netzob.Fuzzing.Generators.DeterministGenerator.DeterministGenerator'>
    >>> next(g)
    33

    >>> g = GeneratorFactory.buildGenerator('determinist', seed=0, minValue=10, maxValue=20, bitsize=8, signed=True)
    >>> type(g)
    <class 'netzob.Fuzzing.Generators.DeterministGenerator.DeterministGenerator'>
    >>> next(g)
    33

    >>> from itertools import cycle
    >>> g = GeneratorFactory.buildGenerator(cycle(range(4, 12)))
    >>> type(g)
    <class 'netzob.Fuzzing.Generators.WrapperGenerator.WrapperGenerator'>
    >>> next(g)
    4

    >>> import random
    >>> g = GeneratorFactory.buildGenerator(repeatfunc(random.random), minValue=0, maxValue=1<<16)
    >>> type(g)
    <class 'netzob.Fuzzing.Generators.WrapperGenerator.WrapperGenerator'>
    >>> isinstance(next(g), int)
    True

    """

    @staticmethod
    def buildGenerator(generator='xorshift', seed=1, **kwargs):
        # """
        # Provide a generator using either a name
        # (compatible with :class:`randomstate.Randomstate`), an :class:`Iterable
        # <typing.Iterable>` object or a :class:`Generator <typing.Generator>`
        # function with no argument.

        # :param generator: The generator we want to create.
        # :type generator: str, callable or generator function
        # """

        """
        Provide a generator using an :class:`Iterable
        <typing.Iterable>` object or a :class:`Generator <typing.Generator>`
        function with no argument.

        :param generator: The generator we want to create.
        :type generator: str, callable or generator function
        """

        # Check if the generator is already instantiated
        if isinstance(generator, Generator):
            return generator

        # Check if the generator is a string corresponding to a number generator name
        elif isinstance(generator, str):

            # # Check if we want a number generator from the randomstate.prng module
            # for importer, modname, ispkg in pkgutil.iter_modules(randomstate.prng.__path__):
            #     if generator == modname:
            #         prng_module = __import__('randomstate.prng', globals(), locals(), [modname], 0)
            #         generator_module = prng_module.__dict__[modname]
            #         generator_class = generator_module.RandomState
            #         generator_instance = generator_class(seed=seed)
            #         return WrapperGenerator(repeatfunc(generator_instance.random_sample), **kwargs)

            # Else check if we want a sub-generator from this Generator package
            for subclass in Generator.__subclasses__():
                if generator == subclass.name:
                    return subclass(seed=seed, **kwargs)

        # Check if the generator is already an iterator
        elif isinstance(generator, Iterable):
            return WrapperGenerator(iter(generator), **kwargs)

        raise ValueError("Generator not supported: '{}'".format(generator))


def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.

    Example:  ``repeatfunc(random.random)``
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))
