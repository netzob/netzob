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
from flask_restplus import Namespace, Resource, fields

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob_web.api.parameters import pagination_parameters
from netzob_web.extensions import projects_manager
from . import parameters

api = Namespace('symbols',
                description="Handle symbols of your protocol",
                path=projects_manager.PATH+'/symbols')  # pylint: disable=invalid-name

@api.route('/')
class Symbols(Resource):

    @api.expect(pagination_parameters, validate = True)    
    def get(self, pid):
        """List all symbols.

        Returns a list of symbols starting from ``offset`` limited by ``limit`` parameter.
        """

        args = pagination_parameters.parse_args(request)
        limit = args['limit']
        offset = args['offset']
        
        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.get_symbols(limit = limit, offset = offset)

    @api.expect(parameters.new_symbol, validate = True)
    def post(self, pid):
        """Create a new symbol."""

        args = parameters.new_symbol.parse_args(request)
        
        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.add_symbol(name = args['name'])


@api.route('/<string:sid>/')
class SymbolByID(Resource):

    def get(self, pid, sid):
        """Fetch a symbol by its id"""
        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.get_symbol(sid)

    @api.expect(parameters.new_symbol, validate = True)
    def patch(self, pid, sid):
        """Patch symbol details by its id"""

        args = parameters.new_symbol.parse_args(request)

        new_name = None
        if "name" in args.keys():
            new_name = args["name"]
            
        new_description = None
        if "description" in args.keys():
            new_description = args["description"]
        
        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.update_symbol(sid, name = new_name, description = new_description)

    def delete(self, pid, sid):
        """Delete a symbol by its id"""

        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.delete_symbol(sid)

@api.route('/<string:sid>/specialize')
class SymbolSpecialize(Resource):

    def get(self, pid, sid):
        """Specialize a symbol by its id"""

        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.specialize_symbol(sid)

@api.route('/<string:sid>/cells')
class SymbolCells(Resource):

    def get(self, pid, sid):
        """Fetches symbol's cells by its id"""

        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.get_symbol_cells(sid)
    
@api.route('/<string:sid>/split_align')
class SymbolSplitAlign(Resource):

    def get(self, pid, sid):
        """Executes an alignment process on the specified symbol"""

        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.symbol_split_align(sid)


@api.route('/<string:sid>/messages')
class SymbolMessages(Resource):

    @api.expect(pagination_parameters, validate = True)    
    def get(self, pid, sid):
        """Fetch symbol's messages by its id"""

        args = pagination_parameters.parse_args(request)
        limit = args['limit']
        offset = args['offset']
        
        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.get_symbol_messages(sid, limit = limit, offset = offset)

    
@api.route('/<string:sid>/messages/<string:mid>')
class SymbolMessage(Resource):

    def delete(self, pid, sid, mid):
        """Remove a message from a symbol"""

        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.remove_message_from_symbol(sid, mid)
    

    def put(self, pid, sid, mid):
        """Append a message to a symbol"""

        
        
        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.add_message_in_symbol(sid, mid)
    

@api.route('/<string:sid>/fields')
class SymbolFields(Resource):

    @api.expect(pagination_parameters, validate = True)
    def get(self, pid, sid):
        """Fetch symbol's fields by its id"""

        args = pagination_parameters.parse_args(request)
        limit = args['limit']
        offset = args['offset']        

        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.get_symbol_fields(sid, limit = limit, offset = offset)
    
@api.route('/<string:sid>/field/<string:fid>')
class SymbolField(Resource):

    def delete(self, pid, sid, fid):
        """Remove a field from a symbol"""

        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.remove_field_from_symbol(sid, fid)

    @api.expect(parameters.add_field, validate = True)
    def put(self, pid, sid, fid):
        """Append a field to a symbol"""

        args = parameters.add_field.parse_args(request)
        
        fid_before_new = None
        if "fid_before_new" in args.keys():
            fid_before_new = args['fid_before_new']
        
        project_handler = projects_manager.get_project_handler(pid)
        return project_handler.add_field_in_symbol(sid, fid, fid_before_new = fid_before_new)


    
    
