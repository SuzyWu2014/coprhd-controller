/*
 * Copyright (c) 2008-2011 EMC Corporation
 * All Rights Reserved
 */

package com.emc.storageos.model;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlElementWrapper;
import javax.xml.bind.annotation.adapters.XmlJavaTypeAdapter;

import java.net.URI;
import java.util.Calendar;
import java.util.LinkedHashSet;
import java.util.Set;

import com.emc.storageos.model.adapters.CalendarAdapter;

@XmlAccessorType(XmlAccessType.PROPERTY)
public abstract class DataObjectRestRep {
    private String name;
    private URI id;
    private RestLinkRep link;
    private Calendar creationTime;
    private Boolean inactive;
    private Boolean global;
    private Boolean remote;
    private RelatedResourceRep vdc;
    private Set<String> tags;
    private Boolean internal;

    public DataObjectRestRep() {
    }

    public DataObjectRestRep(String name, URI id, RestLinkRep link,
            Calendar creationTime, Boolean inactive, Set<String> tags) {
        this.name = name;
        this.id = id;
        this.link = link;
        this.creationTime = creationTime;
        this.inactive = inactive;
        this.tags = tags;
    }

    /**
     * The name assigned to this resource in ViPR. The resource name is set by
     * a user and can be changed at any time. It is not a unique identifier.
     * 
     * @valid none
     */
    @XmlElement
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    /**
     * An identifier that is generated by ViPR when the resource is created.
     * The resource ID is guaranteed to be unique and immutable across all
     * virtual data centers for all time.
     * 
     * @valid urn:storageos:<i>resource-type</i>:<i>UUID</i>:
     */
    @XmlElement(name = "id")
    public URI getId() {
        return id;
    }

    public void setId(URI id) {
        this.id = id;
    }

    /**
     * A hyperlink to the details for this resource
     * 
     * @valid none
     */
    @XmlElement(name = "link")
    public RestLinkRep getLink() {
        return link;
    }

    public void setLink(RestLinkRep link) {
        this.link = link;
    }

    /**
     * A timestamp that shows when this resource was created in ViPR
     * 
     * @valid <i>YYYY</i>-<i>MM</i>-<i>DDTHH</i>:<i>mm</i>:<i>ss</i>Z
     */
    @XmlElement(name = "creation_time")
    @XmlJavaTypeAdapter(CalendarAdapter.class)
    public Calendar getCreationTime() {
        return creationTime;
    }

    public void setCreationTime(Calendar creationTime) {
        this.creationTime = creationTime;
    }

    /**
     * Keywords and labels that can be added by a user to a resource
     * to make it easy to find when doing a search.
     * 
     * @valid none
     */
    @XmlElementWrapper(name = "tags")
    /**
     * A keyword or label
     *
     * @valid none
     */
    @XmlElement(name = "tag")
    public Set<String> getTags() {
        if (tags == null) {
            tags = new LinkedHashSet<String>();
        }
        return tags;
    }

    public void setTags(Set<String> tags) {
        this.tags = tags;
    }

    /**
     * Whether or not the resource is inactive. When a user removes
     * a resource, the resource is put in this state before
     * it is removed from the ViPR database.
     * 
     * @valid true
     * @valid false
     */
    @XmlElement
    public Boolean getInactive() {
        return inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    /**
     * @return the global
     */
    public Boolean getGlobal() {
        return global;
    }

    /**
     * @param global the global to set
     */
    public void setGlobal(Boolean global) {
        this.global = global;
    }

    /**
     * @return the remote
     */
    public Boolean getRemote() {
        return remote;
    }

    /**
     * @param remote the remote to set
     */
    public void setRemote(Boolean remote) {
        this.remote = remote;
    }

    @Override
    public String toString() {
        return id.toString() + " " + name;
    }

    /**
     * @return the vdc
     */
    public RelatedResourceRep getVdc() {
        return vdc;
    }

    /**
     * @param vdc the vdc to set
     */
    public void setVdc(RelatedResourceRep vdc) {
        this.vdc = vdc;
    }

    /**
     * Whether or not the resource is an internal resource.
     * 
     * @valid true
     * @valid false
     */
    @XmlElement
    public Boolean getInternal() {
        return internal;
    }

    public void setInternal(Boolean internal) {
        this.internal = internal;
    }
}
