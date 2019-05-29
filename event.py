import datetime
import dateutil.parser
from datetime import tzinfo, timedelta

from timezones import LocalTimezone
from timezones import UTCTimezone

LocalTZ = LocalTimezone()
UTCTZ = UTCTimezone()


class Event:
	"""
	Generic parent event class with mandatory methods to create, 
	parse and match events, and. to create mPulse annotation.
	"""

	TAG_EVENT = "Akamai"

	def __init__(self, eventId = None):
		self.eventId = eventId
		self.tags = []

	def matchCriteria(self, criteria):
		return True

	def parseJson(self, json):
		return

	def getEventId(self):
		return self.eventId

	def __str__(self):
		return 	""

	def getAnnotationTitle(self):
		"""Return the annotation title corresponding to this event and ready to be used in mPulse Annotation API. 
		By default it returns the eventName attribute.
		:returns: a python String object
		"""		
		return ""

	def getAnnotationText(self):
		"""Return the annotation text corresponding to this event and ready to be used in mPulse Annotation API.
		:returns: a python String object
		"""		
		return ""

	def getEventStartTime(self):
		"""Return the event time in Epoch time (in milliseconds)
		:param json: the Event to be parsed
		:returns: event epoch time (in milliseconds)
		"""
		return None

	def getEventEndTime(self):
		"""Return the event time in Epoch time (in milliseconds)
		:param json: the Event to be parsed
		:returns: event epoch time (in milliseconds)
		"""
		return None

	def addTag(self, tag):
		"""Add a new tag to this event.
		:param tag: the new tag to be added
		:type tag: a string containing the new tag
		"""
		self.tags.append(tag)

	def getTags(self):
		"""Return a List of tags
		:returns: a List object with the event tags
		"""
		return self.tags

	def getTagsText(self):
		"""Returns a string representation of the tags (e.g. #Akamai #FastPurge)
		:returns: a String object
		"""
		text = ""
		for tag in self.tags:
			text = text + "#" + tag + " "
		if text != "":
			text = text[:-1]
		return text

	def clearTags(self):
		"""Remove all the tags set (and preset by the constructor) for this Event.
		"""
		self.tags = []

class EventViewerEvent(Event):
	"""
	This event class inheritis from Event parent class.
	All Akamai events that comes from EventViewer API should be instanciated 
	below EventViewerEvent.
	"""

	def parseJson(self, json):
		"""Parse a JSON object describing an Event.
		:param json: the Event to be parsed
		:type json: a python JSON object
		"""
		self.eventId = json['eventId']
		epoch_time = json['eventTime']
		#dt = datetime.datetime.strptime(epoch_time, "%Y-%m-%dT%H:%M:%S.%fZ")		
		dt = datetime.datetime.strptime(epoch_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTCTZ).astimezone(LocalTZ)
		self.eventTime = str(int(dt.strftime("%s")) * 1000)
		self.eventTypeId = json['eventType']['eventTypeId']
		self.eventTypeName = json['eventType']['eventTypeName']
		self.eventDefinitionId = json['eventType']['eventDefinition']['eventDefinitionId']
		self.eventName = json['eventType']['eventDefinition']['eventName']
		self.username = json['username']
		self.impersonator = json['impersonator']
		self.eventData = json['eventData']

	def getEventStartTime(self):
		"""Return the event time in Epoch time (in milliseconds)
		:param json: the Event to be parsed
		:returns: event epoch time (in milliseconds)
		"""
		return self.eventTime

	def getEventTypeId(self):
		return self.eventTypeId

	def getEventTypeName(self):
		return self.eventTypeName

	def getEventDefinitionId(self):
		return self.eventDefinitionId

	def getEventName(self):
		return self.eventName

	def getUsername(self):
		return self.username

	def getImpersonator(self):
		return self.impersonator

	def getEventData(self):
		return self.eventData

	def __str__(self):
		return 	"          eventId: " + self.eventId + \
				"\n        eventTime: " + self.eventTime + \
				"\n      eventTypeId: " + self.eventTypeId + \
				"\n    eventTypeName: " + self.eventTypeName + \
				"\n         username: " + self.username + \
				"\n     impersonator: " + str(self.impersonator) + \
				"\neventDefinitionId: " + str(self.eventDefinitionId) + \
				"\n        eventName: " + str(self.eventName)

	def getAnnotationTitle(self):
		"""Return the annotation title corresponding to this event and ready to be used in mPulse Annotation API. 
		By default it returns the eventName attribute.
		:returns: a python String object
		"""		
		return self.eventName

	def getAnnotationText(self):
		"""Return the annotation text corresponding to this event and ready to be used in mPulse Annotation API.
		:returns: a python String object
		"""		
		return ""

