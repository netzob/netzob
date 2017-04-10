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
# | File contributors :                                                       |
# |       - Georges Bossert <gbossert (a) miskin.fr>                          |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from flask_restplus import reqparse

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+

new_message = reqparse.RequestParser()
new_message.add_argument('cid',
                        type = str,
                        required = True,
                        location = 'json',
                        help = "Capture ID")
new_message.add_argument('data',
                        type = str,
                        required = True,
                        location = 'json',
                        help = "Data transported by the message")
new_message.add_argument('date',
                        type = str,
                        required = False,
                        location = 'json',
                        help = "Message's date")
new_message.add_argument('source',
                        type = str,
                        required = False,
                        location = 'json',
                        help = "Name of the source of the message")
new_message.add_argument('destination',
                        type = str,
                        required = False,
                        location = 'json',
                        help = "Name of the destination of the message")
new_message.add_argument('messageType',
                        type = str,
                        required = True,
                        location = 'json',
                        help = "Type of message to create")
