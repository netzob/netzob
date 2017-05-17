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
import base64

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from flask import request
from flask_restplus import Namespace, Resource

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob_web.api.parameters import pagination_parameters
from netzob_web.extensions import projects_manager
from . import parameters

api = Namespace('misc',
                description="Various tools",
                path=projects_manager.PATH+'/misc')  # pylint: disable=invalid-name


@api.route('/parse_pcap')
class ParsePCAP(Resource):

    @api.expect(parameters.parse_pcap, validate = True)
    def post(self, pid):
        """Parse the specified PCAP

        Returns a list of messages that are embedded in the pcap
        """

        args = parameters.parse_pcap.parse_args(request)
        filename = args['filename']
        content = args['pcap']
        layer = args['layer']
        bpf_filter = args['bpf']

        content = ''.join(content.split(',')[1:])
        payload = base64.b64decode(content)

        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.parse_pcap(filename = filename, layer = layer, bpf_filter = bpf_filter, pcap_content = payload)

@api.route('/parse_raw')
class ParseRAW(Resource):

    @api.expect(parameters.parse_raw, validate = True)
    def post(self, pid):
        """Parse the specified RAW file

        Returns a list of messages that are embedded in the raw file
        """

        args = parameters.parse_raw.parse_args(request)
        filename = args['filename']
        content = args['raw']
        delimiter = bytes(args['delimiter'], 'utf-8')

        content = ''.join(content.split(',')[1:])
        payload = base64.b64decode(content)

        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.parse_raw(filename = filename, delimiter = delimiter, raw_content = payload)

    
