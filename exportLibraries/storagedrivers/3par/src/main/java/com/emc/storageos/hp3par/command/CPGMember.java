/*
 * Copyright 2016 EMC Corporation
 * All Rights Reserved
 */
package com.emc.storageos.hp3par.command;

public class CPGMember {
    private Integer id;
    private String uuid;
    private String name;
    private UserUsage UsrUsage;
    private SaUsage SAUsage;
    private SdUsage SDUsage;
    private SdGrowth SDGrowth;
    private Integer state;
    private boolean dedupCapable;
    
    public Integer getId() {
        return id;
    }
    public void setId(Integer id) {
        this.id = id;
    }
    public String getUuid() {
        return uuid;
    }
    public void setUuid(String uuid) {
        this.uuid = uuid;
    }
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public UserUsage getUsrUsage() {
        return UsrUsage;
    }
    public void setUsrUsage(UserUsage usrUsage) {
        UsrUsage = usrUsage;
    }
    public SaUsage getSAUsage() {
        return SAUsage;
    }
    public void setSAUsage(SaUsage sAUsage) {
        SAUsage = sAUsage;
    }
    public SdUsage getSDUsage() {
        return SDUsage;
    }
    public void setSDUsage(SdUsage sDUsage) {
        SDUsage = sDUsage;
    }
    public SdGrowth getSDGrowth() {
        return SDGrowth;
    }
    public void setSDGrowth(SdGrowth sDGrowth) {
        SDGrowth = sDGrowth;
    }
    public Integer getState() {
        return state;
    }
    public void setState(Integer state) {
        this.state = state;
    }
	public boolean isDedupCapable() {
		return dedupCapable;
	}
	public void setDedupCapable(boolean dedupCapable) {
		this.dedupCapable = dedupCapable;
	}
}
