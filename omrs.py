#/usr/bin/env python

"""omrs.py: Simple REST client for testing OpenMRS API"""

#
# Setup:
# 
# pip install requests pyyaml python-dateutil
#

import argparse
import yaml
import requests
import json
from datetime import datetime
import dateutil.parser
import sys
import re

#=========================================================================
# Default configuration
#=========================================================================

DEFAULT_CONFIG_FILE = 'omrs.yml'
DEFAULT_USER = 'admin'
DEFAULT_PASSWORD = 'Admin123'
DEFAULT_CAUSE_OF_DEATH = '1067AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' # Unknown
DEFAULT_CONCEPT_SOURCE = 'CIEL'

#=========================================================================
# Command line parsing
#=========================================================================

parser = argparse.ArgumentParser(description='OpenMRS REST API Client',
	formatter_class=argparse.RawTextHelpFormatter)
subparsers = parser.add_subparsers()

parser.add_argument('--config', '-c', metavar='PATH', default=DEFAULT_CONFIG_FILE,
	help='Path to configuration file')
parser.add_argument('--api', '-a', metavar='URL',
	default='https://demo.openmrs.org/openmrs/ws/rest/v1',
	help='URL of OpenMRS API up through version number without ending slash')
parser.add_argument('--user', '-u', metavar='USERNAME', default=DEFAULT_USER,
	help='Username for authentication to API')
parser.add_argument('--pw', '-p', metavar='PASSWORD', default=DEFAULT_PASSWORD,
	help='Password for authentication to API')
parser.add_argument('--quiet', '-q', action='store_true')

parser_find = subparsers.add_parser('find', description='Find uuids for patient or concepts')
parser_find_group = parser_find.add_mutually_exclusive_group(required=True)
parser_find_group.add_argument('--patient', '-p', metavar='IDENTIFIER',
	help='Return patient\'s UUID)')
parser_find_group.add_argument('--concept', '-c', metavar='CONCEPT_NAME_OR_CODE',
	help='Find concept(s) by name or code')
parser_find.set_defaults(func='find')

parser_patient = subparsers.add_parser('patient', description='Create patient')
parser_patient.add_argument('--givenName', '-gn', required=True,
	help='Given name when creating a patient')
parser_patient.add_argument('--familyName', '-fn', required=True,
	help='Family name when creating a patient')
parser_patient.add_argument('--gender', '-g', required=True,
	help='Specify as "M" or "F" when creating a patient')
parser_patient.add_argument('--age', '-a', required=True,
	help='Specify patient\'s age')
parser_patient.set_defaults(func='patient')

parser_obs = subparsers.add_parser('obs',
	description='Create an observation.')
parser_obs.add_argument('--patient', '-p', required=True,
	help='Patient identifier or UUID')
parser_obs.add_argument('--code', '-c', required=True,
	help='Concept code')
parser_obs.add_argument('--source', '-s',
	help='(optional) Concept source (default:%s)' % DEFAULT_CONCEPT_SOURCE)
parser_obs.add_argument('--obsDatetime', '-dt',
	help='(optional) obsDatetime (use format YYYY-MM-DD[ HH:MM])')
parser_value_group = parser_obs.add_mutually_exclusive_group(required=True)
parser_value_group.add_argument('--value', '-v',
	help='Value of observation (concept code for coded value)')
parser_value_group.add_argument('--valueCoded', '-vc',
	help='Concept value with optional source in "SOURCE:CODE" format (default source:%s)' % DEFAULT_CONCEPT_SOURCE)
parser_obs.set_defaults(func='obs')

parser_died = subparsers.add_parser('died',
	description='Record the death of a patient.')
parser_died.add_argument('--patient', '-p', required=True,
	help='Patient who died (identifier or UUID)')
parser_died.add_argument('--deathDate', '-d',
	help='Date of patient\'s death (default is today)')
parser_died.add_argument('--causeOfDeath', '-c',
	help='Cause of death (uuid or concept code)')
parser_died.set_defaults(func='died')

parser_locations = subparsers.add_parser('locations', description='List locations')
parser_locations.set_defaults(func='locations')

parser_identifiertypes = subparsers.add_parser('identifiertypes',
	description='List patient identifier types')
parser_identifiertypes.set_defaults(func='identifiertypes')

parser_help = subparsers.add_parser('help',
	description='Display this help text')
parser_help.set_defaults(func='help')

args = parser.parse_args()

config = yaml.safe_load(open('omrs.yml'))
base_url = config['base_url']
api = '%s/ws/rest/v1' % base_url
user = config['user']
pw = config['pw']
identifierTypeUuid = config['identifier_type_uuid']
locationUuid = config['location_uuid']

#=========================================================================
# Convenience methods
#=========================================================================

def attr_from_response(attr, resp):
	if attr in resp:
		return resp[attr]
	else:
		print('Invalid response:')
		print(resp)
		sys.exit(1)

def openmrs_get(url):
	'''Request a list of results from API and return them'''
	resp = requests.get(url, auth=(user, pw))
	try:
		resp_json = resp.json()
	except:
		print('Invalid response:')
		print(resp)
		sys.exit(1)
	results = attr_from_response('results', resp_json)
	return results

def openmrs_post(url, data_json):
	'''Create a new resource and return its uuid'''
	headers = {
		'Content-type': 'application/json'
		}
	resp = requests.post(url, data_json, headers=headers, auth=(user, pw))
	try:
		resp_json = resp.json()
	except:
		print('Invalid response:')
		print(resp)
		sys.exit(1)
	uuid = attr_from_response('uuid', resp_json)
	return uuid

valueCodeRe = re.compile(r'^((.*?):)?(.*)$')