class FastPurgeCPCodeEvent(EventViewerEvent):
	""" 
	A class used to represent a purge event by CP Code. 
	Event definition ID: 229233
	"""

	TAG_FAST_PURGE_EVENT = "FastPurgeCPC"

	def __init__(self, eventId = None):
		EventViewerEvent.__init__(self)
		self.addTag(Event.TAG_EVENT)
		self.addTag(self.TAG_FAST_PURGE_EVENT)

	def matchCriteria(self, criteria):
		Event.matchCriteria(self, criteria)
		for cpcode in criteria.split(';'):
			if cpcode in self.purgeRequest:
				return True
		return False

	def getPurgeAction(self):
		return self.purgeAction

	def getPurgeNetwork(self):
		return self.purgeNetwork

	def getPurgeRequest(self):
		return self.purgeRequest

	def getPurgeResponse(self):
		return self.purgeResponse

	def parseJson(self, json):
		EventViewerEvent.parseJson(self, json)
		eventData = json['eventData']
		for kv in eventData:
			k = kv['key']
			v = kv['value']
			if k == 'Purge action':
				self.purgeAction = v
			if k == 'Purge network':
				self.purgeNetwork = v
			if k == 'Purge request':
				self.purgeRequest = v
			if k == 'Purge response':
				self.purgeResponse = v

	def __str__(self):
		return EventViewerEvent.__str__(self) + \
				"\n      purgeAction: " + str(self.purgeAction) + \
				"\n     purgeNetwork: " + str(self.purgeNetwork) + \
				"\n     purgeRequest: " + str(self.purgeRequest) + \
				"\n    purgeResponse: " + str(self.purgeResponse)

	def getAnnotationText(self):
		"""Return the annotation text corresponding to this event and ready to be used in mPulse Annotation API.
		:returns: a python String object
		"""		
		return "Purge request on " + self.purgeNetwork + " network: " + self.purgeRequest + " " + self.getTagsText()

class FastPurgeUrlEvent(EventViewerEvent):
	""" 
	A class used to represent a purge event by URL. 
	Event definition ID: 894488
	"""

	TAG_FAST_PURGE_EVENT = "FastPurgeURL"

	def __init__(self, eventId = None):
		EventViewerEvent.__init__(self)
		self.addTag(Event.TAG_EVENT)
		self.addTag(self.TAG_FAST_PURGE_EVENT)

	def matchCriteria(self, criteria):
		Event.matchCriteria(self, criteria)
		for url in criteria.split(';'):
			if url in self.purgeRequest:
				return True
		return False

	def getPurgeAction(self):
		return self.purgeAction

	def getPurgeNetwork(self):
		return self.purgeNetwork

	def getPurgeRequest(self):
		return self.purgeRequest

	def getPurgeResponse(self):
		return self.purgeResponse

	def parseJson(self, json):
		EventViewerEvent.parseJson(self, json)
		eventData = json['eventData']
		for kv in eventData:
			k = kv['key']
			v = kv['value']
			if k == 'Purge action':
				self.purgeAction = v
			if k == 'Purge network':
				self.purgeNetwork = v
			if k == 'Purge request':
				self.purgeRequest = v
			if k == 'Purge response':
				self.purgeResponse = v

	def __str__(self):
		return EventViewerEvent.__str__(self) + \
				"\n      purgeAction: " + str(self.purgeAction) + \
				"\n     purgeNetwork: " + str(self.purgeNetwork) + \
				"\n     purgeRequest: " + str(self.purgeRequest) + \
				"\n    purgeResponse: " + str(self.purgeResponse)

	def getAnnotationText(self):
		"""Return the annotation text corresponding to this event and ready to be used in mPulse Annotation API.
		:returns: a python String object
		"""		
		return "Purge request on network: " + self.purgeNetwork + " request: " + self.purgeRequest + " " + self.getTagsText()

