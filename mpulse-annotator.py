#!/usr/bin/env python

import sys, getopt
import requests
import sys
import json
import logging
import time
import csv
import datetime
import dateutil.parser
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin
from event import Event, FastPurgeCPCodeEvent, FastPurgeUrlEvent, PropertyManagerEvent, EccuEvent
from mpulseapihandler import MPulseAPIHandler
from logging.handlers import RotatingFileHandler


# Default filename for logger
DEFAULT_LOGGER_FILE = 'logs/mpulse-annotator.log'

# Default filename for the events selector configuration file
EVENTS_SELECTOR_FILE = 'events-selector.csv'

# Events Selector ID
EVENTS_SELECTOR_ECCU         = '000001'
EVENTS_SELECTOR_PMACTIVATION = '238252'
EVENTS_SELECTOR_FASTPURGE    = '229233'

# Delay in seconds between calls to create mPulse annotation (to avoid rate limit)
ANNOTATION_CREATE_DELAY 	 = 20


# Global variables
global l
global baseUrl


def initLogger():
	"""Initialize the logger.	
	:param filename: logger filename
	:type filename: a String object
	"""
	global l
	l = logging.getLogger("Rotating Log")
	l.setLevel(logging.DEBUG)
	handler = RotatingFileHandler(DEFAULT_LOGGER_FILE, maxBytes=10*1024*1024, backupCount=10)
	formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] %(message)s')  
	handler.setFormatter(formatter)
	l.addHandler(handler)


def decomment(csvfile):
    for row in csvfile:
        raw = row.split('#')[0].strip()
        if raw: yield raw


def parseEventsSelector(csvfile):
	"""Parse the events selector CSV file. 
	The CSV has two columns: the event definition ID, and the Event class name to be loaded 
	for this particular type of event. 
	The CSV file can contained comments (starting with '#') that will be ignored.
	:param csvfile: the CSV file path and file name
	:type csvfile: a String object
	:returns: a python Dictionary where key is the event type ID and value is the class name
	"""
	selector = {}
	with open(csvfile, mode='r') as infile:
		reader = csv.reader(decomment(infile))
		for row in reader:
			if row[1] == 'FastPurgeCPCodeEvent':
				selector[row[0]] = [ FastPurgeCPCodeEvent, row[2] ]
				l.debug("Selector '" + row[1] + "' added to event selectors list with criteria '" + row[2] + "'")
			if row[1] == 'FastPurgeUrlEvent':
				l.debug("Selector '" + row[1] + "' added to event selectors list with criteria '" + row[2] + "'")
				selector[row[0]] = [ FastPurgeUrlEvent, row[2] ]
			if row[1] == 'PropertyManagerEvent':
				l.debug("Selector '" + row[1] + "' added to event selectors list with criteria '" + row[2] + "'")
				selector[row[0]] = [ PropertyManagerEvent, row[2] ]
			if row[1] == 'EccuEvent':
				l.debug("Selector '" + row[1] + "' added to event selectors list with criteria '" + row[2] + "'")
				selector[row[0]] = [ EccuEvent, row[2] ]
	return selector


def parseEvents(json_object, eventsSelector):
	""" Parse a JSON object with a list of events obtained from EventViewer API.
	:param json_object: a JSON object that contains the array of events as returned by EventViewer API
	:type json_object: a native Python JSON object
	:param eventsSelector: a dictionary to select events during parsing
	:type eventsSelector: a python dictionary type
	:returns: an array of Event objects
	"""
	events = []
	for event in json_object:
		eventDefinitionId = event['eventType']['eventDefinition']['eventDefinitionId']
		if eventDefinitionId in eventsSelector:
			e = eventsSelector[eventDefinitionId][0]() # Instanciate object using dynamic class name
			try: 
				e.parseJson(event)
				if e.matchCriteria(eventsSelector[eventDefinitionId][1]):
					events.append(e)
			except:
				l.error('An error occured while parsing event: ' + event)
	return events

