/*
 * Copyright (c) 2015 EMC Corporation
 * All Rights Reserved
 */
package com.emc.sa.service.hpux;

import static com.emc.sa.service.ServiceParams.DO_FORMAT;
import static com.emc.sa.service.ServiceParams.FILE_SYSTEM_TYPE;
import static com.emc.sa.service.ServiceParams.MOUNT_POINT;
import static com.emc.sa.service.vipr.ViPRExecutionUtils.logInfo;

import java.util.List;

import com.emc.hpux.HpuxSystem;
import com.emc.sa.engine.ExecutionUtils;
import com.emc.sa.engine.bind.BindingUtils;
import com.emc.sa.engine.bind.Param;
import com.emc.storageos.db.client.model.Initiator;
import com.emc.storageos.model.block.BlockObjectRestRep;

public final class MountBlockVolumeHelper {

    private String hostname;

    @Param(MOUNT_POINT)
    protected String mountPoint;

    @Param(FILE_SYSTEM_TYPE)
    protected String fsType;

    @Param(value = DO_FORMAT, required = false)
    protected boolean doFormat = true;

    /** The flag which indicates whether we're using EMC PowerPath for multipathing or not. */
    protected boolean usePowerPath;

    private HpuxSystem hpux;

    private HpuxSupport hpuxSupport;

    private MountBlockVolumeHelper(HpuxSupport hpuxSupport) {
        this.hpuxSupport = hpuxSupport;
        this.hpux = hpuxSupport.getTargetSystem();
        this.hostname = hpuxSupport.getHostName();
    }

    public static MountBlockVolumeHelper create(final HpuxSystem hpux, List<Initiator> ports) {
        HpuxSupport hpuxSupport = new HpuxSupport(hpux);
        MountBlockVolumeHelper mountBlockVolumeHelper = new MountBlockVolumeHelper(hpuxSupport);
        BindingUtils.bind(mountBlockVolumeHelper, ExecutionUtils.currentContext().getParameters());
        return mountBlockVolumeHelper;
    }

    public void precheck() {
        hpuxSupport.verifyMountPoint(mountPoint);
        usePowerPath = hpuxSupport.checkForPowerPath();
        if (usePowerPath) {
            logInfo("aix.mount.block.powerpath.detected");
        } else {
            logInfo("aix.mount.block.powerpath.not.detected");
        }
    }

    public void mount(final BlockObjectRestRep volume) {

        if (usePowerPath) {
            logInfo("UpdatePowerPathEntries.title");
            hpuxSupport.updatePowerPathEntries();
        }

        String rdisk = hpuxSupport.findRDisk(volume, usePowerPath);

        if (doFormat) {
            // logInfo("aix.mount.block.create.filesystem", hostname, hdisk);
            // hpux.makeFilesystem(rdisk, fsType);
        }

        logInfo("aix.mount.block.mount.device", hostname, rdisk, mountPoint, fsType, volume.getWwn());
        hpuxSupport.createDirectory(mountPoint);
        // hpuxSupport.addToFilesystemsConfig(rdisk, mountPoint, fsType);
        hpuxSupport.mount(mountPoint);

        hpuxSupport.setVolumeMountPointTag(volume, mountPoint);
    }

}
