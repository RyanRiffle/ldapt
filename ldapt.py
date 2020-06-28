#!/usr/bin/env python
import ldap
import argparse
import json
from os import path
from util import *
from jinja2 import Environment, meta
import sys

parser = argparse.ArgumentParser(prog='ldapt', description='LDAP utility with the ability to output based on templates.')
# Optional arguments
parser.add_argument('-D', dest='bind_dn', metavar='bind_dn', type=str, help='user to bind')
parser.add_argument('-w', dest='bind_pw', metavar='bind_pw', type=str, help='bind password')
parser.add_argument('-p', dest='port', metavar='port', type=int, help='port directory server is on, defaults to 10389')
parser.add_argument('-b', dest='base', metavar='base', type=str, help='base search DN')
parser.add_argument('-j', dest='json', action='store_const', const='json', help='output as JSON')
parser.add_argument('-H', dest='host', metavar='host', type=str, help='host directory server is on, defaults to localhost')
parser.add_argument('-A', dest='attr_only', action='store_const', const='attr_only', help='only show attributes, don\'t show the DN or blank line')
parser.add_argument('-g', dest='generate', metavar='template.lt', type=str, help='generate output using template')
parser.add_argument('-o', dest='output', metavar='file', type=str, help='write output to file')

# Mandatory arguments
parser.add_argument('filter', metavar='filter', type=str, help='search filter')
parser.add_argument('attributes', metavar='attr', type=str, nargs='*', help='attribute filter')

args = parser.parse_args()
# Defaults so that application works without a syntax.json
syntax = {'formatting': {
	'dn': '',
	'attributes': '',
	'separator': '='
},
'filters': []
}
filters = []
dn_only = False

def PrintLDIFResult(result):
	for item in result:
		if ((not args.attr_only) or (dn_only)):
			print(syntax['formatting']['dn'] + item[0] + bcolors.ENDC)
		if not dn_only:
			for attr in item[1]:
				for value in item[1][attr]:
					val_filters = ProcessValueFilters(value)
					#attr_fil = '' if len(attr_filters) == 0 else GetTotalSyntax(attr_filters.pop())
					val_fil = '' if len(val_filters) == 0 else GetTotalSyntax(val_filters[len(val_filters) - 1])

					print(syntax['formatting']['attributes'] + attr + bcolors.ENDC + syntax['formatting']['separator'] + val_fil + value + bcolors.ENDC)
		if not args.attr_only:
			print('')

def PrintJSONResult(result):
	print(json.dumps(result))

def GetTotalSyntax(attr):
	if args.output:
		return ''
	total = ''
	if 'indent' in attr:
		total += ' '*attr['indent']
	if 'prefix' in attr:
		total += attr['prefix']
	if 'color' in attr:
		total += SyntaxColorToCode(attr['color'])
	if 'bold' in attr:
		if attr['bold'] == True:
			total += bcolors.BOLD
	if 'underline' in attr:
		if attr['underline'] == True:
			total += bcolors.UNDERLINE
	return total

def ProcessValueFilters(value):
	applicable_value = []
	for f in filters:
		if f['value'] == value:
			applicable_value.append(f)
	applicable_attr = []#[v for v in filters if v['attribute'] == key]
	return applicable_value

try:
	syntax_obj = None
	if path.exists('syntax.json'):
		with open('syntax.json') as f:
			syntax_obj = json.loads(f.read())
			if 'filters' in syntax_obj:
				filters = syntax_obj['filters']
			syntax = syntax_obj
			if 'formatting' in syntax_obj:
				if 'dn' in syntax_obj['formatting']:
					dn = syntax_obj['formatting']['dn']
					syntax['formatting']['dn'] = GetTotalSyntax(dn)
				if 'attributes' in syntax_obj['formatting']:
					attr = syntax_obj['formatting']['attributes']
					syntax['formatting']['attributes'] = GetTotalSyntax(attr)
except Exception as e:
	print(bcolors.FAIL + 'Error parsing syntax.json' + bcolors.ENDC)
	print(str(e))

try:
	if not args.port:
		args.port = 10389
	if not args.host:
		args.host = 'ldap://localhost'
	if args.attributes == ['dn']:
		dn_only = True
		args.attributes = None

	connect = ldap.initialize('ldap://localhost' + ':' + str(args.port))
	connect.set_option(ldap.OPT_REFERRALS, 0)
	connect.simple_bind_s(args.bind_dn, args.bind_pw)

	result = None

	# When generating output based on template, only return attributes the template needs
	if args.generate:
		template_attributes = []
		with open(args.generate) as f:
			env = Environment()
			ast = env.parse(f.read())
			for item in sorted(meta.find_undeclared_variables(ast)):
				template_attributes.append(item)
		result = connect.search_s(args.base, ldap.SCOPE_SUBTREE, args.filter, template_attributes)
	else:
		result = connect.search_s(args.base, ldap.SCOPE_SUBTREE, args.filter, args.attributes)

	if args.output:
		sys.stdout = open(args.output, 'w')
		bcolors.ENDC = ''


	if args.generate:
		FromTemplate(args.generate, result)
	elif args.json:
		PrintJSONResult(result)
	else:
		PrintLDIFResult(result)
except Exception as e:
	print(e)