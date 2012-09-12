# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import cyclone.locale
import cyclone.web

from cyclone2 import views
from cyclone2 import config
from cyclone2.utils import DatabaseMixin

import logging

from pycket.session import SessionMixin


class Application(cyclone.web.Application):
    def __init__(self, config_file):
        handlers = [
            (r"/",              views.IndexHandler),
            (r"/auth/login",    views.LoginHandler),
            (r"/auth/logout",   views.LogoutHandler),
            (r"/lang/(.+)",     views.LangHandler),
            (r"/vm/list",       views.ListVMHandler),
            (r"/vm/show/(.*)",  views.ShowVMHandler),
            (r"/cluster/list",  views.ShowClusters),
            (r"/task/list",     views.ShowTasksHandler),
        ]

        settings = config.parse_config(config_file)
        if settings.get("debug"):
            logging.basicConfig(level=logging.DEBUG)
            logging.debug("Application debug logging enabled")

        # Initialize localesK
        locales = settings.get("locale_path")
        if locales:
            cyclone.locale.load_gettext_translations(locales, "cyclone2")

        settings['pycket'] = {
            'engine': 'redis',
            'storage': {
                'host': 'localhost',
                'port': 6379,
                'db_sessions': 10,
                'db_notifications': 11
            }
        }

        # Set up database connections
        DatabaseMixin.setup(settings)

        settings["login_url"] = "/auth/login"
        #settings["autoescape"] = None

        cyclone.web.Application.__init__(self, handlers, **settings)
