/*
 * Copyright 2016 Dell Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
package com.emc.storageos.driver.dellsc.helpers;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.emc.storageos.driver.dellsc.DellSCDriverException;
import com.emc.storageos.driver.dellsc.DellSCDriverTask;
import com.emc.storageos.driver.dellsc.DellSCUtil;
import com.emc.storageos.driver.dellsc.scapi.StorageCenterAPI;
import com.emc.storageos.driver.dellsc.scapi.StorageCenterAPIException;
import com.emc.storageos.driver.dellsc.scapi.objects.ScReplay;
import com.emc.storageos.driver.dellsc.scapi.objects.ScReplayProfile;
import com.emc.storageos.storagedriver.DriverTask;
import com.emc.storageos.storagedriver.DriverTask.TaskStatus;
import com.emc.storageos.storagedriver.model.StorageVolume;
import com.emc.storageos.storagedriver.model.VolumeConsistencyGroup;
import com.emc.storageos.storagedriver.model.VolumeSnapshot;
import com.emc.storageos.storagedriver.storagecapabilities.CapabilityInstance;
import com.emc.storageos.storagedriver.storagecapabilities.StorageCapabilities;

/**
 * Consistency group handling.
 */
public class DellSCConsistencyGroups {

    private static final Logger LOG = LoggerFactory.getLogger(DellSCConsistencyGroups.class);

    private DellSCConnectionManager connectionManager;
    private DellSCUtil util;

    /**
     * Initialize the instance.
     */
    public DellSCConsistencyGroups() {
        this.connectionManager = DellSCConnectionManager.getInstance();
        this.util = DellSCUtil.getInstance();
    }

    /**
     * Create a consistency group.
     *
     * @param volumeConsistencyGroup The group to create.
     * @return The consistency group creation task.
     */
    public DriverTask createConsistencyGroup(VolumeConsistencyGroup volumeConsistencyGroup) {
        DellSCDriverTask task = new DellSCDriverTask("createConsistencyGroup");
        String ssn = volumeConsistencyGroup.getStorageSystemId();
        try {
            StorageCenterAPI api = connectionManager.getConnection(ssn);
            ScReplayProfile cg = api.createConsistencyGroup(
                    ssn,
                    volumeConsistencyGroup.getDisplayName());

            util.getVolumeConsistencyGroupFromReplayProfile(cg, volumeConsistencyGroup);

            task.setStatus(TaskStatus.READY);
        } catch (StorageCenterAPIException | DellSCDriverException dex) {
            String error = String.format("Error creating CG %s: %s", volumeConsistencyGroup.getDisplayName(), dex);
            LOG.error(error);
            task.setFailed(error);
        }
        return task;
    }

    /**
     * Add volumes to consistency groups.
     *
     * @param volumes The volumes to add.
     * @param capabilities The requested capabilities.
     * @return The driver task.
     */
    public DriverTask addVolumesToConsistencyGroup(List<StorageVolume> volumes, StorageCapabilities capabilities) {
        DellSCDriverTask task = new DellSCDriverTask("addVolumesToCG");

        StringBuilder errBuffer = new StringBuilder();
        int addCount = 0;
        Map<String, List<ScReplayProfile>> consistencyGroups = new HashMap<>();
        for (StorageVolume volume : volumes) {
            String ssn = volume.getStorageSystemId();
            try {
                StorageCenterAPI api = connectionManager.getConnection(ssn);
                String cgID = util.findCG(api, ssn, volume.getConsistencyGroup(), consistencyGroups);
                if (cgID == null) {
                    throw new DellSCDriverException(
                            String.format("Unable to locate CG %s", volume.getConsistencyGroup()));
                }

                api.addVolumeToConsistencyGroup(volume.getNativeId(), cgID);
                addCount++;
            } catch (StorageCenterAPIException | DellSCDriverException dex) {
                String error = String.format(
                        "Error adding volume %s to consistency group: %s", volume.getNativeId(), dex);
                LOG.warn(error);
                errBuffer.append(String.format("%s%n", error));
            }
        }

        task.setMessage(errBuffer.toString());

        if (addCount == volumes.size()) {
            task.setStatus(TaskStatus.READY);
        } else if (addCount == 0) {
            task.setStatus(TaskStatus.FAILED);
        } else {
            task.setStatus(TaskStatus.PARTIALLY_FAILED);
        }

        return task;
    }

