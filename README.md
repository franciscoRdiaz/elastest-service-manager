[![][ElasTest Logo]][ElasTest]

Copyright © 2017-2019 [ElasTest]. Licensed under [Apache 2.0 License].

elastest-service-manager (esm)
==============================

ElasTest Service Manager. [![Build Status](https://travis-ci.org/elastest/elastest-service-manager.svg?branch=master)](https://travis-ci.org/elastest/elastest-service-manager)

# What is ElasTest

This repository is part of [ElasTest], which is an open source elastic platform
aimed to simplify end-to-end testing. ElasTest platform is based on three
principles: i) Test orchestration: Combining intelligently testing units for
creating a more complete test suite following the “divide and conquer” principle.
ii) Instrumentation and monitoring: Customizing the SuT (Subject under Test)
infrastructure so that it reproduces real-world operational behavior and allowing
to gather relevant information during testing. iii) Test recommendation: Using machine
learning and cognitive computing for recommending testing actions and providing
testers with friendly interactive facilities for decision taking.

# Documentation

The [ElasTest] project provides detailed documentation including tutorials,
installation and development guide.

## Generated Code
Some of the code in the ESM is generated using [swagger-codegen](https://github.com/swagger-api/swagger-codegen).
See ```./gen_api_skels.sh``` on how the command line is to generate the code.
The ESM uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

To run the ESM, please execute the following from the root directory:

```
pip3 install -r requirements.txt
python3 ./runesm.py
```

If you want to view the Swagger UI you can simply navigate to this URL in your browser:
```
http://localhost:8080/ui/
```

To retreive the swagger specification of the running ESM simply use `curl` or `wget` against this URL
```
http://localhost:8080/swagger.json
```

To launch the integration tests, use tox:
```
pip install tox
tox
```
## Overview
This service broker was in part generated by the [swagger-codegen](https://github.com/swagger-api/swagger-codegen) project. By using the [OpenAPI-Spec](https://github.com/swagger-api/swagger-core/wiki) from a remote server, you can easily generate a server stub. Using the swagger specification for this broker, you can also generate a client to interact with the broker, should `curl` not be your preference. The implementation uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask and requires Python 3.6. To use Python 3.5 you will need the `typing` module dependency, but this is included in the `requirements.txt` file. Python 2.x is not supported.

To launch the tests, use tox:
```shell
sudo pip install tox
tox
```

## Running It

Ensure you have all dependencies required: `pip3 install -r requirements.txt`

Configure the following OS environment variables:

* `SB_PORT`: this is the port under which the service broker runs. By default it runs on `8080`.

Example config and run:

```shell
export SB_PORT=9999
./runme.py
 * SB_PORT: 9999
 ./runme.py
 * Running on http://0.0.0.0:9999/ (Press CTRL+C to quit)
```

The service manager endpoint should only be the scheme (http or https) and the fully qualified host name, optionally including the port number if it differs from the standard port 80 or 443.

## Viewing the API

Navigate to the following URL in your browser

```
http://localhost:8080/v2/ui/
```

The OSBA Swagger definition can be accessed here:

```
http://localhost:8080/v2/swagger.json
```

## Using the API

To use the API please see the [open service broker API specification](https://www.openservicebrokerapi.org/) or use the UI version from within your browser.

### Get the Catalog

```shell
curl -v -X GET http://127.0.0.1:9999/v2/catalog -H 'X_Broker_Api_Version: 2.12'
Note: Unnecessary use of -X or --request, GET is already inferred.
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 9999 (#0)
> GET /v2/catalog HTTP/1.1
> Host: 127.0.0.1:9999
> User-Agent: curl/7.51.0
> Accept: */*
> X_Broker_Api_Version: 2.11
>
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: application/json
< Content-Length: 449
< Server: Werkzeug/0.11.15 Python/3.6.0
< Date: Thu, 09 Mar 2017 16:03:43 GMT
<
{
  "services": [
    {
      "bindable": false,
      "description": "Monitoring service",
      "id": "a_service_type",
      "name": "a service name",
      "plan_updateable": false,
      "plans": [
        {
          "description": "This is a best effort plan. No SLA, QoS, QoE or anything like that is guaranteed",
          "id": "best_effort",
          "name": "Best effort plan"
        }
      ],
      "tags": []
    }
  ]
}
```

### Provision (create) a service instance

```shell
curl -v -d @payload.json -X PUT -H "X-Broker-API-Version: 2.12" -H "Content-Type: application/json" http://localhost:9999/v2/service_instances/123-123-123\?accept_incomplete\=true
```

where `payload.json` is:

```json
{
  "organization_guid": "my-org-id-very-rich-company",
  "plan_id":           "plan-id-for-free",
  "service_id":        "a_service_type",
  "space_guid":        "space-guid-here",
  "parameters":        {
    "parameter1": 1,
    "parameter2": "value"
  }
}
```

`curl` will output

```shell
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 9999 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 9999 (#0)
> PUT /v2/service_instances/123-123-123?accept_incomplete=true HTTP/1.1
> Host: localhost:9999
> User-Agent: curl/7.51.0
> Accept: */*
> X-Broker-API-Version: 2.12
> Content-Type: application/json
> Content-Length: 272
>
* upload completely sent off: 272 out of 272 bytes
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: application/json
< Content-Length: 119
< Server: Werkzeug/0.11.15 Python/3.6.0
< Date: Thu, 09 Mar 2017 16:12:47 GMT
<
{
  "dashboard_url": "http://mon.sm.192.168.64.4.xip.io/mon/somon2c1e6fa57ac0154e",
  "operation": "provisioning..."
}
```

### Deprovision (delete) a service instance

```shell
curl -v -X DELETE -H "X-Broker-API-Version: 2.12" -H "Content-Type: application/json" http://localhost:9999/v2/service_instances/123-123-123\?service_id\="a_service_type"\&plan_id\="plan-id-for-free"
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 9999 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 9999 (#0)
> DELETE /v2/service_instances/123-123-123?service_id=a_service_type&plan_id=plan-id-for-free HTTP/1.1
> Host: localhost:9999
> User-Agent: curl/7.51.0
> Accept: */*
> X-Broker-API-Version: 2.12
> Content-Type: application/json
>
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: application/json
< Content-Length: 5
< Server: Werkzeug/0.11.15 Python/3.6.0
< Date: Fri, 10 Mar 2017 16:17:36 GMT
<
null
```



### Bind and Unbind

Currently not supported.

## Deploy on Docker

There is a docker build file `./Dockerfile` in the root of this project. You can use this to create a docker image that can then be ran upon your docker environment.

There is also a docker compose file `./docker-compose` in the root of this project. You can use this to bring up the ESM with a DB backend.

## Deploy on OpenShift

TO FOLLOW...

There are deployment manifests within `./deploy` that will deploy a service broker to OpenShift. There are two main modifications that you will have to do:

1. Change the route `./deploy/sv_route.yaml`. See line 11.
2. Change the configuration of the service broker. Configuration is done by modifying `./deploy/sb_dc.yaml` under the `env` stanza, lines 31-38. 
3. Deploy: `oc create -f ./deploy`.
4. Build: `oc start-build svcbroker`.
5. Destroy: `oc delete -f ./deploy`.

## Notes

To build the swagger-codegen [tool yourself](https://github.com/swagger-api/swagger-codegen/tree/master#building)

``` sh
# server files
java -jar $SWAGGER_CODE_GEN_REPO/modules/swagger-codegen-cli/target/swagger-codegen-cli.jar generate -i  ./apidef/swagger/open_service_broker_api.yaml -l python-flask -o ./ -DsupportPython2=true -DpackageName=svcbroker

# client files
java -jar $SWAGGER_CODE_GEN_REPO/modules/swagger-codegen-cli/target/swagger-codegen-cli.jar generate -i  ./apidef/swagger/open_service_broker_api.yaml -l python -o ./client -DpackageName=svcbroker-client
```

# Source
Source code for other ElasTest projects can be found in the [GitHub ElasTest
Group].

# Support
If you need help and support with the ESM, please refer to the ElasTest [Bugtracker]. 
Here you can find the help you need.

# News
Follow us on Twitter @[ElasTest Twitter].

# Contribution policy
You can contribute to the ElasTest community through bug-reports, bug-fixes,
new code or new documentation. For contributing to the ElasTest community,
you can use the issue support of GitHub providing full information about your
contribution and its value. In your contributions, you must comply with the
following guidelines

* You must specify the specific contents of your contribution either through a
  detailed bug description, through a pull-request or through a patch.
* You must specify the licensing restrictions of the code you contribute.
* For newly created code to be incorporated in the ElasTest code-base, you
  must accept ElasTest to own the code copyright, so that its open source
  nature is guaranteed.
* You must justify appropriately the need and value of your contribution. The
  ElasTest project has no obligations in relation to accepting contributions
  from third parties.
* The ElasTest project leaders have the right of asking for further
  explanations, tests or validations of any code contributed to the community
  before it being incorporated into the ElasTest code-base. You must be ready
  to addressing all these kind of concerns before having your code approved.

# Licensing and distribution
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


[Apache 2.0 License]: http://www.apache.org/licenses/LICENSE-2.0
[ElasTest]: http://elastest.io/
[ElasTest Logo]: http://elastest.io/images/logos_elastest/elastest-logo-gray-small.png
[ElasTest Twitter]: https://twitter.com/elastestio
[GitHub ElasTest Group]: https://github.com/elastest
[Bugtracker]: https://github.com/elastest/bugtracker