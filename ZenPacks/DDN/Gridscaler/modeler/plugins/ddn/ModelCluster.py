import logging

log = logging.getLogger('zen.zenpymodelCluster')

from ZenPacks.DDN.Gridscaler.lib import DDNRunCmd as gsc
from ZenPacks.DDN.Gridscaler.lib import DDNGsUtil as gs
from ZenPacks.DDN.Gridscaler.lib.DDNModelPlugin import DDNModelPlugin


class ModelCluster(DDNModelPlugin):
    """ Models GridScaler Cluster for device level attributes"""
    modname = 'ZenPacks.DDN.Gridscaler.GridscalerDevice'

    def prepTask(self, device, log):
        self.device = device
        log.info("%s: preparing for Gridscaler cluster", device.id)
        cmdinfo = [{
                       'cmd':
                           '/opt/ddn/directmon/gridscaler/scripts/get_gs_metrics.py',
                       'parser': gs.GsClusterParser,
                       'filter': '',
                   }]

        myCmds = []
        for c in cmdinfo:
            myCmds.append(gsc.Cmd(command=c['cmd'], template=c['filter'],
                                  config=self.config, parser=c['parser']))
        self.cmd = myCmds
        log.debug('XXX _prepGSCluster(): self.cmd = %r', self.cmd)

    def parseResults(self, resultList):
        errmsgs = {}  # any accumulated errors
        aggregate = []  # aggregate dictionary result
        nw_ips = None  # network ips
        log.debug('XXXX within _parseResults with %r', resultList)
        for success, result in resultList:
            log.debug("XXXX _parseResults (success/ds %s) %s", success, result)
            if success:
                om = self.objectMap()
                if isinstance(result.result, dict):
                    # dictionary of device with attributes
                    info = gs.dictflatten(result.result)
                    # add title new key
                    info['id'] = self.config.id  # cannot be clusterId
                    # remove few fields not needed.
                    del info['clientNodes']
                    del info['nsdNodes']
                    del info['ID']
                    del info['name']
                    log.debug('XXX created objectmap %r', om)
                    om.updateFromDict(info)
                    log.debug('XXX updated omap %r', om)
                    aggregate.append(om)
                else:
                    log.warn('XXXX success result type %s value %r',
                             type(result.result), result.result)
            else:
                errmsgs.update(result.result)

        d, self._task_defer = self._task_defer, None
        log.debug('XXX got deferred as d %r, aggregate %r', d, aggregate)
        if d is None or d.called:
            return  # already processed, nothing to do now

        if errmsgs:
            log.warn('XXXX cluster collection failed %s',
                     str(errmsgs))
            ## TODO raise an event with data
            d.callback([{}])
            return

        res = aggregate
        log.debug("collected Cluster Info : %r" % res)
        d.callback(res)

    def process(self, device, results, log):
        """ Process results, return iterable of datamaps or None."""
        log.debug('XXXX modeler process(dev=%r) got results %s',
                  device, str(results))
        return results
