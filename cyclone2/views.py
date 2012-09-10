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

from cyclone2.utils import BaseHandler

import logging
from pycket.session import SessionMixin
from pycket.session import SessionManager

from vim import VimHelper


class TemplateFields(dict):
    """
    Helper class to make sure our template doesn't fail due to an invalid key
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        self[name] = value


class IndexHandler(BaseHandler, VimHelper):

    @cyclone.web.authenticated
    def get(self):

        session = SessionManager(self)
        sessionid = self.get_current_session()

        f = TemplateFields()
        f['username'] = self.session.get("user")
        f['servername'] = self.session.get("server")
        f['servertype'] = self.ServerType(sessionid)
        f['serverapi'] = self.ApiVersion(sessionid)
        self.render("index.html", fields=f)


class LogoutHandler(BaseHandler, VimHelper):
    def get(self):
        session = SessionManager(self)
        session.delete('authenticated')
        sessionid = self.get_current_session()
        self.Disconnect(sessionid)
        self.redirect("/auth/login")


class LoginHandler(BaseHandler, VimHelper):
    def get(self):
        sessionid = self.get_current_session()
        logging.debug("LoginHandler: sessionid %s" % sessionid)
        session = SessionManager(self)

        tpl_fields = TemplateFields()
        tpl_fields['post'] = False
        tpl_fields['server'] = session.get('server')
        tpl_fields['username'] = session.get('user')

        # using the next field makes it easier across logins
        tpl_fields['next'] = self.get_argument('next', '/')
        logging.debug("LoginHandler: next: %s" % tpl_fields['next'])

        logging.debug('LoginHandler: login page about to be rendered')
        self.render("login.html", fields=tpl_fields)

    def post(self):
        session = SessionManager(self)
        session.set('server', self.get_argument("server"))
        session.set('user', self.get_argument("username"))

        sessionid = self.get_current_session()

        tpl_fields = TemplateFields()
        tpl_fields['post'] = True
        tpl_fields['ip'] = self.request.remote_ip
        tpl_fields['server'] = self.get_argument("server")
        tpl_fields['username'] = self.get_argument("username")
        tpl_fields['next'] = self.get_argument('next', '/')

        # build this up to pass unto
        cred = {'server': self.get_argument('server'),
                'username': self.get_argument('username'),
                'password': self.get_argument('password'),
                'sessionid': sessionid
                }

        connect = VimHelper.Authenticate(self, cred)
        logging.debug("LoginHandler: result of VimHelper.Authenticate: %s" %
                      connect)
        if connect is "authenticated":
            session.set('authenticated', True)
            tpl_fields['vierror'] = connect
            self.redirect(tpl_fields['next'])
            return True
        else:
            tpl_fields['authenticated'] = False
            tpl_fields['vierror'] = connect

        logging.debug("LoginHandler: next: %s" % next)

        self.render("login.html", fields=tpl_fields)


class ListVMHandler(BaseHandler):
    """
    List all VMs - will add a filter later
    """

    @cyclone.web.authenticated
    def get(self):

        sessionid = self.get_current_session()
        vh = VimHelper()
        logging.debug("about to pull vms using sessionid %s" % sessionid)
        vms = vh.ListVMs(sessionid)
        f = TemplateFields()
        f['username'] = self.get_current_user()
        f['servername'] = self.session.get('server')
        f['servertype'] = vh.ServerType(sessionid)
        f['serverapi'] = vh.ApiVersion(sessionid)
        f['vmlist'] = vms

        self.render("listvms.html", fields=f)


class ShowVMHandler(BaseHandler):
    """
    Show a specific VM
    """
    @cyclone.web.authenticated
    def get(self, vmpath):

        logging.debug("ShowVMHandler: %s" % vmpath)
        vh = VimHelper()
        sessionid = self.get_current_session()

        f = TemplateFields()
        f['username'] = self.get_secure_cookie("user")
        f['servername'] = self.get_secure_cookie("server")
        f['servertype'] = vh.ServerType(sessionid)
        f['serverapi'] = vh.ApiVersion(sessionid)
        vm = vh.GetVM(sessionid, vmpath)
        f['vmstatus'] = vm.get_status()
        f['vmproperties'] = vm.get_properties()
        self.render("showvm.html", fields=f)


class LangHandler(BaseHandler):
    def get(self, lang_code):
        if lang_code in cyclone.locale.get_supported_locales():
            self.set_secure_cookie("lang", lang_code)

        self.redirect(self.request.headers.get("Referer",
                                               self.get_argument("next", "/")))
