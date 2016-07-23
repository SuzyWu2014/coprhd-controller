/*
 * Copyright (c) 2016 EMC Corporation
 * All Rights Reserved
 */
package com.emc.storageos.volumecontroller.impl.validators.smis.vnx;

import static com.emc.storageos.db.client.util.CommonTransformerFunctions.fctnBlockObjectToNativeID;

import java.net.URI;
import java.util.Collection;
import java.util.List;
import java.util.Set;

import com.emc.storageos.db.client.model.ExportMask;
import com.emc.storageos.db.client.model.StorageSystem;
import com.emc.storageos.db.client.model.Volume;
import com.emc.storageos.volumecontroller.impl.smis.SmisConstants;
import com.google.common.base.Function;
import com.google.common.collect.Collections2;
import com.google.common.collect.Sets;

public class VnxExportMaskVolumesValidator extends VnxExportMaskValidator {

    private final Collection<URI> expectedVolumeURIs;

    public VnxExportMaskVolumesValidator(StorageSystem storage, ExportMask exportMask, Collection<URI> expectedVolumeURIs) {
        super(storage, exportMask, "volumes");
        this.expectedVolumeURIs = expectedVolumeURIs;
    }

    @Override
    protected String getAssociatorProperty() {
        return SmisConstants.CP_DEVICE_ID;
    }

    @Override
    protected String getAssociatorClass() {
        return SmisConstants.STORAGE_VOLUME_CLASS;
    }

    @Override
    protected Function<? super String, String> getHardwareTransformer() {
        return null;
    }

    @Override
    protected Set<String> getDatabaseResources() {
        if (expectedVolumeURIs == null || expectedVolumeURIs.isEmpty()) {
            return Sets.newHashSet();
        }
        List<Volume> volumes = getDbClient().queryObject(Volume.class, expectedVolumeURIs);
        Collection<String> transformed = Collections2.transform(volumes, fctnBlockObjectToNativeID());
        return Sets.newHashSet(transformed);
    }

}