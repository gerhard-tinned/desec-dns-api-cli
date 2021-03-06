#!/usr/bin/python
"""
Author Gerhard Steinbeis
Version: 0.2.0
"""

from __future__ import print_function
import json
import requests


class deSEC_DNS_API(object):
    """
    Class to handle the deSEC DNS APIT requests
    Requires: api_url, api_token
    """

    def __init__(self, api_url, api_token, debug=False):
        """
        Initially set the base url and the auth header

        Keyword arguments:
        api_url -- The API url used to cennect to
        api_token -- The API token used to authentiocate on the API
        debug -- Enable / Disable debug output (default False)
        """
        super(deSEC_DNS_API, self).__init__()
        self.url_base = api_url
        self.header = {'Authorization': 'Token ' + api_token}
        self.debug = debug
        self.http_body = None
        self.http_code = None
        self.http_errmsg = None
        self.single_result = False


    def http_request(self, url, header, method='GET', data=None):
        """
        Function performing http requests

        Keyword arguments:
        url -- The api url to send the request to
        header -- Headers to send with the HTTP request
        method -- The HTTP method used for the request (default 'GET')
        data -- The request data to be sent with the request (default None)
        """
        self.http_errmsg = ''
        if self.debug:
            print("*** DEBUG: http-request : http-url    : " + url)
            print("*** DEBUG: http-request : http-method : " + method)
            print("*** DEBUG: http-request : http-header : " + str(header))
            print("*** DEBUG: http-request : http-data   : " + str(data))

        if data is None:
            req_data = None
        else:
            # encode data if passed to the function
            req_data = data.encode('utf-8')
        
        
        # Set the request type (GET, POST, PATCH, DELETE)
        
        try:
            ret = requests.request(method=method, url=url, data=data, headers=header)
        except requests.exceptions.RequestException as err:
            self.http_code = err.code
            self.http_errmsg = err.msg
            self.http_body = err.read()
            if self.debug:
                print("*** DEBUG: http-response: http-code   : "  + str(self.http_code))
                print("*** DEBUG: http-response: http-error  : '" + str(err.code) + ": " + err.msg + "'")
                print("*** DEBUG: http-response: http-body   :\n" + self.http_body + "\n")
            return False

        self.http_body = ret.text
        self.http_code = ret.status_code
        if self.debug:
            print("*** DEBUG: http-request : url         : "  + ret.geturl())
            print("*** DEBUG: http-response: http-code   : "  + str(self.http_code))
            print("*** DEBUG: http-response: http-header :\n" + str(ret.info()))
            print("*** DEBUG: http-response: http-body   :\n" + self.http_body + "\n")

        return True


    def get_response_dict(self):
        """
        Function to get json response parsed

        Return: array of dicts
        """

        # decode http_body from json to dict
        ret_dict = json.loads(self.http_body)

        # if single result is expected, create an array to remain structure
        if self.single_result:
            ret_dict = [ret_dict]

        if self.debug:
            print("*** DEBUG: json2dict    : ret_dict    : " + str(ret_dict))

        return ret_dict



    def domain_list(self, zone=None):
        """
        Function to request the domain list
        Return: boolean (based on http_code)

        Keyword arguments:
        zone -- The domain name that should be filtered for
        """

        # check for zone to filter result
        url_addition = ''
        self.single_result = False
        if zone:
            url_addition = zone + "/"
            self.single_result = True

        # compile request url
        req_url = self.url_base + url_addition
        # request the list from the api
        self.http_request(url=req_url, header=self.header, data=None, method='GET')

        # return code indicates success
        if self.http_code < 300:
            return True
        else:
            return False


    def domain_create(self, zone):
        """
        Function to create a new domain
        Return: boolean (based on http_code)

        Keyword arguments:
        zone -- The domain name that should be created
        """
        self.single_result = True

        # compose POST data
        post_data = dict()
        post_data['name'] = zone
        data = json.dumps(post_data)

        # Extend headers with Content-Type
        headers = self.header
        headers['Content-Type'] = "application/json"

        # compile request url
        req_url = self.url_base
        # request the list from the api
        self.http_request(url=req_url, header=headers, data=data, method='POST')

        # return code indicates success
        if self.http_code < 300:
            return True
        else:
            return False


    def domain_delete(self, zone):
        """
        Function to delete a domain
        Return: boolean (based on http_code)

        Keyword arguments:
        zone -- The domain name that should be deleted
        """

        # set zone to specify domain
        url_addition = ''
        url_addition = zone + "/"

        # compile request url
        req_url = self.url_base + url_addition
        # request the list from the api
        self.http_request(url=req_url, header=self.header, method='DELETE')

        # return code indicates success
        if self.http_code < 300:
            return True
        else:
            return False




    def rrset_list(self, zone, type=None, subname=None):
        """
        Function to request the rrset list
        Return: boolean (based on http_code)

        Keyword arguments:
        zone -- The domain that should be used
        type -- The type of rrsets that should be shown (default None)
        subname -- The subname of rrset that should be shown (default None)
        """
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
        req_url = self.url_base + zone + "/rrsets/" + url_addition
        # request the list from the api
        self.http_request(url=req_url, header=self.header, data=None, method='GET')

        # return code indicates success
        if self.http_code < 300:
            return True
        else:
            return False


    def rrset_create(self, zone, type, subname, records, ttl):
        """
        Function to create a new rrset
        Return: boolean (based on http_code)

        Keyword arguments:
        zone -- The domain that should be used
        type -- The type of rrsets that should be created
        subname -- The subname of rrset that should be created
        records -- The records that should be set for this rrset
        ttl -- The ttl that should be set for this rrset
        """
        self.single_result = True

        # compose POST data
        post_data = dict()
        post_data['subname'] = subname
        post_data['type'] = type
        post_data['ttl'] = ttl
        post_data['records'] = records.split(",")
        data = json.dumps(post_data)

        if self.debug:
            print("*** DEBUG: data=" + data)

        # Extend headers with Content-Type
        headers = self.header
        headers['Content-Type'] = "application/json"

        # compile request url
        req_url = self.url_base + zone + "/rrsets/"
        # request the list from the api
        self.http_request(url=req_url, header=headers, data=data, method='POST')

        # return code indicates success
        if self.http_code < 300:
            return True
        else:
            return False


    def rrset_delete(self, zone, type, subname):
        """
        Function to delete a new rrset
        Return: boolean (based on http_code)

        Keyword arguments:
        zone -- The domain that should be used
        type -- The type of rrsets that should be deleted
        subname -- The subname of rrset that should be deleted
        """
        self.single_result = True

        # compile request url
        req_url = self.url_base + zone + "/rrsets/" + subname + ".../" + type + "/"
        # request the list from the api
        self.http_request(url=req_url, header=self.header, data=None, method='DELETE')

        # return code indicates success
        if self.http_code < 300:
            return True
        else:
            return False


    def rrset_modify(self, zone, type, subname, records=None, ttl=None):
        """
        Function to modify a new rrset
        Return: boolean (based on http_code)

        Keyword arguments:
        zone -- The domain that should be used
        type -- The type of rrsets that should be modified
        subname -- The subname of rrset that should be modified
        records -- The records that should be set for this rrset (default None)
        ttl -- The ttl that should be set for this rrset (default None)
        """
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
        req_url = self.url_base + zone + "/rrsets/" + subname + ".../" + type + "/"
        # request the list from the api
        self.http_request(url=req_url, header=headers, data=data, method='PATCH')

        # return code indicates success
        if self.http_code < 300:
            return True
        else:
            return False
