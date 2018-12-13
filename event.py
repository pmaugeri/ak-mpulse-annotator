
class Event:

	def __init__(self, eventId = None):
		self.eventId = eventId

	def parseJson(self, json):
		self.eventId = json['eventId']
		self.eventTime = json['eventTime']
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
		return "eventId: " + self.eventId + \
		"\neventTime: " + self.eventTime + \
		"\neventTypeId: " + self.eventTypeId + \
		"\neventTypeName: " + self.eventTypeName + \
		"\nusername: " + self.username + \
		"\nimpersonator: " + str(self.impersonator) + \
		"\neventDefinitionId: " + str(self.eventDefinitionId) + \
		"\neventName: " + str(self.eventName)




class FastPurgeEvent(Event):

	def __init__(self, eventId = None):
		Event.__init__(self)

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
		"\npurgeAction: " + str(self.purgeAction) + \
		"\npurgeNetwork: " + str(self.purgeNetwork) + \
		"\npurgeRequest: " + str(self.purgeRequest) + \
		"\npurgeResponse: " + str(self.purgeResponse)

