/*
 * Copyright (c) 2015-2016 EMC Corporation
 * All Rights Reserved
 */
package com.emc.storageos.volumecontroller.impl.file;

import java.net.URI;
import java.util.List;

import com.emc.storageos.db.client.model.FileShare;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.emc.storageos.db.client.DbClient;
import com.emc.storageos.db.client.model.FileShare.MirrorStatus;
import com.emc.storageos.db.client.model.Operation.Status;
import com.emc.storageos.exceptions.DeviceControllerException;
import com.emc.storageos.services.OperationTypeEnum;
import com.emc.storageos.svcs.errorhandling.model.ServiceCoded;

public class MirrorFileFailbackTaskCompleter extends MirrorFileTaskCompleter {

    private static final Logger _log = LoggerFactory.getLogger(MirrorFileFailbackTaskCompleter.class);

    public MirrorFileFailbackTaskCompleter(Class clazz, List<URI> ids, String opId, URI storageUri) {
        super(clazz, ids, opId, storageUri);
    }

    public MirrorFileFailbackTaskCompleter(Class clazz, URI id, String opId) {
        super(clazz, id, opId);
    }

    public MirrorFileFailbackTaskCompleter(URI sourceURI, URI targetURI, String opId) {
        super(sourceURI, targetURI, opId);
    }

    @Override
    protected void complete(DbClient dbClient, Status status, ServiceCoded coded) throws DeviceControllerException {
        try {
            setDbClient(dbClient);
            recordMirrorOperation(dbClient, OperationTypeEnum.FAILBACK_FILE_MIRROR, status, getSourceFileShare().getId().toString(),
                    getTargetFileShare().getId().toString());

        } catch (Exception e) {
            _log.error("Failed updating status. MirrorSessionFailback {}, for task " + getOpId(), getId(), e);
        } finally {
            super.complete(dbClient, status, coded);
        }
    }

    @Override
    protected String getFileMirrorStatusForSuccess(FileShare fs) {
        if(fs.getStorageDevice().equals(getStorageUri())) {
        	_log.info("failback operation is successful - fs name {} and mirror state {}", fs.getName(), MirrorStatus.SYNCHRONIZED.name());
            return MirrorStatus.FAILED_OVER.name();
        } else {
        	_log.info("failback operation is successful - fs name {} and mirror state {}", fs.getName(), MirrorStatus.UNKNOWN.name());
            return MirrorStatus.SYNCHRONIZED.name();
        }
    }

}
