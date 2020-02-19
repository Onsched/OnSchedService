# OnSchedService class

This class is intended to facilitate using the OnSched API from a Python3 based
backend.

This service is designed to aid in the creation of backend routes.  Using the class you can directly access
data from the OnSched API, and output from each method is formatted as a Python dictionary for use in your
server side code.

To use, instantiate a OnSchedService object and pass in client_id, client_secret, scope, and 
environment (live for production, sandbox for development and testing).
```python
# for production
onsched = OnSchedService(client_id='<your client id>', 
                         client_secret='<your client secret>', 
                         scope='<your scopes>', 
                         environment='live')

# for testing
# if environment is not specified, it will default to sandbox
onsched = OnSchedService(client_id='<your client id>', 
                         client_secret='<your client secret>', 
                         scope='<your scopes>', 
                         environment='sandbox')
```

|       Method        | OnSched API Endpoint |
|---------------------|----------------------|
| appointments | GET /consumer/v1/appointments |
| availability | GET /consumer/v1/availability/{serviceId}/{startDate}/{endDate} |
| book_appointment | PUT /consumer/v1/appointments/{id}/book |
| cancel_appointment | PUT /consumer/v1/appointments/{id}/cancel |
| create_appointment | POST /consumer/v1/appointments |
| create_resource | POST /setup/v1/resources |
| create_service | POST /setup/v1/services |
| create_service_allocation | POST /setup/v1/services/{id}/allocations |
| customers | GET /consumer/v1/customers |
| delete_resource | DELETE /setup/v1/resources/{id} |
| delete_service | DELETE /setup/v1/services/{id} |
| location | GET /consumer/v1/locations/{id} |
| locations | GET /consumer/v1/locations |
| service_allocation | GET /consumer/v1/services/allocations/{id} |
| service_allocations | GET /consumer/v1/services/{id}/allocations |
| services | GET /consumer/v1/services |
| update_resource | PUT /setup/v1/resources/{id} |

We suggest you build your endpoints to directly map to 
API mappings
### Requirements: 
- Python 3.6+

### Required modules
```python
$ pip install oauthlib
$ pip install requests_oauthlib
```

### Example usage
```python3

onsched = OnSchedService(client_id='DemoUser',
                         client_secret='DemoUser',
                         scope='OnSchedApi setup')

customers = onsched.customers(location_id='ab5343d7-4e60-463d-b6be-0c7d61e25ce5')
print("all customers:\n", customers)
customers = onsched.customers(email='mike@onsched.com')
print("one customer:\n", customers)

delta = timedelta(days=1)
start_date = date.today()
end_date = start_date + delta

availability = onsched.availability(5, start_date, end_date)
print("availability:\n", availability)

time_slot1 = availability['availableTimes'][0]
time_slot2 = availability['availableTimes'][1]

appointment_service_id = '5'

appointment1_start_time = datetime.fromisoformat(time_slot1['startDateTime'])
appointment1_end_time = datetime.fromisoformat(time_slot1['endDateTime'])
appointment1_resource_id = time_slot1['resourceId']

appointment2_start_time = time_slot2['startDateTime']
appointment2_end_time = time_slot2['endDateTime']
appointment2_resource_id = time_slot2['resourceId']

appointment1 = onsched.create_appointment(service_id=appointment_service_id,
                                          start_date_time=appointment1_start_time,
                                          end_date_time=appointment1_end_time,
                                          resource_id=appointment1_resource_id)
print("appointment1:\n", appointment1)

appointment2 = onsched.create_appointment(service_id=appointment_service_id,
                                          start_date_time=appointment2_start_time,
                                          end_date_time=appointment2_end_time,
                                          resource_id=appointment2_resource_id)
print("appointment2:\n", appointment2)

booking1 = onsched.book_appointment(appointment_id=appointment1['id'])
print("booking1:\n", booking1)
print("cancel booking1:\n", onsched.cancel_appointment(booking1['id']))

booking2 = onsched.book_appointment(appointment_id=appointment2['id'],
                                    email='mike@onsched.com',
                                    name='Mike',
                                    phone='7195555555')
print("booking2:\n", booking2)
print( "cancel booking2:\n", onsched.cancel_appointment(appointment_id=booking2['id']) )

# get all bookings by user email
appointments = onsched.appointments(email='mike@onsched.com')
print("appointments:\n", appointments)

# create a new service
locations = onsched.locations()
print("locations:\n", locations)

# find the location with 'burlingtonmedical' as a friendly id
# location = next(location for location in locations['data'] if location['friendlyId'] == 'burlingtonmedical')

location = onsched.location(location_id='e4d61bd8-cdf3-4fc9-887e-2320dce062e0')
print("location:\n", location)

services = onsched.services(location_id=location['id'])
print("services:\n", services)

last_service = services['data'][-1]
print("last service before create:\n", last_service)

# create the service
python_service = onsched.create_service(name="Python Service",
                                        description="Python Test Service setup",
                                        duration=45,
                                        location_id=location['id'])
print("python_service:\n", python_service)

services = onsched.services(location_id=location['id'])
print("services:\n", services)

last_service = services['data'][-1]
print("last service after create:\n", last_service)

# delete the service
deleted_service = onsched.delete_service(service_id=python_service['id'])
print("delete service:\n", deleted_service)

last_service = services['data'][-1]
print("last service after delete:\n", last_service)

service_allocations = onsched.service_allocations(service_id=5)
print("service allocations: \n", service_allocations)

# Create a resource
resource = onsched.create_resource(name='Python Resource', location_id=location['id'])
print("resource:\n", resource)

# update the service
updated_resource = onsched.update_resource(resource_id=resource['id'], name='New Python Resource', email='python@onsched.com')
print("updated resource:\n", updated_resource)

# delete the resource
print("delete resource: \n", onsched.delete_resource(resource_id=resource['id']))

# create a service allocation
delta = timedelta(days=1)
start_date = date.today() + delta

allocation = onsched.create_service_allocation(service_id=2416,
                                               start_date=start_date,
                                               end_date=start_date,
                                               start_time=1200,
                                               end_time=1230,
                                               location_id='e4d61bd8-cdf3-4fc9-887e-2320dce062e0')
print("allocation:\n", allocation)

service_allocations = onsched.service_allocations(service_id=2416)
print("service allocations:\n", service_allocations)

service_allocation = onsched.service_allocation(service_allocation_id=2409)
print("service allocation:\n", service_allocation)
```
