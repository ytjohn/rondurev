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
from cyclone2.utils import DatabaseMixin

import logging
from pycket.session import SessionMixin
from pycket.session import SessionManager

from vim import VimHelper

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


#class deadVimHelper(object):
#    """
#    Making this seemed the easiest way to set my "vimserver" cbject at a semi-global level
#    I assume there is a better, even easier way.
#
#    TODO: Being replaced by VimHelper
#    """
#
#    vimserver = {}
#
#
#    def IsConnected(self):
#        session = SessionManager(self)
#        # sessiontest = SessionHelper(self)
#        self.sessionid = session.get('sessionid')
#        logging.debug("VimHelper.sessionid %s" % self.sessionid)
#        try:
#            VimHelper.vimserver[self.sessionid].is_connected()
#            logging.debug("VimHelper.IsConnected: yes, %s connected" % self.sessionid)
#            return True
#        except KeyError:
#            logging.debug("VimHelper.IsConnected: no, invalid session %s" % self.sessionid)
#            self.session.delete("user")
#            self.session.delete("server")
#            self.redirect("/auth/login")
#            return False
#        except AttributeError:
#            logging.debug("VimHelper.IsConnected: no, %s not connected" % self.sessionid)
#            self.session.delete("user")
#            self.session.delete("server")
#            self.redirect("/auth/login")
#            return False
#
#    def Authenticate(self, cred):
#        session = SessionManager(self)
#        logging.debug("VimHelper.Authenticate")
#        self.sessionid = session.get('sessionid')
#        logging.debug("VimHelper.sessionid %s" % self.sessionid)
#        VimHelper.vimserver[self.sessionid] = VIServer()
#        # Catch exceptions
#        try:
#            logging.debug('VimHelper.Authenticate: running the connect command')
#            VimHelper.vimserver[self.sessionid].connect(cred['server'], cred['username'], cred['password'])
#            logging.debug('VimHelper.Authenticate: successfully connected')
#            return "authenticated"
#        except VIException, vierror:
#            logging.warn(vierror)
#            return vierror
#        except Exception, vierror:
#            logging.warn(vierror)
#            return vierror

class IndexHandler(BaseHandler, VimHelper):

    @cyclone.web.authenticated
    def get(self):

        session = SessionManager(self)
        self.sessionid = session.get('sessionid')
        # Make sure we're connected
        logging.debug("IndexHandler: about to run VimHelper.IsConnected")

        # VimHelper.IsConnected(self.sessionid)
        logging.debug("IndexHandler: just ran VimHelper.IsConnected")
        # self.sessionid = self.get_current_session()

        f = TemplateFields()
        f['username']  = self.session.get("user")
        f['servername'] = self.session.get("server")
        #f['servertype'] = VimHelper.vimserver[self.sessionid].get_server_type()
        #f['serverapi']  = VimHelper.vimserver[self.sessionid].get_api_version()
        self.render("index.html", fields=f)




class LogoutHandler(BaseHandler, VimHelper):
    def get(self):
        sessionid = self.get_current_session()
        if VimHelper.IsConnected(self, sessionid):
            VimHelper.vimserver.disconnect()
        self.redirect("/auth/login")

class LoginHandler(BaseHandler, VimHelper):
    def get(self):
        self.sessionid = self.get_current_session()
        logging.debug("LoginHandler: sessionid %s" % self.sessionid)
        session = SessionManager(self)

        tpl_fields = TemplateFields()
        tpl_fields['post'] = False
        tpl_fields['server'] = session.get('server')
        tpl_fields['username'] = session.get('user')
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

        # build this up to pass unto
        cred = {'server': self.get_argument('server'),
                'username': self.get_argument('username'),
                'password': self.get_argument('password'),
                'sessionid': sessionid
                }

        connect = VimHelper.Authenticate(self, cred)
        logging.debug("LoginHandler: result of VimHelper.Authenticate: %s" % connect)
        if connect is "authenticated":
            tpl_fields['vierror'] = connect
            self.redirect("/")
            return True
        else:
            tpl_fields['authenticated'] = False
            tpl_fields['vierror'] = connect

        self.render("login.html", fields=tpl_fields)

class ListVMHandler(BaseHandler):
    """
    List all VMs - will add a filter later
    """
    # @cyclone.web.authenticated
    def get(self):

        sessionid = self.get_current_session()
        # Make sure we're still connected
        vh = VimHelper()
        #logging.debug("ListVMHandler: about to run VimHelper.IsConnected")
        #vh.IsConnected(sessionid)
        #logging.debug("ListVMHandler: just ran VimHelper.IsConnected")
        # sessionid = self.get_current_session()
        # vms = VimHelper.ListVMs(self, self.sessionid)
        vms = vh.ListVMs(sessionid)
        logging.debug("returned from gettting vms: %s" % vms)
        #vh.IsConnected()
        #vh.ListVMs(sessionid)
        f = TemplateFields()
        # f['username']  = self.get_secure_cookie("user")
        #f['servername'] = self.get_secure_cookie("server")
        #f['servertype'] = VimHelper.vimserver[self.sessionid].get_server_type()
        #f['serverapi']  = VimHelper.vimserver[self.sessionid].get_api_version()
        # vmlist = VimHelper.vimserver[self.sessionid].get_registered_vms()
        f['vmlist'] = vms

        self.render("listvms.html", fields=f)
        #logging.debug("ListVMHandler: about to do self.write")
        #self.write(vms)
        #logging.debug("ListVMHandler: just did self.write")

class ShowVMHandler(BaseHandler, VimHelper):
    """
    List all VMs - will add a filter later
    """
    @cyclone.web.authenticated
    def get(self, vmpath):

        # vmpath = self.get_argument(vmpath)
        logging.debug("ShowVMHandler: %s" % vmpath)

        # Make sure we're still connected
        logging.debug("ShowVMHandler: about to run VimHelper.IsConnected")
        VimHelper.IsConnected(self)
        logging.debug("ShowVMHandler: just ran VimHelper.IsConnected")
        self.sessionid = self.get_current_session()

        f = TemplateFields()
        f['username']  = self.get_secure_cookie("user")
        f['servername'] = self.get_secure_cookie("server")
        f['servertype'] = VimHelper.vimserver[self.sessionid].get_server_type()
        f['serverapi']  = VimHelper.vimserver[self.sessionid].get_api_version()
        vm = VimHelper.vimserver[self.sessionid].get_vm_by_path(vmpath)
        f['vmstatus'] = vm.get_status()
        f['vmproperties'] = vm.get_properties()

        self.render("showvm.html", fields=f)


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



