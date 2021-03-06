/*
 * Copyright (c) 2013 EMC Corporation
 * All Rights Reserved
 */
package com.emc.storageos.vplex.api;

import java.util.ArrayList;
import java.util.List;

/**
 * Info for a VPlex engine
 */
public class VPlexEngineInfo extends VPlexResourceInfo {

    private List<VPlexDirectorInfo> directorInfoList = new ArrayList<VPlexDirectorInfo>();

    /**
     * Getter for the director info for the engine.
     * 
     * @return The director info for the engine.
     */
    public List<VPlexDirectorInfo> getDirectorInfo() {
        return directorInfoList;
    }

    /**
     * Setter for the director info for the engine.
     * 
     * @param infoList The director info for the engine.
     */
    public void setDirectorInfo(List<VPlexDirectorInfo> infoList) {
        directorInfoList = infoList;
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public String toString() {
        StringBuilder str = new StringBuilder();
        str.append("EngineInfo ( ");
        str.append(super.toString());
        for (VPlexDirectorInfo directorInfo : directorInfoList) {
            str.append(", ");
            str.append(directorInfo.toString());
        }
        str.append(" )");
        return str.toString();
    }
}
