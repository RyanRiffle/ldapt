# ldapt
A ldapsearch client using Jinja2 to take the returned data and create new data. This project was created for directory servers hosting IDM and access management software like IBM Security Access Manager and IBM Security Identity Manager to simply create accounts based on other account access. 

There are two tools in this repository -- `ldapt` and `template`. **ldapt** is used to search LDAP and generate other data using a template based on the entries returned. **template** is used to read CSV, JSON, or prompt for values and render the Jinja2 template with that data.


## Usage
```
usage: ldapt [-h] [-D bind_dn] [-w bind_pw] [-p port] [-b base] [-j] [-H host]
             [-A] [-g template.lt] [-o file]
             filter [attr [attr ...]]

LDAP utility with the ability to output based on templates.

positional arguments:
  filter          search filter
  attr            attribute filter

optional arguments:
  -h, --help      show this help message and exit
  -D bind_dn      user to bind
  -w bind_pw      bind password
  -p port         port directory server is on, defaults to 10389
  -b base         base search DN
  -j              output as JSON
  -H host         host directory server is on, defaults to localhost
  -A              only show attributes, don't show the DN or blank line
  -g template.lt  generate output using template
  -o file         write output to file

```

## Examples Scenarios
Create an LDIF to unlock all accounts belonging to OU. Please note that in the template the two blank lines are necessary.

**unlock.template**
```
dn: uid={{ uid[0] }},ou=testou,dc=testdc
changetype: modify
delete: pwdAccountLockedTime
-
delete: pwdFailureTime


```

**Unlock accounts**
```
ldapt -D cn=admin -w secret -g unlock.template -b ou=testout,dc=testdc uid=* | ldapmodify -D cn=admin -w secret
```