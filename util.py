from jinja2 import Template

class bcolors:
    MAGENTA = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def SyntaxColorToCode(color):
	if color.lower() == 'magenta':
		return bcolors.MAGENTA
	elif color.lower() == 'blue':
		return bcolors.OKBLUE
	elif color.lower() == 'green':
		return bcolors.OKGREEN
	elif color.lower() == 'yellow':
		return bcolors.WARNING
	elif color.lower() == 'red':
		return bcolors.FAIL

	return ''

def FromTemplate(template, result):
	with open(template) as f:
		template = Template(f.read())
		for item in result:
			attr = None
			if (type(item) == tuple):
				attr = item[1]
				attr['dn'] = item[0]
			else:
				attr = item

			out = template.render(attr)
			print(out)