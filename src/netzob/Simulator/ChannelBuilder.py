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
#|       - Alexandre Pigné <alexandre.pigne (a) amossys.fr>                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
try:
    from typing import Mapping
except ImportError:
    pass

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger, public_api


@NetzobLogger
class ChannelBuilder(object):
    """This builder pattern enables the creation of any kind of
    :class:`~netzob.Simulator.AbstractChannel.AbstractChannel`.

    Initialize the builder context by providing the kind of object to build.

    Sub classes should use specific setter methods (i.e. ``set_key`` to set
    ``key`` attribute in final object) to handle the setting of attributes
    in a specific way. Otherwise, the named attribute of
    :meth:`~ChannelBuilder.set` will be used.

    Two data-stores are available in a ``ChannelBuilder`` instance:

    * :attr:`~.ChannelBuilder.attrs`:
      a map between argument name in __init__ method of the channel,
    * :attr:`~.ChannelBuilder.after_init_callbacks`:
      a list of callback to be called **after** __init__ method call.

    :param kind: the kind of object to build
    :type kind: an AbstractChannel class
    """

    @public_api
    def __init__(self, kind):
        self.kind = kind  # type: Type[AbstractChannel]
        self.attrs = {}
        self.after_init_callbacks = []

    @public_api
    def set(self, key, value):
        """
        Set a named parameter that will be passed to :meth:`build`.

        :param key: a named parameter expected by :meth:`self.kind.__init__`
        :type key: str, required
        :param value: any object
        :type value: object, required
        """
        setter_name = "set_{}".format(key)
        setter = getattr(self, setter_name, None)
        if callable(setter):
            setter(value)
        else:
            self._logger.debug("The setter '{}' is not provided by {}"
                               .format(setter_name, type(self).__name__))
        return self

    @public_api
    def set_map(self, mapping):
        # type: (Mapping) -> ChannelBuilder
        """
        Set a mapping of key-value named parameters.

        It is a shortcut method to address multiple key-value pairs successively.
        See :meth:`set` for details.

        :param mapping: A key-value parameter mapping
        :type mapping: ~typing.Mapping[str, ~typing.Any], required
        """
        for key, value in mapping.items():
            self.set(key, value)
        return self

    def set_timeout(self, value):
        """
        Default setter of timeout attribute
        """
        self.attrs['timeout'] = value

    @public_api
    def build(self):
        """
        Generate the final object instance using gathered information.
        """
        channel = self.kind(**self.attrs)
        for cb in self.after_init_callbacks:
            cb(channel)
        return channel
