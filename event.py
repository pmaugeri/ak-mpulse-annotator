import datetime


class Event:

	def __init__(self, eventId = None):
		self.eventId = eventId

	def matchCriteria(self, criteria):
		return True

	def parseJson(self, json):
		"""Parse a JSON object describing an Event.
		:param json: the Event to be parsed
		:type json: a python JSON object
		"""
		self.eventId = json['eventId']
		epoch_time = json['eventTime']
		dt = datetime.datetime.strptime(epoch_time, "%Y-%m-%dT%H:%M:%S.%fZ")		
		self.eventTime = str(int(dt.strftime("%s")) * 1000)
		self.eventTypeId = json['eventType']['eventTypeId']
		self.eventTypeName = json['eventType']['eventTypeName']
		self.eventDefinitionId = json['eventType']['eventDefinition']['eventDefinitionId']
		self.eventName = json['eventType']['eventDefinition']['eventName']
		self.username = json['username']
		self.impersonator = json['impersonator']
		self.eventData = json['eventData']

	def getEventId(self):
		return self.eventId

	def getEventTime(self):
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


class FastPurgeEvent(Event):

	def __init__(self, eventId = None):
		Event.__init__(self)

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
		Event.parseJson(self, json)
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
		return Event.__str__(self) + \
				"\n      purgeAction: " + str(self.purgeAction) + \
				"\n     purgeNetwork: " + str(self.purgeNetwork) + \
				"\n     purgeRequest: " + str(self.purgeRequest) + \
				"\n    purgeResponse: " + str(self.purgeResponse)

	def getAnnotationText(self):
		"""Return the annotation text corresponding to this event and ready to be used in mPulse Annotation API.
		:returns: a python String object
		"""		
		return "Purge request on " + self.purgeNetwork + " network: " + self.purgeRequest


class PropertyManagerEvent(Event):

	def __init__(self, eventId = None):
		Event.__init__(self)

	def matchCriteria(self, criteria):
		Event.matchCriteria(self, criteria)
		if criteria == '':
			return True
		for prop in criteria.split(';'):
			if prop == self.propertyName:
				return True
		return False

	def parseJson(self, json):
		Event.parseJson(self, json)
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
		return Event.__str__(self) + \
				"\n     propertyName: " +  str(self.propertyName) + \
				"\n  propertyVersion: " +  str(self.propertyVersion) + \
				"\n         username: " +  str(self.username)

	def getAnnotationText(self):
		"""Return the annotation text corresponding to this event and ready to be used in mPulse Annotation API.
		:returns: a python String object
		"""		
		return "" + self.propertyName + " v" + self.propertyVersion

