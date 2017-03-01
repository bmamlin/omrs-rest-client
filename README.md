OpenMRS REST Client
===================

This is a simple command line client for testing the [OpenMRS](https://openmrs.org/)
REST API.

## Setup

You must have a few python libraries installed to run this script

`pip install requests pyyaml python-dateutil`

Alternatively, if you have [Docker](https://www.docker.com/) installed (why wouldn't 
you?), then you don't need to install or configure python and can run the script using
Docker:

`docker-compose run --rm omrs omrs.py help`

## Usage

`./omrs.py help`

* Displays usage

`./omrs.py patient -gn Norman -fn Schnoggenlocher -g m -a 42`

* Create a 42 year-old male patient named Norman Schnoggenlocher

`./omrs.py find -c weight`

* Search concepts for "weight" and show UUID of each

`./omrs.py obs -p 123-0 -c 5089AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA -v 70 -dt 2017-03-01 23:11`

* Create an observation for patient 123-0 for Weight (kg) = 70 on 1 March, 2017 at 23:11

`./omrs.py obs -p 123-0 -c 1284AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA -vc 142412AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`

* Create an observation for patient 123-0 for PROBLEM LIST = Diarrhea _(note that `-vc` is used to indicate a "value coded" for an observation answered with a coded concept)_

`./omrs.py died -p 123-0 -d 2017-03-01`

* Mark patient 123-0 as having died on 1 March, 2017

`./omrs.py identifiertypes`

* List known identifier types and their UUID

`./omrs.py locations`

* List know locations and their UUID

## Options

The following options may be optionally specified on the command line.

* **--config**: location of configuration file (default is `omrs.yml`)
* **--api**: URL of OpenMRS instance running REST web services module (defaults to demo)
* **--user** and **--pw**: credentials to use for REST API calls (default to demo admin)
* **--quiet**: suppresses some output