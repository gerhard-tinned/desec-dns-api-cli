#!/usr/bin/python
#
# Author Gerhard Steinbeis
# Version: 0.1.2
#

import urllib2
import json



class deSEC_DNS_API(object):

	#
	# Initially set the base url and the auth header
	#
	def __init__(self, api_url, api_token, debug=False):
		super(deSEC_DNS_API, self).__init__()
		self.url_base = api_url
		self.header = {'Authorization': 'Token ' + api_token}
		self.debug = debug
		self.http_body = None
		self.http_code = None
		self.single_result = False


	#
	# Function performing http requests
	#
	def http_request(self, url, header, type='GET', data=None):
		self.http_errmsg = ''
		if self.debug :
			print("*** DEBUG: http-request : http-url    : " + url)
			print("*** DEBUG: http-request : http-type   : " + type)
			print("*** DEBUG: http-request : http-header : " + str(header))
			print("*** DEBUG: http-request : http-data   : " + str(data))

		opener = urllib2.build_opener(urllib2.HTTPHandler())
		request = urllib2.Request(url, data=data, headers=header)
		# Set the request type (GET, POST, PATCH, DELETE)
		request.get_method = lambda: type
		try:
			ret = opener.open(request)
		except urllib2.HTTPError as err:
			self.http_code   = err.code
			self.http_errmsg = err.msg
			self.http_body   = err.read()
			if self.debug:
				print("*** DEBUG: http-response: http-code   : "  + str(self.http_code))
				print("*** DEBUG: http-response: http-error  : '" + str(err.code) + ": " + err.msg + "'")
				print("*** DEBUG: http-response: http-body   :\n" + self.http_body + "\n")
			return False

		self.http_body = ret.read()
		self.http_code = ret.getcode()
		if self.debug:
			print("*** DEBUG: http-request : url         : "  + ret.geturl())
			print("*** DEBUG: http-response: http-code   : "  + str(self.http_code))
			print("*** DEBUG: http-response: http-header :\n" + str(ret.info()))
			print("*** DEBUG: http-response: http-body   :\n" + self.http_body + "\n")

		return True


	#
	# Function to get json response parsed
	#
	# Return: array of dicts
	#
	def get_response_dict(self):
		# decode http_body from json to dict
		ret_dict = json.loads(self.http_body)

		# if single result is expected, create an array to remain structure
		if self.single_result == True:
			ret_dict = [ret_dict]

		if self.debug:
			print("*** DEBUG: json2dict    : ret_dict    : " + str(ret_dict))

		return ret_dict


  ##############################################################################


	#
	# Function to request the domain list
	#
	# Return: boolean (based on http_code)
	#
	def domain_list(self, dname=None):
		
		# check for dname to filter result
		url_addition = ''
		self.single_result = False
		if dname:
			url_addition = dname + "/"
			self.single_result = True

		# compile request url
		req_url = self.url_base + url_addition
		# request the list from the api
		ret_state = self.http_request(url=req_url, header=self.header, data=None, type='GET')

		# return code indicates success
		if self.http_code < 300:
			return True
		else:
			return False


	#
	# Function to create a new domain
	#
	# Return: boolean (based on http_code)
	#
	def domain_create(self, dname):		
		self.single_result = True

		# compose POST data
		post_data = dict()
		post_data['name'] = dname
		data = json.dumps(post_data)

		# Extend headers with Content-Type
		headers = self.header
		headers['Content-Type'] = "application/json"

		# compile request url
		req_url = self.url_base
		# request the list from the api
		ret_state = self.http_request(url=req_url, header=headers, data=data, type='POST')

		# return code indicates success
		if self.http_code < 300:
			return True
		else:
			return False


	#
	# Function to delete a domain
	#
	# Return: boolean (based on http_code)
	#
	def domain_delete(self, dname):
		
		# set dname to specify domain
		url_addition = ''
		url_addition = dname + "/"

		# compile request url
		req_url = self.url_base + url_addition
		# request the list from the api
		ret_state = self.http_request(url=req_url, header=self.header, type='DELETE')

		# return code indicates success
		if self.http_code < 300:
			return True
		else:
			return False


  ##############################################################################


	#
	# Function to request the rrset list
	#
	# Return: boolean (based on http_code)
	#
	def rrset_list(self, dname, type=None, subname=None):
		# check for filter arguments
		url_addition = ''
		self.single_result = False
		if type:
			url_addition = "?type=" + type
		if subname:
			url_addition = "?subname=" + subname
		if type and subname:
			url_addition = subname + ".../" + type + "/"
			self.single_result = True
		
		# compile request url
		req_url = self.url_base + dname + "/rrsets/" + url_addition
		# request the list from the api
		ret_state = self.http_request(url=req_url, header=self.header, data=None, type='GET')

		# return code indicates success
		if self.http_code < 300:
			return True
		else:
			return False


	#
	# Function to create a new rrset
	#
	# Return: boolean (based on http_code)
	#
	def rrset_create(self, dname, type, subname, records, ttl):
		self.single_result = True

		# compose POST data
		post_data = dict()
		post_data['subname'] = subname
		post_data['type'] = type
		post_data['ttl'] = ttl
		post_data['records'] = records.split(",") 
		data = json.dumps(post_data)

		if self.debug:
			print "*** DEBUG: data=" + data

		# Extend headers with Content-Type
		headers = self.header
		headers['Content-Type'] = "application/json"

		# compile request url
		req_url = self.url_base + dname + "/rrsets/"
		# request the list from the api
		ret_state = self.http_request(url=req_url, header=headers, data=data, type='POST')

		# return code indicates success
		if self.http_code < 300:
			return True
		else:
			return False


	#
	# Function to delete a new rrset
	#
	# Return: boolean (based on http_code)
	#
	def rrset_delete(self, dname, type, subname):
		self.single_result = True

		# compile request url
		req_url = self.url_base + dname + "/rrsets/" + subname + ".../" + type + "/"
		# request the list from the api
		ret_state = self.http_request(url=req_url, header=self.header, data=None, type='DELETE')

		# return code indicates success
		if self.http_code < 300:
			return True
		else:
			return False


	#
	# Function to modify a new rrset
	#
	# Return: boolean (based on http_code)
	#
	def rrset_modify(self, dname, type, subname, records=None, ttl=None):
		self.single_result = True

		# compose POST data
		post_data = dict()
		if ttl:
			post_data['ttl'] = ttl
		if records:
			post_data['records'] = records.split(",") 
		data = json.dumps(post_data)

		# Extend headers with Content-Type
		headers = self.header
		headers['Content-Type'] = "application/json"

		# compile request url
		req_url = self.url_base + dname + "/rrsets/" + subname + ".../" + type + "/"
		# request the list from the api
		ret_state = self.http_request(url=req_url, header=headers, data=data, type='PATCH')

		# return code indicates success
		if self.http_code < 300:
			return True
		else:
			return False

