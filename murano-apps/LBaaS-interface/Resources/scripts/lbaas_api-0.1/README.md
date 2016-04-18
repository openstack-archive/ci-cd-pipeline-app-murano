LBaaS API specification
=======================

Listeners API
-------------

**/v1/listeners** - objects representing a group of machines balancing on LB on specific protocol and port. Each listener contains mapping configuration to members and their listening ports. 
Example: listener ‘A’ listen to HTTP port 80 and maps to 3 machines with their own IPs listening on HTTP port 8080.

	                        ---> Member, Machine1_IP (HTTP, 8080)
    Listener ‘A’ (HTTP, 80) ---> Member, Machine2_IP (HTTP, 8080)
      	                    ---> Member, Machine3_IP (HTTP, 8080)

**POST /v1/listeners**

Creates a new listener object. Returns 201 if succeed.
Parameters:

* **name** - The name of listener. Type string. Required. Should be unique across listener objects.
* **protocol** - The protocol of listener. Type string. Should be one of {“http”, “tcp”}. It is not validated by API! Required.
* **protocol_port** - Protocol TCP port which listener will be listening to. Type integer. Required.
* **algorithm** - Load-balancing algorithm. Type string. If passed, should be compatible with one of possible haproxy algorithm. Optional, default value if not passed - “roundrobin”.

Request body example:

	{
	  “protocol”: “http”,
	  “protocol_port”: 80,
	  “name”: “app”,
	  “algorithm”: “roundrobin”
	}


**GET /v1/listeners**

Gets all listeners from LBaaS. Also contains all containing members information. Returns 200 if succeed.

**GET /v1/listeners/<name>**

Gets particular listener from LBaaS. name - the listener’s name.

**PUT /v1/listeners/<name>**

Update listener info by its name. Returns 200 code if succeed.
Request body example:

    {
	  “protocol_port”: 8080,
	  “name”: “app”
	}


**DELETE /v1/listeners/<name>**

Deletes the whole listener by its name. Returns 204 if succeed.


Members API
-----------

**/v1/members** - objects representing a machine which is able to receive requests on specific port of specific protocol. Each member belongs to specific listener.

**POST /v1/members**

Creates a new member object. Returns 201 if succeed.
Parameters:
* **name** - The name of member. Type string. Required. Should be unique across member objects.
* **protocol_port** - Protocol TCP port which member is listening to. Type integer. Required.
* **address** - Hostname or IP address of member machine. Type string. Required.
* **listener_name** - The name of listener which adds the current member to. Member will belong to this listener. Each listener may have a number of members. Type string. Required.

Request body example:

	{
	  “address”: “10.0.20.5”,
	  “protocol_port”: 80,
	  “name”: “my_server”,
	  “listener_name”: “app”
	}



**GET /v1/members**

Gets all members from LBaaS. Returns 200 if succeed.

**GET /v1/members/<name>**

Gets particular member from LBaaS. name - the member’s name.


**PUT /v1/members/<name>**

Update listener info by its name. Returns 200 code if succeed.

Request body example:

    {
	  “protocol_port”: 8080,
	}


**DELETE /v1/members/<name>**

Deletes the whole member by its name. Returns 204 if succeed.
