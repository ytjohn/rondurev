__author__ = 'John'

from pysphere import VIServer
# from pycket.session import SessionManager
import logging


class VimHelper(object):
    """
    Making this seemed the easiest way to set my "vimserver" cbject at a
    semi-global level
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
        # TODO: Make sure sessionid exists
        """
        A test to make sure we're still connected to the VIM server. This
        could fail if the server
         has gone away or this server process has been restarted mid-session
         . Should be called before
         any other interaction with the server. Failure to do so could cause
          an exception error.
        """
        logging.debug("VimHelper.sessionid %s" % sessionid)
        try:
            if self.vimserver[sessionid].is_connected():
                logging.debug(
                    "VimHelper.IsConnected: yes, %s is connected" % sessionid)
                return True
            else:
                logging.debug(
                    "VimHelper.IsConnected: %s is no longer connected ("
                    "logged out)" % sessionid)
                return False
        except KeyError:
            logging.debug(
                "VimHelper.IsConnected: no, invalid session %s" % sessionid)
            return False
        except AttributeError:
            logging.debug(
                "VimHelper.IsConnected: no, %s not connected" % sessionid)
            return False

    def Authenticate(self, cred):
        """
        Connect Authenticate to the VIM server
        """
        logging.debug("VimHelper.Authenticate")
        sessionid = cred['sessionid']
        logging.debug("VimHelper.sessionid %s" % sessionid)
        self.vimserver[sessionid] = VIServer()
        # Catch exceptions
        try:
            logging.debug(
                'VimHelper.Authenticate: running the connect command')
            self.vimserver[sessionid].connect(cred['server'], cred['username'],
                cred['password'])
            logging.debug('VimHelper.Authenticate: successfully connected')
            return "authenticated"
        #except VIException, vierror:
        #    logging.warn(vierror)
        #   return vierror
        except Exception, vierror:
            logging.warn(vierror)
            return vierror

    def Disconnect(self, sessionid):
        if VimHelper.IsConnected(self, sessionid):
            VimHelper.vimserver[sessionid].disconnect()

    def Dummy(self, inf=0):
        """
        Just a quick dummy class for testing purposes.
        """
        return 5 + inf

    def ListVMs(self, sessionid):
        """
        Return a dictionary list of all VMs in search
        """
        # TODO: add options for searching

        logging.debug("VimHelper.ListVMs sessionid %s" % sessionid)
        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.ListVMs: not connected")
            return False

        vms = self.vimserver[sessionid].get_registered_vms()
        return vms

    def ServerType(self, sessionid):
        logging.debug("VimHelper.ServerType sessionid %s" % sessionid)
        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.ServerType: not connected")
            return False

        return VimHelper.vimserver[sessionid].get_server_type()

    def ApiVersion(self, sessionid):
        logging.debug("VimHelper.ApiVersion sessionid %s" % sessionid)
        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.ApiVersion: not connected")
            return False

        return VimHelper.vimserver[sessionid].get_api_version()

    def GetVM(self, sessionid, vmpath):
        logging.debug("VimHelper.ApiVersion sessionid %s" % sessionid)
        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.ApiVersion: not connected")
            return False

        vm = VimHelper.vimserver[sessionid].get_vm_by_path(vmpath)
        #TODO: what happens if the requested vm doesn't exist?
        return vm
