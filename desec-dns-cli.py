#!/usr/bin/python
#
# Author: Gerhard Steinbeis
# Version: 0.1.3
#

import sys
import os.path
import yaml
import argparse
# tabulate - structured console output 
#   https://bitbucket.org/astanin/python-tabulate
from tabulate import tabulate
from desec_dns_api import deSEC_DNS_API



#
# Argument parsing and help
#
# create argparser
parser = argparse.ArgumentParser(description="A python script utilysing the deSEC DNS api to manipulate DNS resource records from the command line.")

# add subparsers
subparsers = parser.add_subparsers()

# add subparser for "domain"
parser_domain = subparsers.add_parser('domain', 						help="allows to manage domains")
parser_domain.set_defaults(command='domain')
subparser_domain = parser_domain.add_subparsers(						help="available sub-commands")

parser_domain_list = subparser_domain.add_parser('list', 				help="list domains of the account")
parser_domain_list.set_defaults(command='domain', subcommand='list')
parser_domain_list.add_argument('--dname',  type=str, required=False,  	help="show a specific domain instead of all")
parser_domain_list.add_argument("--debug", action='store_true', 		help="show debug information")

parser_domain_create = subparser_domain.add_parser('create', 			help="create new domains in the account")
parser_domain_create.set_defaults(command='domain', subcommand='create')
parser_domain_create.add_argument('--dname',  type=str, required=True,  help="specifies the domain name to be created")
parser_domain_create.add_argument("--debug", action='store_true', 		help="show debug information")

parser_domain_delete = subparser_domain.add_parser('delete', 			help="delete domains from the account")
parser_domain_delete.set_defaults(command='domain', subcommand='delete')
parser_domain_delete.add_argument('--dname',  type=str, required=True,  help="specifies the domain name to be deleted")
parser_domain_delete.add_argument("--debug", action='store_true', 		help="show debug information")


# add subparser for "rrset"
parser_rrset = subparsers.add_parser('rrset', 							help="allows to manage resource-record-sets (RRset)")
parser_rrset.set_defaults(command='rrset')
subparser_rrset = parser_rrset.add_subparsers(							help="available sub-commands")

parser_rrset_list = subparser_rrset.add_parser('list', 					help="list rrsets for a domain")
parser_rrset_list.set_defaults(command='rrset', subcommand='list')
parser_rrset_list.add_argument('--dname',   type=str, required=True,  	help="specify the domain / zone to list the rrsets for")
parser_rrset_list.add_argument('--type',    type=str, required=False, 	help="filter the rrsets by type (A, MX, TXT, ...)")
parser_rrset_list.add_argument('--subname', type=str, required=False, 	help="filter the rrsets by sub-domain / host-part (www, ...)")
parser_rrset_list.add_argument("--debug", 	action='store_true', 		help="show debug information")

parser_rrset_create = subparser_rrset.add_parser('create', 				help="create a new rrsets for a domain")
parser_rrset_create.set_defaults(command='rrset', subcommand='create')
parser_rrset_create.add_argument('--dname',   type=str, required=True,  help="specify the domain / zone to add the rrsets to")
parser_rrset_create.add_argument('--type',    type=str, required=True,  help="specify the type of the rrset (A, MX, TXT, ...)")
parser_rrset_create.add_argument('--ttl',     type=int, required=True,  help="specify the ttl in seconds for the rrset")
parser_rrset_create.add_argument('--subname', type=str, required=True,  help="specify the sub-domain / host-part for the rrset")
parser_rrset_create.add_argument('--records', type=str, required=True,  help="specify the records as comma separated list. Text records must contain quotes which requires to state the argument douple-quoted like this '\"Text Record 1\",\"Text Record 2\"' while MX records contain a priority and a text component, the priority should be outside the second quotes like this '10 \"smtp1.domain.tld\",20 \"smtp2.domain.tld\"'")
parser_rrset_create.add_argument("--debug", 	action='store_true',	help="show debug information")

