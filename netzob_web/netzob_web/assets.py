# -*- coding: utf-8 -*-
"""Application assets."""
from flask_assets import Bundle, Environment

css = Bundle(
    'libs/bootstrap/dist/css/bootstrap.css',
    'css/style.css',
    'libs/datatables.net-bs/css/dataTables.bootstrap.min.css',
    'libs/datatables.net-select-bs/css/select.bootstrap.min.css',
    filters='cssmin',
    output='public/css/common.css'
)

js = Bundle(
    'libs/jquery/dist/jquery.js',
    'libs/bootstrap/dist/js/bootstrap.js',
    'js/plugins.js',
    'js/netzob-frontend.js',    
    'libs/datatables.net/js/jquery.dataTables.min.js',
    'libs/datatables.net-bs/js/dataTables.bootstrap.min.js',
    'libs/datatables.net-select/js/dataTables.select.min.js',
    'libs/jpillora/jquery.rest/dist/1/jquery.rest.min.js',
    'js/netzob-api.js',    
    filters='jsmin',
    output='public/js/common.js'
)

assets = Environment()

assets.register('js_all', js)
assets.register('css_all', css)
