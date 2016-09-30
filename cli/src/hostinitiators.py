#!/usr/bin/python

#
# Copyright (c) 2013 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.
#

import common
import json
from common import SOSError
from host import Host
from storagesystem import StorageSystem
import sys

'''
The class definition for the operation on the ViPR HostInitiator
'''


class HostInitiator(object):
    # Indentation START for the class

    '''
    /compute/initiators/search
    /compute/initiators/{id}
    /compute/initiators/{id}/deactivate
    /compute/initiators/{id}/exports
    '''
    # All URIs for the Host Initiator operations
    URI_INITIATOR_DETAILS = "/compute/initiators/{0}"
    URI_INITIATOR_DETAILS_BULK = "/compute/initiators/bulk"
    URI_HOST_LIST_INITIATORS = "/compute/hosts/{0}/initiators"
    URI_INITIATOR_DEACTIVATE = "/compute/initiators/{0}/deactivate"
    URI_INITIATOR_ALIASGET = "/compute/initiators/{0}/alias/{1}"
    URI_INITIATOR_ALIASSET = "/compute/initiators/{0}/alias"
    URI_INITIATOR_PAIR = "/compute/hosts/{0}/paired-initiators"
    URI_INITIATOR_ASSOCIATE = "/compute/initiators/{0}/associate/{1}"
    URI_INITIATOR_DISSOCIATE = "/compute/initiators/{0}/dissociate"

    INITIATOR_PROTOCOL_LIST = ['FC', 'iSCSI']

    __hostObject = None

    def __init__(self, ipAddr, port):
        '''
        Constructor: takes IP address and port of the ViPR instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__hostObject = Host(self.__ipAddr, self.__port)

    '''
    Returns the initiator URI for matching the name of the initiator
    '''

    def query_by_name(self, initiatorName, hostName):

        hostUri = self.get_host_uri(hostName)
        initiatorList = self.get_host_object().list_initiators(hostUri)

        # Match the name and return uri
        for initiator in initiatorList:
            if(initiator['name'] == initiatorName):
                return initiator['id']

        raise SOSError(
            SOSError.NOT_FOUND_ERR,
            "Initiator with name '" +
            initiatorName +
            "' not found")

    '''
    Returns the initiator URI for matching the name of the initiator
    '''

    def query_by_portwwn(self, initiatorWWN, hostName, tenant=None):
        hostUri = self.get_host_uri(hostName, tenant)
        initiatorList = self.get_host_object().list_initiators(hostUri)
       
        # Match the name and return uri
        for initiator in initiatorList:
            initiatorDetails = self.show_by_uri(initiator['id'])

            if(initiatorDetails and
               initiatorDetails['initiator_port'] == initiatorWWN):
                return initiator['id']

        raise SOSError(
            SOSError.NOT_FOUND_ERR,
            "Initiator with WWN '" +
            initiatorWWN +
            "' not found")

    """
    Initiator create operation
    """

    def create(self, sync, hostlabel, protocol, initiatorwwn, portwwn, initname,synctime, tenant):
        hostUri = self.get_host_uri(hostlabel, tenant)
        request = {'protocol': protocol,
                   'initiator_port': portwwn,
                   'name': initname
                   }

        if(initiatorwwn):
            request['initiator_node'] = initiatorwwn

        body = json.dumps(request)
      
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            HostInitiator.URI_HOST_LIST_INITIATORS.format(hostUri),
            body)
        o = common.json_decode(s)
        return self.check_for_sync(o, sync,synctime)
        
    """
    Initiator pair create operation
    """
    def create_pair(self, sync, hostlabel, protocol, initiatorwwn1, portwwn1, initname1,
                    initiatorwwn2, portwwn2, initname2, synctime, tenant):

        hostUri = self.get_host_uri(hostlabel, tenant)
        request = {
            "first_initiator": {
                "protocol": protocol,
                "initiator_node": initiatorwwn1,
                "initiator_port": portwwn1,
                "name": initname1
            },
            "second_initiator": {
                "protocol": protocol,
                "initiator_node": initiatorwwn2,
                "initiator_port": portwwn2,
                "name": initname2
            }
        }

        if(initiatorwwn1):
            request["first_initiator"]["initiator_node"] = initiatorwwn1
        if(initiatorwwn2):
            request["second_initiator"]["initiator_node"] = initiatorwwn2

        body = json.dumps(request)
      
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            HostInitiator.URI_INITIATOR_PAIR.format(hostUri),
            body)
        o = common.json_decode(s)
        return self.check_for_sync(o, sync,synctime)
        
    """
    Associate initiators operation
    """
    def associate_initiator(self, initiatorUri, associatedInitiatorUri):

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "PUT",
            HostInitiator.URI_INITIATOR_ASSOCIATE.format(initiatorUri, associatedInitiatorUri),
            None)
        o = common.json_decode(s)
        return o
        
    """
    Dissociate initiators operation
    """
    def dissociate_initiator(self, initiatorUri):
              
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "PUT",
            HostInitiator.URI_INITIATOR_DISSOCIATE.format(initiatorUri),
            None)
        o = common.json_decode(s)
        return o
    
    """
    Initiator update operation
    """

    def update(self, initiatorUri, newprotocol, newinitiatorwwn, newportwwn, newinitname):

        request = dict()

        if(newprotocol):
            request['protocol'] = newprotocol

        if(newinitiatorwwn):
            request['initiator_node'] = newinitiatorwwn

        if(newportwwn):
            request['initiator_port'] = newportwwn
            
        if(newinitname):
            request['name'] = newinitname    

        body = json.dumps(request)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "PUT",
            HostInitiator.URI_INITIATOR_DETAILS.format(initiatorUri),
            body)
        o = common.json_decode(s)
        return o

    """
    Initiator delete operation
    """

    def delete(self, initiator_uri):
        '''
        Makes a REST API call to delete a initiator by its UUID
        '''
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "POST",
            HostInitiator.URI_INITIATOR_DEACTIVATE.format(initiator_uri),
            None)
        return

    '''
    Lists all initiators present in the system
    returns list of initiator elements
    <initiator>
     <name>...</name>
     <id>...</id>
     <link rel="..." href="..." />
    </initiator>
    '''

    def list_all(self):

        initiatorsList = []
        # Get all hosts in the system
        hostUris = self.__hostObject.list_host_uris()

        # Get the list of initiators from each host
        if(hostUris.__len__() > 0):
            for host in hostUris:
                tempInitiatorList = self.__hostObject.list_initiators(host)
                if(tempInitiatorList.__len__() > 0):
                    for tempInitiator in tempInitiatorList:
                        initiatorsList.append(tempInitiator)
        else:
            raise SOSError(
                SOSError.NOT_FOUND_ERR,
                "No initiators found in the system")

        return initiatorsList

    '''
    Lists all initiator uris present in the system
    '''

    def list_all_by_uri(self):

        initiatorsList = []
        # Get all hosts in the system
        hostUris = self.__hostObject.list_host_uris()

        # Get the list of initiators from each host
        if(hostUris.__len__() > 0):
            for host in hostUris:
                tempInitiatorList = self.__hostObject.list_initiators(host)
                if(tempInitiatorList.__len__() > 0):
                    for tempInitiator in tempInitiatorList:
                        initiatorsList.append(tempInitiator['id'])
        else:
            raise SOSError(
                SOSError.NOT_FOUND_ERR,
                "No hosts found in the system")

        return initiatorsList

    '''
    Gets the list  of initiator names
    '''

    def list_all_by_name(self):
        initiatorsList = []
        # Get all hosts in the system
        hostUris = self.__hostObject.list_host_uris()

        # Get the list of initiators from each host
        if(hostUris.__len__() > 0):
            for host in hostUris:
                tempInitiatorList = self.__hostObject.list_initiators(host)
                if(tempInitiatorList.__len__() > 0):
                    for tempInitiator in tempInitiatorList:
                        initiatorsList.append(tempInitiator['name'])
        else:
            raise SOSError(
                SOSError.NOT_FOUND_ERR,
                "No hosts found in the system")

        return initiatorsList

    """
    Gets details of list of initiators
    """

    def show(self, initiatorList):
        initiatorListDetails = []
        if(initiatorList is not None):
            for initiator in initiatorList:
                initiatorUri = initiator['id']
                hostDetail = self.show_by_uri(initiatorUri)
                if(hostDetail is not None and len(hostDetail) > 0):
                    initiatorListDetails.append(hostDetail)

        return initiatorListDetails

    """
    Gets initiator details matching the protocol type
    """

    def show_by_protocol(self, initiatorList, protocol):
        initiatorListDetails = []
        if(initiatorList is not None):
            for initiator in initiatorList:
                initiatorUri = initiator['id']
                initiatorDetail = self.show_by_uri(initiatorUri)
                if(initiatorDetail and
                   len(initiatorDetail) > 0 and
                   initiatorDetail['protocol'] == protocol):
                    initiatorListDetails.append(initiatorDetail)

        return initiatorListDetails

    """
    Gets initiator details matching the name
    """

    def show_by_name(self, initiatorList, name, xml):
        initiatorListDetails = None
        if(initiatorList is not None):
            for initiator in initiatorList:
                initiatorUri = initiator['id']
                initiatorDetail = self.show_by_uri(initiatorUri)
                if(initiatorDetail is not None and len(initiatorDetail) > 0
                   and initiatorDetail['name'] == name):
                    if(xml):
                        initiatorListDetails = self.show_by_uri(
                            initiatorUri,
                            xml)
                    else:
                        initiatorListDetails = initiatorDetail
                    break

        return initiatorListDetails

    """
    Gets initiator details matching the wwn
    """

    def show_by_initiatorwwn(self, initiatorList, name, xml):
        initiatorListDetails = None
        if(initiatorList is not None):
            for initiator in initiatorList:
                initiatorUri = initiator['id']
                initiatorDetail = self.show_by_uri(initiatorUri)
                if(initiatorDetail is not None and len(initiatorDetail) > 0
                   and initiatorDetail['initiator_node'] == name):
                    if(xml):
                        initiatorListDetails = self.show_by_uri(
                            initiatorUri,
                            xml)
                    else:
                        initiatorListDetails = initiatorDetail
                    break

        return initiatorListDetails

    """
    Gets details of the initiator for a given uri
    """

    def show_by_uri(self, uri, xml=False):
        '''
        Makes a REST API call to retrieve details of a Host based on its UUID
        '''
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "GET",
            HostInitiator.URI_INITIATOR_DETAILS.format(uri),
            None, None)
        o = common.json_decode(s)
        inactive = common.get_node_value(o, 'inactive')

        if(inactive):
            return None
        if(xml):
            (s, h) = common.service_json_request(
                self.__ipAddr, self.__port, "GET",
                HostInitiator.URI_INITIATOR_DETAILS.format(uri),
                None, None, xml)
            return s
        else:
            return o

    '''
    Given the name of the host, returns the hostUri/id
    '''

    def get_host_uri(self, hostName, tenant=None):
        return self.__hostObject.query_by_name(hostName, tenant)

    def get_host_object(self):
        return self.__hostObject

    def list_tasks(self, host_name, initiatorportwwn, task_id=None, tenant=None):

        uri = self.query_by_portwwn(initiatorportwwn, host_name, tenant)
        
      

        hostinitiator = self.show_by_uri(uri)
        if(hostinitiator['initiator_port'] == initiatorportwwn):
            if(not task_id):
                
                return common.get_tasks_by_resourceuri(
                    "initiator", uri, self.__ipAddr, self.__port)

            else:
                
                res = common.get_task_by_resourceuri_and_taskId(
                    "initiator", uri, task_id,
                    self.__ipAddr, self.__port)
                if(res):
                    return res
        raise SOSError(
            SOSError.NOT_FOUND_ERR,
            "Initiator with Initiatorportwwn : " +
            initiatorportwwn +
            " not found")

    def check_for_sync(self, result, sync,synctime):
        if(sync):
            if(len(result["resource"]) > 0):
                resource = result["resource"]
                
                return (
                    common.block_until_complete("initiator", resource["id"],
                                                result["id"], self.__ipAddr,
                                                self.__port,synctime)
                                                
                                    
                )
            else:
                
                raise SOSError(
                    SOSError.SOS_FAILURE_ERR,
                    "error: task list is empty, no task response found")
        else:
            return result

    '''
    show all tasks by initiator uri
    '''

    def show_task_by_uri(self, initiator_uri, task_id=None):

        if(not task_id):
            return (
                common.get_tasks_by_resourceuri(
                    "initiator", initiator_uri, self.__ipAddr, self.__port)
            )
        else:
            return (
                common.get_task_by_resourceuri_and_taskId(
                    "initiator", initiator_uri, task_id,
                    self.__ipAddr, self.__port)
            )

    """
    Initiator alias get operation
    """

    def aliasget(self, initiator_uri, device_name, device_type):
        '''
        Makes a REST API call to get the initiator alias against a storage system
        '''
        from storagesystem import StorageSystem
        obj = StorageSystem(self.__ipAddr, self.__port)
        device_detail = obj.show(name=device_name, type=device_type)
        system_uri = device_detail['id']

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "GET",
            HostInitiator.URI_INITIATOR_ALIASGET.format(initiator_uri, system_uri),
            None)
        o = common.json_decode(s)
        return o


    """
    Initiator alias set operation
    """

    def aliasset(self, initiator_uri, device_name, device_type, alias):
        '''
        Makes a REST API call to get the initiator alias against a storage system
        '''

        from storagesystem import StorageSystem
        obj = StorageSystem(self.__ipAddr, self.__port)
        device_detail = obj.show(name=device_name, type=device_type)
        system_uri = device_detail['id']

        request = {'system_uri': system_uri,
                   'initiator_alias': alias
                   }
        body = json.dumps(request)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "PUT",
            HostInitiator.URI_INITIATOR_ALIASSET.format(initiator_uri),
            body)
        o = common.json_decode(s)
        return o

    # Indentation END for the class
# Start Parser definitions
def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ViPR Initiator create CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Creates an Initiator')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument(
        '-hl', '-hostlabel',
        help='Host label in which initiator needs to be created',
        metavar='<hostlabel>',
        dest='hostlabel',
        required=True)
    mandatory_args.add_argument('-pl', '-protocol ',
                                choices=HostInitiator.INITIATOR_PROTOCOL_LIST,
                                dest='protocol',
                                help='Initiator protocol',
                                required=True)

    create_parser.add_argument('-wwn', '-initiatorwwn',
                               help='WWN of the initiator node ',
                               dest='initiatorwwn',
                               metavar='<initiatorwwn>')

    create_parser.add_argument('-synchronous', '-sync',
                               dest='sync',
                               help='Execute in synchronous mode',
                               action='store_true')
    create_parser.add_argument('-synctimeout','-syncto',
                               help='sync timeout in seconds ',
                               dest='synctimeout',
                               default=0,
                               type=int)
    
    create_parser.add_argument('-initiatorname', '-initname',
                               help='Initiator Alias Name',
                               dest='initname',
                               metavar='<initiatorname>' )
    
    create_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>')

    mandatory_args.add_argument(
        '-pwwn', '-initiatorportwwn',
        help='Port wwn, it can be WWN for FC, IQN/EUI for iSCSI',
        dest='initiatorportwwn',
        metavar='<initiatorportwwn>',
        required=True)

    create_parser.set_defaults(func=initiator_create)

'''
Preprocessor for the initiator create operation
'''


def initiator_create(args):
    if not args.sync and args.synctimeout !=0:
        raise SOSError(SOSError.CMD_LINE_ERR,"error: Cannot use synctimeout without Sync ")
    if(args.protocol == "FC" and args.initiatorwwn is None):
        raise SOSError(
            SOSError.CMD_LINE_ERR, sys.argv[0] + " " + sys.argv[1] +
            " " + sys.argv[2] + ": error:" +
            "-initiatorwwn is required for FC type initiator")

    if(args.protocol == "iSCSI" and args.initiatorwwn):
        raise SOSError(
            SOSError.CMD_LINE_ERR, sys.argv[0] + " " + sys.argv[1] +
            " " + sys.argv[2] + ": error:" +
            "-initiatorwwn is not required for iSCSI type initiator")

    initiatorObj = HostInitiator(args.ip, args.port)
    try:
        initiatorObj.create(
            args.sync,
            args.hostlabel,
            args.protocol,
            args.initiatorwwn,
            args.initiatorportwwn,
            args.initname,args.synctimeout,
            args.tenant)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "create",
            "initiator",
            e.err_text,
            e.err_code)
            

def create_pair_parser(subcommand_parsers, common_parser):
    # create command parser
    create_pair_parser = subcommand_parsers.add_parser(
        'create-pair',
        description='ViPR initiator pair create CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Creates a pair of initiators and links them together')

    mandatory_args = create_pair_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument(
        '-hl', '-hostlabel',
        help='Host label in which initiator needs to be created',
        metavar='<hostlabel>',
        dest='hostlabel',
        required=True)
    mandatory_args.add_argument('-pl', '-protocol ',
                                choices=HostInitiator.INITIATOR_PROTOCOL_LIST,
                                dest='protocol',
                                help='Initiator protocol',
                                required=True)
    mandatory_args.add_argument(
        '-pwwn1', '-initiatorportwwn1',
        help='Port WWN of the first initiator, it can be WWN for FC, IQN/EUI for iSCSI',
        dest='initiatorportwwn1',
        metavar='<initiatorportwwn1>',
        required=True)
    mandatory_args.add_argument(
        '-pwwn2', '-initiatorportwwn2',
        help='Port WWN of the second initiator, it can be WWN for FC, IQN/EUI for iSCSI',
        dest='initiatorportwwn2',
        metavar='<initiatorportwwn2>',
        required=True)

    create_pair_parser.add_argument('-wwn1', '-initiatorwwn',
                               help='WWN of the first initiator node ',
                               dest='initiatorwwn1',
                               metavar='<initiatorwwn1>')
                               
    create_pair_parser.add_argument('-wwn2', '-initiatorwwn2',
                               help='WWN of the second initiator node',
                               dest='initiatorwwn2',
                               metavar='<initiatorwwn2>')

    create_pair_parser.add_argument('-synchronous', '-sync',
                               dest='sync',
                               help='Execute in synchronous mode',
                               action='store_true')
    create_pair_parser.add_argument('-synctimeout','-syncto',
                               help='sync timeout in seconds ',
                               dest='synctimeout',
                               default=0,
                               type=int)
    
    create_pair_parser.add_argument('-initiatorname1', '-initname1',
                               help='Alias for first initiator',
                               dest='initname1',
                               metavar='<initiatorname1>')
    create_pair_parser.add_argument('-initiatorname2', '-initname2',
                               help='Alias for second initiator',
                               dest='initname2',
                               metavar='<initiatorname2>' )
    
    create_pair_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>')

    create_pair_parser.set_defaults(func=initiator_pair_create)
    
def initiator_pair_create(args):
    if not args.sync and args.synctimeout !=0:
        raise SOSError(SOSError.CMD_LINE_ERR,"error: Cannot use synctimeout without Sync ")
    if(args.protocol == "FC" and args.initiatorwwn1 is None):
        raise SOSError(
            SOSError.CMD_LINE_ERR, sys.argv[0] + " " + sys.argv[1] +
            " " + sys.argv[2] + ": error:" +
            "-initiatorwwn1 is required for first initiator of type FC")

    if(args.protocol == "iSCSI" and args.initiatorwwn1):
        raise SOSError(
            SOSError.CMD_LINE_ERR, sys.argv[0] + " " + sys.argv[1] +
            " " + sys.argv[2] + ": error:" +
            "-initiatorwwn1 is required for first initiator of type iSCSI")
            
    if(args.protocol == "FC" and args.initiatorwwn2 is None):
        raise SOSError(
            SOSError.CMD_LINE_ERR, sys.argv[0] + " " + sys.argv[1] +
            " " + sys.argv[2] + ": error:" +
            "-initiatorwwn2 is required for second initiator of type FC")

    if(args.protocol == "iSCSI" and args.initiatorwwn1):
        raise SOSError(
            SOSError.CMD_LINE_ERR, sys.argv[0] + " " + sys.argv[1] +
            " " + sys.argv[2] + ": error:" +
            "-initiatorwwn2 is required for second initiator of type iSCSI")

    initiatorObj = HostInitiator(args.ip, args.port)
    try:
        initiatorObj.create_pair(
            args.sync,
            args.hostlabel,
            args.protocol,
            args.initiatorwwn1,
            args.initiatorportwwn1,
            args.initname1,
            args.initiatorwwn2,
            args.initiatorportwwn2,
            args.initname2,
            args.synctimeout,
            args.tenant)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "create",
            "initiator pair",
            e.err_text,
            e.err_code)
            


# list command parser
def list_parser(subcommand_parsers, common_parser):
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ViPR Initiator List CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Lists initiators')
    mandatory_args = list_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-hl', '-hostlabel',
                                dest='hostlabel',
                                metavar='<hostlabel>',
                                help='Host for which initiators to be listed',
                                required=True)
    list_parser.add_argument('-pl', '-protocol ',
                             choices=HostInitiator.INITIATOR_PROTOCOL_LIST,
                             dest='protocol',
                             help='Initiator protocol')
    list_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>' )
    list_parser.add_argument('-v', '-verbose',
                             dest='verbose',
                             action='store_true',
                             help='Lists Initiators with details')
    list_parser.add_argument('-l', '-long',
                             dest='largetable',
                             action='store_true',
                             help='Lists Initiators in a large table')
    list_parser.set_defaults(func=initiator_list)


'''
Preprocessor for initiator list operation
'''


def initiator_list(args):

    initiatorList = None
    initiatorObj = HostInitiator(args.ip, args.port)
    from common import TableGenerator

    try:
        if(args.hostlabel):
            hostUri = initiatorObj.get_host_uri(args.hostlabel, args.tenant)
            initiatorList = initiatorObj.get_host_object().list_initiators(
                hostUri)
        else:
            initiatorList = initiatorObj.list_all()

        if(len(initiatorList) > 0):
            initiatorListDetails = []
            if(args.protocol is None):
                initiatorListDetails = initiatorObj.show(initiatorList)
            else:
                initiatorListDetails = initiatorObj.show_by_protocol(
                    initiatorList,
                    args.protocol)

            if(args.verbose):
                return common.format_json_object(initiatorListDetails)
            else:
                if(args.largetable):
                    for item in initiatorListDetails:
                        if(not ('initiator_node' in item) or item['initiator_node']==""):
                            item['initiator_node']=' '
                    TableGenerator(
                        initiatorListDetails,
                        ['initiator_node',
                         'initiator_port',
                         'protocol']).printTable()
                else:
                    TableGenerator(
                        initiatorListDetails,
                        ['initiator_port']).printTable()

    except SOSError as e:
        common.format_err_msg_and_raise(
            "list",
            "initiator",
            e.err_text,
            e.err_code)


# show command parser
def show_parser(subcommand_parsers, common_parser):
    show_parser = subcommand_parsers.add_parser(
        'show',
        description='ViPR Initiator Show CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show Initiator details')
    show_parser.add_argument('-xml',
                             dest='xml',
                             action='store_true',
                             help='XML response')
    mandatory_args = show_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-pwwn', '-initiatorportwwn',
                                metavar='<name>',
                                dest='initiatorportwwn',
                                help='Port WWN of initiator',
                                required=True)
    show_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>' )
    mandatory_args.add_argument(
        '-hl', '-hostlabel',
        dest='hostlabel',
        metavar='<hostlabel>',
        help='Host for which initiators to be searched',
        required=True)
    show_parser.set_defaults(func=initiator_show)


def initiator_show(args):

    try:
        initiatorObj = HostInitiator(args.ip, args.port)
        initiatorUri = initiatorObj.query_by_portwwn(
            args.initiatorportwwn,
            args.hostlabel, args.tenant)
        if(initiatorUri):
            initiatorDetails = initiatorObj.show_by_uri(initiatorUri, args.xml)

        if(args.xml):
            return common.format_xml(initiatorDetails)
        return common.format_json_object(initiatorDetails)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "show",
            "initiator",
            e.err_text,
            e.err_code)

    return
    

# associate initiator command parser
def initiator_associate_parser(subcommand_parsers, common_parser):
    associate_initiator_parser = subcommand_parsers.add_parser(
        'associate',
        description='ViPR Associate Initiator CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Associate (pair) two existing initiators')

    mandatory_args = associate_initiator_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-hl', '-hostlabel',
                                help='Host label in which initiator needs to be created',
                                metavar='<hostlabel>',
                                dest='hostlabel',
                                required=True)
    mandatory_args.add_argument('-pwwn1', '-initiatorportwwn1',
                                metavar='<name1>',
                                dest='initiatorportwwn1',
                                help='Port WWN of first initiator',
                                required=True)
    mandatory_args.add_argument('-pwwn2', '-initiatorportwwn2',
                                metavar='<name2>',
                                dest='initiatorportwwn2',
                                help='Port WWN of initiator to be associated with first initiator',
                                required=True)
    associate_initiator_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>' )
    associate_initiator_parser.set_defaults(func=initiator_associate)


def initiator_associate(args):

    try:
        initiatorObj = HostInitiator(args.ip, args.port)
        initiatorUri1 = initiatorObj.query_by_portwwn(
            args.initiatorportwwn1,
            args.hostlabel, args.tenant)

        initiatorUri2 = initiatorObj.query_by_portwwn(
            args.initiatorportwwn2,
            args.hostlabel, args.tenant)
        
        initiatorObj.associate_initiator(initiatorUri1, initiatorUri2)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "associate",
            "initiator",
            e.err_text,
            e.err_code)

    return
    

    # disociate initiator command parser
def initiator_dissociate_parser(subcommand_parsers, common_parser):
    dissociate_initiator_parser = subcommand_parsers.add_parser(
        'dissociate',
        description='ViPR Dissociate Initiator CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Dissociate existing initiator pair')

    mandatory_args = dissociate_initiator_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-hl', '-hostlabel',
                                help='Host label in which initiator needs to be created',
                                metavar='<hostlabel>',
                                dest='hostlabel',
                                required=True)
    mandatory_args.add_argument('-pwwn', '-initiatorportwwn',
                                metavar='<name>',
                                dest='initiatorportwwn',
                                help='Port WWN of initiator',
                                required=True)
    dissociate_initiator_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>' )
    dissociate_initiator_parser.set_defaults(func=initiator_dissociate)


def initiator_dissociate(args):

    try:
        initiatorObj = HostInitiator(args.ip, args.port)
        initiatorUri = initiatorObj.query_by_portwwn(
            args.initiatorportwwn,
            args.hostlabel, args.tenant)
        
        initiatorObj.dissociate_initiator(initiatorUri)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "associate",
            "initiator",
            e.err_text,
            e.err_code)

    return


def delete_parser(subcommand_parsers, common_parser):
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ViPR Initiator delete CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Deletes an Initiator')
    mandatory_args = delete_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-pwwn', '-initiatorportwwn',
                                metavar='<initiatorportwwn>',
                                dest='initiatorportwwn',
                                help='Port WWN of the Initiator to be deleted',
                                required=True)
    mandatory_args.add_argument('-hl', '-hostlabel',
                                dest='hostlabel',
                                metavar='<hostlabel>',
                                help='Host for which initiator to be searched',
                                required=True)
    delete_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>' )
    delete_parser.set_defaults(func=initiator_delete)


def initiator_delete(args):
    try:

        initiatorObj = HostInitiator(args.ip, args.port)
        initiatorUri = initiatorObj.query_by_portwwn(
            args.initiatorportwwn,
            args.hostlabel, args.tenant)
        initiatorObj.delete(initiatorUri)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "delete",
            "initiator",
            e.err_text,
            e.err_code)

    return


'''
Update Host Parser
'''


def update_parser(subcommand_parsers, common_parser):
    # create command parser
    update_parser = subcommand_parsers.add_parser(
        'update',
        description='ViPR Host update CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Updates an Initiator')

    mandatory_args = update_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-pwwn', '-initiatorportwwn',
                                help='Port WWN of the initiator to be updated',
                                metavar='<initiatorportwwn>',
                                dest='initiatorportwwn',
                                required=True)
    mandatory_args.add_argument(
        '-hl', '-hostlabel',
        dest='hostlabel',
        metavar='<hostlabel>',
        help='Host for which initiators to be searched',
        required=True)

    update_parser.add_argument(
        '-npl', '-newprotocol ',
        choices=HostInitiator.INITIATOR_PROTOCOL_LIST,
        dest='newprotocol',
        help='Initiator protocol')

    update_parser.add_argument(
        '-nwwn', '-newinitiatorwwn',
        help='WWN of the initiator node ',
        dest='newinitiatorwwn',
        metavar='<newinitiatorwwn>')
    
    update_parser.add_argument('-newinitiatorname', '-newinitname',
                               help='Initiator Alias Name',
                               dest='newinitname',
                               metavar='<newinitiatorname>' )
    
    update_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>' )

    mandatory_args.add_argument(
        '-npwwn', '-newinitiatorportwwn',
        help='Port wwn, it can be WWN for FC, IQN/EUI for iSCSI',
        dest='newinitiatorportwwn',
        metavar='<newinitiatorportwwn>',
        required=True)

    update_parser.set_defaults(func=initiator_update)


'''
Preprocessor for the host update operation
'''


def initiator_update(args):

    if(args.newprotocol is None and
       args.newinitiatorwwn is None and
       args.newinitiatorportwwn is None):
        raise SOSError(SOSError.CMD_LINE_ERR, sys.argv[0] + " " + sys.argv[1] +
                       " " + sys.argv[2] + ": error:" +
                       "At least one of the arguments :"
                       "-newprotocol -newinitiatorwwn -newinitiatorportwwn"
                       " should be provided to update the Host")
    if(args.newprotocol == "iSCSI" and args.newinitiatorwwn):
        raise SOSError(SOSError.CMD_LINE_ERR, sys.argv[0] + " " + sys.argv[1] +
                       " " + sys.argv[2] + ": error: -newinititorwwn " +
                       "is not required for iSCSI type initiator")

    initiatorObj = HostInitiator(args.ip, args.port)
    try:

        initiatorUri = initiatorObj.query_by_portwwn(
            args.initiatorportwwn,
            args.hostlabel, args.tenant)
        initiatorObj.update(
            initiatorUri,
            args.newprotocol,
            args.newinitiatorwwn,
            args.newinitiatorportwwn,
            args.newinitname)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "update",
            "initiator",
            e.err_text,
            e.err_code)

#
# Host Main parser routine
#


def task_parser(subcommand_parsers, common_parser):
    # show command parser
    task_parser = subcommand_parsers.add_parser(
        'tasks',
        description='ViPR host initiator tasks  CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='check tasks of a host initiator')

    mandatory_args = task_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-pwwn', '-initiatorportwwn',
                                metavar='<initiatorportwwn>',
                                dest='initiatorportwwn',
                                help='Port WWN of the Initiator to be searched',
                                required=True)
    mandatory_args.add_argument('-hl', '-hostlabel',
                                dest='hostlabel',
                                metavar='<hostlabel>',
                                help='Host for which initiator to be searched',
                                required=True)
    task_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>' )

    task_parser.add_argument('-id',
                             dest='id',
                             metavar='<id>',
                             help='Task ID')

    task_parser.add_argument('-v', '-verbose',
                             dest='verbose',
                             action="store_true",
                             help='List all tasks')

    task_parser.set_defaults(func=host_initiator_list_tasks)


def host_initiator_list_tasks(args):
    obj = HostInitiator(args.ip, args.port)

    try:
        # if(not args.tenant):
        #    args.tenant = ""
        if(args.id):
            res = obj.list_tasks(
                args.hostlabel,
                args.initiatorportwwn,
                args.id, args.tenant)
            if(res):
                return common.format_json_object(res)
        elif(args.hostlabel):
           
            res = obj.list_tasks(args.hostlabel, args.initiatorportwwn, None, args.tenant)
           
            if(res and len(res) > 0):
                if(args.verbose):
                    return common.format_json_object(res)
                else:
                    from common import TableGenerator
                    TableGenerator(res, ["module/id",
                                         "state"]).printTable()

    except SOSError as e:
        common.format_err_msg_and_raise("get tasks list", "initiator",
                                        e.err_text, e.err_code)

#
# initiator alias get parser
#
def aliasget_parser(subcommand_parsers, common_parser):
    aliasget_parser = subcommand_parsers.add_parser(
        'aliasget',
        description='ViPR Initiator aliasget CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Gets the alias of an Initiator against a storage system if set')
    mandatory_args = aliasget_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-pwwn', '-initiatorportwwn',
                                metavar='<initiatorportwwn>',
                                dest='initiatorportwwn',
                                help='Port WWN of the Initiator to be deleted',
                                required=True)
    mandatory_args.add_argument('-hl', '-hostlabel',
                                dest='hostlabel',
                                metavar='<hostlabel>',
                                help='Host for which initiator to be searched',
                                required=True)
    mandatory_args.add_argument('-n', '-name',
                                metavar='<name>',
                                dest='name',
                                help='Name of storage system',
                                required=True)
    mandatory_args.add_argument('-t', '-type',
                                choices=StorageSystem.SYSTEM_TYPE_LIST,
                                dest='type',
                                help='Type of storage system',
                                required=True)
    aliasget_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>' )
    aliasget_parser.set_defaults(func=initiator_aliasget)


def initiator_aliasget(args):
    try:

        initiatorObj = HostInitiator(args.ip, args.port)
        initiatorUri = initiatorObj.query_by_portwwn(
            args.initiatorportwwn,
            args.hostlabel, args.tenant)
        alias = initiatorObj.aliasget(initiatorUri,args.name, args.type)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "aliasget",
            "initiator",
            e.err_text,
            e.err_code)

    return alias['initiator_alias']

#
# initiator alias set parser
#
def aliasset_parser(subcommand_parsers, common_parser):
    aliasset_parser = subcommand_parsers.add_parser(
        'aliasset',
        description='ViPR Initiator aliasset CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Sets the alias of an Initiator against a storage system')
    mandatory_args = aliasset_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-pwwn', '-initiatorportwwn',
                                metavar='<initiatorportwwn>',
                                dest='initiatorportwwn',
                                help='Port WWN of the Initiator to be deleted',
                                required=True)
    mandatory_args.add_argument('-hl', '-hostlabel',
                                dest='hostlabel',
                                metavar='<hostlabel>',
                                help='Host for which initiator to be searched',
                                required=True)
    mandatory_args.add_argument('-n', '-name',
                                metavar='<name>',
                                dest='name',
                                help='Name of storage system',
                                required=True)
    mandatory_args.add_argument('-t', '-type',
                                choices=StorageSystem.SYSTEM_TYPE_LIST,
                                dest='type',
                                help='Type of storage system',
                                required=True)
    mandatory_args.add_argument('-ia', '-initiatoralias',
                                dest='alias',
                                metavar='<alias>',
                                help='Alias name that needs to be set',
                                required=True)
    aliasset_parser.add_argument('-tenantname', '-tn',
                               help='Tenant Name',
                               dest='tenant',
                               metavar='<tenantname>' )
    aliasset_parser.set_defaults(func=initiator_aliasset)


def initiator_aliasset(args):
    try:

        initiatorObj = HostInitiator(args.ip, args.port)
        initiatorUri = initiatorObj.query_by_portwwn(
            args.initiatorportwwn,
            args.hostlabel, args.tenant)
        initiatorObj.aliasset(initiatorUri, args.name, args.type, args.alias)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "aliasset",
            "initiator",
            e.err_text,
            e.err_code)

    return

def initiator_parser(parent_subparser, common_parser):

    parser = parent_subparser.add_parser(
        'initiator',
        description='ViPR initiator CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on initiator')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

    # show parser
    show_parser(subcommand_parsers, common_parser)

    # delete parser
    delete_parser(subcommand_parsers, common_parser)

    # update parser
    update_parser(subcommand_parsers, common_parser)

    # task parser
    task_parser(subcommand_parsers, common_parser)

    # alias get parser
    aliasget_parser(subcommand_parsers, common_parser)

    # alias set parser
    aliasset_parser(subcommand_parsers, common_parser)
    
    # create paired initiators parser
    create_pair_parser(subcommand_parsers, common_parser)
    
    # associate initiator command parser
    initiator_associate_parser(subcommand_parsers, common_parser)

    # disociate initiator command parser
    initiator_dissociate_parser(subcommand_parsers, common_parser)