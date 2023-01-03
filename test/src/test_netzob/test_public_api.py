# !/usr/bin/python
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
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports
# +---------------------------------------------------------------------------+
import inspect
import ast
import unittest

# +---------------------------------------------------------------------------+
# | Local application imports
# +---------------------------------------------------------------------------+
from netzob.all import *
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition
from netzob.Model.Grammar.States.AbstractState import AbstractState
from netzob.Simulator.AbstractChannel import AbstractChannel
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractChecksum import AbstractChecksum
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractHash import AbstractHash
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractHMAC import AbstractHMAC
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator


def get_decorators(cls):
    target = cls
    decorators = {}

    def visit_FunctionDef(node):
        decorators[node.name] = []
        for n in node.decorator_list:
            name = ''
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id

            decorators[node.name].append(name)

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_FunctionDef
    node_iter.visit(ast.parse(inspect.getsource(target)))
    return decorators


class test_public_api(unittest.TestCase):

    def test_annotations(self):
        is_failure = False
        log_failures = []
        log_annotations = []

        # One-line used to produce the list: grep -nir public_api src/netzob/| awk -F":" '{ print $1}' |uniq|grep -v .pyc|awk -F".py" '{ print $1}' |awk -F"/" '{print $NF}' | sort |xargs echo
        public_classes = [
            AbstractChannel, AbstractChecksum, AbstractField, AbstractHash, AbstractHMAC, AbstractionLayer, AbstractState, AbstractTransition, AbstractType, Actor, Agg, Alt, Automata, BitArray, CloseChannelTransition, Data, DebugChannel, DomainMutator, EmptySymbol, CustomEthernetChannel, Field, Preset, HexaString, Integer, IPChannel, IPv4, Memory, OpenChannelTransition, Opt, Padding, Protocol, Raw, RawEthernetChannel, CustomIPChannel, Repeat, Size, SSLClient, State, String, Symbol, TCPClient, TCPServer, Timestamp, Transition, UDPClient, UDPServer, UnknownSymbol, Value
        ]

        for public_class in public_classes:
            decorated_members = get_decorators(public_class)

            # First: find all public API methods
            public_api_members = []
            for member, decorators in decorated_members.items():
                for decorator in decorators:
                    if decorator == "public_api":
                        public_api_members.append(member)
                        break

            # Then: verify existence of type annotation for each public API
            interesting_members = inspect.getmembers(public_class, inspect.isfunction)
            for (method_name, method_object) in interesting_members:
                if method_name in public_api_members:
                    if callable(method_object):
                        signature = inspect.signature(method_object)

                        for param_name, param in signature.parameters.items():
                            if param_name != 'self':
                                if param.annotation == inspect.Parameter.empty:
                                    is_failure = True
                                    log_failures.append("In class '{}', method '{}', parameter '{}' has no type annotation".format(public_class.__name__, method_name, param_name))
                                else:
                                    log_annotations.append("In class '{}', method '{}', parameter '{}' has type annotation: '{}'".format(public_class.__name__, method_name, param_name, param.annotation))

                        if signature.return_annotation == inspect.Parameter.empty:
                            is_failure = True
                            log_failures.append("In class '{}', method '{}', return value has no type annotation".format(public_class.__name__, method_name))
                        else:
                            log_annotations.append("In class '{}', method '{}', return value has type annotation: '{}'".format(public_class.__name__, method_name, signature.return_annotation))

            # For public properties, just verify that they have a proper documentation
            interesting_members = inspect.getmembers(public_class, inspect.isdatadescriptor)
            for (method_name, method_object) in interesting_members:
                if method_name in public_api_members:
                    if method_object.__doc__ is None:
                            is_failure = True
                            log_failures.append("In class '{}', property '{}' has no doc".format(public_class.__name__, method_name))

        expected_log_annotations = [
            "In class 'Symbol', method 'specialize', parameter 'presets' has type annotation: 'typing.Dict[typing.Union[str, netzob.Model.Vocabulary.Field.Field], typing.Union[bitarray.bitarray, bytes, netzob.Model.Vocabulary.Types.AbstractType.AbstractType]]'",
            "In class 'Symbol', method 'specialize', parameter 'fuzz' has type annotation: '<class 'netzob.Fuzzing.Fuzz.Fuzz'>'",
            "In class 'Symbol', method 'specialize', parameter 'memory' has type annotation: '<class 'netzob.Model.Vocabulary.Domain.Variables.Memory.Memory'>'"
        ]

        #self.assertTrue(log_annotations == expected_log_annotations)

        #print("List of parameter type annotations:\n  [+] {}".format("\n  [+] ".join(log_annotations)))
        #print(repr(log_annotations))

        if is_failure is True:
            # TODO: remove comment
            #self.fail("Type annotation verification failure. Failures:\n  [+] {}".format("\n  [+] ".join(log_failures)))
            print("Type annotation verification failure. Failures:\n  [+] {}".format("\n  [+] ".join(log_failures)))
