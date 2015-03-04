# Referred from zencommand.py
from twisted.internet import reactor, defer
from twisted.python.failure import Failure
import logging

from Products.DataCollector.SshClient import SshClient
from Products.ZenCollector.pools import getPool


log = logging.getLogger("zen.zenddnnwlib")


class MySshClient(SshClient):
    """
    Connection to SSH server at the remote device
    """

    def __init__(self, *args, **kw):
        SshClient.__init__(self, *args, **kw)
        self.connect_defer = None
        self.defers = {}
        self._taskList = set()
        self.connection_description = '%s:*****@%s:%s' % (self.username,
                                                          self.ip, self.port)
        self.pool = getPool('SSH Connections')
        self.poolkey = hash((self.username, self.password, self.ip, self.port))
        self.is_expired = False

    def run(self):
        d = self.connect_defer = defer.Deferred()
        super(MySshClient, self).run()
        return d

    def serviceStarted(self, sshconn):
        super(MySshClient, self).serviceStarted(sshconn)
        self.pool[self.poolkey] = self
        self.connect_defer.callback(self)

    def addCommand(self, command):
        """
        Run a command against the server
        """
        d = defer.Deferred()
        self.defers[command] = d
        SshClient.addCommand(self, command)
        return d

    def addResult(self, command, data, code, stderr):
        """
        Forward the results of the command execution to the starter
        """
        # don't call the CollectorClient.addResult which adds the result to a
        # member variable for zenmodeler
        d = self.defers.pop(command, None)
        if d is None:
            log.error("Internal error where deferred object not in dictionary."\
                      " Command = '%s' Data = '%s' Code = '%s' Stderr='%s'",
                      command.split()[0], data, code, stderr)
        elif not d.called:
            d.callback((data, code, stderr))

    def clientConnectionLost(self, connector, reason):
        # Connection was lost, but could be because we just closed it. 
        # Not necessarily cause for concern.
        log.debug("Connection %s lost." % self.connection_description)
        self.cleanUpPool()

    def check(self, ip, timeout=2):
        """
        Turn off blocking SshClient.test method
        """
        return True

    def clientFinished(self):
        """
        We don't need to track commands/results when they complete
        """
        SshClient.clientFinished(self)
        self.cmdmap = {}
        self._commands = []
        self.results = []

    def clientConnectionFailed(self, connector, reason):
        """
        If we didn't connect let the modeler know

        @param connector: connector associated with this failure
        @type connector: object
        @param reason: failure object
        @type reason: object
        """
        self.clientFinished()
        message = reason.getErrorMessage()
        self.cleanUpPool()
        self.connect_defer.errback(message)

    def cleanUpPool(self):
        if self.poolkey in self.pool:
            # Clean it up so the next time around 
            # the task will get a new connection
            log.debug("Deleting connection %s from pool." 
                            % self.connection_description)
            del self.pool[self.poolkey]


class SshOptions:
    loginTries = 1
    searchPath = ''
    existenceTest = None

    def __init__(self, username, password, loginTimeout, commandTimeout,
                 keyPath, concurrentSessions):
        self.username = username
        self.password = password
        self.loginTimeout = loginTimeout
        self.commandTimeout = commandTimeout
        self.keyPath = keyPath
        self.concurrentSessions = concurrentSessions


class TimeoutError(Exception):
    """
    Error for a defered call taking too long to complete
    """

    def __init__(self, *args):
        Exception.__init__(self)
        self.args = args


def timeoutCommand(deferred, seconds, obj):
    """
    Cause an error on a deferred when it is taking too long to complete
    """

    def _timeout(deferred, obj):
        """
        took too long... call an errback
        """
        deferred.errback(Failure(TimeoutError(obj)))

    def _cb(arg, timer):
        """
        the command finished, possibly by timing out
        """
        if not timer.called:
            timer.cancel()
        return arg

    timer = reactor.callLater(seconds, _timeout, deferred, obj)
    deferred.mytimer = timer
    deferred.addBoth(_cb, timer)
    return deferred


class SshRunner(object):
    """
    Run a single command across a cached SSH connection
    """
    EXPIRED_MESSAGES = ("WARNING: Your password has expired.\nPassword" \
                        " change required but no TTY available.\n",)

    def __init__(self, connection):
        self._connection = connection
        self.exitCode = None
        self.output = None
        self.stderr = None

    def start(self, cmd):
        """
        Initiate a command on the remote device
        """
        self.defer = defer.Deferred(canceller=self._canceller)
        try:
            d = timeoutCommand(self._connection.addCommand(cmd.command),
                               self._connection.commandTimeout,
                               cmd)
        except Exception, ex:
            log.warning('Error starting command: %s', ex)
            return defer.fail(ex)
        d.addErrback(self.timeout)
        d.addBoth(self.processEnded)
        return d

    def _canceller(self, deferToCancel):
        if not deferToCancel.mytimer.called:
            deferToCancel.mytimer.cancel()
        return None

    def timeout(self, arg):
        """
        Deal with slow executing command/connection (close it)
        """
        # We could send a kill signal, but then we would need to track
        # the command channel to send it. Just close the connection.
        return arg

    def processEnded(self, value):
        """
        Deliver ourselves to the starter with the proper attributes
        """
        if isinstance(value, Failure):
            return value
        self.output, self.exitCode, self.stderr = value

        if not self._connection.is_expired \
                and self.stderr in SshRunner.EXPIRED_MESSAGES:
            log.debug('Connection %s expired, cleaning up pool',
                      self._connection.connection_description)
            self._connection.is_expired = True
            self._connection.cleanUpPool()
        return self
