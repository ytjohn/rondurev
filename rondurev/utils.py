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

import cyclone.escape
import cyclone.redis
import cyclone.sqlite
import cyclone.web
import logging

from twisted.enterprise import adbapi

from pysphere import VIServer
from pycket.session import SessionMixin
from vim import VimHelper


class BaseHandler(cyclone.web.RequestHandler, SessionMixin):

    def get_current_user(self):

        # First, check if active
        active = self.session.get('authenticated')
        if not active:
            logging.debug("BaseHandler: session not active")
            return None

        # Next, check if there is a user name
        user = self.session.get('user')
        if not user:
            return None

        # pull and record the session id
        self.sessionid = self.get_current_session()
        logging.debug("BaseHandler: user %s, sessionid: %s" %
                      (user, self.sessionid))

        # now check to see if we're connected as well
        vh = VimHelper()
        if not vh.IsConnected(self.sessionid):
            logging.debug("BaseHandler: user %s session active, but not " \
                        "connected! (%s)" % (user, self.get_current_session()))
            return None

        return user

    def get_user_locale(self):
        lang = self.get_secure_cookie("lang")
        if lang:
            return cyclone.locale.get(lang)

    def get_current_session(self):
        """
        Returns current session ID, based on secure cookie
        """
        # pycket hard codes "PYCKET_ID" in place.
        # TODO: Plan to update pycket to configure SESSION_NAME_ID
        # and update hard-coded PYCKET_ID below
        return self.get_secure_cookie('PYCKET_ID')


class DatabaseMixin(object):
    mysql = None
    redis = None
    sqlite = None

    @classmethod
    def setup(self, settings):
        conf = settings.get("sqlite_settings")
        if conf:
            DatabaseMixin.sqlite = cyclone.sqlite.InlineSQLite(conf.database)

        conf = settings.get("redis_settings")
        if conf:
            DatabaseMixin.redis = cyclone.redis.lazyConnectionPool(
                            conf.host, conf.port, conf.dbid, conf.poolsize)

        conf = settings.get("mysql_settings")
        if conf:
            DatabaseMixin.mysql = adbapi.ConnectionPool("MySQLdb",
                            host=conf.host, port=conf.port, db=conf.database,
                            user=conf.username, passwd=conf.password,
                            cp_min=1, cp_max=conf.poolsize,
                            cp_reconnect=True, cp_noisy=conf.debug)
