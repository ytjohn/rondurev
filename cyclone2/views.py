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

from cyclone2.utils import BaseHandler
from cyclone2.utils import DatabaseMixin

import logging


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


class VIM(object):
    """
    Making this seemed the easiest way to set my "vimserver" cbject at a semi-global level
    I assume there is a better, even easier way.
    """
    vimserver = None

    def IsConnected(self):
        try:
            VIM.vimserver.is_connected()
            logging.debug("VIM.IsConnected: yes, connected")
            return True
        except AttributeError:
            logging.debug("VIM.IsConnected: no, not connected")
            self.clear_cookie("user")
            self.redirect("/auth/login")
            return False

    def Authenticate(self, cred):
        VIM.vimserver = VIServer()
        # Catch exceptions
        try:
            logging.debug('VIM.Authenticate: running the connect command')
            VIM.vimserver.connect(cred['server'], cred['username'], cred['password'])
            logging.debug('VIM.Authenticate: sucessfully connected')
            return "authenticated"
        except VIException, vierror:
            logging.warn(vierror)
            return vierror
        except Exception, vierror:
            logging.warn(vierror)
            return vierror

class IndexHandler(BaseHandler, VIM):

    @cyclone.web.authenticated
    def get(self):

        # Make sure we're connected
        logging.debug("IndexHandler: about to run VIM.IsConnected")
        VIM.IsConnected(self)
        logging.debug("IndexHandler: just ran VIM.IsConnected")

        f = TemplateFields()
        f['username']  = self.get_secure_cookie("user")
        f['servername'] = self.get_secure_cookie("server")
        f['servertype'] = VIM.vimserver.get_server_type()
        f['serverapi']  = VIM.vimserver.get_api_version()
        self.render("index.html", fields=f)




class LogoutHandler(BaseHandler, VIM):
    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("server")
        if VIM.IsConnected(self):
            VIM.vimserver.disconnect()
        self.redirect("/auth/login")

class LoginHandler(BaseHandler, VIM):
    def get(self):
        tpl_fields = TemplateFields()
        tpl_fields['post'] = False
        tpl_fields['server'] = ""
        tpl_fields['username'] = ""
        logging.debug('LoginHandler: login page about to be rendered')
        self.render("login.html", fields=tpl_fields)

    def post(self):
        tpl_fields = TemplateFields()
        tpl_fields['post'] = True
        tpl_fields['ip'] = self.request.remote_ip
        tpl_fields['server'] = self.get_argument("server")
        tpl_fields['username'] = self.get_argument("username")

        cred = {'server': self.get_argument('server'),
                'username': self.get_argument('username'),
                'password': self.get_argument('password')
                }

        connect = VIM.Authenticate(self, cred)
        logging.debug("LoginHandler: result of VIM.Authenticate: %s" % connect)
        if connect is "authenticated":
            self.set_secure_cookie("user", cred['username'])
            self.set_secure_cookie("server", cred['server'])
            tpl_fields['vierror'] = connect
            self.redirect("/")
            return True
        else:
            self.clear_cookie("user")
            tpl_fields['authenticated'] = False
            tpl_fields['vierror'] = connect

        self.render("login.html", fields=tpl_fields)

class ListVMHandler(BaseHandler, VIM):
    """
    List all VMs - will add a filter later
    """
    @cyclone.web.authenticated
    def get(self):

        # Make sure we're still connected

        logging.debug("ListVMHandler: about to run VIM.IsConnected")
        VIM.IsConnected(self)
        logging.debug("ListVMHandler: just ran VIM.IsConnected")

        f = TemplateFields()
        f['username']  = self.get_secure_cookie("user")
        f['servername'] = self.get_secure_cookie("server")
        f['servertype'] = VIM.vimserver.get_server_type()
        f['serverapi']  = VIM.vimserver.get_api_version()
        vmlist = VIM.vimserver.get_registered_vms()
        f['vmlist'] = vmlist

        self.render("listvms.html", fields=f)

class ShowVMHandler(BaseHandler, VIM):
    """
    List all VMs - will add a filter later
    """
    @cyclone.web.authenticated
    def get(self, vmpath):

        # vmpath = self.get_argument(vmpath)
        logging.debug("ShowVMHandler: %s" % vmpath)

        # Make sure we're still connected
        logging.debug("ShowVMHandler: about to run VIM.IsConnected")
        VIM.IsConnected(self)
        logging.debug("ShowVMHandler: just ran VIM.IsConnected")


        f = TemplateFields()
        f['username']  = self.get_secure_cookie("user")
        f['servername'] = self.get_secure_cookie("server")
        f['servertype'] = VIM.vimserver.get_server_type()
        f['serverapi']  = VIM.vimserver.get_api_version()
        vm = VIM.vimserver.get_vm_by_path(vmpath)
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



