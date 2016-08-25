/*
 * Copyright (c) 2013 EMC Corporation
 * All Rights Reserved
 */

package com.emc.storageos.volumecontroller.impl.block.taskcompleter;

import java.net.URI;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.emc.storageos.db.client.DbClient;
import com.emc.storageos.db.client.model.ExportGroup;
import com.emc.storageos.db.client.model.ExportMask;
import com.emc.storageos.db.client.model.Operation;
import com.emc.storageos.exceptions.DeviceControllerException;
import com.emc.storageos.svcs.errorhandling.model.ServiceCoded;

@SuppressWarnings("serial")
public class ExportMaskDeleteCompleter extends ExportTaskCompleter {
    private static final Logger _log = LoggerFactory.getLogger(ExportMaskDeleteCompleter.class);

    public ExportMaskDeleteCompleter(URI egUri, URI emUri, String task) {
        super(ExportGroup.class, egUri, emUri, task);
    }

    @Override
    protected void complete(DbClient dbClient, Operation.Status status, ServiceCoded coded) throws DeviceControllerException {
        try {
            ExportGroup exportGroup = dbClient.queryObject(ExportGroup.class, getId());
            ExportMask exportMask = (getMask() != null) ?
                    dbClient.queryObject(ExportMask.class, getMask()) : null;
            if (exportMask != null && status == Operation.Status.ready) {
                exportGroup.removeExportMask(exportMask.getId());
                dbClient.updateObject(exportGroup);
                // The ExportMask object is needed for unzoning operations that are likely executed in future steps,
                // therefore deleting the ExportMask here is premature. The ZoneDeleteCompleter will take care of that
                // when the zone step is complete.
                _log.info(
                        String.format("ExportMask %s will not be deleted by this step completer; unzoning step will delete the ExportMask",
                                exportMask.forDisplay()));
            }
            _log.info(String.format("Done ExportMaskDelete - EG: %s, OpId: %s, status: %s",
                    getId().toString(), getOpId(), status.name()));
        } catch (Exception e) {
            _log.error(String.format("Failed updating status for ExportMaskDelete - EG: %s, OpId: %s",
                    getId().toString(), getOpId()), e);
        } finally {
            super.complete(dbClient, status, coded);
        }
    }

}
