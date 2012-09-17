__author__ = 'John'

from pysphere import VIServer
from pysphere import VIException

# from pycket.session import SessionManager
import logging
import uuid


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

    try:
        taskid
    except NameError:
        taskid = {}

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
                status = self.vimserver[sessionid].keep_session_alive()
                logging.debug("IsConnected: alive? %s" % status)
                return status
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
        except VIException, vierror:
            logging.debug("VimHelper.IsConnected: VIException: %s (%s)" % (
                vierror, sessionid))
        except Exception, vierror:
            logging.debug("VimHelper.IsConnected: unknown exception: %s (%s)"
                          %(vierror, sessionid))



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
        except VIException, vierror:
            logging.warn(vierror)
            return vierror
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

    def ListVMs(self, sessionid, mor=None):
        """
        Return a dictionary list of all VMs in search

        Arguments:
        sessionid - string with current session id
        mor - managed object to search from
        """
        # TODO: add options for searching

        logging.debug("VimHelper.ListVMs sessionid %s" % sessionid)
        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.ListVMs: not connected")
            return False

        vms = self.vimserver[sessionid].get_registered_vms(mor)
        return vms

    def GetClusters(self, sessionid, mor=None):
        """
        Return a dictionary list of all Clusters in search

        Arguments:
        sessionid - string with current session id
        mor - managed object to search from
        """

        logging.debug("VimHelper.GetClusters sessionid %s" % sessionid)
        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.GetClusters: not connected")
            return False

        vms = self.vimserver[sessionid].get_clusters(mor)
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
        logging.debug("VimHelper.GetVM sessionid %s" % sessionid)
        if not self.IsConnected(sessionid):
            logging.debug("VimHelper.GetVM: not connected")
            return False

        vm = VimHelper.vimserver[sessionid].get_vm_by_path(vmpath)
        #TODO: what happens if the requested vm doesn't exist?
        return vm

    def VMPowerOn(self, sessionid, vmpath):

        vm = self.GetVM(sessionid, vmpath)
        task = vm.power_on(sync_run=False)
        track = Tasks()
        id = track.add(task)
        return id

    def VMPowerOff(self, sessionid, vmpath):

        vm = self.GetVM(sessionid, vmpath)
        task = vm.power_off(sync_run=False)
        track = Tasks()
        id = track.add(task)
        return id

    def GetTasks(self, sessionid):
        """
        Returns a list of tasks
        """

        try:
            self.tasks[sessionid]
        except Exception:
            self.AddTask(sessionid, 'Initial Placeholder Task')

        return self.tasks[sessionid]

    try:
        tasks
    except NameError:
        tasks = []

    def AddTask(self, sessionid, task):
        """ Add a task to a list """

        myid = uuid.uuid1().hex
        logging.debug("AddTask %s" % myid)
        logging.debug('')
        thistask = {
            'task' : task,
            'session' : sessionid,
            'something' : myid
        }
        logging.debug("AddTask: %s" % thistask)
        self.tasks.append(thistask)



class Tasks(object):
    """ Class to track tasks by id """
    #Tasks don't need to be persistent because once the program ends,
    #the task ends
    # Thought 2 - parrent class can handle sessions, Task class just handles
    # tracking ids.

    try:
        task
    except NameError:
        logging.debug("Tasks.init: attribute error")
        task = {}

    def add(self, task):
        uu = uuid.uuid1().hex
        self.task[uu] = task
        return uu

    def get(self, id):

        try:
            self.task[id]
        except KeyError:
            return None

        return self.task[id]

    def getids(self):

        ids = []
        for id in self.task:
            ids.append(id)

        return ids



