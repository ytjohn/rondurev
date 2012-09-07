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
        3. If connection is lost to VimHelper (even temporarily), command fails


    Other idea: pass sessionid, which makes things nicer for future issues
    """

    try:
        vimserver
    except NameError:
        vimserver = {}



    def IsConnected(self, sessionid):
        # TODO: Make sre sessionid exists
        logging.debug("VimHelper.sessionid %s" % sessionid)
        try:
            if self.vimserver[sessionid].is_connected():
                logging.debug("VimHelper.IsConnected: yes, %s is connected" % sessionid)
                return True
            else:
                logging.debug("VimHelper.IsConnected: %s is no longer connected (logged out)" % sessionid)
                return False
        except KeyError:
            logging.debug("VimHelper.IsConnected: no, invalid session %s" % sessionid)
            # TODO: make calling class handle logout
            return False
        except AttributeError:
            logging.debug("VimHelper.IsConnected: no, %s not connected" % sessionid)
            # TODO: make calling class handle logout
            return False

    def Authenticate(self, cred):
        # session = SessionManager(self)
        logging.debug("VimHelper.Authenticate")
        self.sessionid = cred['sessionid']
        logging.debug("VimHelper.sessionid %s" % self.sessionid)
        self.vimserver[self.sessionid] = VIServer()
        # Catch exceptions
        try:
            logging.debug('VimHelper.Authenticate: running the connect command')
            self.vimserver[self.sessionid].connect(cred['server'], cred['username'], cred['password'])
            logging.debug('VimHelper.Authenticate: successfully connected')
            return "authenticated"
        #except VIException, vierror:
        #    logging.warn(vierror)
        #   return vierror
        except Exception, vierror:
            logging.warn(vierror)
            return vierror

    def Dummy(self, inf=0):
        return 5 + inf

    def ListVMs(self, sessionid):
        logging.debug("VimHelper.ListVMs sessionid %s" % sessionid)
        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.ListVMs: not connected")
            return False

        vms = self.vimserver[sessionid].get_registered_vms()
        return vms

