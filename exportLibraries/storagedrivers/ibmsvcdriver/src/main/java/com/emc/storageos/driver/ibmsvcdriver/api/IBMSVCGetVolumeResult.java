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

public class IBMSVCGetVolumeResult {

    private IBMSVCAttributes properties;
    private boolean isSuccess;
    private String errorString;

    public IBMSVCGetVolumeResult() {
        this.properties = new IBMSVCAttributes();
    }

    public String getProperty(String propertyName) {
        return properties.get(propertyName);
    }

    void setProperty(String propertyName, String value) {
        properties.put(propertyName, value);
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
