#!/usr/bin/env python
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

# List subpackages to import with the current one
# see docs.python.org/2/tutorial/modules.html

from itertools import product
from typing import Callable, Any, Mapping, Iterable, Tuple
from typing import List, Dict  # noqa: F401


def partialclass(klass, *args, **keywords):
    """partialclass(klass, *args, **keywords) - new type with partialclass
    application of the given arguments and keywords.
    """
    def init_klass(self, *fargs, **fkeywords):
        kwargs = keywords.copy()
        kwargs.update(fkeywords)
        klass.__init__(self, *(args + fargs), **kwargs)

    def reduce_klass(self):
        # simply use base class type and update its __dict__
        return (klass, (), self.__dict__)

    klass_dict = klass.__dict__.copy()
    klass_dict.update({
        '__init__': init_klass,
        '__reduce__': reduce_klass
    })
    return type(klass.__name__, (klass,), klass_dict)


def typeSpecifier(klass: Callable[..., Any],
                  name_pattern: str,
                  defaults: Mapping[str, Iterable[Tuple[Any, str]]]):
    """
    Create class wrapper functions of `klass` with default parameters.
    The name of these class is also computed from a pattern

    :param: klass: the callable from which default values should be applied
    :type: klass: callable (i.e. a derivated AbstractType class)
    :param: name_pattern: the pattern name of the specialized type
    :type: name_pattern: str
    :param: defaults: a structure of default specialization values
    :type: defaults: a map of expected argument from klass with a list of
    specialization values (tuple of the value and the argument name for the
    pattern)

    >>> from netzob.all import *
    >>> (v1, v2) = (uint8be(0x80), int8be(-0x80))
    >>> v1, v2
    (128, -128)
    >>> v1 == v2
    False
    >>> next(Field(v1).specialize()) == next(Field(v2).specialize())
    True
    >>> (v1, v2) = (uint16be(0x1234), uint16le(0x3412))
    >>> next(Field(v1).specialize()) == next(Field(v2).specialize())
    True
    """

    # build the list of all named presets
    kw_pairs = []  # type: List[Iterable[Tuple[str, Any]]]
    for key, values in defaults.items():
        kw_pairs.append([(key, value) for value in values])

    # build the product of all possible combinations, grouped by attribute
    prod = product(*kw_pairs)
    kw_prod = map(dict, prod)  # type: Iterable[Dict[str, Tuple[str, Any]]]

    # build the partialclass functions (with their name)
    types = {}
    for kwargs in kw_prod:
        # process leave tuples (value, name) to generate type descriptions

        # type name: generate a unique name based on user's type specification
        kw_names = {k: name for (k, (_, name)) in kwargs.items()}
        name = name_pattern.format(**kw_names)

        # type values: create a default value structure from user's type spec
        kw_values = {k: v for (k, (v, _)) in kwargs.items()}
        types[name] = partialclass(klass, **kw_values)
    return types
