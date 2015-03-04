import json
import logging
import collections
import re

log = logging.getLogger('zen.zengsutil')

# Model utils

def GsParser(results, key, log):
    """
        Given the output of get_gs_metrics.py, look for the key and 
        give out a dictionary 
    """
    try:
        jsonres = json.loads(results)
    except Exception as e:
        log.error('XXXX json load failed for %s', results)
        return {}

    return jsonres.get(key, {})

def GsClusterParser(results, key):
    cluster = GsParser(results, 'cluster', log)
    if key:
        return cluster.get(key)
    return cluster

def GsClientsParser(results, clnt):
    hlist = GsParser(results, 'host_list', log)
    clientnodes = {}
    for k, v in hlist.items():
        # NSD nodes are server nodes, so filter based on them
        if v.get('designatedLicence') == 'server' or \
                        v.get('requiredLicence') == 'server':
            # invalid client node
            continue
        clientnodes[k] = v  # add item to our result
    if clnt:
        return clientnodes.get(clnt)
    return clientnodes

def GsFslistParser(results, fsid):
    fslist = GsParser(results, 'fs_list', log)
    if fsid:
        return fslist.get(fsid)
    return fslist

def GsNsdParser(results, nsd):
    hlist = GsParser(results, 'host_list', log)
    nsdnodes = {}
    # filter results for Nsd Nodes
    for k, v in hlist.items():
        # NSD nodes are server nodes, so filter based on them
        if v.get('designatedLicence') != 'server' or \
                        v.get('requiredLicence') != 'server':
            # invalid nsd node
            continue
        nsdnodes[k] = v  # add item to our result
    if nsd:
        return nsdnodes.get(nsd)
    return nsdnodes



# Metric utils

def GsMetrics(results, log):
    return GsParser(results, 'io_stats', log)

def GsFsMetrics(results, key=''):
    stats = GsMetrics(results, log)
    tot_stats = stats.get('fs_total', {})
    if key:
        return tot_stats.get(key)
    return tot_stats


def GsNSDMetrics(results, key):
    stats = GsMetrics(results, log)
    tot_stats = stats.get(key, {})
    return tot_stats.get('total', {})

def GsClusterMetrics(results):
    stats = GsMetrics(results, log)
    if stats:
        stats = stats.get('cluster')
    return stats


def dictflatten(dictres):
    flatdict = {}
    for k, v in dictres.items():
        v = str(v)
        flatdict[k] = v
    return flatdict

def string_construct_repeat_counts(s):
    d = collections.defaultdict(int)
    for c in s:
        d[c] += 1
    return d

# parse results of nasctl vip_show
def GridNasVipParse(results, notused):
    conf = {}
    res = results.strip('\n')  # Strip leading/trailing newlines
    stripped = False
    for line in res.split('\n'):
        d = string_construct_repeat_counts(line)
        if not stripped:
            # strip all output till a line is found which is only '-'s
            if len(line) == d[line[0]]:
                stripped = True
            continue
        line = re.sub('\s+', ':', line)
        tokens = line.split(':')
        if len(tokens) < 6:
            continue
        key = tokens[0].replace('/', '_')  # VIP - replace special chars with underscore
        model = {}
        model['id'] = key
        model['NetworkAddress'] = tokens[0].split('/')[0]
        model['NetworkMask'] = tokens[0].split('/')[1]
        model['ActiveNode'] = tokens[1]
        model['ActiveInterface'] = tokens[2]
        model['StandbyNode'] = str(tokens[5:])
        conf[key] = model
    log.debug('XXXX GridNasVipParse - returns %r', conf)
    return conf

#
# parse results of nasctl cifs_show
def GridNasCIFSParse(results, notused):
    conf = {}
    res = results.strip('\n')  # Strip leading/trailing newlines
    stripped = False
    for line in res.split('\n'):
        d = string_construct_repeat_counts(line)
        if not stripped:
            # strip all output till a line is found which is only '-'s
            if len(line) == d[line[0]]:
                stripped = True
            continue
        line = re.sub('\s+', ':', line)
        line = line.strip(':')
        tokens = line.split(':')
        if len(tokens) < 4:
            continue
        key = tokens[0].strip()
        model = {}
        model['id'] = key
        model['NetworkAddress'] = tokens[1].strip()
        model['Status'] = tokens[2].strip()
        if tokens[3].strip() == 'No':
            model['ADStatus'] = 'Not Joined'
        elif tokens[3].strip() == 'Yes':
            model['ADStatus'] = 'Joined'
        else:
            model['ADStatus'] = tokens[3].strip()

        conf[key] = model
    log.debug('XXXX GridNasCIFSParse - returns %r', conf)
    return conf


