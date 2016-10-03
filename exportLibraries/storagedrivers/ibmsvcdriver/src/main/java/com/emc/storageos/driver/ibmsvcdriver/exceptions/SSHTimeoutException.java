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
package com.emc.storageos.driver.ibmsvcdriver.exceptions;

public class SSHTimeoutException extends SSHException {

    private static final long serialVersionUID = -8139496089823230886L;

    private int timeout;

    public SSHTimeoutException(String message, int timeout) {
        super(message);
    }

    public int getTimeout() {
        return timeout;
    }
}