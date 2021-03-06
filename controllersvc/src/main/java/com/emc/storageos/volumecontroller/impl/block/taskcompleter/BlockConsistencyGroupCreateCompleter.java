/*
 * Copyright (c) 2015 EMC Corporation
 * All Rights Reserved
 */
package com.emc.storageos.volumecontroller.impl.block.taskcompleter;

import java.net.URI;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.emc.storageos.db.client.DbClient;
import com.emc.storageos.db.client.model.BlockConsistencyGroup;
import com.emc.storageos.db.client.model.Operation;
import com.emc.storageos.svcs.errorhandling.model.ServiceCoded;
import com.emc.storageos.volumecontroller.impl.monitoring.RecordableEventManager;

public class BlockConsistencyGroupCreateCompleter extends BlockConsistencyGroupTaskCompleter {
    private static final Logger _log = LoggerFactory.getLogger(BlockConsistencyGroupCreateCompleter.class);
    public static final String CONSISTENCY_GROUP_CREATED_MSG = "Consistency group %s created.";
    public static final String CONSISTENCY_GROUP_CREATE_FAILED_MSG = "Failed to create consistency group  %s";

    public BlockConsistencyGroupCreateCompleter(URI consistencyGroup, String opId) {
        super(BlockConsistencyGroup.class, consistencyGroup, opId);
    }

    @Override
    protected void complete(DbClient dbClient, Operation.Status status, ServiceCoded coded) {
        try {
            super.complete(dbClient, status, coded);
            
            BlockConsistencyGroup consistencyGroup = dbClient.queryObject(BlockConsistencyGroup.class, getConsistencyGroupURI());
            switch (status) {
                case error:
                    dbClient.error(BlockConsistencyGroup.class, consistencyGroup.getId(), getOpId(),
                            coded);
                    break;
                case ready:
                    dbClient.ready(BlockConsistencyGroup.class, consistencyGroup.getId(), getOpId());
                    break;
                default:
                    _log.error(String.format("Unexpected status %s when creating consistency group %s", status.name(),
                            getConsistencyGroupURI().toString()));
                    break;
            }
            
            recordBourneBlockConsistencyGroupEvent(dbClient, consistencyGroup.getId(), eventType(status),
                    status, eventMessage(status, consistencyGroup));
        } catch (Exception e) {
            _log.error("Failed updating status. BlockConsistencyGroupCreate {}, for task " + getOpId(), getId(), e);
        }
    }

    private RecordableEventManager.EventType eventType(Operation.Status status) {
        return (Operation.Status.ready == status) ?
                RecordableEventManager.EventType.ConsistencyGroupCreated :
                RecordableEventManager.EventType.ConsistencyGroupCreateFailed;
    }

    private String eventMessage(Operation.Status status, BlockConsistencyGroup consistencyGroup) {
        return (Operation.Status.ready == status) ?
                String.format(CONSISTENCY_GROUP_CREATED_MSG, consistencyGroup.getLabel()) :
                String.format(CONSISTENCY_GROUP_CREATE_FAILED_MSG, consistencyGroup.getLabel());
    }

}
