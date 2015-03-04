import logging

log = logging.getLogger('zen.zenpymodelNsd')

from ZenPacks.DDN.Gridscaler.lib import DDNRunCmd as gsc
from ZenPacks.DDN.Gridscaler.lib import DDNGsUtil as gs
from ZenPacks.DDN.Gridscaler.lib.DDNModelPlugin import DDNModelPlugin


class ModelNSD(DDNModelPlugin):
    """ Models GridScaler NSD Clients """
    relname = 'nsdNodes'
    modname = 'ZenPacks.DDN.Gridscaler.NsdNode'

    def prepTask(self, device, log):
        self.device = device
        log.info("%s: preparing for NSD clients", device.id)
        cmdinfo = [{
                       'cmd':
                           '/opt/ddn/directmon/gridscaler/scripts/get_gs_metrics.py',
                       'parser': gs.GsNsdParser,
                       'filter': '',
                   }]

        myCmds = []
        for c in cmdinfo:
            myCmds.append(gsc.Cmd(command=c['cmd'], template=c['filter'],
                                  config=self.config, parser=c['parser']))
        self.cmd = myCmds
        log.debug('XXX _prepNSDClients(): self.cmd = %r', self.cmd)

    def parseResults(self, resultList):
        errmsgs = {}  # any accumulated errors
        res = []  # aggregate list of dev/components maps
        nw_nsd = ''
        pref_nsd = ''
        log.debug('XXXX within _parseResults with %r', resultList)
        for success, result in resultList:
            log.debug("XXXX _parseResults (success/ds %s) %s", success, result)
            if success:
                if isinstance(result.result, dict):
                    rm = self.relMap()
                    # dictionary of device with attributes
                    info = result.result
                    for k, v in info.items():
                        v = gs.dictflatten(v)
                        ip = v.get('IP')
                        if ip:
                            nw_nsd += ip + ','
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
            return  # already processed, nothing to do now or err'd out

        if errmsgs:
            log.warn('XXXX Gridscaler NSD collection failed %s',
                     str(errmsgs))
            ## TODO raise an event with data
            ## If error TODO pass an failed event
            d.callback([{}])
            return

        # should also update the device model for preferredNSD, networkNSDs
        # strip the last comma
        nw_nsd = nw_nsd.strip(',')
        pref_nsd = nw_nsd.split(',')[0]
        devom = self.objectMap({'id': self.config.id,
                                'preferredNSD': self._conn_params['target'],
                                # Update Current target as preferredNSD,
                                'networkNSDs': nw_nsd})
        res.append(devom)
        log.debug("collected NSDClients property: %r" % res)
        d.callback(res)

    def process(self, device, results, log):
        """ Process results, return iterable of datamaps or None."""
        log.debug('XXXX modeler process(dev=%r) got results %s',
                  device, str(results))
        return results
