/*
 * Copyright (c) 2016 EMC Corporation
 * All Rights Reserved
 */
package com.emc.sa.api;

import static com.emc.sa.api.mapper.ScheduledEventMapper.*;
import static com.emc.storageos.api.mapper.DbObjectMapper.toNamedRelatedResource;
import static com.emc.storageos.db.client.URIUtil.asString;
import static com.emc.storageos.db.client.URIUtil.uri;

import java.net.URI;
import java.nio.charset.Charset;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import com.emc.sa.model.dao.ModelClient;
import com.emc.sa.model.util.ExecutionWindowHelper;
import com.emc.storageos.db.client.URIUtil;
import com.emc.storageos.db.client.constraint.ContainmentConstraint;
import com.emc.storageos.db.client.constraint.URIQueryResultList;
import com.emc.storageos.db.client.model.NamedURI;
import com.emc.storageos.db.client.model.Volume;
import com.emc.storageos.svcs.errorhandling.resources.BadRequestException;
import org.apache.commons.codec.binary.*;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

import com.emc.sa.api.utils.ValidationUtils;
import com.emc.sa.catalog.CatalogServiceManager;
import com.emc.sa.descriptor.*;
import com.emc.sa.util.TextUtils;
import com.emc.storageos.api.service.authorization.PermissionsHelper;
import com.emc.storageos.api.service.impl.resource.ArgValidator;
import com.emc.storageos.api.service.impl.response.ResRepFilter;
import com.emc.storageos.api.service.impl.response.RestLinkFactory;
import com.emc.storageos.db.client.model.EncryptionProvider;
import com.emc.storageos.db.client.model.uimodels.*;
import com.emc.storageos.db.exceptions.DatabaseException;
import com.emc.storageos.model.*;
import com.emc.storageos.model.search.SearchResultResourceRep;
import com.emc.storageos.model.search.SearchResults;
import com.emc.storageos.security.authentication.StorageOSUser;
import com.emc.storageos.security.authorization.CheckPermission;
import com.emc.storageos.security.authorization.DefaultPermissions;
import com.emc.storageos.security.authorization.Role;
import com.emc.storageos.services.OperationTypeEnum;
import com.emc.storageos.svcs.errorhandling.resources.APIException;
import com.emc.storageos.volumecontroller.impl.monitoring.RecordableEventManager;
import com.emc.vipr.client.catalog.impl.SearchConstants;
import com.emc.vipr.model.catalog.*;
import com.google.common.collect.Lists;
import com.emc.sa.api.OrderService;

@DefaultPermissions(
        readRoles = {},
        writeRoles = {})
@Path("/catalog/events")
public class ScheduledEventService extends CatalogTaggedResourceService {
    private static final Logger log = LoggerFactory.getLogger(ScheduledEventService.class);
    private static Charset UTF_8 = Charset.forName("UTF-8");
    private static final String EVENT_SERVICE_TYPE = "catalog-event";

    @Autowired
    private ModelClient client;

    @Autowired
    private CatalogServiceManager catalogServiceManager;

    @Autowired
    private OrderService orderService;

    @Override
    protected ResourceTypeEnum getResourceType() {
        return ResourceTypeEnum.SCHEDULED_EVENT;
    }

    @Override
    public String getServiceType() {
        return EVENT_SERVICE_TYPE;
    }

    /**
     * Query scheduled event resource via its URI.
     * @param id    scheduled event URI
     * @return      ScheduledEvent
     */
    @Override
    protected ScheduledEvent queryResource(URI id) {
        return getScheduledEventById(id, false);
    }

    /**
     * Get tenant owner of scheduled event
     * @param id    scheduled event URI
     * @return      URI of the owner tenant
     */
    @Override
    protected URI getTenantOwner(URI id) {
        ScheduledEvent event = queryResource(id);
        return uri(event.getTenant());
    }

    @SuppressWarnings("unchecked")
    @Override
    public Class<ScheduledEvent> getResourceClass() {
        return ScheduledEvent.class;
    }

