# Import zenpacklib from the current directory (zenpacklib.py).
from . import zenpacklib


# Create a ZenPackSpec and name it CFG.
CFG = zenpacklib.ZenPackSpec(
    name=__name__,

    zProperties={
        'DEFAULTS': {'category': 'DDN GridScaler Solution'},

        'zGSNSDList': {
            'type': 'string',
        },
    },

    classes={
        'GridscalerDevice': {
            'base': zenpacklib.Device,
            'label': 'GridscalerDevice',

            'properties': {
                'clusterManager': {
                    'label': 'clusterManager',
                    'order': 4.2,
                },
                'domain': {
                    'label': 'cluster Domain',
                    'order': 4.3,
                },
                'fileCopyCMD': {
                    'label': 'fileCopyCMD',
                    'order': 4.4,
                },
                'gpfsVersion': {
                    'label': 'gpfsVersion',
                    'order': 4.5,
                },
                'numActiveClientNodes': {
                    'label': 'numActiveClientNodes',
                    'order': 4.6,
                },
                'numClientNodes': {
                    'label': 'numClientNodes',
                    'order': 4.7,
                },
                'numFs': {
                    'label': 'numFs',
                    'order': 4.8,
                },
                'numLocalNodesActive': {
                    'label': 'numLocalNodesActive',
                    'order': 4.9,
                },
                'numManagerNodes': {
                    'label': 'numManagerNodes',
                    'order': 4.10,
                },
                'numNSDNodes': {
                    'label': 'numNSDNodes',
                    'order': 4.11,
                },
                'numQuorumNodesActive': {
                    'label': 'numQuorumNodesActive',
                    'order': 4.12,
                },
                'numQuorumNodesDefined': {
                    'label': 'numQuorumNodesDefined',
                    'order': 4.13,
                },
                'numRemoteNodesJoined': {
                    'label': 'numRemoteNodesJoined',
                    'order': 4.14,
                },
                'primaryHost': {
                    'label': 'primaryHost',
                    'order': 4.15,
                },
                'quorumState': {
                    'label': 'quorumState',
                    'order': 4.16,
                },
                'secondaryHost': {
                    'label': 'secondaryHost',
                    'order': 4.17,
                },
                'totalMounts': {
                    'label': 'totalMounts',
                    'order': 4.18,
                },

                'config': {
                    'label': 'config',
                },

                'numNodesDefined': {
                    'label': 'numNodesDefined',
                },

                'shellCMD': {
                    'label': 'shellCMD',
                },

                'numNSD': {
                    'label': 'numNSD',
                },

                'preferredNSD': {
                    'label': 'Preferred Target',
                    'order': 4.19,
                },
                'networkNSDs': {
                    'label': 'nsd Network Targets',
                    'order': 4.20,
                },
            }
        },

        'ClientNode': {
            'base': zenpacklib.Component,
            'label': 'GS_ClientNode',
            'order': 1.4,
            'properties': {
                'adminNode': {
                    'label': 'Admin Node',
                    'order': 4.0,
                },

                'designation': {
                    'label': 'Designation',
                    'order': 4.1,
                },

                'gpfs_state': {
                    'label': 'GPFS State',
                    'order': 4.2,
                },

                'IP': {
                    'label': 'Network IP',
                    'order': 4.3,
                },

                'numLocalNSD': {
                    'label': 'Local NSD',
                    'order': 4.4,
                },

                'mountedFs': {
                    'label': 'Mounted FSs',
                    'order': 4.5,
                },

                'isPrimary': {
                    'label': 'isPrimary',
                    'order': 4.9,
                },
                'isSecondary': {
                    'label': 'isSecondary',
                    'order': 4.10,
                },
                'numMountedFs': {
                    'label': 'numMountedFs',
                    'order': 4.11,
                },
                'isFsMounted': {
                    'label': 'isFsMounted',
                    'order': 4.12,
                },
                'designatedLicence': {
                    'label': 'designatedLicence',
                    'order': 4.13,
                },
                'requiredLicence': {
                    'label': 'requiredLicence',
                    'order': 4.14,
                },
            }
        },

        'NsdNode': {
            'base': zenpacklib.Component,
            'label': 'GS_NsdServer',
            'order': 1.2,
            'properties': {
                'adminNode': {
                    'label': 'Admin Node',
                    'order': 4.0,
                },

                'designation': {
                    'label': 'Designation',
                    'order': 4.1,
                },

                'gpfs_state': {
                    'label': 'GPFS State',
                    'order': 4.2,
                },

                'IP': {
                    'label': 'Network IP',
                    'order': 4.3,
                },

                'numLocalNSD': {
                    'label': 'Local NSD',
                    'order': 4.4,
                },

                'mountedFs': {
                    'label': 'Mounted FSs',
                    'order': 4.5,
                },

                'isPrimary': {
                    'label': 'isPrimary',
                    'order': 4.9,
                },
                'isSecondary': {
                    'label': 'isSecondary',
                    'order': 4.10,
                },
                'numMountedFs': {
                    'label': 'numMountedFs',
                    'order': 4.11,
                },
                'isFsMounted': {
                    'label': 'isFsMounted',
                    'order': 4.12,
                },
                'designatedLicence': {
                    'label': 'designatedLicence',
                    'order': 4.13,
                },
                'requiredLicence': {
                    'label': 'requiredLicence',
                    'order': 4.14,
                },
            }
        },

        'FsList': {
            'base': zenpacklib.Component,
            'label': 'GS_FsList',
            'order': 1.1,
            'properties': {
                'largeLUNSupport': {
                    'label': 'largeLUNSupport',
                    'order': 4.0,
                },

                'numMounts': {
                    'label': 'numMounts',
                    'order': 4.1,
                },
                'maxDataReplica': {
                    'label': 'maxDataReplica',
                    'order': 4.2,
                },
                'defaultMountPoint': {
                    'label': 'defaultMountPoint',
                    'order': 4.3,
                },
                'diskStoragePools': {
                    'label': 'diskStoragePools',
                    'order': 4.4,
                },
                'defaultDetaReplica': {
                    'label': 'defaultDetaReplica',
                    'order': 4.5,
                },
                'disk_list': {
                    'label': 'disk_list',
                    'order': 4.6,
                },
                'blkAllocationType': {
                    'label': 'blkAllocationType',
                    'order': 4.7,
                },
                'logFileSize': {
                    'label': 'logFileSize',
                    'order': 4.8,
                },
                'maxInodeNumber': {
                    'label': 'maxInodeNumber',
                    'order': 4.9,
                },
                'minFragSize': {
                    'label': 'minFragSize',
                    'order': 4.10,
                },
                'blockSize': {
                    'label': 'blockSize',
                    'order': 4.11,
                },
                'version': {
                    'label': 'version',
                    'order': 4.12,
                },
                'strictReplicaAllocation': {
                    'label': 'strictReplicaAllocation',
                    'order': 4.13,
                },
                'perFileSetQuota': {
                    'label': 'perFileSetQuota',
                    'order': 4.14,
                },
                'quotaEnforced': {
                    'label': 'quotaEnforced',
                    'order': 4.15,
                },
                'freeSpace': {
                    'label': 'freeSpace',
                    'order': 4.16,
                },
                'maxMetedataReplica': {
                    'label': 'maxMetedataReplica',
                    'order': 4.17,
                },
                'aclSemantics': {
                    'label': 'aclSemantics',
                    'order': 4.18,
                },
                'fileset_list': {
                    'label': 'fileset_list',
                    'order': 4.19,
                },
                'totalSpace': {
                    'label': 'totalSpace',
                    'order': 4.20,
                },
                'mountPriority': {
                    'label': 'mountPriority',
                    'order': 4.21,
                },
                'inodeSize': {
                    'label': 'inodeSize',
                    'order': 4.22,
                },
                'fastExternalAttribute': {
                    'label': 'fastExternalAttribute',
                    'order': 4.23,
                },
                'freeInodes': {
                    'label': 'freeInodes',
                    'order': 4.24,
                },
                'indirectBlockSize': {
                    'label': 'indirectBlockSize',
                    'order': 4.25,
                },
                'totalInodes': {
                    'label': 'totalInodes',
                    'order': 4.26,
                },
                'autoMountOption': {
                    'label': 'autoMountOption',
                    'order': 4.27,
                },
                'creationTime': {
                    'label': 'creationTime',
                    'order': 4.28,
                },

                'fileLockSemantics': {
                    'label': 'fileLockSemantics',
                    'order': 4.29,
                },
                'dmapiEnabled': {
                    'label': 'dmapiEnabled',
                },
                'defaultMetedataReplica': {
                    'label': 'defaultMetedataReplica',
                },
                'filesetdfEnabled': {
                    'label': 'filesetdfEnabled',
                },

            },
        },
        # GridNAS Entries

        'VirtualNetwork': {
            'base': zenpacklib.Component,
            'label': 'GNAS_VirtualNetwork',
            'order': 2.2,
            'properties': {
                'NetworkAddress': {
                    'label': 'Network Address',
                    'order': 4.0,
                },
                'NetworkMask': {
                    'label': 'Network Mask',
                    'order': 4.1,
                },
                'ActiveNode': {
                    'label': 'ActiveNode',
                    'order': 4.2,
                },
                'ActiveInterface': {
                    'label': 'ActiveInterface',
                    'order': 4.3,
                },
                'StandbyNode': {
                    'label': 'StandbyNode',
                    'order': 4.4,
                },
            },
        },

        'CIFS': {
            'base': zenpacklib.Component,
            'label': 'GNAS_CIFS',
            'order': 2.3,
            'properties': {
                'NetworkAddress': {
                    'label': 'Network Address',
                    'order': 4.0,
                },
                'Status': {
                    'label': 'Status',
                    'order': 4.1,
                },
                'ADStatus': {
                    'label': 'ActiveDirectoryStatus',
                    'order': 4.2,
                },
            },
        },

        'NFS': {
            'base': zenpacklib.Component,
            'label': 'GNAS_NFS',
            'order': 2.4,
            'properties': {
                'NetworkAddress': {
                    'label': 'Network Address',
                    'order': 4.0,
                },
                'Status': {
                    'label': 'Status',
                    'order': 4.1,
                },
            },
        },

        'NetworkShare': {
            'base': zenpacklib.Component,
            'label': 'GNAS_NetworkShare',
            'order': 2.1,
            'properties': {
                'Path': {
                    'label': 'Path',
                    'order': 4.0,
                },
                'Options': {
                    'label': 'Options',
                    'order': 4.1,
                },
            },
        },

        'NasUser': {
            'base': zenpacklib.Component,
            'label': 'GNAS_NasUser',
            'order': 2.5,
            'properties': {
                'UID': {
                    'label': 'UID',
                    'order': 4.0,
                },
                'PrimaryGroup': {
                    'label': 'Primary Group',
                    'order': 4.1,
                },
                'Enabled': {
                    'label': 'Enabled',
                    'order': 4.2,
                },
            },
        },

        'NasGroup': {
            'base': zenpacklib.Component,
            'label': 'GNAS_NasGroup',
            'order': 2.6,
            'properties': {
                'GID': {
                    'label': 'GID',
                    'order': 4.0,
                },
                'Domain': {
                    'label': 'Domain',
                    'order': 4.1,
                },
            },
        },

    },

    class_relationships=zenpacklib.relationships_from_yuml(
        """[GridscalerDevice]++-[ClientNode]
           [GridscalerDevice]++-[NsdNode]
           [GridscalerDevice]++-[FsList]
           [GridscalerDevice]++-[CIFS]
           [GridscalerDevice]++-[NFS]
           [GridscalerDevice]++-[NetworkShare]
           [GridscalerDevice]++-[NasUser]
           [GridscalerDevice]++-[NasGroup]
           [GridscalerDevice]++-[VirtualNetwork]"""
    )
)

# Create the specification.
CFG.create()
