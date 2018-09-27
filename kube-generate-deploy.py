#!/usr/bin/python

import jinja2
import sys
import json
import argparse

def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--template','-t',nargs=1,help='Template file to be loaded')
    parser.add_argument('--data','-d',nargs=1,help='JSON formated data for the template')
    return parser


parser = Parser()
args = parser.parse_args()


if args.template and args.data:
    file = args.template[0]
    data = args.data[0]
    with open(file, 'r') as f:
        content = f.read()
    with open(data, 'r') as d:
        values = d.read()
    template = jinja2.Template(content)
    data_values = json.loads(values)


    ready = template.render(name_web=data_values['name_web'], name_mysql=data_values['name_mysql'], domain=data_values['domain'], replicas_mysql=data_values['replicas_mysql'], mysql_root_pass=data_values['mysql_root_pass'], mysql_db=data_values['mysql_db'],mysql_user=data_values['mysql_user'],mysql_pass=data_values['mysql_pass'], replicas_web=data_values['replicas_web'])

    with open('deploy.yml', 'w') as deploy:
        deploy.write(ready)

else:
    print "Data example file"
    print """
{
  "name_web": "stefan-example-web",
  "name_mysql": "stefan-example-mysql",
  "domain": "stefan.example",
  "replicas_mysql": "1",
  "replicas_web": "3",
  "mysql_root_pass": "stefan123",
  "mysql_db": "stefan",
  "mysql_user": "stefan",
  "mysql_pass": "stefan"
}
"""
    print "Template example file can be found on:  https://github.com/vgeorgiev90/Containers/blob/master/kubernetes/Build/deploy-migrated-wordpress.yml"