    /**
     * Create a scheduled event for one or a series of future orders.
     * Also a latest order is created and set to APPROVAL or SCHEDULED status
     * @param createParam   including schedule time info and order parameters
     * @return                ScheduledEventRestRep
     */
    @POST
    @Path("")
    @Consumes({ MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML })
    @Produces({ MediaType.APPLICATION_XML, MediaType.APPLICATION_JSON })
    public ScheduledEventRestRep createEvent(ScheduledEventCreateParam createParam) {
        StorageOSUser user = getUserFromContext();
        URI tenantId = createParam.getOrderCreateParam().getTenantId();
        if (tenantId != null) {
            verifyAuthorizedInTenantOrg(tenantId, user);
        }
        else {
            tenantId = uri(user.getTenantId());
        }

        ArgValidator.checkFieldNotNull(createParam.getOrderCreateParam().getCatalogService(), "catalogService");
        CatalogService catalogService = catalogServiceManager.getCatalogServiceById(createParam.getOrderCreateParam().getCatalogService());
        if (catalogService == null) {
            throw APIException.badRequests.orderServiceNotFound(
                    asString(createParam.getOrderCreateParam().getCatalogService()));
        }

        validateParam(createParam.getScheduleInfo());

        ScheduledEvent newObject = null;
        try {
            newObject = createScheduledEvent(tenantId, createParam, catalogService);
        } catch (APIException ex){
            log.error(ex.getMessage(), ex);
            throw ex;
        } catch (Exception e) {
            log.error(e.getMessage(), e);
        }

        return map(newObject);
    }

    /**
     * Validate schedule time info related parameters.
     * Order related parameters would be verified later in order creation part.
     * @param scheduleInfo     Schedule Schema
     */
    private void validateParam(ScheduleInfo scheduleInfo) {
        try {
            DateFormat formatter = new SimpleDateFormat(ScheduleInfo.FULL_DAY_FORMAT);
            Date date = formatter.parse(scheduleInfo.getStartDate());
        } catch (Exception e) {
            throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.START_DATE);
        }

