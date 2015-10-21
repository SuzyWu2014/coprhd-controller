/*
 * Copyright (c) 2015 EMC Corporation
 * All Rights Reserved
 */
package com.emc.vipr.client.core;

import static com.emc.vipr.client.impl.jersey.ClientUtils.addQueryParam;
import static com.emc.vipr.client.system.impl.PathConstants.BACKUP_CREATE_URL;
import static com.emc.vipr.client.system.impl.PathConstants.BACKUP_URL;

import javax.ws.rs.core.UriBuilder;

import com.emc.vipr.client.impl.RestClient;
import com.emc.vipr.model.sys.backup.BackupSets;

public class Backup {
	protected final RestClient client;

	public Backup(RestClient client) {
		this.client = client;
	}

	public BackupSets getBackups() {
		return client.get(BackupSets.class, BACKUP_URL, "");
	}

	public void createBackup(String name, boolean force) {
		UriBuilder builder = client.uriBuilder(BACKUP_CREATE_URL);
		addQueryParam(builder, "tag", name);
		if (force) {
			addQueryParam(builder, "force", true);
		}
		client.postURI(String.class, builder.build());
	}

	public void deleteBackup(String name) {
		UriBuilder builder = client.uriBuilder(BACKUP_CREATE_URL);
		addQueryParam(builder, "tag", name);
		client.deleteURI(String.class, builder.build());
	}
}