class PropertyManagerEvent(EventViewerEvent):


	TAG_PROPERTY_MANAGER_EVENT = "PropertyManager"


	def __init__(self, eventId = None):
		EventViewerEvent.__init__(self)
		self.addTag(Event.TAG_EVENT)
		self.addTag(self.TAG_PROPERTY_MANAGER_EVENT)

	def matchCriteria(self, criteria):
		EventViewerEvent.matchCriteria(self, criteria)
		if criteria == '':
			return True
		for prop in criteria.split(';'):
			if prop == self.propertyName:
				return True
		return False

	def parseJson(self, json):
		EventViewerEvent.parseJson(self, json)
		eventData = json['eventData']
		for kv in eventData:
			k = kv['key']
			v = kv['value']
			if k == 'PROPERTY_NAME':
				self.propertyName = v
			if k == 'PROPERTY_VERSION':
				self.propertyVersion = v
			if k == 'USERNAME':
				self.username = v

	def __str__(self):
		return EventViewerEvent.__str__(self) + \
				"\n     propertyName: " +  str(self.propertyName) + \
				"\n  propertyVersion: " +  str(self.propertyVersion) + \
				"\n         username: " +  str(self.username)

	def getAnnotationText(self):
		"""Return the annotation text corresponding to this event and ready to be used in mPulse Annotation API.
		:returns: a python String object
		"""		
		return "" + self.propertyName + " v" + self.propertyVersion + " activated by " + self.username + " " + self.getTagsText()

class EccuEvent(Event):

	TAG_ECCU_EVENT = "ECCU"

	def __init__(self, eventId = None):
		Event.__init__(self)
		self.addTag(Event.TAG_EVENT)
		self.addTag(self.TAG_ECCU_EVENT)

	def parseJson(self, json):	
		"""Parse a JSON object containing an ECCU event description.

		:param json: the Event to be parsed
		:type json: a python JSON object
	    """
		self.eventId = str(json['requestId'])
		try:
			self.requestName = json['requestName']
		except KeyError:
			self.requestName = None
		self.propertyName = json['propertyName']
		self.propertyType = json['propertyType']
		self.propertyNameExactMatch = str(json['propertyNameExactMatch'])
		self.notes = json['notes']
		self.status = json['status']
		self.statusMessage = json['statusMessage']
		self.extendedStatusMessage = json['extendedStatusMessage']
		
		# parse statusUpdateDate
		epoch_time = json['statusUpdateDate']
		date_time_obj = datetime.datetime.strptime(epoch_time, '%Y-%m-%dT%H:%M:%S.%f%z')
		self.eventEndTime = str(int(date_time_obj.timestamp()))

		self.statusUpdateEmails = json['statusUpdateEmails']

		# parse requestDate
		epoch_time = json['requestDate']
		date_time_obj = datetime.datetime.strptime(epoch_time, '%Y-%m-%dT%H:%M:%S.%f%z')
		self.eventTime = str(int(date_time_obj.timestamp()))

		self.requestor = json['requestor']

	def getPropertyName(self):
		return self.propertyName
	
	def setPropertyName(self, name):
		self.propertyName = name

	def getRequestName(self):
		"""Return the ECCU Event request name
		:return: a python String object
		"""
		return self.requestName

	def getEventStartTime(self):
		"""Return the event time in Epoch time (in milliseconds)
		:returns: event epoch time (in milliseconds)
		"""
		return self.eventTime

	def getEventEndTime(self):
		"""Return the event time in Epoch time (in milliseconds)
		:returns: event epoch time (in milliseconds)
		"""
		return self.eventEndTime

	def getAnnotationTitle(self):
		"""Return the annotation title corresponding to this event and ready to be used in mPulse Annotation API. 
		By default it returns the eventName attribute.
		:returns: a python String object
		"""		
		return 'ECCU request'

	def getAnnotationText(self):
		"""Return the annotation text corresponding to this event and ready to be used in mPulse Annotation API.
		:returns: a python String object
		"""	
		result = "ECCU request "
		if self.requestName is not None:
			result += '\'' + self.requestName + '\' '
		result += "on property " + self.propertyName + " requested by " + self.requestor + "." + " " + self.getTagsText()
		return result

	def matchCriteria(self, criteria):
		Event.matchCriteria(self, criteria)
		for c in criteria.split(';'):
			if c in self.propertyName:
				return True
		return False

	def __str__(self):
		return Event.__str__(self) + \
		     	"              requestId: " + self.eventId + \
				"\n           propertyName: " + self.propertyName + \
				"\n           propertyType: " + self.propertyType + \
				"\n propertyNameExactMatch: " + self.propertyNameExactMatch + \
				"\n                  notes: " + self.notes + \
				"\n                 status: " + str(self.status) + \
				"\n          statusMessage: " + str(self.statusMessage) + \
				"\n  extendedStatusMessage: " + str(self.extendedStatusMessage) + \
				"\n       statusUpdateDate: " + str(self.eventEndTime) + \
				"\n     statusUpdateEmails: " + str(self.statusUpdateEmails) + \
				"\n            requestDate: " + str(self.eventTime) + \
				"\n              requestor: " + str(self.requestor)
