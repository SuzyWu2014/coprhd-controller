/**
 *  Copyright (c) 2008-2013 EMC Corporation
 * All Rights Reserved
 *
 * This software contains the intellectual property of EMC Corporation
 * or is licensed to EMC Corporation from third parties.  Use of this
 * software and the intellectual property contained therein is expressly
 * limited to the terms and conditions of the License Agreement under which
 * it is provided by or on behalf of EMC.
 */
package com.emc.storageos.api.service.impl.resource.snapshot;

import com.emc.storageos.coordinator.client.service.CoordinatorClient;
import com.emc.storageos.db.client.DbClient;

/**
 * 
 */
public class HDSBlockSnapshotSessionApiImpl extends DefaultBlockSnapshotSessionApiImpl {

    protected HDSBlockSnapshotSessionApiImpl(DbClient dbClient, CoordinatorClient coordinator) {
        super(dbClient, coordinator);
    }
}
