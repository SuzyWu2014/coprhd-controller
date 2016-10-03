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

import com.emc.storageos.driver.ibmsvcdriver.exceptions.CommandException;
import com.emc.storageos.driver.ibmsvcdriver.utils.ParsePattern;

import java.util.List;

public class IBMSVCQueryHostVolMapCommand extends AbstractIBMSVCQueryCommand<IBMSVCQueryHostVolMapResult> {

    public static final String HOST_VOLMAP_PARAMS_INFO = "HostVolMap";

    private final static ParsePattern[] PARSING_CONFIG = new ParsePattern[] {
            new ParsePattern("(.*)", HOST_VOLMAP_PARAMS_INFO)
    };

    public IBMSVCQueryHostVolMapCommand(String hostId) {
        addArgument("svcinfo lshostvdiskmap -delim : -nohdr " + hostId);
    }

    @Override
    ParsePattern[] getOutputPatternSpecification() {
        return PARSING_CONFIG;
    }

    @Override
    protected void processError() throws CommandException {
        results.setErrorString(getErrorMessage());
        results.setSuccess(false);
    }

    @Override
    void beforeProcessing() {
        results = new IBMSVCQueryHostVolMapResult();
        results.setVolCount(0);
        results.setSuccess(true);
    }

    @Override
    void processMatch(ParsePattern spec, List<String> capturedStrings) {
        switch (spec.getPropertyName()) {

            case HOST_VOLMAP_PARAMS_INFO:

                String[] hostVolData = capturedStrings.get(0).split(":");
                int volCount = hostVolData.length; // not called if query returned empty.

                results.setVolCount(volCount);
                results.setSuccess(true);
                break;
        }
    }
}