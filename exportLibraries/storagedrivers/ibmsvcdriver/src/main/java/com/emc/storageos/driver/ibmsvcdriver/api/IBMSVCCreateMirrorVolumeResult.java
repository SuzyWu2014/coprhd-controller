/*
 * Copyright (c) 2016 EMC Corporation
 * All Rights Reserved
 *
 * This software contains the intellectual property of EMC Corporation
 * or is licensed to EMC Corporation from third parties.  Use of this
 * software and the intellectual property contained therein is expressly
 * limited to the terms and conditions of the License Agreement under which
 * it is provided by or on behalf of EMC.
 */
package com.emc.storageos.driver.ibmsvcdriver.api;

public class IBMSVCCreateMirrorVolumeResult {

    private String srcVolumeId;

    private String srcVolumeName;

    private String srcPoolId;

    private String srcPoolName;

    private boolean isSuccess;

    private String errorString;

    public String getSrcVolumeId() {
        return srcVolumeId;
    }

    public void setSrcVolumeId(String srcVolumeId) {
        this.srcVolumeId = srcVolumeId;
    }

    public String getSrcVolumeName() {
        return srcVolumeName;
    }

    public void setSrcVolumeName(String srcVolumeName) {
        this.srcVolumeName = srcVolumeName;
    }

    public String getSrcPoolId() {
        return srcPoolId;
    }

    public void setSrcPoolId(String srcPoolId) {
        this.srcPoolId = srcPoolId;
    }

    public String getSrcPoolName() {
        return srcPoolName;
    }

    public void setSrcPoolName(String srcPoolName) {
        this.srcPoolName = srcPoolName;
    }

    public boolean isSuccess() {
        return isSuccess;
    }

    public void setSuccess(boolean isSuccess) {
        this.isSuccess = isSuccess;
    }

    public String getErrorString() {
        return errorString;
    }

    public void setErrorString(String errorString) {
        this.errorString = errorString;
    }
}