# parse results of nasctl nfs_show
def GridNasNFSParse(results, notused):
    conf = {}
    res = results.strip('\n')  # Strip leading/trailing newlines
    stripped = False
    for line in res.split('\n'):
        d = string_construct_repeat_counts(line)
        if not stripped:
            # strip all output till a line is found which is only '-'s
            if len(line) == d[line[0]]:
                stripped = True
            continue
        line = re.sub('\s+', ':', line)
        line = line.strip(':')
        tokens = line.split(':')
        if len(tokens) < 3:
            continue
        key = tokens[0].strip()
        model = {}
        model['id'] = key
        model['NetworkAddress'] = tokens[1].strip()
        model['Status'] = tokens[2].strip()
        conf[key] = model
    log.debug('XXXX GridNasNFSParse - returns %r', conf)
    return conf


# parse results of nasctl share_show
def GridNasNetworkShareParse(results, notused):
    conf = {}
    res = results.strip('\n')  # Strip leading/trailing newlines
    stripped = False
    for line in res.split('\n'):
        d = string_construct_repeat_counts(line)
        if not stripped:
            # strip all output till a line is found which is only '-'s
            if len(line) == d[line[0]]:
                stripped = True
            continue
        line = re.sub('\s+', ':', line)
        line = line.strip(':')
        tokens = line.split(':')
        if len(tokens) < 3:
            continue
        key = tokens[0].strip()
        model = {}
        model['id'] = key
        model['title'] = key
        model['Path'] = tokens[1].strip()
        model['Options'] = ','.join(tokens[2:])
        conf[key] = model
    log.debug('XXXX GridNasNetworkShareParse - returns %r', conf)
    return conf


# parse results of nasctl user_show
def GridNasUsersParse(results, notused):
    conf = {}
    res = results.strip('\n')  # Strip leading/trailing newlines
    stripped = False
    for oline in res.split('\n'):
        d = string_construct_repeat_counts(oline)
        if not stripped:
            # strip all output till a line is found which is only '-'s
            if len(oline) == d[oline[0]]:
                stripped = True
            continue
        line = re.sub('\s+', ':', oline)
        line = line.strip(':')
        tokens = line.split(':')
        # pivot on an item which is an integer
        for pos, item in enumerate(tokens):
            if not item.isdigit():
                continue
            break
        else:
            # could not find valid reference to decode values
            # Skip this line
            log.debug('XXX skipping user info %s - cannot decode', oline)
            continue
        key = ' '.join(tokens[:pos])
        model = {}
        model['id'] = key
        model['title'] = key
        model['UID'] = tokens[pos]
        pos = pos + 1
        model['PrimaryGroup'] = ' '.join(tokens[pos:-1])
        model['Enabled'] = tokens[-1].strip()
        key = tokens[0].strip()
        conf[key] = model
    log.debug('XXXX GridNasUsersParse - returns %r', conf)
    return conf


# parse results of nasctl group_show
def GridNasGroupsParse(results, notused):
    conf = {}
    res = results.strip('\n')  # Strip leading/trailing newlines
    stripped = False
    for oline in res.split('\n'):
        d = string_construct_repeat_counts(oline)
        if not stripped:
            # strip all output till a line is found which is only '-'s
            if len(oline) == d[oline[0]]:
                stripped = True
            continue
        line = re.sub('\s+', ':', oline)
        line = line.strip(':')
        tokens = line.split(':')
        for pos, item in enumerate(tokens):
            if not item.isdigit():
                continue
            break
        else:
            # could not find valid reference to decode values
            # Skip this line
            log.debug('XXX skipping group %s - cannot decode', oline)
            continue
        key = ' '.join(tokens[:pos])
        model = {}
        model['id'] = key
        model['title'] = key
        model['GID'] = tokens[pos]
        pos = pos + 1
        model['Domain'] = ' '.join(tokens[pos:])
        conf[key] = model
    log.debug('XXXX GridNasGroupsParse - returns %r', conf)
    return conf