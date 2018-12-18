import requests
import logging
import json 

class MPulseAPIHandler:

	def __init__(self, logger):
		self.logger = logger


	def getSecurityToken(self, apiToken, tenant):
		"""curl -X PUT -H "Content-type: application/json" --data-binary '{"apiToken":"<token>", "tenant": "<tenant>"}' \
					"https://mpulse.soasta.com/concerto/services/rest/RepositoryService/v1/Tokens"

		:param apiToken: mPulse API token
		:type apiToken: a String
		:param tenant: mPulse tenant
		:type tenant: a String
		:returns: a String with the security token, None in case of error
		"""
		payload = "{\"apiToken\": \"" + apiToken + "\", \"tenant\": \"" + tenant + "\"}"
		self.logger.info("requesting an mPulse security token with: " + payload)
		url = 'https://mpulse.soasta.com/concerto/services/rest/RepositoryService/v1/Tokens'
		result = requests.put(url, data = payload, headers={'Content-Type':'application/json'})
		if (result.status_code == 200):
			json_data = result.json()
			self.logger.info('mPulse security token returned: ' + str(json_data['token']) )
			return str(json_data['token'])
		else:
			self.logger.error('Error ' + str(result.status_code) + ': no security token returned')
			return None

	def addAnnotation(self, token, title, text, start, end = None):
		"""Add a new Annotation to mPulse dashboard.

		:param token: the security token as returned by getSecurityToken()
		:type token: a String object
		:param title: the annotation title
		:type title: a String object
		:param text: the annotation body text
		:type text: a String object
		:param start: start time of the annotation in epoch time format in milliseconds
		:type start: an int 
		:param end: (optional) end time of the annotation in epoch time format in milliseconds
		:type end: an int 
		"""
		if end is None:
			payload = "{\"title\":\"" + title + "\", \"start\": \"" + str(start) + "\", \"text\":\"" + text + "\"}"
		else:
			payload = "{\"title\":\"" + title + "\", \"start\": \"" + str(start) + "\", \"end\":\"" + str(end) + "\", \"text\":\"" + text + "\"}"
		self.logger.info("adding new annotation: " + payload)	

		url = "https://mpulse.soasta.com/concerto/mpulse/api/annotations/v1"
		result = requests.post(url, data = payload, headers={'Content-Type':'application/json', 'X-Auth-Token': token })
		if (result.status_code == 200):
			json_data = result.json()
			self.logger.info('annotation successfully added')
		else:
			self.logger.error('Error ' + str(result.status_code) + ': annotation not added!')

