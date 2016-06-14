/*
 * Copyright 2016 EMC Corporation
 * All Rights Reserved
 */
package com.emc.storageos.hp3par.command;

public class FcPath {
    private String wwn;
    private Position portPos;
    
    public String getWwn() {
        return wwn;
    }
    public void setWwn(String wwn) {
        this.wwn = wwn;
    }
    public Position getPostPos() {
        return portPos;
    }
    public void setPostPos(Position postPos) {
        this.portPos = postPos;
    }
}
