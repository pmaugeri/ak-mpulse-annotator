#!/usr/bin/env python

import sys, getopt
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urlparse import urljoin
from event import Event, FastPurgeEvent, PropertyManagerEvent
from mpulseapihandler import MPulseAPIHandler
import sys
import json
import logging
import time
from logging.handlers import RotatingFileHandler
import csv


# Default filename for logger
DEFAULT_LOGGER_FILE = 'mpulse-annotator.log'

# Default filename for the events selector configuration file
EVENTS_SELECTOR_FILE = 'events-selector.csv'


# Global variables
global l
global baseurl


def initLogger():
	"""Initialize the logger.	
	:param filename: logger filename
	:type filename: a String object
	"""
	global l
	l = logging.getLogger("Rotating Log")
	l.setLevel(logging.INFO)
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
			if row[1] == 'FastPurgeEvent':
				selector[row[0]] = [ FastPurgeEvent, row[2] ]
			if row[1] == 'PropertyManagerEvent':
				selector[row[0]] = [ PropertyManagerEvent, row[2] ]
	return selector

def parseEvents(json_object, eventsSelector):
	""" Parse a JSON object with a list of events.
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
			e.parseJson(event)
			if e.matchCriteria(eventsSelector[eventDefinitionId][1]):
				events.append(e)
	return events


def getEvents(sess, start, eventsSelector):
	""" Query EventCenter API and return a list of Event objects.
	:param sess: a session to send HTTP request to PAPI.
	:type sess: Session
	:param start: start date after which the events should be returned (e.g. 2018-12-13T15:00:00)
	:returns: the list of events founds
	:rtype: a Dictionnary of Event objects
	"""
	global l
	global baseurl
	events = []
	
	# Build the initial URL path to make API call
	url_path = '/event-viewer-api/v1/events'
	if start:
		url_path = url_path + '?start=' + start
	
	l.info("request EventViewer v1 API on URL " + url_path)
	result = sess.get(urljoin(baseurl, url_path))
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
				result = sess.get(urljoin(baseurl, url_path))
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
	global baseurl

	initLogger()
	l.info("mpulse-annotator is starting...")




	# Read and parse the command line arguments
	edgercSection = ''
	fromtime = ''
	apitoken = ''
	mpulsetenant = ''
	try:
	  opts, args = getopt.getopt(argv,"hs:t:a:m:",["section=","fromtime=","apitoken","mpulsetenant"])
	except getopt.GetoptError:
	  print 'mpulse-annotator.py -s <section> -t <fromtime> -a <apitoken> -m <mpulsetenant>'
	  sys.exit(2)
	for opt, arg in opts:
	  if opt == '-h':
	     print 'mpulse-annotator.py -s <section> -t <fromtime> -a <apitoken> -m <mpulsetenant>'
	     sys.exit()
	  elif opt in ("-s", "--section"):
	     edgercSection = arg
	  elif opt in ("-t", "--fromtime"):
	     fromtime = arg
	  elif opt in ("-a", "--apitoken"):
	     apitoken = arg
	     l.info("using mPulse API token: " + apitoken)
	  elif opt in ("-m", "--mpulsetenant"):
	     mpulsetenant = arg
	     l.info("using mPulse tenant: " + mpulsetenant)

	# Get a mPulse API handler and retrieve a security token valid for this session
	mpulse = MPulseAPIHandler(l)
	mpulsetoken = mpulse.getSecurityToken(apitoken, mpulsetenant)

	# Create a dictionary to select events during parsing of API call responses
	l.info('loading events selector...')
	eventsSelector = parseEventsSelector(EVENTS_SELECTOR_FILE)

	edgerc = EdgeRc('.edgerc')
	baseurl = 'https://%s' % edgerc.get(edgercSection, 'host')
	sess = requests.Session()
	l.info("session created on " + baseurl + ", using .edgerc section '" + edgercSection + "' and start time '" + fromtime + "'")
	sess.auth = EdgeGridAuth.from_edgerc(edgerc, edgercSection)
	events = getEvents(sess, fromtime, eventsSelector)

	for e in events:
		print e
		print "-- Annotation --"
		print "Title: " + e.getAnnotationTitle()
		print "Text: " + e.getAnnotationText()
		print "Start: " + e.getEventTime()
		mpulse.addAnnotation(mpulsetoken, e.getAnnotationTitle(), e.getAnnotationText(), e.getEventTime())
		print "----------------"



if __name__ == "__main__":
   main(sys.argv[1:])