        if (scheduleInfo.getHourOfDay() < 0 || scheduleInfo.getHourOfDay() > 23) {
            throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.HOUR_OF_DAY);
        }
        if (scheduleInfo.getMinuteOfHour() < 0 || scheduleInfo.getMinuteOfHour() > 59) {
            throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.MINUTE_OF_HOUR);
        }
        if (scheduleInfo.getDurationLength() < 1 || scheduleInfo.getHourOfDay() > 60*24) {
            throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.DURATION_LENGTH);
        }

        if (scheduleInfo.getReoccurrence() < 0 ) {
            throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.REOCCURRENCE);
        } 
        if (scheduleInfo.getReoccurrence() > 1 ) {
	    if (scheduleInfo.getCycleFrequency() < 1 ) {
                throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.CYCLE_FREQUENCE);
            }

            switch (scheduleInfo.getCycleType()) {
                case MONTHLY:
                    if (scheduleInfo.getSectionsInCycle().size() != 1) {
                        throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.SECTIONS_IN_CYCLE);
                    }
                    int day = Integer.valueOf(scheduleInfo.getSectionsInCycle().get(0));
                    if (day < 1 || day > 31) {
                        throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.SECTIONS_IN_CYCLE);
                    }
                    break;
                case WEEKLY:
                    if (scheduleInfo.getSectionsInCycle().size() != 1) {
                        throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.SECTIONS_IN_CYCLE);
                    }
                    int dayOfWeek = Integer.valueOf(scheduleInfo.getSectionsInCycle().get(0));
                    if (dayOfWeek < 1 || dayOfWeek > 7) {
                        throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.SECTIONS_IN_CYCLE);
                    }
                    break;
                case DAILY:
                case HOURLY:
                case MINUTELY:
                    if (scheduleInfo.getSectionsInCycle().size() != 0) {
                        throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.SECTIONS_IN_CYCLE);
                    }
                    break;
                default:
                    throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.CYCLE_TYPE);
            }
        }

        if (scheduleInfo.getDateExceptions() != null) {
            for (String dateException: scheduleInfo.getDateExceptions()) {
                try {
                    DateFormat formatter = new SimpleDateFormat(ScheduleInfo.FULL_DAY_FORMAT);
                    Date date = formatter.parse(dateException);
                } catch (Exception e) {
                    throw APIException.badRequests.schduleInfoInvalid(ScheduleInfo.DATE_EXCEPTIONS);
                }
            }
        }
    }

    /**
     * Check if schedule time info is matched with the desired execution window set by admin.
     * @param scheduleInfo  schedule time info
     * @param window         desired execution window set by admin
     * @return                empty for matching, otherwise including detail unmatched reason.
     */
    private String match(ScheduleInfo scheduleInfo, ExecutionWindow window) {
        String msg="";

        ExecutionWindowHelper windowHelper = new ExecutionWindowHelper(window);
        if (!windowHelper.inHourMinWindow(scheduleInfo.getHourOfDay(), scheduleInfo.getMinuteOfHour())) {
            msg = "Schedule hour/minute info does not match with execution window.";
            return msg;
        }

        switch (scheduleInfo.getCycleType()) {
            case MINUTELY:
            case HOURLY:
                log.warn("Not all of the orders would be scheduled due to schedule cycle type {}", scheduleInfo.getCycleType());
                break;
            case DAILY:
                if (!window.getExecutionWindowType().equals(ExecutionWindowType.DAILY.name())) {
                    msg = "Schedule cycle type has conflicts with execution window.";
                }
                break;
            case WEEKLY:
                if (window.getExecutionWindowType().equals(ExecutionWindowType.MONTHLY.name())) {
                    msg = "Schedule cycle type has conflicts with execution window.";
                } else {
                    if (window.getDayOfWeek() != Integer.valueOf(scheduleInfo.getSectionsInCycle().get(0))) {
                        msg = "Scheduled date has conflicts with execution window.";
                    }
                }
                break;
            case MONTHLY:
                if (window.getExecutionWindowType().equals(ExecutionWindowType.WEEKLY.name())) {
                    msg = "Schedule cycle type has conflicts with execution window.";
                } else if (window.getExecutionWindowType().equals(ExecutionWindowType.MONTHLY.name())) {
                    if (window.getDayOfMonth() != Integer.valueOf(scheduleInfo.getSectionsInCycle().get(0))) {
                        msg = "Scheduled date has conflicts with execution window.";
                    }
                }
                break;
            default:
                log.error("not expected schedule cycle.");
        }

        return msg;
    }

    /**
     * Internal main function to create scheduled event.
     * @param tenantId          owner tenant Id
     * @param param             scheduled event creation param
     * @param catalogService   target catalog service
     * @return                   ScheduledEvent
     * @throws Exception
     */
    private ScheduledEvent createScheduledEvent(URI tenantId, ScheduledEventCreateParam param, CatalogService catalogService) throws Exception{
        if (catalogService.getExecutionWindowRequired()) {
            ExecutionWindow executionWindow = client.findById(catalogService.getDefaultExecutionWindowId().getURI());
            String msg = match(param.getScheduleInfo(), executionWindow);
            if (!msg.isEmpty()) {
                throw APIException.badRequests.schduleInfoNotMatchWithExecutionWindow(msg);
            }
        }

        URI scheduledEventId = URIUtil.createId(ScheduledEvent.class);
        param.getOrderCreateParam().setScheduledEventId(scheduledEventId);
        param.getOrderCreateParam().setScheduledTime(convertCalendarToStr(getFirstScheduledTime(param.getScheduleInfo())));

        OrderRestRep restRep = orderService.createOrder(param.getOrderCreateParam());

        ScheduledEvent newObject = new ScheduledEvent();
        newObject.setId(scheduledEventId);
        newObject.setTenant(tenantId.toString());
        newObject.setCatalogServiceId(param.getOrderCreateParam().getCatalogService());
        newObject.setEventType(param.getScheduleInfo().getReoccurrence() == 1 ? ScheduledEventType.ONCE : ScheduledEventType.REOCCURRENCE);
        if (catalogService.getApprovalRequired()) {
            newObject.setEventStatus(ScheduledEventStatus.APPROVAL);
            // TODO: send event for approve requirement
        } else {
            newObject.setEventStatus(ScheduledEventStatus.APPROVED);
        }
        newObject.setScheduleInfo(new String(org.apache.commons.codec.binary.Base64.encodeBase64(param.getScheduleInfo().serialize()), UTF_8));
        if (catalogService.getExecutionWindowRequired()) {
            newObject.setExecutionWindowId(catalogService.getDefaultExecutionWindowId());
        } else {
            newObject.setExecutionWindowId(new NamedURI(ExecutionWindow.INFINITE, "INFINITE"));
        }
        newObject.setLatestOrderId(restRep.getId());

        client.save(newObject);

        //auditOpSuccess(OperationTypeEnum.CREATE_SCHEDULED_EVENT, order.auditParameters());
        return newObject;
    }

    /**
     * Convert a Calendar to a readable time string.
     * @param cal
     * @return String time with format: "yyyy-MM-dd HH:mm:ss"
     * @throws Exception
     */
    private String convertCalendarToStr(Calendar cal) throws Exception {
        SimpleDateFormat format = new SimpleDateFormat(ScheduleInfo.FULL_DAYTIME_FORMAT);
        String formatted = format.format(cal.getTime());
        log.info("converted calendar time:{}", formatted);
        return formatted;
    }

    /**
     * Get the first desired schedule time based on current time, start time and schedule schema
     * @param scheduleInfo  schedule schema
     * @return                calendar for the first desired schedule time
     * @throws Exception
     */
    private Calendar getFirstScheduledTime(ScheduleInfo scheduleInfo) throws Exception{

        DateFormat formatter = new SimpleDateFormat(ScheduleInfo.FULL_DAY_FORMAT);
        Date date = formatter.parse(scheduleInfo.getStartDate());

        Calendar startTime = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
        startTime.setTimeZone(TimeZone.getTimeZone("UTC"));
        startTime.setTime(date);
        startTime.set(Calendar.HOUR_OF_DAY, scheduleInfo.getHourOfDay());
        startTime.set(Calendar.MINUTE, scheduleInfo.getMinuteOfHour());
        startTime.set(Calendar.SECOND, 0);
        log.info("startTime: {}", startTime.toString());

        Calendar currTZTime = Calendar.getInstance();
        Calendar currTime = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
        currTime.setTimeInMillis(currTZTime.getTimeInMillis());
        log.info("currTime: {}", currTime.toString());

        Calendar initTime = startTime.before(currTime)? currTime:startTime;
        log.info("initTime: {}", initTime.toString());

        int year = initTime.get(Calendar.YEAR);
        int month = initTime.get(Calendar.MONTH);
        int day = initTime.get(Calendar.DAY_OF_MONTH);
        int hour = scheduleInfo.getHourOfDay();
        int min = scheduleInfo.getMinuteOfHour();

        Calendar scheduledTime = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
        startTime.setTimeZone(TimeZone.getTimeZone("UTC"));
        scheduledTime.set(year, month, day, hour, min, 0);

        switch (scheduleInfo.getCycleType()) {
            case MONTHLY:
                day = Integer.valueOf(scheduleInfo.getSectionsInCycle().get(0));
                scheduledTime.set(Calendar.DAY_OF_MONTH, day);
                break;
            case WEEKLY:
                day = Integer.valueOf(scheduleInfo.getSectionsInCycle().get(0));
                int daysDiff = (day%7 + 1) - scheduledTime.get(Calendar.DAY_OF_WEEK); // java dayOfWeek starts from Sun.
                scheduledTime.add(Calendar.DAY_OF_WEEK, daysDiff);
                break;
            case DAILY:
            case HOURLY:
            case MINUTELY:
                 break;
            default:
                 log.error("not expected schedule cycle.");
        }
        log.info("scheduledTime: {}", scheduledTime.toString());

        while (scheduledTime.before(initTime)) {
            scheduledTime = getNextScheduledTime(scheduledTime, scheduleInfo);
            log.info("scheduledTime in loop: {}", scheduledTime.toString());
        }

        return scheduledTime;
    }

    /**
     * Get next desired schedule time based on the previous one and schedule schema
     * @param scheduledTime     previous schedule time
     * @param scheduleInfo      schedule schema
     * @return
     */
    private Calendar getNextScheduledTime(Calendar scheduledTime, ScheduleInfo scheduleInfo) {
        switch (scheduleInfo.getCycleType()) {
            case MONTHLY:
                scheduledTime.add(Calendar.MONTH, scheduleInfo.getCycleFrequency());
                break;
            case WEEKLY:
                scheduledTime.add(Calendar.WEEK_OF_MONTH, scheduleInfo.getCycleFrequency());
                break;
            case DAILY:
                scheduledTime.add(Calendar.DAY_OF_MONTH, scheduleInfo.getCycleFrequency());
                break;
            case HOURLY:
                scheduledTime.add(Calendar.HOUR_OF_DAY, scheduleInfo.getCycleFrequency());
                break;
            case MINUTELY:
                scheduledTime.add(Calendar.MINUTE, scheduleInfo.getCycleFrequency());
                break;
            default:
                log.error("not expected schedule cycle.");
        }
        return scheduledTime;
    }

    /**
     * Get a scheduled event via its URI
     * @param id    target schedule event URI
     * @return      ScheduledEventRestRep
     */
    @GET
    @Path("/{id}")
    @Consumes({ MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML })
    public ScheduledEventRestRep getScheduledEvent(@PathParam("id") String id) {
        ScheduledEvent scheduledEvent = queryResource(uri(id));

        StorageOSUser user = getUserFromContext();
        verifyAuthorizedInTenantOrg(uri(scheduledEvent.getTenant()), user);

        return map(scheduledEvent);
    }

    private ScheduledEvent getScheduledEventById(URI id, boolean checkInactive) {
        ScheduledEvent scheduledEvent = client.scheduledEvents().findById(id);
        ArgValidator.checkEntity(scheduledEvent, id, isIdEmbeddedInURL(id), checkInactive);
        return scheduledEvent;
    }

    /**
     * Update a scheduled event for one or a series of future orders.
     * @param updateParam   including schedule time info
     * @return                ScheduledEventRestRep
     */
    @PUT
    @Path("/{id}")
    @Consumes({ MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML })
    @Produces({ MediaType.APPLICATION_XML, MediaType.APPLICATION_JSON })
    public ScheduledEventRestRep updateEvent(@PathParam("id") String id, ScheduledEventUpdateParam updateParam) {
        ScheduledEvent scheduledEvent = queryResource(uri(id));
        ArgValidator.checkEntity(scheduledEvent, uri(id), true);

        validateParam(updateParam.getScheduleInfo());

        try {
            updateScheduledEvent(scheduledEvent, updateParam.getScheduleInfo());
        } catch (APIException ex){
            log.error(ex.getMessage(), ex);
            throw ex;
        } catch (Exception e) {
            log.error(e.getMessage(), e);
        }

        return map(scheduledEvent);
    }

    /**
     * Internal main function to update scheduled event.
     * @param scheduledEvent   target scheduled event
     * @param scheduleInfo     target schedule schema
     * @return                   updated scheduledEvent
     * @throws Exception
     */
    private ScheduledEvent updateScheduledEvent(ScheduledEvent scheduledEvent, ScheduleInfo scheduleInfo) throws Exception{
        CatalogService catalogService = catalogServiceManager.getCatalogServiceById(scheduledEvent.getCatalogServiceId());
        if (catalogService.getExecutionWindowRequired()) {
            ExecutionWindow executionWindow = client.findById(catalogService.getDefaultExecutionWindowId().getURI());
            String msg = match(scheduleInfo, executionWindow);
            if (!msg.isEmpty()) {
                throw APIException.badRequests.schduleInfoNotMatchWithExecutionWindow(msg);
            }
        }

        Order order = client.orders().findById(scheduledEvent.getLatestOrderId());
        order.setScheduledTime(convertCalendarToStr(getFirstScheduledTime(scheduleInfo)));
        client.save(order);

        if (catalogService.getExecutionWindowRequired()) {
            scheduledEvent.setExecutionWindowId(catalogService.getDefaultExecutionWindowId());
        } else {
            scheduledEvent.setExecutionWindowId(new NamedURI(ExecutionWindow.INFINITE, "INFINITE"));
        }
        // TODO: update execution window when admin change it in catalog service

        scheduledEvent.setScheduleInfo(new String(org.apache.commons.codec.binary.Base64.encodeBase64(scheduleInfo.serialize()), UTF_8));
        client.save(scheduledEvent);

        return scheduledEvent;
    }

    /**
     * Cancel a scheduled event which should be in APPROVAL or APPROVED status.
     * @param id    Scheduled Event URI
     * @return      OK if cancellation completed successfully
     */
    @POST
    @Path("/{id}/cancel")
    @Consumes({ MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML })
    public Response cancelScheduledEvent(@PathParam("id") String id) {
        ScheduledEvent scheduledEvent = queryResource(uri(id));
        ArgValidator.checkEntity(scheduledEvent, uri(id), true);

        StorageOSUser user = getUserFromContext();
        verifyAuthorizedInTenantOrg(uri(scheduledEvent.getTenant()), user);

        if(! (scheduledEvent.getEventStatus().equals(ScheduledEventStatus.APPROVAL) ||
                scheduledEvent.getEventStatus().equals(ScheduledEventStatus.APPROVED) ||
                scheduledEvent.getEventStatus().equals(ScheduledEventStatus.REJECTED)) ) {
            throw APIException.badRequests.unexpectedValueForProperty(ScheduledEvent.EVENT_STATUS, "APPROVAL|APPROVED|REJECTED",
                    scheduledEvent.getEventStatus().name());
        }

        Order order = client.orders().findById(scheduledEvent.getLatestOrderId());
        ArgValidator.checkEntity(order, uri(id), true);
        order.setOrderStatus(OrderStatus.CANCELLED.name());
        client.save(order);

        scheduledEvent.setEventStatus(ScheduledEventStatus.CANCELLED);
        client.save(scheduledEvent);
        return Response.ok().build();
    }

    /**
     * Deactivates the scheduled event and its orders
     *
     * @param id the URN of a scheduled event to be deactivated
     * @return OK if deactivation completed successfully
     * @throws DatabaseException when a DB error occurs
     */
    @POST
    @Path("/{id}/deactivate")
    @Produces({ MediaType.APPLICATION_XML, MediaType.APPLICATION_JSON })
    @CheckPermission(roles = { Role.TENANT_ADMIN })
    public Response deactivateScheduledEvent(@PathParam("id") String id) throws DatabaseException {
        ScheduledEvent scheduledEvent = queryResource(uri(id));
        ArgValidator.checkEntity(scheduledEvent, uri(id), true);

        // deactivate all the orders from the scheduled event
        URIQueryResultList resultList = new URIQueryResultList();
        _dbClient.queryByConstraint(
                ContainmentConstraint.Factory.getScheduledEventOrderConstraint(uri(id)), resultList);
        for (URI uri : resultList) {
            log.info("deleting order: {}", uri);
            Order order = _dbClient.queryObject(Order.class, uri);
            client.delete(order);
        }

        // deactive the scheduled event
        client.delete(scheduledEvent);
        return Response.ok().build();
    }
}