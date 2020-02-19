from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from datetime import *
import urllib.parse
import json


class OnSchedService:
    SANDBOX_TOKEN_URL = 'https://sandbox-identity.onsched.com/connect/token'
    SANDBOX_API_URL_BASE = 'https://sandbox-api.onsched.com'
    PROD_TOKEN_URL = 'https://identity.onsched.com/connect/token'
    PROD_API_URL_BASE = 'https://api.onsched.com'

    def __init__(self, client_id, client_secret, scope='OnSchedAPI', environment='sandbox'):
        """Creates an OnSchedService instance.

        :param client_id: client id provided by OnSched
        :type client_id: str
        :param client_secret: client secret provided by OnSched
        :type client_secret: str
        :param scope: client scope provided by OnSched
        :type scope: str
        :param environment: app environment ('sandbox' for sandbox endpoints, 'live' for production endpoints)
        :type environment: str
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.token_url = f'{self.SANDBOX_TOKEN_URL}'
        self.consumer_api = f'{self.SANDBOX_API_URL_BASE}/consumer/v1'
        self.setup_api = f'{self.SANDBOX_API_URL_BASE}/setup/v1'

        if environment=='live':
            self.token_url = f'{self.PROD_TOKEN_URL}'
            self.consumer_api = f'{self.PROD_API_URL_BASE}/consumer/v1'
            self.setup_api = f'{self.PROD_API_URL_BASE}/setup/v1'

        self.session = None
        self.admin_session = None
        self._set_session()
        self._set_setup_session()


    def locations(self):
        """Get a complete list of locations

        :return: location data dictionary

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        locations_url = f'{self.consumer_api}/locations?'

        return self._fetch_data(url=locations_url)


    def location(self, location_id):
        """Get a single location

        :param location_id: the specific location id to be searched
        :type location_id: str

        :return: a single location data
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """

        location_url = f'{self.consumer_api}/locations/{location_id}?'

        return self._fetch_data(url=location_url)


    def services(self, location_id='', service_group='', default_service=False):
        """Get a complete list of services based on location_id

        :param location_id: the location id for which the services will be returned
        :type location_id: str
        :param service_group: filter the search by service group id
        :type service_group: str
        :param default_service: filter the search by service group id
        :type default_service: bool

        :return: services data dictionary

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        services_url = f'{self.consumer_api}/services?'

        params_map = {}
        if location_id:
            params_map['locationId'] = location_id
        if service_group:
            params_map['serviceGroup'] = service_group
        if default_service:
            params_map['defaultService'] = 'true'

        params = urllib.parse.urlencode(params_map)

        services_url += params

        return self._fetch_data(url=services_url)


    def customers(self, location_id='', group_id='', email='', lastname='', deleted=False):
        """Return a list of customers based on a location

        :param location_id: the location id for the search
        :type location_id: str
        :param group_id: the group id for the search
        :type group_id: str
        :param email: the email of the customer to search
        :type email: str
        :param lastname: the lastname of the customer
        :type lastname: str
        :param deleted: search for deleted customers
        :type deleted: bool

        :return: a list of customers matching the criteria
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        customers_url = f'{self.consumer_api}/customers?'

        params_map = {}
        if location_id:
            params_map['locationId'] = location_id
        if group_id:
            params_map['groupId'] = group_id
        if email:
            params_map['email'] = email
        if lastname:
            params_map['lastname'] = lastname
        if deleted:
            params_map['deleted'] = 'true'

        params = urllib.parse.urlencode(params_map)

        customers_url += params

        return self._fetch_data(url=customers_url)


    def availability(self,
                     service_id,
                     start_date,
                     end_date,
                     start_time=0,
                     end_time=0,
                     location_id='',
                     resource_id='',
                     resource_group_id='',
                     resource_ids=None,
                     duration=0,
                     tz_offset=0,
                     day_availability=0,
                     first_day_available=False):
        """Get Availability information for a given service between start_date and end_date

        Choose your search criteria carefully. Availability is an expensive call.
        If you search availability for all resources then you should only do so for a single date.
        If you decide to search availability for multiple dates you should only do so for a specific
        resource by specifying the optional resourceId parameter.

        firstDayAvailable only works with day availability. If set to true it will look for the first day
        available within the range specified by the dayAvailability parameter. The two parameters together can
        be a clever way to display availability for a week or month. Tip - pass in the beginning of the week or month,
        and available times are displayed for the first available date if exists.

        You should only specify the duration parameter if you let your customers choose the duration of the
        appointment. e.g. from a list.

        The tz parameter allows you to select a suitable timezone for the customer to book in. Your app should be
        timezone aware if you use this option. The requested timezone is specified as an offset(plus or minus)
        from GMT time.

        :param service_id: service id for availability search
        :type service_id: str
        :param start_date: start date for availability search
        :type start_date: date
        :param end_date: end date for availability search
        :type end_date: date
        :param start_time: start time specified as military times e.g. 800 = 8:00am, 2230 = 10:30pm. You will
                           only see availability within the boundary of your business start and end times.
                           Defaults to Business Hours Start.
        :type start_time: int
        :param end_time: end time specified as military times e.g. 800 = 8:00am, 2230 = 10:30pm. You will
                         only see availability within the boundary of your business start and end times.
                         Defaults to Business Hours End.
        :type end_time: int
        :param location_id: the id of the business location. Defaults to first business location.
        :type location_id: str
        :param resource_id: resource id for availability search.
        :type resource_id: str
        :param resource_group_id: resource group id for availability search
        :type resource_group_id: str
        :param resource_ids: List of resource id strings for availability search
        :type resource_ids: list
        :param duration: duration of the service in minutes if different than the default
        :type duration: int
        :param tzOffset: request timezone offset to view availability
        :type tz_offset: int
        :param day_availability: Return day availability for number of days specified from start_date.
        :type day_availability: int
        :param first_day_available: Return available times for the first available day
        :type first_day_available: bool

        :return: Returns a list of times available as well as information about the resource and service
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        :exception TypeError: raised if date inputs are in incorrect format
        """
        if type(start_date) is date:
            startDate = start_date.isoformat()
        elif type(start_date) is str:
            startDate = start_date
        else:
            raise TypeError
        if type(end_date) is date:
            endDate = end_date.isoformat()
        elif type(end_date) is str:
            endDate = end_date
        else:
            raise TypeError

        availability_url = f'{self.consumer_api}/availability/{service_id}/{startDate}/{endDate}?'

        params_map = {}
        if start_time:
            params_map['startTime'] = start_time
        if end_time:
            params_map['endTime'] = end_time
        if location_id:
            params_map['locationId'] = location_id
        if resource_id:
            params_map['resourceId'] = resource_id
        if resource_group_id:
            params_map['resourceGroupId'] = resource_group_id
        if resource_ids:
            params_map['resourceIds'] = resource_ids.join(',')
        if duration:
            params_map['duration'] = duration
        if tz_offset:
            params_map['tzOffset'] = tz_offset
        if day_availability:
            params_map['dayAvailability'] = day_availability
        if first_day_available == True:
            params_map['first_day_available'] = 'true'

        params = urllib.parse.urlencode(params_map)

        availability_url += params

        return self._fetch_data(url=availability_url)


    def appointments(self,
                     location_id='',
                     email='',
                     lastname='',
                     service_id='',
                     service_allocation_id='',
                     resource_id='',
                     customer_id='',
                     start_date=None,
                     end_date=None,
                     status='',
                     booked_by=''):
        """List all appointments

        :param location_id: filter appointments by location
        :type location_id: str
        :param email: filter appointments by customer email
        :type email: str
        :param lastname: filter appointments by customer lastname
        :type lastname: str
        :param service_id: filter appointments by service_id
        :type service_id: str
        :param service_allocation_id: filter appointments by service_allocation_id
        :type service_allocation_id: str
        :param resource_id: filter appointments by resource_id
        :type resource_id: str
        :param customer_id: filter appointments by customer_id
        :type customer_id: str
        :param start_date: filter appointments by on/after start date
        :type start_date: datetime
        :param end_date: filter appointments by on/before end date
        :type end_date: datetime
        :param status: filter appointments by booking status. valid values are IN, BK, CN, RE, RS
        :type status: str
        :param booked_by: filter appointments by the user email that made the booking
        :type booked_by: str

        :return: Returns a dictionary containing a list of appointments filtered
                 by the parameters specified
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        :exception TypeError: raised if date_time inputs are in incorrect format
        """
        appointments_url = f'{self.consumer_api}/appointments?'

        params_map = {}
        if location_id:
            params_map['locationId'] = location_id
        if email:
            params_map['email'] = email
        if lastname:
            params_map['lastname'] = lastname
        if service_id:
            params_map['serviceId'] = service_id
        if service_allocation_id:
            params_map['serviceAllocationId'] = service_allocation_id
        if resource_id:
            params_map['resourceId'] = resource_id
        if customer_id:
            params_map['customerId'] = customer_id
        if status:
            params_map['status'] = status
        if booked_by:
            params_map['bookedBy'] = booked_by
        if start_date:
            if type(start_date) is datetime or type(start_date) is date:
                params_map['startDate'] = start_date.isoformat()
            elif type(start_date) is str:
                params_map['startDate'] = start_date
            else:
                raise TypeError
        if end_date:
            if type(end_date) is datetime or type(end_date) is date:
                params_map['endDate'] = end_date.isoformat()
            elif type(end_date) is str:
                params_map['endDate'] = end_date
            else:
                raise TypeError

        params = urllib.parse.urlencode(params_map)

        appointments_url += params

        return self._fetch_data(url=appointments_url)


    def create_appointment(self,
                           service_id,
                           start_date_time,
                           end_date_time,
                           resource_id,
                           location_id='',
                           customer_id='',
                           service_allocation_id='',
                           booked_by=''):
        """Create a new appointment

        This end point creates a new appointment in an Initial "IN" status.

        A valid serviceId is required. Use GET consumer/v1/services to retrieve a list of your services.

        A valid resourceId is required if your calendar is a resource based calendar. Use consumer/v1/resources to retrieve a list of your resources.

        StartDateTime and EndDateTime are required. Use the ISO 8601 format for DateTime Timezone. e.g. 2016-10-30T9:00:00-5:00

        :param service_id: the service id for the booking
        :type service_id: str
        :param start_date_time: the start time of the appointment
        :type start_date_time: datetime
        :param end_date_time: the end time of the appointment
        :type end_date_time: datetime
        :param location_id: the location id for the booking
        :type location_id: str
        :param resource_id: the resource id for the booking
        :type resource_id: str
        :param customer_id: the customer id if available
        :type customer_id: str
        :param service_allocation_id: the service allocation for the appointment
        :type service_allocation_id: str
        :param booked_by: the person booking the appointment
        :type booked_by: str

        :return: Returns a dictionary containing the appointment reservations, including appointment id
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        :exception TypeError: raised if date_time inputs are in incorrect format
        """
        appointment_url = f'{self.consumer_api}/appointments'

        payload = { 'serviceId': service_id }

        if type(start_date_time) is datetime:
            payload['startDateTime'] = start_date_time.isoformat()
        elif type(start_date_time) is str:
            payload['startDateTime'] = start_date_time
        else:
            raise TypeError

        if type(end_date_time) is datetime:
            payload['endDateTime'] = end_date_time.isoformat()
        elif type(end_date_time) is str:
            payload['endDateTime'] = end_date_time
        else:
            raise TypeError

        if customer_id:
            payload['customerId'] = customer_id
        if booked_by:
            payload['bookedBy'] = booked_by
        if resource_id:
            payload['resourceId'] = resource_id
        if location_id:
            payload['locationId'] = location_id
        if service_allocation_id:
            payload['serviceAllocationId'] = service_allocation_id

        return self._post_data(url=appointment_url, data=payload)


    def book_appointment(self,
                         appointment_id,
                         email='',
                         name='',
                         phone='',
                         phone_type='',
                         phone_ext='',
                         customer_message='',
                         notes='',
                         appointment_booking_fields=None,
                         customer_booking_fields=None):
        """Finalize a booking

        Completes a new booking. Only appointments in the "IN" initial status can be booked,
        by saving all the relevant details of the booking.

        A valid appointment id is required. Use the appointment_id returned from create_appointment

        :param appointment_id: the id on the appointment object returned created by create_appointment
        :type appointment_id: str
        :param email: the customer's email address
        :type email: str
        :param name: the customer's name
        :type name: str
        :param phone: the customer's phone number
        :type phone: str
        :param phone_type: the type of phone, eg one of ('mobile','home','office')
        :type phone_type: str
        :param phone_ext: customers phone extension if available
        :type phone_ext: str
        :param customer_message: any custom message the customer wishes to leave about the appointment
        :type customer_message: str
        :param notes:
        :type notes: str
        :param appointment_booking_fields: custom booking fields dictionary in the form of
                                           [ { name: string, value: string }, { name: string, value: string }, ... ]
        :type appointment_booking_fields: dict
        :param customer_booking_fields: custom customer field dictionary in the form of
                                        [ { name: string, value: string }, { name: string, value: string }, ... ]
        :type customer_booking_fields: dict

        :return: Returns a dictionary of the appointment
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        appointment_url = f'{self.consumer_api}/appointments/{appointment_id}/book'

        payload = {}
        if email:
            payload['email'] = email
        if name:
            payload['name'] = name
        if phone:
            payload['phone'] = phone
        if phone_type:
            payload['phoneType'] = phone_type
        if phone_ext:
            payload['phoneExt'] = phone_ext
        if customer_message:
            payload['customerMessage'] = customer_message
        if notes:
            payload['notes'] = notes
        if appointment_booking_fields:
            payload['appointmentBookingFields'] = appointment_booking_fields
        if customer_booking_fields:
            payload['customerBookingFields'] = customer_booking_fields

        return self._update_data(url=appointment_url, data=payload)


    def cancel_appointment(self, appointment_id):
        """Cancel an appointment which has been booked with book_appointment

        :param appointment_id: the appointment id to be cancelled
        :type appointment_id: str

        :return: returns the booking that has been cancelled with the status updated to CN
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        cancellation_url = f'{self.consumer_api}/appointments/{appointment_id}/cancel'

        return self._update_data(url=cancellation_url, data={})


    # Setup API actions
    def create_resource(self,
                        name,
                        email='',
                        description='',
                        location_id='',
                        group_id='',
                        timezone_id='',
                        addressline1='',
                        addressline2='',
                        city='',
                        state='',
                        country='',
                        postal_code='',
                        contact_preferred_phone_type='',
                        contact_home_phone='',
                        contact_mobile_phone='',
                        contact_business_phone='',
                        contact_business_phone_ext='',
                        contact_skype_username='',
                        effective_date=None,
                        notification_type=0,
                        display_color='',
                        google_calendar_id='',
                        outlook_calendar_id='',
                        ignore_business_hours=False,
                        gender='',
                        hourly=0,
                        calendar_availability=0,
                        sort_key=0,
                        bio_link=''):
        """Create a resource

        :param name: the resource name
        :type name: str
        :param location_id: the location id for the resource
        :type location_id: str
        :param email: an email address for the resource
        :type email: str
        :param description: a description of the resource
        :type description: str
        :param group_id: the resource group id
        :type group_id: str
        :param timezone_id: the timezone id for the resource. defaults to the business timezone if empty
        :type timezone_id: str
        :param addressline1: the address of the resource
        :type addressline1: str
        :param addressline2: the address of the resource
        :type addressline2: str
        :param city: the city of the resource
        :type city: str
        :param state: the state/province of the resource
        :type state: str
        :param country: the country of the resource
        :type country: str
        :param postal_code: the postal code for the resource
        :type postal_code: str
        :param contact_preferred_phone_type: type of contact preferred (mobile|business|home|skype)
        :type contact_preferred_phone_type: str
        :param contact_home_phone: the resource's home phone number
        :type contact_home_phone: str
        :param contact_mobile_phone: the resource's mobile phone number
        :type contact_mobile_phone: str
        :param contact_business_phone: the resource's business phone number
        :type contact_business_phone: str
        :param contact_business_phone_ext: the resource's business phone extension
        :type contact_business_phone_ext: str
        :param contact_skype_username: the resource's skype username
        :type contact_skype_username: str
        :param effective_date: the datetime that this resource will become available in the system
        :type effective_date: datetime
        :param notification_type: the notification type (0: default, 1: email, 2: SMS, 3: email + SMS)
        :type notification_type: int
        :param display_color: the color for the resource, which will control the calendar color in the portal
        :type display_color: str
        :param google_calendar_id: the resource's google calendar
        :type google_calendar_id: str
        :param outlook_calendar_id: the resource's outlook calendar
        :type outlook_calendar_id: str
        :param ignore_business_hours: is the resource available outside normal business hours?
        :type ignore_business_hours: bool
        :param gender: the resource gender (for people)
        :type gender: str
        :param hourly: hourly pay rate for the resource
        :type hourly: int
        :param calendar_availability: which calendar system the resources uses
                                      (0: OnSched Cal, 1: Google Cal, 2: Outlook Cal)
        :type calendar_availability: int
        :param sort_key: a numeric value that can be used for sorting the resources list
        :type sort_key: int
        :param bio_link: a URL for additional resource information
        :type bio_link: str
        :return: A resource object dictionary
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        :exception TypeError: raised if datetime inputs are in incorrect format
        """
        create_resource_url = f'{self.setup_api}/resources'

        payload = { 'name': name }

        payload.update(self._get_resources_data(email=email,
                                                description=description,
                                                location_id=location_id,
                                                group_id=group_id,
                                                timezone_id=timezone_id,
                                                addressline1=addressline1,
                                                addressline2=addressline2,
                                                city=city,
                                                state=state,
                                                country=country,
                                                postal_code=postal_code,
                                                contact_preferred_phone_type=contact_preferred_phone_type,
                                                contact_home_phone=contact_home_phone,
                                                contact_mobile_phone=contact_mobile_phone,
                                                contact_business_phone=contact_business_phone,
                                                contact_business_phone_ext=contact_business_phone_ext,
                                                contact_skype_username=contact_skype_username,
                                                effective_date=effective_date,
                                                notification_type=notification_type,
                                                display_color=display_color,
                                                google_calendar_id=google_calendar_id,
                                                outlook_calendar_id=outlook_calendar_id,
                                                ignore_business_hours=ignore_business_hours,
                                                gender=gender,
                                                hourly=hourly,
                                                calendar_availability=calendar_availability,
                                                sort_key=sort_key,
                                                bio_link=bio_link)
                       )

        return self._post_setup_data(url=create_resource_url, data=payload)


    def update_resource(self,
                        resource_id,
                        name='',
                        email='',
                        description='',
                        location_id='',
                        group_id='',
                        timezone_id='',
                        addressline1='',
                        addressline2='',
                        city='',
                        state='',
                        country='',
                        postal_code='',
                        contact_preferred_phone_type='',
                        contact_home_phone='',
                        contact_mobile_phone='',
                        contact_business_phone='',
                        contact_business_phone_ext='',
                        contact_skype_username='',
                        effective_date=None,
                        notification_type=0,
                        display_color='',
                        google_calendar_id='',
                        outlook_calendar_id='',
                        ignore_business_hours=False,
                        gender='',
                        hourly=0,
                        calendar_availability=0,
                        sort_key=0,
                        bio_link=''):
        """Update a resource

        :param resource_id: the resource id to be updated
        :type resource_id: str
        :param name: the resource name
        :type name: str
        :param location_id: the location id for the resource
        :type location_id: str
        :param email: an email address for the resource
        :type email: str
        :param description: a description of the resource
        :type description: str
        :param group_id: the resource group id
        :type group_id: str
        :param timezone_id: the timezone id for the resource. defaults to the business timezone if empty
        :type timezone_id: str
        :param addressline1: the address of the resource
        :type addressline1: str
        :param addressline2: the address of the resource
        :type addressline2: str
        :param city: the city of the resource
        :type city: str
        :param state: the state/province of the resource
        :type state: str
        :param country: the country of the resource
        :type country: str
        :param postal_code: the postal code for the resource
        :type postal_code: str
        :param contact_preferred_phone_type: type of contact preferred (mobile|business|home|skype)
        :type contact_preferred_phone_type: str
        :param contact_home_phone: the resource's home phone number
        :type contact_home_phone: str
        :param contact_mobile_phone: the resource's mobile phone number
        :type contact_mobile_phone: str
        :param contact_business_phone: the resource's business phone number
        :type contact_business_phone: str
        :param contact_business_phone_ext: the resource's business phone extension
        :type contact_business_phone_ext: str
        :param contact_skype_username: the resource's skype username
        :type contact_skype_username: str
        :param effective_date: the datetime that this resource will become available in the system
        :type effective_date: datetime
        :param notification_type: the notification type (0: default, 1: email, 2: SMS, 3: email + SMS)
        :type notification_type: int
        :param display_color: the color for the resource, which will control the calendar color in the portal
        :type display_color: str
        :param google_calendar_id: the resource's google calendar
        :type google_calendar_id: str
        :param outlook_calendar_id: the resource's outlook calendar
        :type outlook_calendar_id: str
        :param ignore_business_hours: is the resource available outside normal business hours?
        :type ignore_business_hours: bool
        :param gender: the resource gender (for people)
        :type gender: str
        :param hourly: hourly pay rate for the resource
        :type hourly: int
        :param calendar_availability: which calendar system the resources uses
                                      (0: OnSched Cal, 1: Google Cal, 2: Outlook Cal)
        :type calendar_availability: int
        :param sort_key: a numeric value that can be used for sorting the resources list
        :type sort_key: int
        :param bio_link: a URL for additional resource information
        :type bio_link: str

        :return: A resource object dictionary
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        :exception TypeError: raised if datetime inputs are in incorrect format
        """
        update_resource_url = f'{self.setup_api}/resources/{resource_id}'

        payload = {}

        if name:
            payload['name'] = name

        payload.update(self._get_resources_data(email=email,
                                                description=description,
                                                location_id=location_id,
                                                group_id=group_id,
                                                timezone_id=timezone_id,
                                                addressline1=addressline1,
                                                addressline2=addressline2,
                                                city=city,
                                                state=state,
                                                country=country,
                                                postal_code=postal_code,
                                                contact_preferred_phone_type=contact_preferred_phone_type,
                                                contact_home_phone=contact_home_phone,
                                                contact_mobile_phone=contact_mobile_phone,
                                                contact_business_phone=contact_business_phone,
                                                contact_business_phone_ext=contact_business_phone_ext,
                                                contact_skype_username=contact_skype_username,
                                                effective_date=effective_date,
                                                notification_type=notification_type,
                                                display_color=display_color,
                                                google_calendar_id=google_calendar_id,
                                                outlook_calendar_id=outlook_calendar_id,
                                                ignore_business_hours=ignore_business_hours,
                                                gender=gender,
                                                hourly=hourly,
                                                calendar_availability=calendar_availability,
                                                sort_key=sort_key,
                                                bio_link=bio_link)
                       )

        return self._update_setup_data(url=update_resource_url, data=payload)


    def delete_resource(self, resource_id):
        """Delete a resource

        :param resource_id: the id of the resource to be deleted
        :type resource_id: str
        :return: the resource object that has been deleted
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        delete_resource_url = f'{self.setup_api}/resources/{resource_id}'

        return self._delete_setup_data(url=delete_resource_url)


    def create_service(self,
                       name,
                       description,
                       duration,
                       location_id='',
                       service_group_id='',
                       public=False,
                       default_service=False,
                       duration_select=False,
                       duration_interval=0,
                       duration_min=0,
                       duration_max=0,
                       padding=0,
                       consumer_padding=False,
                       fee_amount=0,
                       fee_taxable=False,
                       cancellation_fee_amount=0,
                       cancellation_fee_taxable=False,
                       nonrefundable=False):
        """Create a new service

        :param name: the name of the service
        :type name: str
        :param description: a description of the service
        :type description: str
        :param duration: the default duration of the service
        :type duration: int
        :param location_id: the location id for the service
        :type location_id: str
        :param service_group_id: the service group id for the service
        :type service_group_id: str
        :param public: is this service available for booking?
        :type public: bool
        :param default_service: is this the default service?
        :type default_service: bool
        :param duration_select: is the duration selectable?
        :type duration_select: bool
        :param duration_interval: if duration is selectable, set time intervals
        :type duration_interval: int
        :param duration_min: minimum duration for selectable durations
        :type duration_min: int
        :param duration_max: maximum duration for selectable durations
        :type duration_max: int
        :param padding: padding between bookings in minutes
        :type padding: int
        :param consumer_padding: can the customer add padding?
        :type consumer_padding: bool
        :param fee_amount: cost of the service
        :type fee_amount: int
        :param fee_taxable: is this fee taxable
        :type fee_taxable: bool
        :param cancellation_fee_amount: cost of cancellation
        :type cancellation_fee_amount: int
        :param cancellation_fee_taxable: is the cancellation fee taxable?
        :type cancellation_fee_taxable: bool
        :param nonrefundable: is the service cost refundable
        :type nonrefundable: bool

        :return: a new service object
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        service_url = f'{self.setup_api}/services'

        # if any of the option items are set, build the option dictionary
        options={}
        if default_service or duration_select or duration_interval \
            or duration_min or duration_max or padding or consumer_padding:
            options['durationInterval'] = duration_interval
            options['durationMin'] = duration_min
            options['durationMax'] = duration_max
            options['padding'] = padding
            options['durationSelect'] = 'true' if duration_select else 'false'
            options['durationService'] = 'true' if default_service else 'false'
            options['consumerPadding'] = 'true' if consumer_padding else 'false'

        # if any of the fee items are set, build the fee dictionary
        fee = {}
        if fee_amount or fee_taxable or cancellation_fee_amount or cancellation_fee_taxable or nonrefundable:
            fee['feeAmount'] = fee_amount
            fee['cancellationFeeAmount'] = cancellation_fee_amount
            fee['feeTaxable'] = 'true' if fee_taxable else 'false'
            fee['cancellationFeeTaxable'] = 'true' if cancellation_fee_taxable else 'false'
            fee['nonRefundable'] = 'true' if nonrefundable else 'false'

        payload = { 'name': name, 'description': description }

        if location_id:
            payload['locationId'] = location_id
        if duration:
            payload['duration'] = duration
        if service_group_id:
            payload['serviceGroupId'] = service_group_id
        if public:
            payload['public'] = 'true'
        if options:
            payload['options'] = options
        if fee:
            payload['fee']

        return self._post_data(service_url, payload)


    def delete_service(self, service_id):
        """Delete a service

        :param service_id: the id of the service to be deleted
        :type service_id: str

        :return: the service object that has been deleted
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        delete_service_url = f'{self.setup_api}/services/{service_id}'

        return self._delete_setup_data(url=delete_service_url)


    def service_allocations(self, service_id, start_date=None, end_date=None, location_id=''):
        """Get the service allocations for a given service

        :param service_id: the service id for the event.  Passing a '0' in for service_id
                           will return allocations for all services
        :param start_date: date object for starting date of search
        :type start_date: date
        :param end_date: date object for ending date of search
        :type end_date: date
        :param location_id: filter results by location id
        :type location_id: str

        :return: service allocations data dictionary
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        :exception TypeError: raised if datetime inputs are in incorrect format
        """
        service_allocations_url = f'{self.consumer_api}/services/{service_id}/allocations?'

        params_map = {}
        if location_id:
            params_map['locationId'] = location_id
        if start_date:
            if type(start_date) is date or type(start_date) is datetime:
                params_map['startDate']= start_date.isoformat()
            elif type(start_date) is str:
                params_map['startDate']= start_date
            else:
                raise TypeError
        if end_date:
            if type(end_date) is date or type(end_date) is datetime:
                params_map['endDate']= end_date.isoformat()
            elif type(end_date) is str:
                params_map['endDate']= end_date
            else:
                raise TypeError

        params = urllib.parse.urlencode(params_map)

        service_allocations_url += params

        return self._fetch_setup_data(url=service_allocations_url)


    def service_allocation(self, service_allocation_id):
        """Get a single service allocation

        :param service_allocation_id: the id of the service allocation
        :type service_allocation_id: str

        :return: single service allocation data
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        service_allocation_url = f'{self.consumer_api}/services/allocations/{service_allocation_id}?'

        return self._fetch_data(url=service_allocation_url)


    def create_service_allocation(self,
                                  service_id,
                                  start_date,
                                  end_date,
                                  start_time,
                                  end_time,
                                  location_id='',
                                  resource_id='',
                                  reason='',
                                  all_day=False):
        """Create a new service allocation

        :param service_id: the service id for this allocation
        :type service_id: str
        :param start_date: the starting date of the event
        :type start_date: date
        :param end_date: The ending date of the event
        :type end_date: date
        :param start_time: start time specified as military times e.g. 800 = 8:00am, 2230 = 10:30pm. You will
                           only see availability within the boundary of your business start and end times.
                           Defaults to Business Hours Start.
        :type start_time: int
        :param end_time: end time specified as military times e.g. 800 = 8:00am, 2230 = 10:30pm. You will
                         only see availability within the boundary of your business start and end times.
                         Defaults to Business Hours Start.
        :param location_id: the location id for the event
        :type location_id: str
        :param resource_id: the resource id associated with the service allocation
        :type resource_id: str
        :type end_time: int
        :param reason: The purpose of the event
        :type reason: str
        :param all_day: is event an all day event?
        :type all_day: bool

        :return: a serviceAllocation object containing the data of the new allocation
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        :exception TypeError: raised if datetime inputs are in incorrect format
        """
        create_service_allocation_url = f'{self.setup_api}/services/{service_id}/allocations'

        payload = {}

        if type(start_date) is date:
            payload['startDate'] = start_date.isoformat()
        elif type(start_date) is str:
            payload['startDate'] = start_date
        else:
            raise TypeError

        if type(end_date) is date:
            payload['endDate'] = end_date.isoformat()
        elif type(end_date) is str:
            payload['endDate'] = end_date
        else:
            raise TypeError

        if location_id:
            payload['locationId'] = location_id
        if resource_id:
            payload['resourceId'] = resource_id
        if start_time:
            payload['startTime'] = start_time
        if end_time:
            payload['endTime'] = end_time
        if reason:
            payload['reason'] = reason
        if all_day:
            payload['allDay'] = 'true'

        return self._post_setup_data(url=create_service_allocation_url, data=payload)


    #####################
    # Private methods
    #####################
    def _get_resources_data(self,
                            email='',
                            description='',
                            location_id='',
                            group_id='',
                            timezone_id='',
                            addressline1='',
                            addressline2='',
                            city='',
                            state='',
                            country='',
                            postal_code='',
                            contact_preferred_phone_type='',
                            contact_home_phone='',
                            contact_mobile_phone='',
                            contact_business_phone='',
                            contact_business_phone_ext='',
                            contact_skype_username='',
                            effective_date=None,
                            notification_type=0,
                            display_color='',
                            google_calendar_id='',
                            outlook_calendar_id='',
                            ignore_business_hours=False,
                            gender='',
                            hourly=0,
                            calendar_availability=0,
                            sort_key=0,
                            bio_link=''):
        """Gather resource data into a dictionary

        :param name: the resource name
        :type name: str
        :param location_id: the location id for the resource
        :type location_id: str
        :param email: an email address for the resource
        :type email: str
        :param description: a description of the resource
        :type description: str
        :param group_id: the resource group id
        :type group_id: str
        :param timezone_id: the timezone id for the resource. defaults to the business timezone if empty
        :type timezone_id: str
        :param addressline1: the address of the resource
        :type addressline1: str
        :param addressline2: the address of the resource
        :type addressline2: str
        :param city: the city of the resource
        :type city: str
        :param state: the state/province of the resource
        :type state: str
        :param country: the country of the resource
        :type country: str
        :param postal_code: the postal code for the resource
        :type postal_code: str
        :param contact_preferred_phone_type: type of contact preferred (mobile|business|home|skype)
        :type contact_preferred_phone_type: str
        :param contact_home_phone: the resource's home phone number
        :type contact_home_phone: str
        :param contact_mobile_phone: the resource's mobile phone number
        :type contact_mobile_phone: str
        :param contact_business_phone: the resource's business phone number
        :type contact_business_phone: str
        :param contact_business_phone_ext: the resource's business phone extension
        :type contact_business_phone_ext: str
        :param contact_skype_username: the resource's skype username
        :type contact_skype_username: str
        :param effective_date: the datetime that this resource will become available in the system
        :type effective_date: datetime
        :param notification_type: the notification type (0: default, 1: email, 2: SMS, 3: email + SMS)
        :type notification_type: int
        :param display_color: the color for the resource, which will control the calendar color in the portal
        :type display_color: str
        :param google_calendar_id: the resource's google calendar
        :type google_calendar_id: str
        :param outlook_calendar_id: the resource's outlook calendar
        :type outlook_calendar_id: str
        :param ignore_business_hours: is the resource available outside normal business hours?
        :type ignore_business_hours: bool
        :param gender: the resource gender (for people)
        :type gender: str
        :param hourly: hourly pay rate for the resource
        :type hourly: int
        :param calendar_availability: which calendar system the resources uses
                                      (0: OnSched Cal, 1: Google Cal, 2: Outlook Cal)
        :type calendar_availability: int
        :param sort_key: a numeric value that can be used for sorting the resources list
        :type sort_key: int
        :param bio_link: a URL for additional resource information
        :type bio_link: str

        :return: A resource object dictionary
        :rtype: dict

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        :exception TypeError: raised if datetime inputs are in incorrect format
        """
        payload = {}

        if email:
            payload['email'] = email
        if description:
            payload['description'] = description
        if location_id:
            payload['locationId'] = location_id
        if group_id:
            payload['groupId'] = group_id
        if timezone_id:
            payload['timezoneId'] = timezone_id
        # set the address if submitted
        address = {}
        if addressline1 or addressline2 or city or state or postal_code or country:
            address['addressline1'] = addressline1
            address['addressline2'] = addressline2
            address['city'] = city
            address['state'] = state
            address['postalCode'] = postal_code
            address['country'] = country

        # set the contact information if present
        contact = {}
        if contact_preferred_phone_type or contact_home_phone \
                or contact_mobile_phone or contact_business_phone \
                or contact_business_phone_ext or contact_skype_username:

            contact['PreferredPhoneType'] = contact_preferred_phone_type

            if contact_home_phone:
                contact['homePhone'] = contact_home_phone
            if contact_mobile_phone:
                contact['mobilePhone'] = contact_mobile_phone
            if contact_business_phone:
                contact['businessPhone'] = contact_business_phone
            if contact_business_phone_ext:
                contact['businessPhoneExt'] = contact_business_phone_ext
            if contact_skype_username:
                contact['skypeUsername'] = contact_skype_username

        # set the options that are present
        options = {}
        if effective_date or notification_type or display_color \
                or google_calendar_id or outlook_calendar_id \
                or ignore_business_hours or gender or hourly \
                or calendar_availability or sort_key or bio_link:
            if effective_date:
                if type(effective_date) is datetime:
                    options['effectiveDate'] = effective_date.isoformat()
                elif type(effective_date) is str:
                    options['effectiveDate'] = effective_date
                else:
                    raise TypeError

            if notification_type:
                options['notificationType'] = notification_type
            if display_color:
                options['displayColor'] = display_color
            if google_calendar_id:
                options['googleCalendarId'] = google_calendar_id
            if outlook_calendar_id:
                options['outlookCalendarId'] = outlook_calendar_id
            if ignore_business_hours:
                options['ignoreBusinessHours'] = 'true'
            if gender:
                options['gender'] = gender
            if hourly:
                options['hourly'] = hourly
            if calendar_availability:
                options['calendarAvailability'] = calendar_availability
            if sort_key:
                options['sortKey'] = sort_key
            if bio_link:
                options['bioLink'] = bio_link

        if address:
            payload['address'] = address
        if contact:
            payload['contact'] = contact
        if options:
            payload['options'] = options

        return payload


    def _fetch_data(self, url):
        """Perform a GET request on the given URL

        :param url: complete API URL

        :return: API response formatted as a data dictionary

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        self._set_session()  # verify the session is setup

        offset = 0
        has_more = False
        data = None

        response = self.session.get(url + f'&limit=100&offset={offset}')
        response.raise_for_status()

        formatted_response = json.loads(response.text)

        if 'hasMore' in formatted_response:
            has_more = formatted_response['hasMore']
        if 'data' in formatted_response:
            data = formatted_response['data']

        # loop over the data until 'hasMore' is False
        while has_more:
            offset += 100
            response = self.session.get(url + f'&limit=100&offset={offset}')
            response.raise_for_status()

            formatted_response = json.loads(response.text)

            data += formatted_response['data']
            # update has_more
            has_more = formatted_response['hasMore']

        # use the final response
        result = formatted_response
        # if data exists, replace data with the accumulated result
        if data:
            result['count'] = result['total']
            result['data'] = data

        return result


    def _post_data(self, url, data):
        """Perform a POST request on the given URL

        :param url: complete API URL
        :type: str
        :param data: a dictionary of data to post to the API.  the data is submitted as JSON
        :type: dict

        :return: API response formatted as a data dictionary

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        self._set_session()  # verify the session is setup

        response = self.session.post(url, json=data)

        response.raise_for_status()

        return json.loads(response.text)


    def _update_data(self, url, data):
        """Perform a PUT request on the given URL

        :param url: complete API URL
        :param data: a dictionary of data to send to the update (PUT/PATCH) endpoint.  the data is submitted as JSON

        :return: API response formatted as a data dictionary

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        self._set_session()  # verify the session is setup

        response = self.session.put(url, json=data)

        response.raise_for_status()

        return json.loads(response.text)


    def _fetch_setup_data(self, url):
        """Perform a GET request on the given URL

        :param url: complete API URL

        :return: API response formatted as a data dictionary

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        self._set_setup_session()  # verify the session is setup

        offset = 0
        has_more = False
        data = None

        response = self.admin_session.get(url + f'&limit=100&offset={offset}')
        response.raise_for_status()

        formatted_response = json.loads(response.text)

        if 'hasMore' in formatted_response:
            has_more = formatted_response['hasMore']
        if 'data' in formatted_response:
            data = formatted_response['data']

        # loop over the data until 'hasMore' is False
        while has_more:
            offset += 100
            response = self.admin_session.get(url + f'&limit=100&offset={offset}')
            response.raise_for_status()

            formatted_response = json.loads(response.text)

            data += formatted_response['data']
            # update has_more
            has_more = formatted_response['hasMore']

        # use the final response
        result = formatted_response
        # if data exists, replace data with the accumulated result
        if data:
            result['count'] = result['total']
            result['data'] = data

        return result


    def _post_setup_data(self, url, data):
        """Perform a POST request on the given URL

        :param url: complete API URL
        :type: str
        :param data: a dictionary of data to post to the API.  the data is submitted as JSON
        :type: dict

        :return: API response formatted as a data dictionary

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        self._set_setup_session()  # verify the session is setup

        response = self.admin_session.post(url, json=data)

        response.raise_for_status()

        return json.loads(response.text)


    def _update_setup_data(self, url, data):
        """Perform a PUT request on the given URL

        :param url: complete API URL
        :param data: a dictionary of data to send to the update (PUT/PATCH) endpoint.  the data is submitted as JSON

        :return: API response formatted as a data dictionary

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        self._set_setup_session()  # verify the session is setup

        response = self.admin_session.put(url, json=data)

        response.raise_for_status()

        return json.loads(response.text)


    def _delete_setup_data(self, url):
        """Perform a PUT request on the given URL

        :param url: complete API URL
        :param data: a dictionary of data to send to the update (PUT/PATCH) endpoint.  the data is submitted as JSON

        :return: API response formatted as a data dictionary

        :exception HTTPError: raised if the HTTP request returned an unsuccessful status code
        :exception Timeout: raised if the request times out
        :exception TooManyRedirects: raised if a request exceeds the configured number of maximum re-directions
        """
        self._set_setup_session()

        response = self.admin_session.delete(url)

        response.raise_for_status()

        return json.loads(response.text)


    def _set_session(self):
        """Setup session and token objects by querying the OAuth server
        :return: None
        """
        current_time = datetime.now(timezone.utc)
        unix_timestamp = current_time.timestamp()

        # check if the token is already set up and
        # if the access token is valid
        if self.session and \
                self.session.token and \
                (self.session.token['expires_at'] > unix_timestamp):
            return
        else:
            client = BackendApplicationClient(client_id=self.client_id, scope=self.scope)
            self.session = OAuth2Session(client=client)

            self.session.fetch_token(token_url=self.token_url,
                                     client_id=self.client_id,
                                     client_secret=self.client_secret)


    def _set_setup_session(self):
        """Setup admin session and token objects for accessing the OnSchedule Setup API
        :return: None
        """
        current_time = datetime.now(timezone.utc)
        unix_timestamp = current_time.timestamp()

        # check if the token is already set up and
        # if the access token is valid
        if self.admin_session and \
                self.admin_session.token and \
                (self.admin_session.token['expires_at'] > unix_timestamp):
            return
        else:
            client = BackendApplicationClient(client_id=self.client_id, scope=self.scope)  # TODO: change scope here for setup API
            self.admin_session = OAuth2Session(client=client)

            self.admin_session.fetch_token(token_url=self.token_url,
                                           client_id=self.client_id,
                                           client_secret=self.client_secret)

