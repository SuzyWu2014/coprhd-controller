#!/usr/bin/python

# Copyright (c) 2016 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import common
from common import SOSError
import json
import tag
from volume import Volume

class VolumeGroup(object):

    '''
    The class definition for operations on 'VolumeGroup'.
    '''

    # Commonly used URIs for the 'VolumeGroup' module
    URI_VOLUME_GROUP_LIST = '/volume-groups/block'
    URI_VOLUME_GROUP = '/volume-groups/block/{0}'
    URI_VOLUME_GROUP_VOLUMES = '/volume-groups/block/{0}/volumes'
    URI_VOLUME_GROUP_HOSTS = '/volume-groups/block/{0}/hosts'
    URI_VOLUME_GROUP_CLUSTERS = '/volume-groups/block/{0}/clusters'
    URI_VOLUME_GROUP_CHILDREN = '/volume-groups/block/{0}/volume-groups'
    URI_DEACTIVATE = URI_VOLUME_GROUP + '/deactivate'
    URI_TAG_VOLUME_GROUP = URI_VOLUME_GROUP + "/tags"

    # URIs for VolumeGroup Full Copy Operations
    URI_VOLUME_GROUP_CLONE = "/volume-groups/block/{0}/protection/full-copies"
    URI_VOLUME_GROUP_CLONE_ACTIVATE = "/volume-groups/block/{0}/protection/full-copies/activate"
    URI_VOLUME_GROUP_CLONE_DETACH = "/volume-groups/block/{0}/protection/full-copies/detach"
    URI_VOLUME_GROUP_CLONE_RESTORE = "/volume-groups/block/{0}/protection/full-copies/restore"
    URI_VOLUME_GROUP_CLONE_RESYNCRONIZE = "/volume-groups/block/{0}/protection/full-copies/resynchronize"
    URI_VOLUME_GROUP_CLONE_LIST = URI_VOLUME_GROUP_CLONE
    URI_VOLUME_GROUP_CLONE_GET= "/volume-groups/block/{0}/protection/full-copies/{1}"
    
    # URIs for VolumeGroup Snapshot Operations
    URI_VOLUME_GROUP_SNAPSHOT = "/volume-groups/block/{0}/protection/snapshots"
    URI_VOLUME_GROUP_SNAPSHOT_ACTIVATE = URI_VOLUME_GROUP_SNAPSHOT + "/activate"
    URI_VOLUME_GROUP_SNAPSHOT_DEACTIVATE = URI_VOLUME_GROUP_SNAPSHOT + "/deactivate"
    URI_VOLUME_GROUP_SNAPSHOT_RESTORE = URI_VOLUME_GROUP_SNAPSHOT + "/restore"
    URI_VOLUME_GROUP_SNAPSHOT_RESYNCHRONIZE = URI_VOLUME_GROUP_SNAPSHOT + "/resynchronize"
    URI_VOLUME_GROUP_SNAPSHOT_LIST = URI_VOLUME_GROUP_SNAPSHOT
    URI_VOLUME_GROUP_SNAPSHOT_SHOW= URI_VOLUME_GROUP_SNAPSHOT + "/{1}"
    URI_VOLUME_GROUP_SNAPSHOT_GET_COPY_SETS= URI_VOLUME_GROUP_SNAPSHOT + "/copy-sets"

    # URIs for VolumeGroup Snapshot Session Operations
    URI_VOLUME_GROUP_SNAPSHOT_SESSION = "/volume-groups/block/{0}/protection/snapshot-sessions"
    URI_VOLUME_GROUP_SNAPSHOT_SESSION_LIST = URI_VOLUME_GROUP_SNAPSHOT_SESSION
    URI_VOLUME_GROUP_SNAPSHOT_SESSION_SHOW= URI_VOLUME_GROUP_SNAPSHOT_SESSION + "/{1}"
    URI_VOLUME_GROUP_SNAPSHOT_SESSION_GET_COPY_SETS = URI_VOLUME_GROUP_SNAPSHOT_SESSION + "/copy-sets"

    def __init__(self, ipAddr, port):
        '''
        Constructor: takes IP address and port of the ViPR instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        
    def create(self, name, description, roles, parent, migrationType, migrationGroupBy):
        '''
        Makes REST API call to create volume group
        Parameters:
            name: name of volume group
            description: description for the volume group
            roles: comma separated list of roles for the volume group
        Returns:
            Created volume group details in JSON response payload
        '''
        request = dict()
        request["name"] = name
        request["description"] = description
        request["roles"] = roles.split(',')
        request["parent"] = parent
        request["migration_type"] = migrationType
        request["migration_group_by"] = migrationGroupBy

        body = json.dumps(request)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                    VolumeGroup.URI_VOLUME_GROUP_LIST, body)
        o = common.json_decode(s)
        return o


    def list(self):
        '''
        Makes REST API call and retrieves volume groups 
        Parameters: None
        Returns:
            List of volume group UUIDs in JSON response payload
        '''
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                    VolumeGroup.URI_VOLUME_GROUP_LIST, None)
        o = common.json_decode(s)

        if("volume_group" in o):
            return common.get_list(o, 'volume_group')
        return []

    def show_by_uri(self, uri, xml=False):
        '''
        Makes REST API call and retrieves volume group details based on UUID
        Parameters:
            uri: UUID of volume group
        Returns:
            volume group details in JSON response payload
        '''
        if(xml):
            (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                            "GET", VolumeGroup.URI_VOLUME_GROUP.format(uri),
                             None, None, xml)
            return s

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                    "GET", VolumeGroup.URI_VOLUME_GROUP.format(uri), None)
        o = common.json_decode(s)
        inactive = common.get_node_value(o, 'inactive')
        if(inactive == True):
            return None

        return o

    def show(self, name, xml=False):
        '''
        Retrieves volume group details based on volume group name
        Parameters:
            name: name of the volume group
        Returns:
            volume group details in JSON response payload
        '''
        volume_group_uri = self.query_by_name(name)
        volume_group_detail = self.show_by_uri(volume_group_uri, xml)
        return volume_group_detail
    
    
    def query_by_name(self, name):
        '''
        Retrieves UUID of volume group based on its name
        Parameters:
            name: name of volume group
        Returns: UUID of volume group
        Throws:
            SOSError - when volume group name is not found
        '''
        if (common.is_uri(name)):
            return name
        
        try:
            volume_groups = self.list()
            for app in volume_groups:
                app_detail = self.show_by_uri(app['id']);
                if(app_detail and app_detail['name'] == name):
                    return app_detail['id']
            raise SOSError(SOSError.NOT_FOUND_ERR,
                            'VolumeGroup: ' + name + ' not found')
        except SOSError as e:
            raise e
            

    def delete_by_uri(self, uri):
        '''
        Deletes a volume group based on volume group UUID
        Parameters:
            uri: UUID of volume group
        '''
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                    "POST", VolumeGroup.URI_DEACTIVATE.format(uri), None)
        return

    def delete_by_name(self, name):
        '''
        Deletes a volume group based on volume group name
        Parameters:
            name: name of volume group
        '''
        volume_group_uri = self.query_by_name(name)
        return self.delete_by_uri(volume_group_uri)

    def update(self, name, new_name, new_description, add_volumes, cg_id, rg_name, remove_volumes, parent, add_hosts, add_clusters, remove_hosts, remove_clusters):
        '''
        Makes REST API call and updates volume group name and description
        Parameters:
            name: name of volume group
            new_name: new name of the volume group
            new_description: new description of the volume group

        Returns:
            List of volume group resources in response payload
        '''
        volume_group_uri = self.query_by_name(name)

        request = dict()
        if(new_name and len(new_name) > 0):
            request["name"] = new_name
        if(new_description and len(new_description) > 0):
            request["description"] = new_description
        if(parent and len(parent) > 0):
            request["parent"] = parent
        if(add_volumes and len(add_volumes) > 0):
            add_vols = dict()
            add_vols["volume"] = add_volumes.split(',')
            if(cg_id and len(cg_id) > 0):
                add_vols["consistency_group"] = cg_id
            if(rg_name and len(rg_name) > 0):
                add_vols["replication_group_name"] = rg_name
            request["add_volumes"] = add_vols
        if(remove_volumes and len(remove_volumes) > 0):
            remove_vols = dict()
            remove_vols["volume"] = remove_volumes.split(',')
            request["remove_volumes"] = remove_vols
        if(add_hosts and len(add_hosts) > 0):
            request["add_hosts"] = add_hosts.split(',')
        if(add_clusters and len(add_clusters) > 0):
            request["add_clusters"] = add_clusters.split(',')
        if(remove_hosts and len(remove_hosts) > 0):
            request["remove_hosts"] = remove_hosts.split(',')
        if(remove_clusters and len(remove_clusters) > 0):
            request["remove_clusters"] = remove_clusters.split(',')

        body = json.dumps(request)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                    VolumeGroup.URI_VOLUME_GROUP.format(volume_group_uri), body)


    def tag(self, name, addtags, removetags):
        '''
        Makes REST API call and tags volume group
        Parameters:
            name: name of volume group
            addtags : tags to be added
            removetags : tags to be removed

        Returns:
            response of the tag operation
        '''
        volume_group_uri = self.query_by_name(name)

        return (
            tag.tag_resource(self.__ipAddr, self.__port,
                              VolumeGroup.URI_TAG_VOLUME_GROUP,
                               volume_group_uri, addtags, removetags)
        )
    
    #Routine for volume group volumes 
    def volume_show(self, name ,xml=False):
        
        volume_group_uri = self.query_by_name(name)
        
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                        VolumeGroup.URI_VOLUME_GROUP_VOLUMES.format(volume_group_uri), None)
        o = common.json_decode(s)
     
        
        return o
    
    #Routine for children volume groups for a volume group 
    def volume_group_children_show(self, name ,xml=False):
        
        volume_group_uri = self.query_by_name(name)
        
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                        VolumeGroup.URI_VOLUME_GROUP_CHILDREN.format(volume_group_uri), None)
        o = common.json_decode(s)
     
        
        return o


    def volume_group_clone_activate(self, name, cloneUris, partial, sync):
        '''
        Makes REST API call to activate volume group clone
        Parameters:
            partial: Enable the flag to operate on clones for subset of VolumeGroup.
                     Please specify one clone from each Array Replication Group
            volumes: A clone of a volume group specifying which clone Set to act on.
                    For partial operation, specify one clone from each Array Replication Group
        Returns:
            response of the activate operation
        '''
        volume_group_uri = self.query_by_name(name)
        
        request = dict()
        request["volumes"] = cloneUris.split(',')
        
        # if partial request
        if (partial):
            request["partial"] = partial

        body = json.dumps(request)

        (s, h) = common.service_json_request(
                self.__ipAddr, self.__port,
                "POST",
                VolumeGroup.URI_VOLUME_GROUP_CLONE_ACTIVATE.format(volume_group_uri), body)
            
        o = common.json_decode(s)
        if(sync):
            task = o["task"][0]
            return self.check_for_sync(task,sync)
        else:
            return o 

    def volume_group_clone_detach(self, name, cloneUris, partial, sync):
        '''
        Makes REST API call to detach volume group clone
        Parameters:
            partial: Enable the flag to operate on clones for subset of VolumeGroup.
                     Please specify one clone from each Array Replication Group
            volumes: A clone of a volume group specifying which clone Set to act on.
                    For partial operation, specify one clone from each Array Replication Group
        Returns:
            response of the detach operation
        '''
        volume_group_uri = self.query_by_name(name)
        
        request = dict()
        request["volumes"] = cloneUris.split(',')
        
        # if partial request
        if (partial):
            request["partial"] = partial

        body = json.dumps(request)
        
        (s, h) = common.service_json_request(
                self.__ipAddr, self.__port,
                "POST",
                VolumeGroup.URI_VOLUME_GROUP_CLONE_DETACH.format(volume_group_uri), body)
            
        o = common.json_decode(s)
        if(sync):
            task = o["task"][0]
            return self.check_for_sync(task,sync)
        else:
            return o

    def volume_group_clone_restore(self, name, cloneUris, partial, sync):
        '''
        Makes REST API call to restore volume group clone
        Parameters:
            partial: Enable the flag to operate on clones for subset of VolumeGroup.
                     Please specify one clone from each Array Replication Group
            volumes: A clone of a volume group specifying which clone Set to act on.
                    For partial operation, specify one clone from each Array Replication Group
        Returns:
            response of the restore operation
        '''
        volume_group_uri = self.query_by_name(name)
        
        request = dict()
        request["volumes"] = cloneUris.split(',')
        
        # if partial request
        if (partial):
            request["partial"] = partial

        body = json.dumps(request)

        (s, h) = common.service_json_request(
                self.__ipAddr, self.__port,
                "POST",
                VolumeGroup.URI_VOLUME_GROUP_CLONE_RESTORE.format(volume_group_uri), body)
            
        o = common.json_decode(s)
        if(sync):
            task = o["task"][0]
            return self.check_for_sync(task,sync)
        else:
            return o
        
    def volume_group_clone_resync(self, name, cloneUris, partial, sync):
        '''
        Makes REST API call to resynchronize volume group clone
        Parameters:
            partial: Enable the flag to operate on clones for subset of VolumeGroup.
                     Please specify one clone from each Array Replication Group
            volumes: A clone of a volume group specifying which clone Set to act on.
                    For partial operation, specify one clone from each Array Replication Group
        Returns:
            response of the resynchronize operation
        '''
        volume_group_uri = self.query_by_name(name)
        
        request = dict()
        request["volumes"] = cloneUris.split(',')
        
        # if partial request
        if (partial):
            request["partial"] = partial

        body = json.dumps(request)
        
        (s, h) = common.service_json_request(
                self.__ipAddr, self.__port,
                "POST",
                VolumeGroup.URI_VOLUME_GROUP_CLONE_RESYNCRONIZE.format(volume_group_uri), body)
            
        o = common.json_decode(s)
        if(sync):
            task = o["task"][0]
            return self.check_for_sync(task,sync)
        else:
            return o   

    def volume_group_clone_list(self, name):
        
        volume_group_uri = self.query_by_name(name)
        
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            VolumeGroup.URI_VOLUME_GROUP_CLONE_LIST.format(volume_group_uri), None)
            
        o = common.json_decode(s)
        return o      
    
    def volume_group_clone_get(self, name, cloneURI):
        
        volumeGroupUri = self.query_by_name(name)
        
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            VolumeGroup.URI_VOLUME_GROUP_CLONE_GET.format(volumeGroupUri, cloneURI), None)

        o = common.json_decode(s)
        return o                            
        
    # Creates clone(s) for the given volume group
    def clone(self, name, clone_name, count, create_inactive, partial, volumeUris, sync):
        '''
        Makes REST API call to clone volume group
        Parameters:
            name: name with which clone to be created
            count: number of clones to create
            create_inactive: with this flag, created clone will not be activated
            partial: Enable the flag to create clones for subset of VolumeGroup.
                     Please specify one volume from each Array Replication Group
            volumes: A list of volumes specifying their Array Replication Groups to be cloned.
                    This field is valid only when partial flag is provided
        Returns:
            response of the create operation
        '''
        
        volumeGroupUri = self.query_by_name(name)

        request = {
            'name': clone_name,
            'type': None,
            'count': 1,
            'create_inactive': create_inactive
        }

        if(count and count > 1):
            request["count"] = count

        # if partial request
        if (partial):
            request["partial"] = partial
            request["volumes"] = volumeUris.split(',')
            

        body = json.dumps(request)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             VolumeGroup.URI_VOLUME_GROUP_CLONE.format(volumeGroupUri),
                                             body)
        o = common.json_decode(s)
        if(sync):
            task = o["task"][0]
            return self.check_for_sync(task, sync)
        else:
            return o   

    # Creates snapshot for the given volume group
    def snapshot(self, name, snapshot_name, create_inactive, partial, volumeUris, sync):
        '''
        Makes REST API call to create volume group snapshot
        Parameters:
            name: name with which snapshot to be created
            create_inactive: with this flag, created snapshot will not be activated
            partial: Enable the flag to create snapshot for subset of VolumeGroup.
                     Please specify one volume from each Array Replication Group
            volumes: A list of volumes specifying their Array Replication Groups.
                    This field is valid only when partial flag is provided
        Returns:
            response of the create operation
        '''

        volumeGroupUri = self.query_by_name(name)

        request = {
            'name': snapshot_name,
            'create_inactive': create_inactive
        }

        # if partial request
        if (partial):
            request["partial"] = partial
            request["volumes"] = volumeUris.split(',')

        body = json.dumps(request)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT.format(volumeGroupUri),
                                             body)
        o = common.json_decode(s)
        if(sync):
            task = o["task"][0]
            return self.check_for_sync(task, sync)
        else:
            return o

    def volume_group_snapshot_operation(self, name, snapshotUris, partial, sync, uri):
        '''
        Makes REST API call to activate/deactivate/restore/resync volume group snapshot
        Parameters:
            partial: Enable the flag to operate on snapshots for subset of VolumeGroup.
                     Please specify one snapshot from each Array Replication Group
            snapshots: A snapshot of a volume group specifying which snapshot Set to act on.
                    For partial operation, specify one snapshot from each Array Replication Group
        Returns:
            response of the operation
        '''
        volume_group_uri = self.query_by_name(name)

        request = dict()
        request["snapshots"] = snapshotUris.split(',')

        # if partial request
        if (partial):
            request["partial"] = partial

        body = json.dumps(request)

        (s, h) = common.service_json_request(
                self.__ipAddr, self.__port,
                "POST",
                uri.format(volume_group_uri), body)

        o = common.json_decode(s)
        if(sync):
            task = o["task"][0]
            return self.check_for_sync(task,sync)
        else:
            return o

    def volume_group_snapshot_list(self, name):
        volume_group_uri = self.query_by_name(name)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_LIST.format(volume_group_uri), None)

        o = common.json_decode(s)

        if('snapshot' in o):
            return o['snapshot']
        else:
            return []

    def snapshot_query(self, name, snapshotname):
        '''
        This function will take the snapshot name and volume group name
        as input and get uri of the first occurrence of snapshot.
        paramters:
             name : Name of volume group.
             snapshotname : Name of the snapshot
        return
            return with uri of the given snapshot.
        '''
        uris = self.volume_group_snapshot_list(name)
        for ss in uris:
            if (ss['name'] == snapshotname):
                return ss['id']
        raise SOSError(SOSError.SOS_FAILURE_ERR, "Snapshot " + snapshotname +
                       ": not found")

    def volume_group_snapshot_show(self, name, snapshotname):
        volumeGroupUri = self.query_by_name(name)
        snapshotUri = self.snapshot_query(name, snapshotname)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_SHOW.format(volumeGroupUri, snapshotUri), None)

        o = common.json_decode(s)
        return o

    def volume_group_snapshot_get_sets(self, name):
        volumeGroupUri = self.query_by_name(name)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_GET_COPY_SETS.format(volumeGroupUri), None)

        o = common.json_decode(s)
        return o

    def volume_group_snapshot_get(self, name, setname):
        volumeGroupUri = self.query_by_name(name)

        request = dict()
        request["copy_set_name"] = setname

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_GET_COPY_SETS.format(volumeGroupUri), json.dumps(request))

        o = common.json_decode(s)

        if('snapshot' in o):
            return o['snapshot']
        else:
            return []

    # snapshot session

    # Creates snapshot session for the given volume group
    def snapshotsession(self, name, snapshotsession_name, copy_on_ha, partial, volumeUris, sync):
        '''
        Makes REST API call to create volume group snapshot session
        Parameters:
            name: name with which snapshot session to be created
            copy_on_ha: with this flag, create snapshot session on HA side of VPLEX Distributed volumes
            partial: Enable the flag to create snapshot session for subset of VolumeGroup.
                     Please specify one volume from each Array Replication Group
            volumes: A list of volumes specifying their Array Replication Groups.
                    This field is valid only when partial flag is provided
        Returns:
            response of the create operation
        '''

        volumeGroupUri = self.query_by_name(name)

        request = {
            'name': snapshotsession_name,
            'copy_on_high_availability_side': copy_on_ha
        }

        # if partial request
        if (partial):
            request["partial"] = partial
            request["volumes"] = volumeUris.split(',')

        body = json.dumps(request)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_SESSION.format(volumeGroupUri),
                                             body)
        o = common.json_decode(s)
        if(sync):
            task = o["task"][0]
            return self.check_for_sync(task, sync)
        else:
            return o

    def volume_group_snapshotsession_list(self, name):
        volumeGroupUri = self.query_by_name(name)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_SESSION_LIST.format(volumeGroupUri), None)

        o = common.json_decode(s)

        if('snapshot_session' in o):
            return o['snapshot_session']
        else:
            return []

    def snapshotsession_query(self, name, snapshotsessionname):
        '''
        This function will take the snapshot session name and volume group name
        as input and get uri of the first occurrence of snapshot session.
        paramters:
             name : Name of volume group.
             snapshotsessionname : Name of the snapshot session
        return
            return with uri of the given snapshot session.
        '''
        uris = self.volume_group_snapshotsession_list(name)
        for ss in uris:
            if (ss['name'] == snapshotsessionname):
                return ss['id']
        raise SOSError(SOSError.SOS_FAILURE_ERR, "Snapshot session " + snapshotsessionname +
                       ": not found")

    def volume_group_snapshotsession_show(self, name, snapshotsessionname):
        volumeGroupUri = self.query_by_name(name)
        snapshotsessionUri = self.snapshotsession_query(name, snapshotsessionname)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_SESSION_SHOW.format(volumeGroupUri, snapshotsessionUri), None)

        o = common.json_decode(s)
        return o

    def volume_group_snapshotsession_get_sets(self, name):
        volumeGroupUri = self.query_by_name(name)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_SESSION_GET_COPY_SETS.format(volumeGroupUri), None)

        o = common.json_decode(s)
        return o

    def volume_group_snapshotsession_get(self, name, setname):
        volumeGroupUri = self.query_by_name(name)

        request = dict()
        request["copy_set_name"] = setname

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_SESSION_GET_COPY_SETS.format(volumeGroupUri), json.dumps(request))

        o = common.json_decode(s)

        if('snapshot_session' in o):
            return o['snapshot_session']
        else:
            return []

    # Blocks the operation until the task is complete/error out/timeout
    def check_for_sync(self, result, sync):
        if(sync):
            if(len(result["resource"]) > 0):
                resource = result["resource"]
                return (
                    common.block_until_complete("volume", resource["id"],
                                                result["id"], self.__ipAddr,
                                                self.__port)
                )
            else:
                raise SOSError(
                    SOSError.SOS_FAILURE_ERR,
                    "error: task list is empty, no task response found")
        else:
            return result



#SHOW resource parser

def show_volume_group_volume_parser(subcommand_parsers, common_parser):
    volume_group_volume_parser = subcommand_parsers.add_parser('show-volumes',
                        description='ViPR VolumeGroup Show Volumes CLI usage.',
                                                parents=[common_parser],
                                                conflict_handler='resolve',
                                                help='Show volume group volumes')
    volume_group_volume_parser.add_argument('-xml',
                             dest='xml',
                             action='store_true',
                             help='XML response')
    mandatory_args = volume_group_volume_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-n', '-name',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    volume_group_volume_parser.set_defaults(func=volume_group_volume_show)

def volume_group_volume_show(args):
    obj = VolumeGroup(args.ip, args.port)
    try:
        res = obj.volume_show(args.name, args.xml)
        if(res):
            if (args.xml == True):
                return common.format_xml(res)
            return common.format_json_object(res)
    except SOSError as e:
        raise e

def show_volume_group_children_parser(subcommand_parsers, common_parser):
    volume_group_volume_parser = subcommand_parsers.add_parser('show-children',
                        description='ViPR VolumeGroup Show Children CLI usage.',
                                                parents=[common_parser],
                                                conflict_handler='resolve',
                                                help='Show volume group child volume groups')
    volume_group_volume_parser.add_argument('-xml',
                             dest='xml',
                             action='store_true',
                             help='XML response')
    mandatory_args = volume_group_volume_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-n', '-name',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    volume_group_volume_parser.set_defaults(func=volume_group_children_show)

def volume_group_children_show(args):
    obj = VolumeGroup(args.ip, args.port)
    try:
        res = obj.volume_group_children_show(args.name, args.xml)
        if(res):
            if (args.xml == True):
                return common.format_xml(res)
            return common.format_json_object(res)
    except SOSError as e:
        raise e


def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser('create',
                    description='ViPR VolumeGroup Create CLI usage.',
                    parents=[common_parser],
                    conflict_handler='resolve',
                    help='Create a volume group')
    mandatory_args = create_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-n', '-name',
                                metavar='<name>',
                                dest='name',
                                help='Name of VolumeGroup',
                                required=True)
    mandatory_args.add_argument('-r', '-roles',
                               metavar='<roles>',
                               dest='roles',
                               help='[COPY | DR]',
                                required=True)
    create_parser.add_argument('-d', '-description',
                               metavar='<description>',
                               dest='description',
                               help='description for volume group')
    create_parser.add_argument('-pa', '-parent',
                               metavar='<parent>',
                               dest='parent',
                               help='parent volume group for volume group')
    create_parser.add_argument('-mt', '-migrationType',
                               metavar='<migrationType>',
                               dest='migrationType',
                               help='migration type for mobility volume group')
    create_parser.add_argument('-mg', '-migrationGroupBy',
                               metavar='<migrationGroupBy>',
                               dest='migrationGroupBy',
                               help='migration group by for mobility volume group')
    
    create_parser.set_defaults(func=create)


def create(args):
    obj = VolumeGroup(args.ip, args.port)
    try:
        obj.create(args.name, args.description, args.roles, args.parent, args.migrationType, args.migrationGroupBy)
    except SOSError as e:
        if (e.err_code in [SOSError.NOT_FOUND_ERR,
                            SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code,
                           "VolumeGroup create failed: " + e.err_text)
        else:
            raise e


def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser('delete',
                description='ViPR VolumeGroup Delete CLI usage.',
                                                  parents=[common_parser],
                                                  conflict_handler='resolve',
                                                  help='Delete a volume group')
    mandatory_args = delete_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-n', '-name',
                                metavar='<name>',
                                dest='name',
                                help='Name of VolumeGroup',
                                required=True)
    delete_parser.set_defaults(func=delete_by_name)


def delete_by_name(args):
    obj = VolumeGroup(args.ip, args.port)
    
    try:
        obj.delete_by_name(args.name)

    except SOSError as e:
        if (e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "VolumeGroup delete failed: " + e.err_text)
        else:
            raise e


# show command parser
def show_parser(subcommand_parsers, common_parser):
    show_parser = subcommand_parsers.add_parser('show',
                        description='ViPR VolumeGroup Show CLI usage.',
                                                parents=[common_parser],
                                                conflict_handler='resolve',
                                                help='Show volume group details')
    show_parser.add_argument('-xml',
                             dest='xml',
                             action='store_true',
                             help='XML response')
    mandatory_args = show_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-n', '-name',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    show_parser.set_defaults(func=show)

def show(args):
    obj = VolumeGroup(args.ip, args.port)
    try:
        res = obj.show(args.name, args.xml)
        if(res):
            if (args.xml == True):
                return common.format_xml(res)
            return common.format_json_object(res)
    except SOSError as e:
        raise e
    
# list command parser
def list_parser(subcommand_parsers, common_parser):
    list_parser = subcommand_parsers.add_parser('list',
                        description='ViPR VolumeGroup List CLI usage.',
                        parents=[common_parser],
                        conflict_handler='resolve',
                        help='Lists volume groups')
    list_parser.add_argument('-v', '-verbose',
                             dest='verbose',
                             help='List volume groups with details',
                             action='store_true')
    list_parser.add_argument('-l', '-long',
                             dest='largetable',
                             help='List volume groups in table format',
                             action='store_true')
    list_parser.set_defaults(func=list)


def list(args):
    obj = VolumeGroup(args.ip, args.port)

    try:
        from common import TableGenerator
        volume_groups = obj.list()
        records = []
        for volume_group in volume_groups:
            volume_group_uri = volume_group['id']
            app_detail = obj.show_by_uri(volume_group_uri)
            if(app_detail):
                records.append(app_detail)

        if(len(records) > 0):
            if(args.verbose == True):
                return common.format_json_object(records)

            elif(args.largetable == True):
                TableGenerator(records, ['name', 'description',
                                          'roles', 'tags']).printTable()
            else:
                TableGenerator(records, ['name']).printTable()

        else:
            return

    except SOSError as e:
        raise e


# update volume group command parser
def update_parser(subcommand_parsers, common_parser):
    update_parser = subcommand_parsers.add_parser('update',
                        description='ViPR update volume group CLI usage',
                        parents=[common_parser],
                        conflict_handler='resolve',
                        help='Update volume group properties')
    mandatory_args = update_parser.add_argument_group(
                                            'mandatory arguments')
    mandatory_args.add_argument('-n', '-name',
                                metavar='<name>',
                                dest='name',
                                help='Name of existing volume group',
                                required=True)
    update_parser.add_argument('-nn', '-newname',
                                       metavar='<newname>',
                                       dest='newname',
                                       help='New name of volume group')
    update_parser.add_argument('-d', '-description',
                                       metavar='<description>',
                                       dest='description',
                                       help='New description of volume group')
    update_parser.add_argument('-r', '-remove_volumes',
                                       metavar='<tenant/project/volume_label | volume_uid,...>',
                                       dest='remove_volumes',
                                       help='A list of volumes to remove from the volume group')
    update_parser.add_argument('-a', '-add_volumes',
                                       metavar='<tenant/project/volume_label | volume_uid,...>',
                                       dest='add_volumes',
                                       help='A list of volumes to add to the volume group')
    update_parser.add_argument('-cg', '-consistency_group',
                                       metavar='<consistency_group>',
                                       dest='consistency_group',
                                       help='A consistency group for adding volumes to the volume group')
    update_parser.add_argument('-rg', '-replication_group',
                                       metavar='<replication_group>',
                                       dest='replication_group',
                                       help='A replication group name on the array where volumes will be added to')
    update_parser.add_argument('-pa', '-parent',
                                       metavar='<parent>',
                                       dest='parent',
                                       help='A parent volume group for the volume group')
    update_parser.add_argument('-rh', '-remove_hosts',
                                       metavar='<remove_hosts>',
                                       dest='remove_hosts',
                                       help='A list of hosts to remove from the volume group')
    update_parser.add_argument('-ah', '-add_hosts',
                                       metavar='<add_hosts>',
                                       dest='add_hosts',
                                       help='A list of hosts to add to the volume group')
    update_parser.add_argument('-rc', '-remove_clusters',
                                       metavar='<remove_clusters>',
                                       dest='remove_clusters',
                                       help='A list of clusters to remove from the volume group')
    update_parser.add_argument('-ac', '-add_clusters',
                                       metavar='<add_clusters>',
                                       dest='add_clusters',
                                       help='A list of clusters to add to the volume group')


    update_parser.set_defaults(func=update)


def update(args):

    if(args.newname is None and args.description is None and args.add_volumes is None and args.remove_volumes is None and args.parent is None and args.remove_hosts is None and args.add_hosts is None and args.add_clusters is None and args.remove_clusters is None):
        raise SOSError(SOSError.CMD_LINE_ERR,
            "viprcli volume group update: error: at least one of " +
            "the arguments -np/-newname -d/-description -a/-add_volumes " +
            " -r/-remove_volumes -rh/-remove_hosts -ah/-add_hosts " +
            " -rc/-remove_clusters -ac/-add_clusters required")
     
    add_vols = []
    if(args.add_volumes and len(args.add_volumes) > 0):
        for item in args.add_volumes.split(','):
            if (common.is_uri(item)):
                add_vols.append(item)
            else:
                vol = Volume(args.ip, args.port)
                volid = vol.show(item,  False, False)['id']
                add_vols.append(volid)
                    
    rem_vols = []
    if(args.remove_volumes and len(args.remove_volumes) > 0):
        for item in args.remove_volumes.split(','):
            if (common.is_uri(item)):
                rem_vols.append(item)
            else:
                vol = Volume(args.ip, args.port)
                try:
                    volid = vol.show(item,  False, False)['id']
                    rem_vols.append(volid)
                except:
                    continue
                    
    obj = VolumeGroup(args.ip, args.port)
    try:
        obj.update(args.name, args.newname,
                    args.description, ",".join(add_vols), args.consistency_group, args.replication_group, ",".join(rem_vols), args.parent, args.add_hosts, args.add_clusters, args.remove_hosts, args.remove_clusters)
    except SOSError as e:
        raise e

def tag_parser(subcommand_parsers, common_parser):
    tag_parser = subcommand_parsers.add_parser('tag',
                    description='ViPR Tag volume group CLI usage',
                    parents=[common_parser],
                    conflict_handler='resolve',
                    help='Update Tags of volume group')
    mandatory_args = tag_parser.add_argument_group(
                                    'mandatory arguments')
    mandatory_args.add_argument('-n', '-name',
                                metavar='<name>',
                                dest='name',
                                help='Name of existing volume group',
                                required=True)

    tag.add_tag_parameters(tag_parser)

    tag_parser.set_defaults(func=tag_volume_group)


def tag_volume_group(args):

    if(args.add is None and args.remove is None):
        raise SOSError(SOSError.CMD_LINE_ERR,
                        "viprcli volume group tag: error: at least one of " +
                       "the arguments -add -remove is required")
    obj = VolumeGroup(args.ip, args.port)
    try:
        obj.tag(args.name,
                args.add, args.remove)
    except SOSError as e:
        common.format_err_msg_and_raise("volumegroup", "tag", e.err_text,
                                         e.err_code)


    
# Common Parser for clone 
def volume_clone_list_parser(cc_common_parser):
    mandatory_args = cc_common_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    cc_common_parser.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project')
    cc_common_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')    

# Common Parser for clone 
def volume_clone_get_parser(cc_common_parser):
    mandatory_args = cc_common_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-volume', '-v',
                                metavar='<clonename>',
                                dest='clone',
                                help='Name of clone',
                                required=True)
    cc_common_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')

# Common Parser for clone operations
def volume_group_clone_common_parser(cc_common_parser):
    mandatory_args = cc_common_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    cc_common_parser.add_argument('-partial',
                              dest='partial',
                              action='store_true',
                              help='To operate on clones for subset of VolumeGroup. ' +
                              'Please specify one clone from each Array Replication Group')
    mandatory_args.add_argument('-volumes', '-v',
                            metavar='<clonename,...>',
                            dest='clones',
                            help='A clone of a volume group specifying which clone Set to act on. ' +
                            'For partial operation, specify one clone from each Array Replication Group',
                            required=True)
    
    cc_common_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')  
    cc_common_parser.add_argument('-synchronous', '-sync',
                                  dest='sync',
                                  action='store_true',
                                  help='Synchronous mode enabled')

def query_volumes_for_partial_request(args):
    volumeUris = []
    vol = Volume(args.ip, args.port)
    if (args.partial and args.volumes):
        if (len(args.volumes) < 1):
            raise SOSError(
            SOSError.CMD_LINE_ERR,
            'error: At least one volume should be specified for partial operation')
        for item in args.volumes.split(','):
            name = args.tenant + "/" + args.project + "/" + item
            volid = vol.show(name, False, False)['id']
            volumeUris.append(volid)
            
    return volumeUris
    
def query_clones(args):
    cloneUris = []
    vol = Volume(args.ip, args.port)
    if (args.clones):
        if (len(args.clones) < 1):
            raise SOSError(
            SOSError.CMD_LINE_ERR,
            'error: At least one clone should be specified')
        for item in args.clones.split(','):
            name = args.tenant + "/" + args.project + "/" + item
            volid = vol.show(name, False, False)['id']
            cloneUris.append(volid)
            
    return cloneUris

# volume clone routines
def clone_parser(subcommand_parsers, common_parser):
    clone_parser = subcommand_parsers.add_parser(
        'clone',
        description='ViPR VolumeGroup Clone(FullCopy) CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Clone a VolumeGroup')
    
    mandatory_args = clone_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    mandatory_args.add_argument('-clonename',
                                metavar='<clonename>',
                                dest='cloneName',
                                help='Name of clone to create',
                                required=True)

    clone_parser.add_argument('-count', '-cu',
                              dest='count',
                              metavar='<count>',
                              type=int,
                              default=0,
                              help='Number of clones to be created')
    clone_parser.add_argument('-inactive',
                              dest='inactive',
                              action='store_true',
                              help='If inactive is set to true, then the operation will create clone,' +
                              'but not activate the synchronization between source and target volumes.')
    clone_parser.add_argument('-partial',
                              dest='partial',
                              action='store_true',
                              help='To create clones for subset of VolumeGroup. ' +
                              'Please specify one volume from each Array Replication Group')
    clone_parser.add_argument('-volumes', '-v',
                            metavar='<volume_label,...>',
                            dest='volumes',
                            help='A list of volumes specifying their Array Replication Groups to be cloned.' +
                            ' This field is valid only when partial flag is provided')
    clone_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    clone_parser.add_argument('-synchronous', '-sync',
                       dest='sync',
                       action='store_true',
                       help='Synchronous mode enabled')

    clone_parser.set_defaults(func=volume_group_clone)


def volume_group_clone(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""
        
    if(args.volumes and len(args.volumes.split(',')) > 1 and args.sync):
        raise SOSError(
            SOSError.CMD_LINE_ERR,
            'error: Synchronous operation is not allowed as ' +
            'we cannot track multiple tasks created for multiple volume groups specified')
    try:
        volumeUris = query_volumes_for_partial_request(args)
        obj.clone(args.name, args.cloneName, args.count, args.inactive,
                  args.partial, ",".join(volumeUris), args.sync)
        return
    
    except SOSError as e:
        common.format_err_msg_and_raise(
            "clone",
            "volume",
            e.err_text,
            e.err_code)
             
#clone_activate_parser
def clone_activate_parser(subcommand_parsers, common_parser):
    clone_activate_parser = subcommand_parsers.add_parser(
        'clone-activate',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Activate the Clone of a VolumeGroup',
        description='ViPR Activate Clone of a VolumeGroup CLI usage.')
    
    # Add parameter from common clone parser.
    volume_group_clone_common_parser(clone_activate_parser)
    clone_activate_parser.set_defaults(func=volume_group_clone_activate)
    
# Activate Clone Function
def volume_group_clone_activate(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""
        
    try:
        cloneUris = query_clones(args)
        
        obj.volume_group_clone_activate(
            args.name,
            ",".join(cloneUris),
            args.partial,
            args.sync)
        return

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Clone Activate: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "clone",
                "activate",
                e.err_text,
                e.err_code)  
                                 
#clone_detach_parser
def clone_detach_parser(subcommand_parsers, common_parser):
    clone_detach_parser = subcommand_parsers.add_parser(
        'clone-detach',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Detach the Clone of a VolumeGroup',
        description='ViPR Detach Clone of a VolumeGroup CLI usage.')
    
    # Add parameter from common clone parser.
    volume_group_clone_common_parser(clone_detach_parser)
    clone_detach_parser.set_defaults(func=volume_group_clone_detach)
    
# Detach Clone Function
def volume_group_clone_detach(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""
        
    try:
        cloneUris = query_clones(args)
        
        obj.volume_group_clone_detach(
            args.name,
            ",".join(cloneUris),
            args.partial,
            args.sync)
        return

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Clone Detach: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "clone",
                "detach",
                e.err_text,
                e.err_code)     
    
#clone_restore_parser
def clone_restore_parser(subcommand_parsers, common_parser):
    clone_restore_parser = subcommand_parsers.add_parser(
        'clone-restore',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Restore Clone of a VolumeGroup',
        description='ViPR Restore Clone of a VolumeGroup CLI usage.')
    
    # Add parameter from common clone parser.
    volume_group_clone_common_parser(clone_restore_parser)
    clone_restore_parser.set_defaults(func=volume_group_clone_restore)
    
# Restore Clone Function
def volume_group_clone_restore(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""
        
    try:
        cloneUris = query_clones(args)
        
        obj.volume_group_clone_restore(
            args.name,
            ",".join(cloneUris),
            args.partial,
            args.sync)
        return

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Clone Restore: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "clone",
                "restore",
                e.err_text,
                e.err_code)
            
#clone_resync_parser
def clone_resync_parser(subcommand_parsers, common_parser):
    clone_resync_parser = subcommand_parsers.add_parser(
        'clone-resync',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Resynchronize the Clone of a VolumeGroup',
        description='ViPR Resynchronize Clone of a VolumeGroup CLI usage.')
    
    # Add parameter from common clone parser.
    volume_group_clone_common_parser(clone_resync_parser)
    clone_resync_parser.set_defaults(func=volume_group_clone_resync)
    
# Resync Clone Function
def volume_group_clone_resync(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""
        
    try:
        cloneUris = query_clones(args)
        
        obj.volume_group_clone_resync(
            args.name,
            ",".join(cloneUris),
            args.partial,
            args.sync)
        return

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Clone Resync: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "clone",
                "resync",
                e.err_text,
                e.err_code) 
 
def clone_list_parser(subcommand_parsers, common_parser):
    clone_list_parser = subcommand_parsers.add_parser(
        'clone-list',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get Clone list of a VolumeGroup',
        description='ViPR Clone List of a VolumeGroup CLI usage.')
    
    # Add parameter from common clone parser.
    volume_clone_list_parser(clone_list_parser)
    clone_list_parser.set_defaults(func=volume_group_clone_list)
    
# List Clone Function
def volume_group_clone_list(args):
    obj = VolumeGroup(args.ip, args.port)
        
    try:
        res= obj.volume_group_clone_list(args.name)
        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Clone List: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "clone",
                "list",
                e.err_text,
                e.err_code)     

def clone_get_parser(subcommand_parsers, common_parser):
    clone_get_parser = subcommand_parsers.add_parser(
        'clone-show',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show a Clone details of a VolumeGroup',
        description='ViPR Clone show of a VolumeGroup CLI usage.')
    
    # Add parameter from common clone parser.
    volume_clone_get_parser(clone_get_parser)
    clone_get_parser.set_defaults(func=volume_group_clone_get)
    
# Get Clone Function
def volume_group_clone_get(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""
        
    try:
        vol = Volume(args.ip, args.port)
        cloneURI = vol.volume_query(args.tenant + "/" + args.project + "/" + args.clone)
        res= obj.volume_group_clone_get(args.name,
            cloneURI)
        
        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Clone show: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "clone",
                "show",
                e.err_text,
                e.err_code)   

# volume group snapshot routines
def snapshot_parser(subcommand_parsers, common_parser):
    snapshot_parser = subcommand_parsers.add_parser(
        'snapshot',
        description='ViPR VolumeGroup Snapshot CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='VolumeGroup Snapshot')

    mandatory_args = snapshot_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    mandatory_args.add_argument('-snapshotname', '-ssn',
                                metavar='<snapshotname>',
                                dest='snapshotname',
                                help='Name of Snapshot',
                                required=True)
    snapshot_parser.add_argument('-createinactive', '-ci',
                              dest='createinactive',
                              action='store_true',
                              help='Create snapshot with inactive state')
    snapshot_parser.add_argument('-readonly', '-ro',
                              dest='readonly',
                              action='store_true',
                              help='Create read only snapshot')
    snapshot_parser.add_argument('-partial',
                              dest='partial',
                              action='store_true',
                              help='To create snapshot for subset of VolumeGroup. ' +
                              'Please specify one volume from each Array Replication Group')
    snapshot_parser.add_argument('-volumes', '-v',
                            metavar='<volume_label,...>',
                            dest='volumes',
                            help='A list of volumes specifying their Array Replication Groups.' +
                            ' This field is valid only when partial flag is provided')
    snapshot_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')

    snapshot_parser.set_defaults(func=volume_group_snapshot)

def volume_group_snapshot(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""

    try:
        volumeUris = query_volumes_for_partial_request(args)
        obj.snapshot(args.name, args.snapshotname, args.createinactive, args.partial, ",".join(volumeUris), False)
        return

    except SOSError as e:
        common.format_err_msg_and_raise(
            "create",
            "volume group snapshot",
            e.err_text,
            e.err_code)

# Common Parser for snapshot operations
def volume_group_snapshot_common_parser(cc_common_parser):
    mandatory_args = cc_common_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    cc_common_parser.add_argument('-partial',
                              dest='partial',
                              action='store_true',
                              help='To operate on snapshots for subset of VolumeGroup. ' +
                              'Please specify one snapshot from each Array Replication Group')
    mandatory_args.add_argument('-snapshots', '-s',
                            metavar='<snapshotname,...>',
                            dest='snapshots',
                            help='A snapshot of a volume group specifying which snapshot Set to act on. ' +
                            'For partial operation, specify one snapshot from each Array Replication Group',
                            required=True)

    cc_common_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    cc_common_parser.add_argument('-synchronous', '-sync',
                                  dest='sync',
                                  action='store_true',
                                  help='Synchronous mode enabled')

def volume_group_snapshot_operation(args, operation, uri):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""

    try:
        obj.volume_group_snapshot_operation(
            args.name,
            args.snapshots, #",".join(snapshotUris),
            args.partial,
            args.sync,
            uri)
        return

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Snapshot " + operation + ": " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "snapshot",
                operation,
                e.err_text,
                e.err_code)

# snapshot_activate_parser
def snapshot_activate_parser(subcommand_parsers, common_parser):
    snapshot_activate_parser = subcommand_parsers.add_parser(
        'snapshot-activate',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Activate snapshot of a VolumeGroup',
        description='ViPR Activate Snapshot of a VolumeGroup CLI usage.')

    # Add parameter from common snapshot parser.
    volume_group_snapshot_common_parser(snapshot_activate_parser)
    snapshot_activate_parser.set_defaults(func=volume_group_snapshot_activate)

# Activate Snapshot Function
def volume_group_snapshot_activate(args):
    volume_group_snapshot_operation(args, "activate", VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_ACTIVATE)

# snapshot_deactivate_parser
def snapshot_deactivate_parser(subcommand_parsers, common_parser):
    snapshot_deactivate_parser = subcommand_parsers.add_parser(
        'snapshot-deactivate',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Deactivate snapshot of a VolumeGroup',
        description='ViPR Deactivate Snapshot of a VolumeGroup CLI usage.')

    # Add parameter from common snapshot parser.
    volume_group_snapshot_common_parser(snapshot_deactivate_parser)
    snapshot_deactivate_parser.set_defaults(func=volume_group_snapshot_deactivate)

# Deactivate Snapshot Function
def volume_group_snapshot_deactivate(args):
    volume_group_snapshot_operation(args, "deactivate", VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_DEACTIVATE)

# snapshot_restore_parser
def snapshot_restore_parser(subcommand_parsers, common_parser):
    snapshot_restore_parser = subcommand_parsers.add_parser(
        'snapshot-restore',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Restore snapshot of a VolumeGroup',
        description='ViPR Restore Snapshot of a VolumeGroup CLI usage.')

    # Add parameter from common snapshot parser.
    volume_group_snapshot_common_parser(snapshot_restore_parser)
    snapshot_restore_parser.set_defaults(func=volume_group_snapshot_restore)

# Restore Snapshot Function
def volume_group_snapshot_restore(args):
    volume_group_snapshot_operation(args, "restore", VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_RESTORE)

# snapshot_resync_parser
def snapshot_resync_parser(subcommand_parsers, common_parser):
    snapshot_resync_parser = subcommand_parsers.add_parser(
        'snapshot-resync',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Resynchronize snapshot of a VolumeGroup',
        description='ViPR Resynchronize Snapshot of a VolumeGroup CLI usage.')

    # Add parameter from common snapshot parser.
    volume_group_snapshot_common_parser(snapshot_resync_parser)
    snapshot_resync_parser.set_defaults(func=volume_group_snapshot_resync)

# Resynchronize Snapshot Function
def volume_group_snapshot_resync(args):
    volume_group_snapshot_operation(args, "resynchronize", VolumeGroup.URI_VOLUME_GROUP_SNAPSHOT_RESYNCHRONIZE)

# snapshot_list_parser
def snapshot_list_parser(subcommand_parsers, common_parser):
    snapshot_list_parser = subcommand_parsers.add_parser(
        'snapshot-list',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get Snapshot list of a VolumeGroup',
        description='ViPR List Snapshot of a VolumeGroup CLI usage.')

    mandatory_args = snapshot_list_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    snapshot_list_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    snapshot_list_parser.set_defaults(func=volume_group_snapshot_list)

# List Snapshot Function
def volume_group_snapshot_list(args):
    obj = VolumeGroup(args.ip, args.port)

    try:
        res= obj.volume_group_snapshot_list(args.name)
        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Snapshot List: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "snapshot",
                "list",
                e.err_text,
                e.err_code)

# snapshot_show_parser
def snapshot_show_parser(subcommand_parsers, common_parser):
    snapshot_show_parser = subcommand_parsers.add_parser(
        'snapshot-show',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show a Snapshot details of a VolumeGroup',
        description='ViPR Show Snapshot of a VolumeGroup CLI usage.')

    mandatory_args = snapshot_show_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    mandatory_args.add_argument('-snapshotname', '-ssn',
                                metavar='<snapshotname>',
                                dest='snapshotname',
                                help='Name of Snapshot',
                                required=True)
    snapshot_show_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')

    snapshot_show_parser.set_defaults(func=volume_group_snapshot_show)

# Get Snapshot Function
def volume_group_snapshot_show(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""

    try:
        res= obj.volume_group_snapshot_show(args.name,
            args.snapshotname)

        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Snapshot show: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "snapshot",
                "show",
                e.err_text,
                e.err_code)

# snapshot_get_sets_parser
def snapshot_get_sets_parser(subcommand_parsers, common_parser):
    snapshot_get_sets_parser = subcommand_parsers.add_parser(
        'snapshot-get-sets',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get copy set names of a VolumeGroup',
        description='ViPR Get Copy Set Names of a VolumeGroup CLI usage.')

    mandatory_args = snapshot_get_sets_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    snapshot_get_sets_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    snapshot_get_sets_parser.set_defaults(func=volume_group_snapshot_get_sets)

# Get Snapshot Sets Function
def volume_group_snapshot_get_sets(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""

    try:
        res= obj.volume_group_snapshot_get_sets(args.name)

        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Snapshot get sets: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "snapshot",
                "get sets",
                e.err_text,
                e.err_code)

# snapshot_get_parser
def snapshot_get_parser(subcommand_parsers, common_parser):
    snapshot_get_parser = subcommand_parsers.add_parser(
        'snapshot-get',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get snapshots of a VolumeGroup by set name',
        description='ViPR Get Snapshots of a VolumeGroup by Copy Set Name CLI usage.')

    mandatory_args = snapshot_get_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    snapshot_get_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    snapshot_get_parser.add_argument('-setname', '-sn',
                              dest='setname',
                              help='Copy set name',
                              required=True)
    snapshot_get_parser.set_defaults(func=volume_group_snapshot_get)

# Get Snapshots by Copy Set Name Function
def volume_group_snapshot_get(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""

    try:
        res= obj.volume_group_snapshot_get(args.name, args.setname)

        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Snapshots get" +
                args.name + " with " + args.setname +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "snapshot",
                "get snapshots by set name",
                e.err_text,
                e.err_code)

# volume group snapshot session routines
def snapshotsession_parser(subcommand_parsers, common_parser):
    snapshotsession_parser = subcommand_parsers.add_parser(
        'snapshotsession',
        description='ViPR VolumeGroup Snapshot Session CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='VolumeGroup Snapshot Session')

    mandatory_args = snapshotsession_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    mandatory_args.add_argument('-snapshotsessionname', '-ssn',
                                metavar='<snapshotsessionname>',
                                dest='snapshotsessionname',
                                help='Name of Snapshot Session',
                                required=True)
    snapshotsession_parser.add_argument('-copyonha', '-ha',
                              action='store_true',
                              help='Create snapshot session on HA side of VPLEX Distributed volumes')
    snapshotsession_parser.add_argument('-readonly', '-ro',
                              dest='readonly',
                              action='store_true',
                              help='Create read only snapshot session')
    snapshotsession_parser.add_argument('-partial',
                              dest='partial',
                              action='store_true',
                              help='To create snapshot session for subset of VolumeGroup. ' +
                              'Please specify one volume from each Array Replication Group')
    snapshotsession_parser.add_argument('-volumes', '-v',
                            metavar='<volume_label,...>',
                            dest='volumes',
                            help='A list of volumes specifying their Array Replication Groups.' +
                            ' This field is valid only when partial flag is provided')
    snapshotsession_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')

    snapshotsession_parser.set_defaults(func=volume_group_snapshotsession)

def volume_group_snapshotsession(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""

    try:
        volumeUris = query_volumes_for_partial_request(args)
        obj.snapshotsession(args.name, args.snapshotsessionname, args.copyonha, args.partial, ",".join(volumeUris), False)
        return

    except SOSError as e:
        common.format_err_msg_and_raise(
            "create",
            "volume group snapshot session",
            e.err_text,
            e.err_code)

# snapshotsession_list_parser
def snapshotsession_list_parser(subcommand_parsers, common_parser):
    snapshotsession_list_parser = subcommand_parsers.add_parser(
        'snapshotsession-list',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get Snapshot Session list of a VolumeGroup',
        description='ViPR List Snapshot Session of a VolumeGroup CLI usage.')

    mandatory_args = snapshotsession_list_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    snapshotsession_list_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    snapshotsession_list_parser.set_defaults(func=volume_group_snapshotsession_list)

# List Snapshot Session Function
def volume_group_snapshotsession_list(args):
    obj = VolumeGroup(args.ip, args.port)

    try:
        res= obj.volume_group_snapshotsession_list(args.name)
        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Snapshot Session List: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "snapshot session",
                "list",
                e.err_text,
                e.err_code)

# snapshotsession_show_parser
def snapshotsession_show_parser(subcommand_parsers, common_parser):
    snapshotsession_show_parser = subcommand_parsers.add_parser(
        'snapshotsession-show',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show a Snapshot Session details of a VolumeGroup',
        description='ViPR Show Snapshot Session of a VolumeGroup CLI usage.')

    mandatory_args = snapshotsession_show_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    mandatory_args.add_argument('-snapshotsessionname', '-ssn',
                                metavar='<snapshotsessionname>',
                                dest='snapshotsessionname',
                                help='Name of Snapshot Session',
                                required=True)
    snapshotsession_show_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')

    snapshotsession_show_parser.set_defaults(func=volume_group_snapshotsession_show)

# Show Snapsnot Session Function
def volume_group_snapshotsession_show(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""

    try:
        res= obj.volume_group_snapshotsession_show(args.name,
            args.snapshotsessionname)

        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Snapshot Session Show: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "snapshot session",
                "show",
                e.err_text,
                e.err_code)

# snapshotsession_get_sets_parser
def snapshotsession_get_sets_parser(subcommand_parsers, common_parser):
    snapshotsession_get_sets_parser = subcommand_parsers.add_parser(
        'snapshotsession-get-sets',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get Snapshot Session copy set names of a VolumeGroup',
        description='ViPR Get Snapshot Session Copy Set Names of a VolumeGroup CLI usage.')

    mandatory_args = snapshotsession_get_sets_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    snapshotsession_get_sets_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    snapshotsession_get_sets_parser.set_defaults(func=volume_group_snapshotsession_get_sets)

# Get Snapshot Session Copy Sets Function
def volume_group_snapshotsession_get_sets(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""

    try:
        res= obj.volume_group_snapshotsession_get_sets(args.name)

        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Snapshot Session Get Sets: " +
                args.name +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "snapshot session",
                "get sets",
                e.err_text,
                e.err_code)

# snapshotsession_get_parser
def snapshotsession_get_parser(subcommand_parsers, common_parser):
    snapshotsession_get_parser = subcommand_parsers.add_parser(
        'snapshotsession-get',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get Snapshot Session of a VolumeGroup by set name',
        description='ViPR Get Snapshot Session of a VolumeGroup by Copy Set Name CLI usage.')

    mandatory_args = snapshotsession_get_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of volume group',
                                required=True)
    snapshotsession_get_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    snapshotsession_get_parser.add_argument('-setname', '-sn',
                              dest='setname',
                              help='Copy set name',
                              required=True)
    snapshotsession_get_parser.set_defaults(func=volume_group_snapshotsession_get)

# Get Snapshot Session by Copy Set Name Function
def volume_group_snapshotsession_get(args):
    obj = VolumeGroup(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""

    try:
        res= obj.volume_group_snapshotsession_get(args.name, args.setname)

        return common.format_json_object(res)

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Snapshot Session Get" +
                args.name + " with " + args.setname +
                ", Failed\n" +
                e.err_text)
        else:
            common.format_err_msg_and_raise(
                "snapshot session",
                "get snapshot session by set name",
                e.err_text,
                e.err_code)

# VolumeGroup Main parser routine
def volume_group_parser(parent_subparser, common_parser):
    # main volume group parser

    parser = parent_subparser.add_parser('volumegroup',
                                         description='ViPR VolumeGroup CLI usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Operations on VolumeGroup')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # update command parser
    update_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # show command parser
    show_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

    # volume group tag parser
    tag_parser(subcommand_parsers, common_parser)
    
    # list volumes parser
    show_volume_group_volume_parser(subcommand_parsers, common_parser)
    
    # list child volume groups parser
    show_volume_group_children_parser(subcommand_parsers, common_parser)
    
    
    #clone
    # Clone create command parser
    clone_parser(subcommand_parsers, common_parser)
    
    # Clone activate command parser
    clone_activate_parser(subcommand_parsers, common_parser)
    
    # Clone detach command parser
    clone_detach_parser(subcommand_parsers, common_parser)
        
    # Clone restore command parser
    clone_restore_parser(subcommand_parsers, common_parser)
    
    # Clone resync command parser
    clone_resync_parser(subcommand_parsers, common_parser)
    
    # GET full-copy volumes of a volume group command parser
    clone_list_parser(subcommand_parsers, common_parser)
    
    # GET full-copy volume of a volume group command parser
    clone_get_parser(subcommand_parsers, common_parser)
    
    #snapshot
    # snapshot create command parser
    snapshot_parser(subcommand_parsers, common_parser)

    # snapshot activate command parser
    snapshot_activate_parser(subcommand_parsers, common_parser)

    # snapshot deactivate command parser
    snapshot_deactivate_parser(subcommand_parsers, common_parser)

    # snapshot restore command parser
    snapshot_restore_parser(subcommand_parsers, common_parser)

    # snapshot resync command parser
    snapshot_resync_parser(subcommand_parsers, common_parser)

    # Get snapshot list of a volume group command parser
    snapshot_list_parser(subcommand_parsers, common_parser)

    # Show snapshot of a volume group command parser
    snapshot_show_parser(subcommand_parsers, common_parser)

    # Get snapshot set names of a volume group command parser
    snapshot_get_sets_parser(subcommand_parsers, common_parser)

    # Get snapshots with set name of a volume group command parser
    snapshot_get_parser(subcommand_parsers, common_parser)

    # snapshot session
    # snapshot session create command parser
    snapshotsession_parser(subcommand_parsers, common_parser)

    # Get snapshot session list of a volume group command parser
    snapshotsession_list_parser(subcommand_parsers, common_parser)

    # Show snapshot session of a volume group command parser
    snapshotsession_show_parser(subcommand_parsers, common_parser)

    # Get snapshot session set names of a volume group command parser
    snapshotsession_get_sets_parser(subcommand_parsers, common_parser)

    # Get snapshot session with set name of a volume group command parser
    snapshotsession_get_parser(subcommand_parsers, common_parser)