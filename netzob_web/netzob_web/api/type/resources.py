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

api = Namespace('types',
                description="Handle types of your domains",
                path=projects_manager.PATH+'/types')  # pylint: disable=invalid-name


@api.route('/')
class Types(Resource):

    @api.expect(pagination_parameters, validate = True)
    def get(self, pid):
        """List all types

        Returns a list of data types starting from ``offset`` limited by ``limit`` parameter.
        """

        args = pagination_parameters.parse_args(request)
        limit = args['limit']
        offset = args['offset']        
        
        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.get_datatypes(limit = limit, offset = offset)


@api.route('/<string:tid>/')
class TypeByID(Resource):

    def get(self, pid, tid):
        """Fetch a type by its ID"""

        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.get_datatype(tid = tid)

    def delete(self, pid, tid):
        """Delete a type"""

        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.delete_datatype(tid = tid)

@api.route('/ascii')
class ASCIITypes(Resource):

    @api.expect(parameters.new_ascii, validate = True)
    def post(self, pid):
        """Create a new ASCII type."""
        
        args = parameters.new_ascii.parse_args(request)
        value = args['value']
        nb_char_min = args['nb_char_min'] 
        nb_char_max = args['nb_char_max']

        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.create_type_ascii(value = value, nb_char_min = nb_char_min, nb_char_max = nb_char_max)
    
@api.route('/raw')
class RawTypes(Resource):

    @api.expect(parameters.new_raw, validate = True)
    def post(self, pid):
        """Create a new RAW datatype."""
        
        args = parameters.new_raw.parse_args(request)
        value = args['value']
        nb_byte_min = args['nb_byte_min'] 
        nb_byte_max = args['nb_byte_max']

        project_handler = projects_manager.get_project_handler(pid)        
        return project_handler.create_type_raw(value = value, nb_byte_min = nb_byte_min, nb_byte_max = nb_byte_max)
