import json
import sys

import requests


if len(sys.argv) < 3:
    print(
        "Usage: {0} <LBaaS URL> <Router IP list>\nExample: {0} "
        "http://192.168.10.5:8993/v1 '192.168.10.8,192.168.10.10'".format(
            __file__
        )
    )
    exit(1)

url = sys.argv[1]
pcf_router_ips = sys.argv[2].split(',')

# Configure LBaaS.
requests.post(
    "%s/listeners" % url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(
        {
            "name": "http-in",
            "protocol": "http",
            "protocol_port": 80,
            "options": {
                "option": "forwardfor",
                "reqadd": "X-Forwarded-Proto:\\ http"
            }
        }
    )
)

requests.post(
    "%s/listeners" % url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(
        {
            "name": "https-in",
            "protocol": "http",
            "protocol_port": 443,
            "options": {
                "option": "forwardfor",
                "reqadd": "X-Forwarded-Proto:\\ https"
            }
        }
    )
)
requests.post(
    "%s/listeners" % url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(
        {
            "name": "ssl-in",
            "protocol": "tcp",
            "protocol_port": 4443
        }
    )
)

requests.put(
    '%s/listeners/https-in' % url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(
        {
            'ssl_info': [
                "ssl", "crt", "/etc/ssl/cf.pem", "no-sslv3", "ciphers",
                "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:"
                "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDH"
                "E-RSA-AES128-CBC-SHA256:ECDHE-RSA-AES256-CBC-SHA384:ECDHE-RS"
                "A-AES128-CBC-SHA:ECDHE-RSA-AES256-CBC-SHA:AES128-SHA256:AES1"
                "28-SHA:RC4-SHA"
            ]
        }
    )
)


def configure_member(name, address):
    requests.post(
        "%s/members" % url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "name": "%s-ssl" % name,
                "protocol_port": 80,
                "listener_name": "ssl-in",
                "address": address
            }
        )
    )

    requests.post(
        "%s/members" % url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "name": "%s-http" % name,
                "protocol_port": 80,
                "listener_name": "http-in",
                "address": address
            }
        )
    )

    requests.post(
        "%s/members" % url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "name": "%s-https" % name,
                "protocol_port": 80,
                "listener_name": "https-in",
                "address": address
            }
        )
    )


for index, address in enumerate(pcf_router_ips):
    configure_member("%s%s" % ("router", index), address)
