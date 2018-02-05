#!/usr/bin/python
#
# Author: Gerhard Steinbeis
# Version: 0.1.1
#

import sys
import yaml
import argparse
# https://bitbucket.org/astanin/python-tabulate
from tabulate import tabulate
from desec_dns_api import deSEC_DNS_API


# Read settings from config file
with open("desec-dns-cli.yml", "r") as stream:
	try:
		settings = yaml.load(stream)
	except yaml.YAMLError as exc:
		print(exc)
api_url  = settings['api_url']
api_token = settings['api_token']


#
# Argument parsing and help
#
# create argparser
parser = argparse.ArgumentParser()
parser.add_argument("--debug", action='store_true', help="Show debug information")

# add subparsers
subparsers = parser.add_subparsers()

# add subparser for "domain"
parser_domain = subparsers.add_parser('domain')
parser_domain.set_defaults(command='domain')
subparser_domain = parser_domain.add_subparsers()

parser_domain_list = subparser_domain.add_parser('list')
parser_domain_list.set_defaults(command='domain', subcommand='list')
parser_domain_list.add_argument('--dname',  type=str, required=False,  help="Specify the zone name")

parser_domain_create = subparser_domain.add_parser('create')
parser_domain_create.set_defaults(command='domain', subcommand='create')
parser_domain_create.add_argument('--dname',  type=str, required=True,  help="Specify the zone name")

parser_domain_delete = subparser_domain.add_parser('delete')
parser_domain_delete.set_defaults(command='domain', subcommand='delete')
parser_domain_delete.add_argument('--dname',  type=str, required=True,  help="Specify the zone name")


# add subparser for "rrset"
parser_rrset = subparsers.add_parser('rrset')
parser_rrset.set_defaults(command='rrset')
subparser_rrset = parser_rrset.add_subparsers()

parser_rrset_list = subparser_rrset.add_parser('list')
parser_rrset_list.set_defaults(command='rrset', subcommand='list')
parser_rrset_list.add_argument('--dname',   type=str, required=True,  help="Specify the zone name")
parser_rrset_list.add_argument('--type',    type=str, required=False, help="Specify the record type")
parser_rrset_list.add_argument('--subname', type=str, required=False, help="Specify the subdomain name")

parser_rrset_create = subparser_rrset.add_parser('create')
parser_rrset_create.set_defaults(command='rrset', subcommand='create')
parser_rrset_create.add_argument('--dname',   type=str, required=True,  help="Specify the zone name")
parser_rrset_create.add_argument('--type',    type=str, required=True,  help="Specify the record type")
parser_rrset_create.add_argument('--subname', type=str, required=True,  help="Specify the subdomain name")
parser_rrset_create.add_argument('--ttl',     type=str, required=True,  help="Specify the ttl in seconds")
parser_rrset_create.add_argument('--records', type=str, required=True,  help="Specify the records as coma seperated list")

parser_rrset_modify = subparser_rrset.add_parser('modify')
parser_rrset_modify.set_defaults(command='rrset', subcommand='modify')
parser_rrset_modify.add_argument('--dname',   type=str, required=True,  help="Specify the zone name")
parser_rrset_modify.add_argument('--type',    type=str, required=True,  help="Specify the record type")
parser_rrset_modify.add_argument('--subname', type=str, required=True,  help="Specify the subdomain name")
## optionalarguments
parser_rrset_modify.add_argument('--ttl',     type=str, required=False,  help="Specify the ttl in seconds to be updated")
parser_rrset_modify.add_argument('--records', type=str, required=False,  help="Specify the records as coma seperated list to be updated")

parser_rrset_delete = subparser_rrset.add_parser('delete')
parser_rrset_delete.set_defaults(command='rrset', subcommand='delete')
parser_rrset_delete.add_argument('--dname',   type=str, required=True,  help="Specify the zone name")
parser_rrset_delete.add_argument('--type',    type=str, required=True,  help="Specify the record type")
parser_rrset_delete.add_argument('--subname', type=str, required=True,  help="Specify the subdomain name")

# start parsing args
args = parser.parse_args()