parser_rrset_modify = subparser_rrset.add_parser('modify',				help="modify a rrsets from a domain")
parser_rrset_modify.set_defaults(command='rrset', subcommand='modify')
parser_rrset_modify.add_argument('--dname',   type=str, required=True,  help="specify the domain / zone to modify the rrsets")
parser_rrset_modify.add_argument('--type',    type=str, required=True,  help="specify the type of the rrset (A, MX, TXT, ...)")
parser_rrset_modify.add_argument('--ttl',     type=int, required=False, help="specify the ttl in seconds for the rrset")
parser_rrset_modify.add_argument('--subname', type=str, required=True,  help="specify the sub-domain / host-part for the rrset")
parser_rrset_modify.add_argument('--records', type=str, required=False, help="specify the records as comma separated list. Text records must contain quotes which requires to state the argument douple-quoted like this '\"Text Record 1\",\"Text Record 2\"' while MX records contain a priority and a text component, the priority should be outside the second quotes like this '10 \"smtp1.domain.tld\",20 \"smtp2.domain.tld\"'")
parser_rrset_modify.add_argument("--debug", 	action='store_true', 	help="show debug information")

parser_rrset_delete = subparser_rrset.add_parser('delete',				help="delete a rrsets for a domain")
parser_rrset_delete.set_defaults(command='rrset', subcommand='delete')
parser_rrset_delete.add_argument('--dname',   type=str, required=True,  help="specify the domain / zone to modify the rrsets")
parser_rrset_delete.add_argument('--type',    type=int, required=True,  help="specify the type of the rrset (A, MX, TXT, ...)")
parser_rrset_delete.add_argument('--subname', type=str, required=True,  help="specify the sub-domain / host-part for the rrset")
parser_rrset_delete.add_argument("--debug", 	action='store_true', 	help="show debug information")

# start parsing args
args = parser.parse_args()

if args.debug:
	print(args)



################################################################################

# Read settings from config file
if os.path.isfile("desec-dns-cli.yml") == False:
	print("ERROR: The settings file 'desec-dns-cli.yml' is missing.")
	print("Please refer to the example config file and the README for more details.")
	exit()

with open("desec-dns-cli.yml", "r") as stream:
	try:
		settings = yaml.load(stream)
	except yaml.YAMLError as exc:
		print("ERROR: The settings file 'desec-dns-cli.yml' is invalid YAML syntax.")
		print("Please refer to the example config file and the README for more details.")
		exit()

if 'api_url' in settings:
	api_url  = settings['api_url']
else:
	print("ERROR: The 'api_url' settings is missing in the 'desec-dns-cli.yml' config file.")
	print("Please refer to the example config file and the README for more details.")
	exit()

if 'api_token' in settings:
	api_token = settings['api_token']
else:
	print("ERROR: The 'api_token' settings is missing in the 'desec-dns-cli.yml' config file.")
	print("Please refer to the example config file and the README for more details.")
	exit()


# Instantiate deSEC API object
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
		print("Error: The request failed with '" + str(api.http_code) + ": " + api.http_errmsg + "'\n   " + api.http_body)


#
# DOMAIN DELETE
#
if args.command == "domain" and args.subcommand == "delete":
	
	ret_status = api.domain_delete(dname=args.dname)
	if ret_status == True:
		print("Delete executed successfully.")
	else:
		print("Delete failed with '" + str(api.http_code) + " " + api.http_errmsg + "'\n   " + api.http_body)






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
		print("Error: The request failed with " + str(api.http_code) + ": " + api.http_errmsg + "'\n   " + api.http_body)


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
		print("Error: The request failed with " + str(api.http_code) + ": " + api.http_errmsg + "'\n   " + api.http_body)


#
# RRSET CREATE
#
if args.command == "rrset" and args.subcommand == "delete":

	ret_status = api.rrset_delete(dname=args.dname, type=args.type, subname=args.subname)
	if ret_status == True:
		print("Delete executed successfully.")
	else:
		print("Delete failed with '" + str(api.http_code) + " " + api.http_errmsg + "'" + "'\n   " + api.http_body)

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
			print("Error: The request failed with " + str(api.http_code) + ": " + api.http_errmsg + "'\n   " + api.http_body)

	else:
		print(sys.argv[0] + " " + args.command +": error: at least one of --ttl or --records need to be provided")


