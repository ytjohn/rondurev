__author__ = 'John'

from pysphere import VIServer
# from pycket.session import SessionManager
import logging


class VimHelper(object):
    """
    A wrapper around the VIServer method for cyclone (but could work in many
     other instances).

     Goals:
        1. Doesn't rely on parent framework (cyclone/tornado/twisted)
        2. Nothing web/telnet specific, just data in/out
        3. Gracefully handle disconnects from VMWare server
    """

    # create a dictionary object for use by other objects in this class
    try:
        vimserver
    except NameError:
        vimserver = {}

    def IsConnected(self, sessionid):
        # TODO: Make sure sessionid exists
        """
        A test to make sure we're still connected to the VIM server. This
        could fail if the server has gone away or this server process has
        been restarted mid-session. Should be called before any other
        interaction with the server. Failure to do so could cause an
        exception error.

        Returns:
        True: Connected
        False: Not connected
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

        Arguments:
        cred {
            "sessionid": "current session",
            "server": "VIM server to connect to",
            "username": "username to connect as",
            "password": "password to connect with"
            }

        Returns:
        "authenticated" on sucess
        vierror on failure

        Some known returns values for vierror:
        "[InvalidLoginFault]: Cannot complete login due to an incorrect user
         name or password."
        "[Errno -2] Name or service not known"
        "[Errno -3] Temporary failure in name resolution"
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
        except Exception, vierror:
            logging.warn(vierror)
            return vierror

    def Disconnect(self, sessionid):
        """
        Disconnects current sessionid from the VMWare server. Returns nothing.
        """
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
        """
        Return the server type (vcenter, esx, exi)
        """

        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.ServerType: not connected")
            return False

        servertype = self.vimserver[sessionid].get_server_type()
        logging.debug("VimHelper.ServerType %s type: %s" % (sessionid,
            servertype))
        return servertype

    def ApiVersion(self, sessionid):
        """ Return server's API version, which pretty much coincides with
        the server version."""

        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.ApiVersion: not connected")
            return False

        apiversion = self.vimserver[sessionid].get_api_version()
        logging.debug("VimHelper.ApiVersion %s version: %s" % (sessionid,
                                                               apiversion))
        return apiversion

    def GetVM(self, sessionid, vmpath):
        """
        Returns a dictionary object describing a single VM.

        Arguments:
        sessionid: Current session
        vmpath: string of a virtual machine by datastore path.
        """
        logging.debug("VimHelper.ApiVersion sessionid %s" % sessionid)
        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.ApiVersion: not connected")
            return False

        vm = VimHelper.vimserver[sessionid].get_vm_by_path(vmpath)
        #TODO: what happens if the requested vm doesn't exist?
        return vm
