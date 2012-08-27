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
import cyclone.locale
import cyclone.web
from pysphere import VIServer
from pysphere.resources.vi_exception import VIException

from twisted.internet import defer
from twisted.python import log
import cyclone2

from cyclone2.utils import BaseHandler, VIM
from cyclone2.utils import DatabaseMixin



class TemplateFields(dict):
    """Helper class to make sure our
        template doesn't fail due to an invalid key"""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        self[name] = value


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html", hello='world', awesome='bacon')
        # another option would be
        # fields = {'hello': 'world', 'awesome': 'bacon'}
        # self.render('index.html', **fields)

    def post(self):
        tpl_fields = TemplateFields()
        tpl_fields['post'] = True
        tpl_fields['ip'] = self.request.remote_ip
        # you can also fetch your own config variables defined in
        # cyclone2.conf using
        # self.settings.raw.get('section', 'parameter')
        # tpl_fields['mysql_host'] = self.settings.raw.get('mysql', 'host')
        self.render("post.html", fields=tpl_fields)

class LoginHandler(BaseHandler, VIM):
    def get(self):
        tpl_fields = TemplateFields()
        tpl_fields['post'] = False
        self.render("login.html", fields=tpl_fields)

    def post(self):
        tpl_fields = TemplateFields()
        tpl_fields['post'] = True
        tpl_fields['ip'] = self.request.remote_ip
        tpl_fields['server'] = self.get_argument("server")
        tpl_fields['username'] = self.get_argument("username")
        password = self.get_argument("password")

        cred = {'server': self.get_argument('server'),
                'username': self.get_argument('username'),
                'password': self.get_argument('password')
                }

        cyclone2.web.Application.vimserver = VIServer()
        # Catch exceptions
        try:
            cyclone2.web.Application.vimserver.connect(cred['server'], cred['username'], cred['password'])
            cyclone2.web.Application.authenticated = True

            tpl_fields['authenticated'] = True
        except VIException, vierror:
            tpl_fields['auth_error'] = vierror
            tpl_fields['authenticated'] = False
        except Exception, vierror:
            tpl_fields['auth_error'] = vierror
            tpl_fields['authenticated'] = False
           # raise

        #
        #except InvalidLoginFault:
        #    tpl_fields['auth_error'] = "Cannot complete login due to an incorrect user name or password."
        #    tpl_fields['authenticated'] = False

        # this doesn't work, back to the drawing board
        #        VimMixin.setup(cred)
        #        if VimMixin.vimserver is False:
        #            tpl_fields['authenticated'] = False
        #        else:
        #            tpl_fields['authenticated'] = True
        #            tpl_fields['servertype'] = VimMixin.vimserver.get_server_type()

        # tpl_fields['serverapi'] = VimMixin.vimserver.get_api_version()
        # vm1 = server.get_vm_by_name("puppet1-centos6")
        # tpl_fields['vmname'] = vm1.get_property('name')
        # tpl_fields['vmip'] = vm1.get_property('ip_address')

        self.render("login.html", fields=tpl_fields)

class ListVMHandler(BaseHandler, VIM):
    def get(self):
        f = TemplateFields()
        f['authenticated'] = cyclone2.web.Application.authenticated
        f['serverapi'] = cyclone2.web.Application.vimserver.get_api_version()
        self.render("listvms.html", fields=f)


class LangHandler(BaseHandler):
    def get(self, lang_code):
        if lang_code in cyclone.locale.get_supported_locales():
            self.set_secure_cookie("lang", lang_code)

        self.redirect(self.request.headers.get("Referer",
                                               self.get_argument("next", "/")))


class SampleSQLiteHandler(BaseHandler, DatabaseMixin):
    def get(self):
        if self.sqlite:
            response = self.sqlite.runQuery("select strftime('%Y-%m-%d')")
            self.write({"response": response})
        else:
            self.write("SQLite is disabled\r\n")


class SampleRedisHandler(BaseHandler, DatabaseMixin):
    @defer.inlineCallbacks
    def get(self):
        if self.redis:
            try:
                response = yield self.redis.get("foo")
            except Exception, e:
                log.msg("Redis query failed: %s" % str(e))
                raise cyclone.web.HTTPError(503)  # Service Unavailable
            else:
                self.write({"response": response})
        else:
            self.write("Redis is disabled\r\n")


class SampleMySQLHandler(BaseHandler, DatabaseMixin):
    @defer.inlineCallbacks
    def get(self):
        if self.mysql:
            try:
                response = yield self.mysql.runQuery("select now()")
            except Exception, e:
                log.msg("MySQL query failed: %s" % str(e))
                raise cyclone.web.HTTPError(503)  # Service Unavailable
            else:
                self.write({"response": response})
        else:
            self.write("MySQL is disabled\r\n")