# Prepare global parameters
header = {'Authorization': 'Token ' + api_token}

if args.debug:
	print(args)




################################################################################

api = deSEC_DNS_API(api_url=api_url, api_token=api_token, debug=args.debug)

################################################################################


#
# DOMAIN LIST
#
if args.command == "domain" and args.subcommand == "list":
	
	ret_status = api.domain_list(dname=args.dname)

	# create a plain text list from the records array
	if ret_status == True:
		# Post process the result
		res_dict = api.get_response_dict()
		for res_entry in res_dict:
			# remove the keys for console output
			res_entry.pop('keys', None)
		print(tabulate(res_dict, headers='keys', showindex="always", tablefmt="grid"))
	else:
		print("Error: The request failed with " + str(api.http_code) + ": " + api.http_errmsg)


#
# DOMAIN CREATE
#
if args.command == "domain" and args.subcommand == "create":
	
	ret_status = api.domain_create(dname=args.dname)

	# create a plain text list from the records array
	if ret_status == True:
		# Post process the result
		res_dict = api.get_response_dict()
		for res_entry in res_dict:
			# remove the keys for console output
			res_entry.pop('keys', None)
		print(tabulate(res_dict, headers='keys', showindex="always", tablefmt="grid"))
	else:
		print("Error: The request failed with " + str(api.http_code) + ": " + api.http_errmsg)


#
# DOMAIN DELETE
#
if args.command == "domain" and args.subcommand == "delete":
	
	ret_status = api.domain_delete(dname=args.dname)
	if ret_status == True:
		print("Delete executed successfully.")
	else:
		print("Delete failed with '" + str(api.http_code) + " " + api.http_errmsg + "'")






################################################################################


#
# RRSET LIST
#
if args.command == "rrset" and args.subcommand == "list":
	
	ret_status = api.rrset_list(dname=args.dname, type=args.type, subname=args.subname)
	
	# create a plain text list from the records array
	if ret_status == True:
		# Post process the result
		res_dict = api.get_response_dict()
		for res_entry in res_dict:
			# prepare "records" for console output
			res_entry['records'] = '\n'.join(res_entry['records'])
		print(tabulate(res_dict, headers='keys', showindex="always", tablefmt="grid"))
	else:
		print("Error: The request failed with " + str(api.http_code) + ": " + api.http_errmsg)


#
# RRSET CREATE
#
if args.command == "rrset" and args.subcommand == "create":

	ret_status = api.rrset_create(dname=args.dname, type=args.type, subname=args.subname, records=args.records, ttl=args.ttl)

	# create a plain text list from the records array
	if ret_status == True:
		res_dict = api.get_response_dict()
		# Post process the result
		for res_entry in res_dict:
			# prepare "records" for console output
			res_entry['records'] = '\n'.join(res_entry['records'])
		print(tabulate(res_dict, headers='keys', showindex="always", tablefmt="grid"))
	else:
		print("Error: The request failed with " + str(api.http_code) + ": " + api.http_errmsg)


#
# RRSET CREATE
#
if args.command == "rrset" and args.subcommand == "delete":

	ret_status = api.rrset_delete(dname=args.dname, type=args.type, subname=args.subname)
	if ret_status == True:
		print("Delete executed successfully.")
	else:
		print("Delete failed with '" + str(api.http_code) + " " + api.http_errmsg + "'")

#
# RRSET MODIFY
#
if args.command == "rrset" and args.subcommand == "modify":

	if args.ttl or args.records:
		ret_status = api.rrset_modify(dname=args.dname, type=args.type, subname=args.subname, records=args.records, ttl=args.ttl)
	
		if ret_status == True:
			res_dict = api.get_response_dict()
			# Post process the result
			for res_entry in res_dict:
				# prepare "records" for console output
				res_entry['records'] = '\n'.join(res_entry['records'])
			print(tabulate(res_dict, headers='keys', showindex="always", tablefmt="grid"))
		else:
			print("Error: The request failed with " + str(api.http_code) + ": " + api.http_errmsg)

	else:
		print(sys.argv[0] + " " + args.command +": error: at least one of --ttl or --records need to be provided")


