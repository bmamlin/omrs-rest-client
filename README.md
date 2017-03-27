OpenMRS REST Client
===================

This is a simple command line client for testing the [OpenMRS](https://openmrs.org/)
REST API.

## Setup

### Running natively

To run [`omrs.py`](omrs.py) natively, ou must have a few python libraries installed:

`pip install requests pyyaml python-dateutil`

### Run using Docker

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

`./omrs.py obs -p 123-0 -c 1284AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA -vc 142412AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` -dt t-3w

* Create an observation for patient 123-0 of PROBLEM LIST = Diarrhea with timestamp of 3 weeks ago _(note that `-vc` is used to indicate a "value coded" for an observation answered with a coded concept)_

`./omrs.py died -p 123-0 -d 2017-03-01`

* Mark patient 123-0 as having died on 1 March, 2017

`./omrs.py identifiertypes`

* List known identifier types and their UUID

`./omrs.py locations`

* List know locations and their UUID

> Dates can be in the format 'YYYY-MM-DD' or given as a relative dates:
> * "t" for today
> * "t-3d" for 3 days ago
> * "t-7w" for 7 weeks ago
> * "t-2m" for 2 months ago

## Options

The following options may be optionally specified on the command line.

* **--config** (or -c): location of configuration file (default is `omrs.yml`)
* **--base_url** (or -b): URL of OpenMRS instance running REST web services module without ending slash (e.g., `https://demo.openmrs.org/openmrs`)
* **--user** and **--pw** (or -u and -p): credentials to use for REST API calls (default to demo admin)
* **--quiet** (or -q): suppresses some output
* **--version** (or -v): display script version