def parseEccuEvents(json_object, fromTimeStamp, eventsSelector):
	""" Parse a JSON object with a list of events obtained from ECCU Event API.
	:param json_object: a JSON object that contains the array of events as returned by ECCU API
	:type json_object: a native Python JSON object
	:param fromTimeStamp: timestamp to select events (only events started after this timestamp will be returned)
	:type fromTimeStamp: an int
	:param eventsSelector: a dictionary to select events during parsing
	:type eventsSelector: a python dictionary type
	:returns: an array of Event objects
	"""
	events = []
	for event in json_object:
		eventDefinitionId = EVENTS_SELECTOR_ECCU
		if eventDefinitionId in eventsSelector:
			e = eventsSelector[eventDefinitionId][0]() # Instanciate object using dynamic class name
			try: 
				e.parseJson(event)
				if e.getEventStartTime() >= fromTimeStamp:
					if e.matchCriteria(eventsSelector[eventDefinitionId][1]):
						events.append(e)
			except:
				l.error('An error occured while parsing event: ' + event)
	return events


def getECCUEvents(sess, start, eventsSelector):
	""" Query the ECCU API and return a list of Event objects
	
	:param sess: a session to send HTTP request to EventViewer API.
	:type sess: Session
	:param start: the timestamp from which events should be selected 
	:type start: a string with a unix timestamp (since January 1st, 1970 at UTC)
	:param eventsSelector:
	:type eventsSelector:
	:rtype: a Dictionnary of Event objects
	"""
	global l
	global baseUrl
	events = []

	# Build the initial URL path to make API call
	url_path = '/eccu-api/v1/requests'

	l.info("request Enhanced Content Control Utility API v1 on URL " + url_path)
	result = sess.get(urljoin(baseUrl, url_path))
	if (result.status_code == 200):
		data = result.json()
		l.info(str(len(data['requests'])) + " event(s) returned")
		selectedEvents = parseEccuEvents(data['requests'], start, eventsSelector)
		events = events + selectedEvents

	l.info("Total: " + str(len(events)) + " event(s) selected and parsed after start date '" + start + "'")
	return events



def getEventViewerEvents(sess, start, eventsSelector):
	""" Query EventCenter API and return a list of Event objects.
	:param sess: a session to send HTTP request to EventViewer API.
	:type sess: Session
	:param start: start date after which the events should be returned (e.g. 2018-12-13T15:00:00)
	:returns: the list of events founds
	:rtype: a Dictionnary of Event objects
	"""
	global l
	global baseUrl
	events = []
	
	# Build the initial URL path to make API call
	url_path = '/event-viewer-api/v1/events'
	if start:
		url_path = url_path + '?start=' + start
	
	l.info("request EventViewer v1 API on URL " + url_path)
	result = sess.get(urljoin(baseUrl, url_path))
	if (result.status_code == 200):
		data = result.json()
		l.info(str(len(data['events'])) + " event(s) returned")
		selectedEvents = parseEvents(data['events'], eventsSelector)
		events = events + selectedEvents
		l.info(str(len(selectedEvents)) + " event(s) selected and parsed")

		# Iterate on links part
		while data['links'] is not None:

			next_href = None

			# Get the 'next' href from the links part
			for link in data['links']:
				if link['rel'] == 'next':
					next_href = link['href']

			if next_href:
				url_path = next_href
				l.info("request EventViewer v1 API on URL " + url_path)
				result = sess.get(urljoin(baseUrl, url_path))
				if (result.status_code == 200):
					data = result.json()
					l.info(str(len(data['events'])) + " event(s) returned")
					selectedEvents = parseEvents(data['events'], eventsSelector)
					events = events + selectedEvents
					l.info(str(len(selectedEvents)) + " event(s) selected and parsed")
			else:
				break

	l.info("Total: " + str(len(events)) + " event(s) selected and parsed after start date '" + start + "'")
	return events



