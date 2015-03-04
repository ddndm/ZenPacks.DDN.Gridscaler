import logging

log = logging.getLogger('zen.zenpymodelClients')

from ZenPacks.DDN.Gridscaler.lib import DDNRunCmd as gsc
from ZenPacks.DDN.Gridscaler.lib import DDNGsUtil as gs
from ZenPacks.DDN.Gridscaler.lib.DDNModelPlugin import DDNModelPlugin


class ModelClient(DDNModelPlugin):
    """ Models GridScaler Clients """
    relname = 'clientNodes'
    modname = 'ZenPacks.DDN.Gridscaler.ClientNode'

    def prepTask(self, device, log):
        self.device = device
        log.info("%s: preparing for clients", device.id)
        cmdinfo = [{
                       'cmd':
                           '/opt/ddn/directmon/gridscaler/scripts/get_gs_metrics.py',
                       'parser': gs.GsClientsParser,
                       'filter': '',
                   }]

        myCmds = []
        for c in cmdinfo:
            myCmds.append(gsc.Cmd(command=c['cmd'], template=c['filter'],
                                  config=self.config, parser=c['parser']))
        self.cmd = myCmds
        log.debug('XXX _prepFsLists(): self.cmd = %r', self.cmd)

    def parseResults(self, resultList):
        errmsgs = {}  # any accumulated errors
        res = []  # aggregate dictionary result
        log.debug('XXXX within _parseResults with %r', resultList)
        for success, result in resultList:
            log.debug("XXXX _parseResults (success/ds %s) %s", success, result)
            if success:
                if isinstance(result.result, dict):
                    rm = self.relMap()
                    info = result.result
                    for k, v in info.items():
                        v = gs.dictflatten(v)
                        log.debug('XXX client %s, attribs %r', k, v)
                        # update dictionary for key properties
                        v['id'] = str(k)
                        try:
                            v['title'] = v.pop('name')
                        except Exception as e:
                            v['title'] = v['id']

                        om = self.objectMap()
                        om.updateFromDict(v)
                        rm.append(om)
                    res.append(rm)
                else:
                    log.warn('XXXX success result type %s value %r',
                             type(result.result), result.result)
            else:
                errmsgs.update(result.result)

        d, self._task_defer = self._task_defer, None
        if d is None or d.called:
            return  # already processed, nothing to do now

        if errmsgs:
            log.warn('XXXX Gridscaler Client collection failed %s',
                     str(errmsgs))
            ## TODO raise an event with data
            ## If error TODO pass an failed event
            d.callback([{}])
            return

        log.debug("collected Gridscaler Clients property: %r" % res)
        d.callback(res)

    def process(self, device, results, log):
        """ Process results, return iterable of datamaps or None."""
        log.debug('XXXX modeler process(dev=%r) got results %s',
                  device, str(results))
        return results
