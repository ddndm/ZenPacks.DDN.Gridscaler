import logging

log = logging.getLogger('zen.zenpymodeler')

# import zope.interface
import zope.component

from ZenPacks.DDN.GridScalerv2.lib import DDNNetworkLib

from twisted.internet.defer import maybeDeferred, Deferred, DeferredList
# from twisted.python.failure import Failure
from Products.ZenCollector.interfaces import IEventService
from Products.ZenUtils.Executor import TwistedExecutor
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin


class DDNModelPlugin(PythonPlugin):
    """ Base plugin framework for all DDN products/solutions """

    requiredProperties = (
        'zCommandUsername',
        'zCommandPassword',
        'zKeyPath',
        'zSshConcurrentSessions',
        'zCommandPort',
        'zCommandCommandTimeout',
        'zCommandLoginTimeout',
        'zGSNSDList',
        'networkNSDs',
        'preferredNSD'
    )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    def initConnectionParams(self, device):
        """
        Extract and initialize necessary information for connections parameters
        """
        user = getattr(device, 'zCommandUsername', 'root')
        passwd = getattr(device, 'zCommandPassword', 'password')
        targets = getattr(device, 'zGSNSDList', '10.1.1.1')
        targets = targets.split(",")
        # Get PreferredTarget from device, if earlier model was successful
        preferredTarget = getattr(device, 'preferredNSD', None)
        if not preferredTarget:
            preferredTarget = targets[0]  # choose the first target
        port = getattr(device, 'zCommandPort', 22)
        keypath = getattr(device, 'zKeyPath', '~/.ssh/id_rsa')
        concurrentsessions = getattr(device, 'zSshConcurrentSessions', 10)
        logincmdtimeout = getattr(device, 'zCommandLoginTimeout', 15)
        cmdtimeout = getattr(device, 'zCommandCommandTimeout', 60)
        self._conn_params = {'user': user,
                             'pass': passwd,
                             'target': preferredTarget,
                             'port': port,
                             'keypath': keypath,
                             'consess': concurrentsessions,
                             'logincmdtimeout': logincmdtimeout,
                             'cmdtimeout': cmdtimeout,
                             'targets': targets,
                             'currentTarget': preferredTarget}
        self.config = device
        # self.templateId = template

    def __init__(self):
        self._conn_params = {}
        self._internal_defer = None
        self._task_defer = Deferred()
        self._connection = None
        self.cmd = []
        self.config = None
        # self.templateId = None


    def parseResults(self, resultList):
        """No default collect behavior. Must be implemented in subclass."""
        raise NotImplementedError

    def prepTask(self, device, log):
        """No default collect behavior. Must be implemented in subclass."""
        raise NotImplementedError

    def process(self, device, results, log):
        """No default collect behavior. Must be implemented in subclass."""
        raise NotImplementedError

    def collect(self, device, log):
        log.debug("Module : MODELPLUGIN, Message : %s: collection for device",
                  device.id)
        self.initConnectionParams(device)
        self.prepTask(device, log)
        return self.post_collect(device, log)

    def _addDatasource(self, cmd):
        """
        Add a new instantiation of ProcessRunner or SshRunner
        for every datasource.
        """
        runner = DDNNetworkLib.SshRunner(self._connection)
        d = runner.start(cmd)
        d.addBoth(cmd.processCompleted)
        return d

    def _fetchPerf(self, connection):
        """ Run all command in parallel through a connection
            Return a deferred list, one deferred for each command
        """
        # Bundle up the list of tasks
        log.debug("Module : MODELPLUGIN, Message : XXXX _fetchPerf called"\
        " on connection %r", connection)
        deferredCmds = []
        for c in self.cmd:
            task = self._executor.submit(self._addDatasource, c)
            deferredCmds.append(task)
        # Return a deferred List
        dl = DeferredList(deferredCmds, consumeErrors=True)
        return dl


    def connectCallback(self, connection):
        """
        Callback called after a successful connect to the remote device.
        """
        log.debug("Module : MODELPLUGIN, Message : XXX connectCallback with "\
        "connection %r", connection)
        self._connection = connection  # objects of type MySshClient
        self._connection._taskList.add(self)  # all tasks run over a conn
        # creating a new internal deferred list for all tasks
        dl = self._internal_defer = self._fetchPerf(connection)
        dl.addCallback(self.parseResults)
        # return connections for the ssh defered callback chain
        return connection

    def getNextAddress(self):
        """
        get next remote address from the list of NetworkAddress.
        """
        pref_ip = self._conn_params['target']  # current failed IP
        nw_ips = self._conn_params['targets']  # a list of IPs
        log.debug('Module : MODELPLUGIN, Message : XXXX getNextAddress called"\
        " with %s/%s',str(nw_ips), pref_ip)
        for i, ip in enumerate(nw_ips):
            if ip == pref_ip:
                i += 1
                if i == len(nw_ips):
                    pref_ip = nw_ips[0]
                else:
                    pref_ip = nw_ips[i]
                break
        else:
            pref_ip = nw_ips[0]
        log.debug('Module : MODELPLUGIN, Message : XXXX getNextAddress %s',
                  pref_ip)
        return pref_ip

    def connectionFailed(self, msg):
        """
            Connect with next ip if fails
        """
        log.warn("Module : MODELPLUGIN, Message : XXXX connectionFailed"\
        " called for connection %r", msg)
        newtarget = self.getNextAddress()
        if newtarget != self._conn_params['currentTarget']:
            log.warn('Module : MODELPLUGIN, Message : XXXX %s failed.. "\
            "retrying with %s',self._conn_params['target'], newtarget)
            # retry modeling with the chosen target
            self._conn_params['target'] = newtarget
            d = self._internal_defer = maybeDeferred(self._connect)
            d.addCallbacks(self.connectCallback, self.connectionFailed)
            return msg
        self.err_connFailed = True
        if self._task_defer is not None:
            self._task_defer.errback(msg)
        return msg

    def _connect(self):
        """
        create a connection to object the remote device.
        Make a new SSH connection object if there isn't one available.
        This doesn't actually connect to the device.
        """
        # log.debug("Module : MODELPLUGIN, Message : XXXX _connect instance %r,"\
        # " param %s",self, str(self._conn_params))

        options = DDNNetworkLib.SshOptions(self._conn_params['user'],
                                           self._conn_params['pass'],
                                           self._conn_params['logincmdtimeout'],
                                           self._conn_params['cmdtimeout'],
                                           self._conn_params['keypath'],
                                           self._conn_params['consess'])

        connection = DDNNetworkLib.MySshClient(self._conn_params['target'],
                                               self._conn_params['target'],
                                               self._conn_params['port'],
                                               options=options)

        connection.sendEvent = zope.component.queryUtility(IEventService)
        d = connection.run()
        return d

    def post_collect(self, device, log):
        """
            Should get called from collect in subclass before finishing.
        """
        log.debug("Module : MODELPLUGIN, Message : %s: DDN collection for "\
        "device", device.id)
        # prepare the connection
        d = self._internal_defer = maybeDeferred(self._connect)
        d.addCallbacks(self.connectCallback, self.connectionFailed)
        # prepare concurrent executor context
        self._executor = TwistedExecutor(self._conn_params['consess'])
        return self._task_defer