def main(argv):
	
	global l
	global baseUrl

	initLogger()
	l.info("mpulse-annotator is starting...")

	# Read and parse the command line arguments
	baseUrl = ''				# -u command line argument
	clientToken = ''			# -c command line argument
	clientSecret = ''			# -s command line argument
	accessToken = ''			# -o command line argument
	fromtime = ''				# -t command line argument
	apitoken = ''      			# -a command line argument
	mpulsetenant = ''			# -m command line argument
	eventsSelectorFile = None	# -f command line argument
	simulateAdd = False         # -x command line argument
	try:
	  opts, args = getopt.getopt(argv,"hu:c:s:o:t:a:m:f:x",["baseurl","clienttoken", "clientsecret","accesstoken","fromtime=","apitoken","mpulsetenant","eventsselector","simulate"])
	except getopt.GetoptError:
	  print('mpulse-annotator.py -u <baseurl> -c <clienttoken> -s <clientsecret> -o <accesstoken> -t <fromtime> -a <apitoken> -m <mpulsetenant> -f <events-selector-file>')
	  sys.exit(2)
	for opt, arg in opts:
	  if opt == '-h':
	     print('mpulse-annotator.py -u <baseurl> -c <clienttoken> -s <clientsecret> -o <accesstoken> -t <fromtime> -a <apitoken> -m <mpulsetenant> -f <events-selector-file>')
	     sys.exit()
	  elif opt in ("-u", "--baseurl"):
	     baseUrl = 'https://%s' % arg
	  elif opt in ("-c", "--clienttoken"):
	     clientToken = arg
	  elif opt in ("-s", "--clientsecret"):
	     clientSecret = arg
	  elif opt in ("-o", "--accesstoken"):
	     accessToken = arg
	  elif opt in ("-t", "--fromtime"):
	     fromtime = arg
	     l.info('events will be filtered starting from ' + fromtime)
	  elif opt in ("-a", "--apitoken"):
	     apitoken = arg
	     l.info("using mPulse API token: " + apitoken)
	  elif opt in ("-m", "--mpulsetenant"):
	     mpulsetenant = arg
	     l.info("using mPulse tenant: " + mpulsetenant)
	  elif opt in ("-f", "--eventsselector"):
	     eventsSelectorFile = arg
	     l.info("using events selector file: " + eventsSelectorFile)
	  elif opt in ("-x"):
	  	 simulateAdd = True


	# Get a mPulse API handler and retrieve a security token valid for this session
	if simulateAdd:
		l.info('[SIMULATE] Important: No annotation will be added to mPulse dashboard (simulation mode)')
	mpulse = MPulseAPIHandler(l, simulateAdd)
	mpulsetoken = mpulse.getSecurityToken(apitoken, mpulsetenant)

	# Create a dictionary to select events during parsing of API call responses
	if eventsSelectorFile is None:
		eventsSelectorFile = EVENTS_SELECTOR_FILE
	l.info('loading events selector from file ' + eventsSelectorFile)
	eventsSelector = parseEventsSelector(EVENTS_SELECTOR_FILE)

	sess = requests.Session()
	l.info("session created on " + baseUrl + ", using client token '" + clientToken + "' and start time '" + fromtime + "'")
	#sess.auth = EdgeGridAuth.from_edgerc(edgerc, edgercSection)
	sess.auth = EdgeGridAuth(client_token = clientToken, client_secret = clientSecret, access_token = accessToken)
	
	events = []
	events = getEventViewerEvents(sess, fromtime, eventsSelector)
	for e in events:
		l.info('The following annotation will be sent to mPulse API:')
		l.info('  Title: ' + e.getAnnotationTitle())
		l.info('   Text: ' + e.getAnnotationText())
		l.info('  Start: ' + e.getEventStartTime())
		mpulse.addAnnotation(mpulsetoken, e.getAnnotationTitle(), e.getAnnotationText(), e.getEventStartTime())
		l.info('Pause ' + str(ANNOTATION_CREATE_DELAY) + ' seconds...')
		time.sleep(ANNOTATION_CREATE_DELAY)

	date_time_obj = datetime.datetime.strptime(fromtime + '.000+0000', '%Y-%m-%dT%H:%M:%S.%f%z')
	fromtimeTS = str(int(date_time_obj.timestamp()))
	events = getECCUEvents(sess, fromtimeTS, eventsSelector)
	for e in events:
		l.info('The following annotation will be sent to mPulse API:')
		l.info("  Title: " + e.getAnnotationTitle())
		l.info("   Text: " + e.getAnnotationText())
		ts = e.getEventStartTime()
		l.info("  Start: " + ts + " (" + datetime.datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S') + " UTC)")
		if e.getEventEndTime() is not None:
			ts = e.getEventEndTime()
			l.info("    End: " + ts + " (" + datetime.datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S') + " UTC)")
			mpulse.addAnnotation(mpulsetoken, e.getAnnotationTitle(), e.getAnnotationText(), e.getEventStartTime(), e.getEventEndTime())
		else:
			mpulse.addAnnotation(mpulsetoken, e.getAnnotationTitle(), e.getAnnotationText(), e.getEventStartTime())
		l.info('Pause ' + str(ANNOTATION_CREATE_DELAY) + ' seconds...')
		time.sleep(ANNOTATION_CREATE_DELAY)

	l.info("mpulse-annotator is stopping...")


if __name__ == "__main__":
   main(sys.argv[1:])
