package com.emc.storageos.driver.vmaxv3driver.rest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testng.annotations.Test;

/**
 * Created by gang on 6/24/16.
 */
public class SloprovisioningSymmetrixDirectorPortListTest extends BaseRestTest {

    private static final Logger logger = LoggerFactory.getLogger(SloprovisioningSymmetrixDirectorPortListTest.class);

    @Test
    public void test() {
        logger.info("Port list = {}", new SloprovisioningSymmetrixDirectorPortList(this.getDefaultArray().getArrayId(),
            this.getDefaultArray().getDirectorId()).perform(this.getClient()));
    }
}