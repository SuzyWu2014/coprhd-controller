/*
 * Copyright (c) 2016 EMC Corporation
 * All Rights Reserved
 */
package com.emc.storageos.volumecontroller.impl.validators.vplex;

import java.net.URI;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.emc.storageos.coordinator.client.service.CoordinatorClient;
import com.emc.storageos.db.client.DbClient;
import com.emc.storageos.db.client.model.ExportMask;
import com.emc.storageos.db.client.model.Initiator;
import com.emc.storageos.db.client.model.StorageSystem;
import com.emc.storageos.db.client.model.Volume;
import com.emc.storageos.db.client.util.NullColumnValueGetter;
import com.emc.storageos.exceptions.DeviceControllerException;
import com.emc.storageos.util.VPlexUtil;
import com.emc.storageos.volumecontroller.impl.validators.DefaultValidator;
import com.emc.storageos.volumecontroller.impl.validators.Validator;
import com.emc.storageos.volumecontroller.impl.validators.ValidatorLogger;
import com.emc.storageos.vplex.api.VPlexApiClient;
import com.emc.storageos.vplex.api.VPlexApiFactory;
import com.emc.storageos.vplex.api.VPlexStorageViewInfo;
import com.emc.storageos.vplexcontroller.VPlexControllerUtils;

public class VplexExportMaskValidator extends AbstractVplexValidator implements Validator {
    Logger log = LoggerFactory.getLogger(VplexExportMaskValidator.class);
    private StorageSystem vplex;
    private ExportMask mask;
    Collection<URI> volumesToValidate = null;
    Collection<Initiator> initiatorsToValidate = null;
    VPlexApiClient client = null;
    String id = null; // identifying string for ExportMask

    public VplexExportMaskValidator(DbClient dbClient, CoordinatorClient coordinator, ValidatorLogger logger, StorageSystem vplex,
            ExportMask mask) {
        super(dbClient, coordinator, logger);
        this.vplex = vplex;
        this.mask = mask;
        id = String.format("%s (%s)(%s)", mask.getMaskName(), mask.getNativeId(), mask.getId().toString());
    }

    @Override
    public boolean validate() throws Exception {
        if (mask.getInactive()) {
            log.info("Export mask inactive: " + id);
            // no such export mask, ignore, but don't indicate pass
            return false;
        }
        log.info("Initiating validation of Vplex ExportMask: " + id);
        VPlexStorageViewInfo storageView = null;
        try {
            client = VPlexControllerUtils.getVPlexAPIClient(VPlexApiFactory.getInstance(), vplex, dbClient);
            // This will throw an exception if the cluster name cannot be determined
            String vplexClusterName = VPlexUtil.getVplexClusterName(mask, vplex.getId(), client, dbClient);
            // This will throw an exception if the StorageView cannot be found
            storageView = client.getStorageView(vplexClusterName, mask.getMaskName());
            if (volumesToValidate != null) {
                validateNoAdditionalVolumes(storageView);
            }
            if (initiatorsToValidate != null) {
                validateNoAdditionalInitiators(storageView);
            }
        } catch (Exception ex) {
            if (storageView == null) {
                // Not finding the storage view is not an error, so delete can be idempotent
                log.info(String.format("Storage View %s cannot be located on VPLEX", id));
                return false;
            }
            log.info("Unexpected exception validating ExportMask: " + ex.getMessage(), ex);
            if (DefaultValidator.validationEnabled(coordinator)) {
                throw DeviceControllerException.exceptions.unexpectedCondition(
                        "Unexpected exception validating ExportMask: " + ex.getMessage());
            }
        }
        if (logger.hasErrors()) {
            if (DefaultValidator.validationEnabled(coordinator)) {
                throw DeviceControllerException.exceptions.validationError(
                        "Export Mask", logger.getMsgs().toString(), ValidatorLogger.CONTACT_EMC_SUPPORT);
            }
        }
        log.info("Vplex ExportMask validation complete: " + id);

        return true;
    }

    /**
     * Validates the hardware has no additional volumes than were passed in the volumesToValidate list.
     * Uses the virtualVolumeWWNMap to retrieve the volume WWNs and match against hardware.
     * 
     * @param storageView
     *            -- VPlexStorageViewInfo
     */
    private void validateNoAdditionalVolumes(VPlexStorageViewInfo storageView) {
        List<Volume> volumes = dbClient.queryObject(Volume.class, volumesToValidate);
        Set<String> storageViewWwns = storageView.getWwnToHluMap().keySet();
        for (Volume volume : volumes) {
            if (volume == null || volume.getInactive()) {
                continue;
            }
            String volumeWwn = volume.getWWN();
            if (NullColumnValueGetter.isNotNullValue(volumeWwn)) {
                if (storageViewWwns.contains(volumeWwn)) {
                    // Remove matched WWNs
                    storageViewWwns.remove(volumeWwn);
                } else {
                    log.info(String.format("Database volume %s (%s) not in StorageView", volume.getId(), volume.getWWN()));
                }
            }
        }
        // Any remaining WWNs in storageViewWwns had no matching volume, and therefore are error
        for (String wwn : storageViewWwns) {
            logger.logDiff(id, "virtual-volume WWN", "<no matching entry in validation list>", wwn);
        }
    }

    /**
     * Validate the hardware has no additional initiators than were passed in the initiatorsToValidate list.
     * Uses the Initiator PWWNs in the Storage View to match against initiator port WWN.
     * 
     * @param storageView
     *            -- VPlexStorageViewInfo
     */
    private void validateNoAdditionalInitiators(VPlexStorageViewInfo storageView) {
        Set<String> storageViewPwwns = new HashSet<String>(storageView.getInitiatorPwwns());
        for (Initiator initiator : initiatorsToValidate) {
            if (initiator == null || initiator.getInactive()) {
                continue;
            }
            String initiatorPwwn = Initiator.normalizePort(initiator.getInitiatorPort());
            if (storageViewPwwns.contains(initiatorPwwn)) {
                storageViewPwwns.remove(initiatorPwwn);
            } else {
                log.info(String.format("Database initiator %s (%s) not in StorageView", initiator.getId(), initiatorPwwn));
            }
        }
        // Any remaining WWNs in storageViewPwwns had no matching initiator, and therefore are error
        for (String wwn : storageViewPwwns) {
            logger.logDiff(id, "initiator port WWN", "<no matching entry in validation list>", wwn);
        }
    }

    public StorageSystem getVplex() {
        return vplex;
    }

    public void setVplex(StorageSystem vplex) {
        this.vplex = vplex;
    }

    public ExportMask getMask() {
        return mask;
    }

    public void setMask(ExportMask mask) {
        this.mask = mask;
    }

    public Collection<URI> getVolumesToValidate() {
        return volumesToValidate;
    }

    public void setVolumesToValidate(Collection<URI> volumesToValidate) {
        this.volumesToValidate = volumesToValidate;
    }

    public Collection<Initiator> getInitiatorsToValidate() {
        return initiatorsToValidate;
    }

    public void setInitiatorsToValidate(Collection<Initiator> initiatorsToValidate) {
        this.initiatorsToValidate = initiatorsToValidate;
    }

}