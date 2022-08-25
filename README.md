# Service-Now Framework

This is a framework that connects to the API of an Service-Now system.

## Authentication

Credentials are stored in JSON format, in the same directory as the `snow.py` file. The name of the file should be `credentials.json`.

Other authentication methods, such as KDBX, have been tested, but this way it keeps the hard-coded passwords out of the source code.

```
{
	"credentials": {
		"username": "",
		"password": ""
	}
}
```

API calls will automatically send HTTP Basic Authentication with each HTTP method.

## Getting Started

To instantiate a `ServiceNow` object, pass a string of the Service-now sub-domain to connect.

Connection will be established to 'https://' + domain + '.service-now.com'

```
>>> domain = 'your-company'
>>> s = ServiceNow(domain)
```

## Service-Now API Features

As of the most current update, only features for pulling ticket information have been explored.

Some features explored are :
- Get a CMDB Table information
- Get a CMDB Table via Service-Now query-string
- Get Assignment Group by Name
- Get User by Email
- Get Unassigned Tickets by Group Name
- Get Tickets Assigned to Email under a Group Name
- Get Ticket information
- Get Table of a Ticket
- Set a Ticket value
- Set a Ticket "State" value
- Set a Ticket "Assigned To" value

To invoke the Flask API, run the `main.py` function :

```
> python3 main.py
```

A web server will be created and listening on localhost via port tcp/5000. Optional hard-coded parameters will need to be modified to pull data according to the user running the Flask application.

The web server will iterate through a list of `companies` in Service-Now where unassigned tickets are found (MSP's multiple customers, others one) and tickets will be automatically assigned to the configured user.

Ticket types are able to be adjusted to reflect which are necessary to display, this is a simple template showing what is possible.

### An Exercise Left to the Reader

Criteria of the ticket description can potentially be parsed and Python can execute troubleshooting functions, add comments, and ultimately close tickets.