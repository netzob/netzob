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
from flask import request
from flask_restplus import Namespace, Resource

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob_web.api.parameters import pagination_parameters
from netzob_web.extensions import projects_manager
from . import parameters

api = Namespace('captures',
                description="Handle captures of your protocol",
                path=projects_manager.PATH+'/captures')  # pylint: disable=invalid-name


@api.route('/')
class Captures(Resource):

    @api.expect(pagination_parameters, validate = True)
    def get(self, pid):
        """List all captures

        Returns a list of captures starting from ``offset`` limited by ``limit`` parameter.
        """

        args = pagination_parameters.parse_args(request)
        limit = args['limit']
        offset = args['offset']        
        
        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.get_captures(limit = limit, offset = offset)

    @api.expect(parameters.new_capture, validate = True)
    def post(self, pid):
        """Create a new capture."""

        args = parameters.new_capture.parse_args(request)
        name = args['name']
        date = args['date']
        
        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.add_capture(name = name, date = date)

@api.route('/<string:cid>/')
class CaptureByID(Resource):

    def get(self, pid, cid):
        """Fetch a capture by its ID"""

        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.get_capture(cid = cid)

    def delete(self, pid, cid):
        """Delete a capture by its ID"""
        
        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.capture_message(cid = cid)

@api.route('/<string:cid>/messages')
class CaptureByID(Resource):

    @api.expect(pagination_parameters, validate = True)    
    def get(self, pid, cid):
        """Fetch all a capture by its ID"""

        args = pagination_parameters.parse_args(request)
        limit = args['limit']
        offset = args['offset']        
        
        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.get_messages_in_capture(cid, limit = limit, offset = offset)
