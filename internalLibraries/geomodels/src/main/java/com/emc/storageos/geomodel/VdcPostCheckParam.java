/*
 * Copyright (c) 2008-2014 EMC Corporation
 * All Rights Reserved
 */

package com.emc.storageos.geomodel;

import java.net.URI;
import java.util.List;
import java.util.ArrayList;

import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlRootElement;

@XmlRootElement
public class VdcPostCheckParam {
    private URI rootTenantId;
    private List<URI> vdcList = new ArrayList<URI>();
    private String configChangeType;
    private Boolean fresher;

    @XmlElement(name = "root_id")
    public URI getRootTenantId() {
        return rootTenantId;
    }

    public void setRootTenantId(URI id) {
        this.rootTenantId = id;
    }

    @XmlElement(name = "vdcs")
    public List<URI> getVdcList() {
        return vdcList;
    }

    public void setVdcList(List<URI> vdcList) {
        this.vdcList = vdcList;
    }

    @XmlElement(name = "config_change_type")
    public String getConfigChangeType() {
        return configChangeType;
    }

    public void setConfigChangeType(String configChangeType) {
        this.configChangeType = configChangeType;
    }

    @XmlElement(name = "fresher")
    public Boolean getFresher() {
        return fresher;
    }

    public void setFresher(Boolean isFresher) {
        this.fresher = isFresher;
    }

}