def parse_source_and_code(s):
	'''Parse concept source and code from format "SOURCE:CODE"'''
	m = valueCodeRe.match(s)
	if not m:
		return [DEFAULT_CONCEPT_SOURCE, s]
	(source, code) = (m.group(2) or DEFAULT_CONCEPT_SOURCE, m.group(3))
	return [source, code]

def list_results(arr):
	i = 0
	for elem in arr:
		i += 1
		print('%i: %s (%s)' % (i, elem['display'], elem['uuid']))

#=========================================================================
# OpenMRS REST calls
#=========================================================================

def get_identifier_types():
	url = '%s/patientidentifiertype' % (api)
	return openmrs_get(url)

def get_locations():
	url = '%s/location' % (api)
	return openmrs_get(url)

def find_concepts(q):
	url = '%s/concept?q=%s' % (api, q)
	return openmrs_get(url)

def create_person(givenName, familyName, gender, age=None):
	url = '%s/person' % (api)
	data = {
		'gender': gender,
		'names': [{
			'givenName': givenName,
			'familyName': familyName
			}]
		}
	if age:
		data['age'] = age
	data_json = json.dumps(data)
	return openmrs_post(url, data_json)

def create_patient(person, identifier, location=locationUuid):
	url = '%s/patient' % (api)
	data = {
		'person': person,
		'identifiers': [{
			'identifier': identifier,
			'identifierType': identifierTypeUuid,
			'location': location,
			'preferred': True
			}]
		}
	data_json = json.dumps(data)
	return openmrs_post(url, data_json)

uuidRe = re.compile(r'[0-9a-f\\-]{32,36}', re.I)

def get_patient_uuid(identifierOrUuid):
	if uuidRe.match(identifierOrUuid):
		# If parameter looks like a UUID, just return it
		return identifierOrUuid
	url = '%s/patient?identifier=%s' % (api, identifierOrUuid)
	results = openmrs_get(url)
	if len(results) < 1:
		print('Patient not found: %s', identifierOrUuid)
		sys.exit(1)
	return attr_from_response('uuid', results[0])

def get_patient_identifier():
	# IDGen doesn't have a REST API yet <https://issues.openmrs.org/browse/IDGEN-42>
	# We have to make an HTTP GET request and we hack in internal ID 1 (for "OpenMRS Identifier" type)
	url = '%s/module/idgen/generateIdentifier.form?source=1&username=%s&password=%s' % (base_url, user, pw)
	resp = requests.get(url).json()
	return resp['identifiers'][0]

def get_concept_uuid(code, source=DEFAULT_CONCEPT_SOURCE):
	if uuidRe.match(code):
		# If code looks like a UUID, just return it
		return code
	url = '%s/concept?source=%s&code=%s' % (api, source, code)
	results = openmrs_get(url)
	if len(results) < 1:
		print('Concept not found: %s:%s', (source, code))
		sys.exit(1)
	return attr_from_response('uuid', results[0])

def create_obs(patient, concept, value, valueSource=None, obsDatetime=None):
	url = '%s/obs' % (api)
	if obsDatetime is None:
		obsDatetime = datetime.now()
	else:
		obsDatetime = dateutil.parser.parse(obsDatetime)
	obsDatetime = obsDatetime.strftime('%Y-%m-%dT%H:%M:%S')
	if valueSource:
		value = '%s:%s' % (valueSource, value)
	data = {
		'person': patient,
		'obsDatetime': obsDatetime,
		'concept': concept,
		'value': value
		}
	data_json = json.dumps(data)
	return openmrs_post(url, data_json)

def person_died(person, causeOfDeath=DEFAULT_CAUSE_OF_DEATH, deathDate=None):
	url = '%s/person/%s' % (api, person)
	if deathDate is None:
		deathDate = datetime.now()
	else:
		deathDate = dateutil.parser.parse(deathDate)
	deathDate = deathDate.strftime('%Y-%m-%d')
	data = {
		'dead': True,
		'deathDate': deathDate,
		'causeOfDeath': causeOfDeath
		}
	data_json = json.dumps(data)
	print('POST %s/person/%s' % (api, person))
	print(data_json)
	return openmrs_post(url, data_json)

#=========================================================================
# Main method
#=========================================================================

def main():
	silence = args.quiet or False
	if args.func == 'find':
		if args.patient:
			print(get_patient_uuid(args.patient))
		elif args.concept:
			list_results(find_concepts(args.concept))
	elif args.func == 'locations':
		list_results(get_locations())
	elif args.func == 'identifiertypes':
		list_results(get_identifier_types())
	elif args.func == 'patient':
		person=create_person(givenName=args.givenName, familyName=args.familyName,
			gender=args.gender.upper(), age=args.age)
		identifier=get_patient_identifier()
		patient = create_patient(person, identifier)
		if not silence: print(patient)
	elif args.func == 'obs':
		options = dict(patient=get_patient_uuid(args.patient),
			concept=get_concept_uuid(code=args.code))
		# Weight (kg) = 5089
		# Problem list = 1284, asthma = 121375
		# TODO: support coded answers including valueSource
		# TODO: birthdate for patient
		if args.obsDatetime:
			options['obsDatetime'] = args.obsDatetime	
		if args.valueCoded:
			source, code = parse_source_and_code(args.valueCoded)
			options['valueSource'] = source
			options['value'] = code
		else:
			options['value'] = args.value
		obs = create_obs(**options)
		if not silence: print(obs)
	elif args.func == 'died':
		options = dict(person=get_patient_uuid(args.patient))
		if args.deathDate:
			options['deathDate'] = args.deathDate
		if args.causeOfDeath:
			options['causeOfDeath'] = get_concept_uuid(args.causeOfDeath)
		person_died(**options)
	elif args.func == 'help':
		parser.print_help()
	else:
		print('Unrecognized command')
		system.exit(1)

if __name__ == '__main__':
	main()