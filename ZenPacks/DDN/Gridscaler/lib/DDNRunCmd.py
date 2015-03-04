import logging

log = logging.getLogger('zen.zenremcmd')

from twisted.python.failure import Failure


# Command Cmd() abstraction class used by Modeling and Metric plugins
class Cmd():
    """
    Holds the config of every command to be run
    """

    def __init__(self, config, template, command, parser):
        self.template = template
        self.result = None
        self.command = command
        self.parser = parser
        self.config = config

    # this method has to exist!!!
    def processCompleted(self, pr):
        """
        Return back the datasource with the ProcessRunner/SshRunner stored in
        the the 'result' attribute.
        """
        log.debug("XXXX cmd %s processCompleted with result %s",
                  self.command, pr)
        myresult = (pr.exitCode, pr.output, pr.stderr)
        log.debug("XXXX actual output: %s", str(myresult))

        # on failure initialize result as a dict with {templateId:errmsg}
        if isinstance(pr, Failure):
            msg = str(self.template) + ":" + pr.getErrorMessage()
            self.result = Failure(msg)
            return pr

        self.result = pr
        if self.parser:
            self.result = self.parser(pr.output, self.template) # output,filter

        log.debug('Process %s, result %s, stopped (%s)',
                  self.command,
                  self.result,
                  pr.exitCode)
        return self

    def __str__(self):
        return ' '.join(map(str, [
            self.command,
            self.config,
            self.result,
        ]))