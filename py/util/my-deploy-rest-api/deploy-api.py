#!/usr/bin/python

from flask import Flask, Response
from flask_restful import Api, Resource, reqparse
import subprocess
import json
from jinja2 import Template
import time

app = Flask(__name__)
api = Api(app)


##################### Load auth token ###################

try:
    with open('./.config.json', 'r') as f:
        conf = f.read()
    config = json.loads(conf)
    token = config['token']
except:
    print ".config.json not found.."
    raise SystemExit

###################### Some functions #########################

def gen_template(website, domain):
    with open('./template.yml', 'r') as t:
        temp = t.read()
    template = Template(temp)
    
    ready = template.render(website=website, domain=domain)
    with open('./deployments/' + website, 'w') as f:
        f.write(ready)


def deploy_label(file):
    path = '/root/my-deploy-rest-api/deployments/%s' % file
    reply = subprocess.check_output(['kubectl', 'create', '-f', path])
    cmd = "mysql -e 'create database %s;'" % file
    subprocess.Popen(['kubectl','exec','-it','mysql-replica-0','--','bash', '-c',cmd])
    return Response(reply, status=200)

def check_pods():
    proc = subprocess.Popen(['kubectl','get','pods','-n','default','-o','wide'], stdout=subprocess.PIPE)
    pods = proc.stdout.read()
    return Response(pods, status=200)

def deploy_site(pod,website,domain):
    subprocess.Popen(['kubectl','exec','-it',pod,'--','bash','-c','/mnt/deploy.sh ' + website + " " + domain])
    return "All executed , new website is now deployed do not forget to import database...", 200


##################### API classes #############################

class Exec(Resource):

    def get(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("token", location='headers', required=True)
        args = parser.parse_args()
        if args['token'] == token:
            return deploy_label(name)
        else:
            print "Auth token  {} not valid...".format(args['token'])

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("token", location='headers', required=True)
        parser.add_argument("website", required=True)
        parser.add_argument("domain", required=True)
        args = parser.parse_args()
        if args['token'] == token:
            return deploy_site(name, args['website'], args['domain'])
        else:
            print "Auth token {} not valid...".format(args['token'])


    def delete(self, name):
        return "OK", 200


class Check(Resource):

    def get(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("token", location='headers', required=True)
        args = parser.parse_args()
        if name == 'pods' and args['token'] == token:
            return check_pods()
        elif name == 'configs' and args ['token'] == token:
            return Response(subprocess.check_output(['ls', './deployments']), status=200)
        else:
            return 401

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("token", location='headers', required=True)
        parser.add_argument("domain", required=True)
        args = parser.parse_args()

        if args['token'] == token:
            gen_template(name, args['domain'])
            return "Created...", 200
        else:
            return "Auth token {} is not valid".format(args['token']), 401





#### Add resource and path mappings for the API
api.add_resource(Exec, "/exec/<string:name>")
api.add_resource(Check, "/check/<string:name>")

#### Run the api with devel server in debug mode
app.run(host='0.0.0.0', port=5000,debug=True)