    /**
     * Remove volumes from consistency groups.
     *
     * @param volumes The volumes.
     * @param capabilities The requested capabilities.
     * @return The driver task.
     */
    public DriverTask removeVolumesFromConsistencyGroup(List<StorageVolume> volumes, StorageCapabilities capabilities) {
        DellSCDriverTask task = new DellSCDriverTask("removeVolumeFromCG");

        StringBuilder errBuffer = new StringBuilder();
        int removeCount = 0;
        Map<String, List<ScReplayProfile>> consistencyGroups = new HashMap<>();
        for (StorageVolume volume : volumes) {
            String ssn = volume.getStorageSystemId();
            try {
                StorageCenterAPI api = connectionManager.getConnection(ssn);
                String cgID = util.findCG(api, ssn, volume.getConsistencyGroup(), consistencyGroups);
                if (cgID == null) {
                    // Easy to remove from nothing
                    continue;
                }

                api.removeVolumeFromConsistencyGroup(volume.getNativeId(), cgID);
                removeCount++;
            } catch (StorageCenterAPIException | DellSCDriverException dex) {
                String error = String.format(
                        "Error adding volume %s to consistency group: %s", volume.getNativeId(), dex);
                LOG.warn(error);
                errBuffer.append(String.format("%s%n", error));
            }
        }

        task.setMessage(errBuffer.toString());

        if (removeCount == volumes.size()) {
            task.setStatus(TaskStatus.READY);
        } else if (removeCount == 0) {
            task.setStatus(TaskStatus.FAILED);
        } else {
            task.setStatus(TaskStatus.PARTIALLY_FAILED);
        }

        return task;
    }

    /**
     * Delete a consistency group.
     *
     * @param volumeConsistencyGroup The group to delete.
     * @return The consistency group delete task.
     */
    public DriverTask deleteConsistencyGroup(VolumeConsistencyGroup volumeConsistencyGroup) {
        DellSCDriverTask task = new DellSCDriverTask("deleteVolume");
        try {
            StorageCenterAPI api = connectionManager.getConnection(volumeConsistencyGroup.getStorageSystemId());
            api.deleteConsistencyGroup(volumeConsistencyGroup.getNativeId());
            task.setStatus(TaskStatus.READY);
        } catch (StorageCenterAPIException | DellSCDriverException dex) {
            String error = String.format("Error deleting CG %s: %s", volumeConsistencyGroup.getDisplayName(), dex);
            LOG.error(error);
            task.setFailed(error);
        }
        return task;
    }

    /**
     * Create consistency group snapshots.
     *
     * @param volumeConsistencyGroup The consistency group.
     * @param snapshots The snapshots.
     * @param capabilities The requested capabilities.
     * @return The create task.
     */
    public DriverTask createConsistencyGroupSnapshot(VolumeConsistencyGroup volumeConsistencyGroup,
            List<VolumeSnapshot> snapshots,
            List<CapabilityInstance> capabilities) {
        DellSCDriverTask task = new DellSCDriverTask("createCGSnapshot");
        try {
            StorageCenterAPI api = connectionManager.getConnection(volumeConsistencyGroup.getStorageSystemId());
            ScReplay[] replays = api.createConsistencyGroupSnapshots(volumeConsistencyGroup.getNativeId());
            if (populateCgSnapshotInfo(snapshots, replays)) {
                task.setStatus(TaskStatus.READY);
            } else {
                task.setStatus(TaskStatus.PARTIALLY_FAILED);
            }
        } catch (StorageCenterAPIException | DellSCDriverException dex) {
            String error = String.format("Error creating CG snapshots %s: %s", volumeConsistencyGroup.getDisplayName(), dex);
            LOG.error(error);
            task.setFailed(error);
        }
        return task;
    }

    /**
     * Populates VolumeSnapshot info from CG created replays.
     *
     * @param snapshots The expected VolumeSnapshot objects.
     * @param replays The created replays.
     * @return True if successful, false if errors encountered.
     */
    private boolean populateCgSnapshotInfo(List<VolumeSnapshot> snapshots, ScReplay[] replays) {
        boolean complete = true;

        for (VolumeSnapshot snapshot : snapshots) {
            boolean found = false;

            for (ScReplay replay : replays) {
                if (replay.parent.instanceId.startsWith(snapshot.getParentId())) {
                    // Found match, populate the info
                    util.getVolumeSnapshotFromReplay(replay, snapshot);
                    found = true;
                    break;
                }
            }

            if (!found) {
                complete = false;
                LOG.warn("Unable to find snapshot for {}", snapshot.getDisplayName());
            }
        }
        return complete;
    }
}
