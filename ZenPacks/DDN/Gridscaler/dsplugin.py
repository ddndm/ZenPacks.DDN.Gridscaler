import logging

from ZenPacks.DDN.Gridscaler.lib import DDNRunCmd as gsc
from ZenPacks.DDN.Gridscaler.lib import DDNGsUtil as gsu
from ZenPacks.DDN.Gridscaler.lib.DDNMetricPlugin import DDNMetricPlugin
from Products.ZenEvents import ZenEventClasses
from Products.DataCollector.plugins.DataMaps import ObjectMap


log = logging.getLogger('zen.zenpymetrics')

#
# TODO - all the 3 plugins below are same code, except for 
# component/relation definition (modname, relname, compname)
# 

GSMODEL = {None:
               {'modname': 'ZenPacks.DDN.Gridscaler.GridscalerDevice',
                'compname': '',
                'relname': ''},
           'fsLists':
               {'modname': 'ZenPacks.DDN.Gridscaler.FsList',
                'compname': 'fsLists',
                'relname': 'fsLists'},
           'ndsNodes':
               {'modname': 'ZenPacks.DDN.Gridscaler.NsdNode',
                'compname': 'nsdNodes',
                'relname': 'nsdNodes'}
}

DEVMODEL = GSMODEL[None]


class GsMetricPlugin(DDNMetricPlugin):
    """ This plugin collects metrics for all gridscaler components """

    # List of device attributes you'll need to do collection.
    @classmethod
    def params(cls, datasource, context):
        log.info("XXXX GsMetricPlugin params(cls=%r, datasource=%r, context=%r"
                 % (cls, datasource, context))
        return {}

    def __init__(self):
        super(GsMetricPlugin, self).__init__()

    def prepTask(self, config):
        cmds = ('/opt/ddn/directmon/gridscaler/scripts/get_gs_metrics.py',)
        for c in cmds:
            self.cmd.append(gsc.Cmd(command=c, template='metrics',
                                    config=self.config,
                                    parser=self.parseMetricResults))
        log.debug('XXX _prepMetricsCmd(): self.cmd = %r', self.cmd)


    def getNetworkAddress(self):
        nw_ips = self.conn_params.get('networkNSDs')
        if not nw_ips:
            nw_ips = self.conn_params.get('defaultTargets', self.config.id)
        return nw_ips

    def updateModel(self, compname=DEVMODEL['compname'],
                    modname=DEVMODEL['modname']):
        nw_ip = self.getNetworkAddress()
        pref_ip = self.conn_params['target']  # current passed target!
        if self.err_connFailed:
            pref_ip = self.getNextAddress()
        # First update the device component
        # Do not update 'id' on ObjectMap
        devmap = ObjectMap(data={'networkNSDs': nw_ip,
                                 'preferredNSD': pref_ip},
                           compname=compname,
                           modname=modname)
        return [devmap]

    def parseMetricResults(self, results, notused):
        """ parse the results for each datasource part of config """
        log.debug("XXX parseGSMetricResults called (config:%s, results: %s)",
                  self.config, results)

        aggregate = {}
        for ds in self.config.datasources:
            # the below template is available as part of ds.points.id
            component = component_key = ds.component
            log.warn("Ds Template %s "%ds.template)
            if ds.template == 'GS_NsdServer':  # NSD
                res = gsu.GsNSDMetrics(results, component)
            elif ds.template == 'GS_FsList':  # FS
                res = gsu.GsFsMetrics(results, component)
            elif ds.template == 'GSDeviceMetrics':  # device metrics
                component_key = 'GSDevice'
                res = gsu.GsClusterMetrics(results)
            else:
                # unexpected, log an error and return none
                log.error('XXXX unexpected datasource %r', ds)
                continue
            aggregate[component] = res

        log.debug('XXX result=%s', (str(aggregate)))
        return aggregate

    def onSuccess(self, result, config):
        log.debug('XXXX onSuccess: values is %s', str(result))
        aggregate = self.new_data()
        aggregate['values'] = result
        aggregate['maps'] = self.updateModel()
        return aggregate

    def onError(self, result, config):
        log.debug("XXXX onError(self=%r, result=%r, config=%r)",
                  self, result.getErrorMessage(), config)
        aggregate = self.new_data()
        aggregate['events'] = [{
                                   'component': '',
                                   'device': config.id,
                                   'summary': 'error connection failed %s' %
                                              str(self.conn_params),
                                   'eventClass': '/Perf',
                                   'eventKey': 'GridscalerPerf',
                                   'severity': ZenEventClasses.Error,
                               }]
        aggregate['maps'] = self.updateModel()
        return aggregate
