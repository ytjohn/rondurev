__author__ = 'John'

from pysphere import VIServer
# from pycket.session import SessionManager
import logging

class VimHelper(object):
    """
    Making this seemed the easiest way to set my "vimserver" cbject at a semi-global level
    I assume there is a better, even easier way.

    Expectations:
        1. pycket sessions are in place and working
        2. The current session id is stored in the sessionid key
            ex: session.get('sessionid')
        3. If connection is lost to VimHelper (even temporarily), command fails


    Other idea: pass sessionid, which makes things nicer for future issues
    """

    def __init__(self):
        self.vimserver = {}


    def IsConnected(self, sessionid):
        # session = SessionManager(self)
        # sessiontest = SessionHelper(self)
        # self.sessionid = session.get('sessionid')
        # TODO: Make sre sessionid exists
        logging.debug("VimHelper.sessionid %s" % self.sessionid)
        try:
            self.vimserver[self.sessionid].is_connected()
            logging.debug("VimHelper.IsConnected: yes, %s connected" % self.sessionid)
            return True
        except KeyError:
            logging.debug("VimHelper.IsConnected: no, invalid session %s" % self.sessionid)
            # TODO: make calling class handle logout
            # self.session.delete("user")
            # self.session.delete("server")
            # self.redirect("/auth/login")
            return False
        except AttributeError:
            logging.debug("VimHelper.IsConnected: no, %s not connected" % self.sessionid)
            # TODO: make calling class handle logout
            # self.session.delete("user")
            # self.session.delete("server")
            # self.redirect("/auth/login")
            return False

    def Authenticate(self, cred):
        session = SessionManager(self)
        logging.debug("VimHelper.Authenticate")
        self.sessionid = session.get('sessionid')
        logging.debug("VimHelper.sessionid %s" % self.sessionid)
        self.vimserver[self.sessionid] = VIServer()
        # Catch exceptions
        try:
            logging.debug('VimHelper.Authenticate: running the connect command')
            self.vimserver[self.sessionid].connect(cred['server'], cred['username'], cred['password'])
            logging.debug('VimHelper.Authenticate: successfully connected')
            return "authenticated"
        except VIException, vierror:
            logging.warn(vierror)
            return vierror
        except Exception, vierror:
            logging.warn(vierror)
            return vierror

    def Dummy(self, inf=0):
        return 5 + inf

    def ListVMs(self, sessionid):
        logging.debug("VimHelper.ListVMs sessionid %s" % sessionid)
        if not VimHelper.IsConnected(self):
            logging.debug("VimHelper.ListVMs: not connected")
            return False

        vms = self.vimserver[sessionid].get_registered_vms()
        return vms
