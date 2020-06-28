#!/usr/bin/env python
import json
import csv
import argparse
from util import *
from jinja2 import Environment, meta

parser = argparse.ArgumentParser(prog='template', description='Utility to create formatted data using a template. Pass in a CSV or JSON file to bulk create according to the template. Passing neither will prompt for user input')
parser.add_argument('-j', dest='json', metavar='json', help='Read input file as JSON')
parser.add_argument('-c', dest='csv', metavar='csv', help="Read input file as CSV")
parser.add_argument('-l', dest='list', action='store_const', const='list', help='List variables in template')

# Mandatory arguments
parser.add_argument('template', metavar='template', type=str, help='template file')

def FromJSON(in_file):
	with open(in_file) as f:
		data = json.loads(f.read())
		FromTemplate(args.template, data)

def FromCSV(in_file):
	with open(in_file) as f:
		reader = csv.DictReader(f, delimiter=',')
		rows = []
		for row in reader:
			rows.append(row)
		FromTemplate(args.template, rows)

args = parser.parse_args()

if args.json:
	FromJSON(args.json)
elif args.csv:
	FromCSV(args.csv)
elif args.list:
	with open(args.template) as f:
		env = Environment()
		ast = env.parse(f.read())
		for item in sorted(meta.find_undeclared_variables(ast)):
			print(item)
else:
	data = {}
	with open(args.template) as f:
		env = Environment()
		ast = env.parse(f.read())
		for item in sorted(meta.find_undeclared_variables(ast)):
			data[item] = raw_input(item + ": ")
	print('\n' * 2)
	FromTemplate(args.template, [data])