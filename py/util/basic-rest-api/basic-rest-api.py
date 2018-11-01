#!/usr/bin/python

from flask import Flask
from flask_restful import Api, Resource, reqparse
import subprocess
import json
from jinja2 import Template


app = Flask(__name__)
api = Api(app)

#### Load the auth token from a file config.json
try:
    with open('config.json', 'r') as f:
        conf = f.read()
    config = json.loads(conf)
    token = config['token']
except:
    print "config.json not found.." 
    raise SystemExit

############## Api endpoint to execute the provisioning script #########
class Exec(Resource):

    def post(self, name):
#### Get args one for subcommand: vginit or volume , one for state present/absent
        choice = ['present', 'absent']
        choice2 = ['vginit', 'volume']
        parser = reqparse.RequestParser()
        parser.add_argument("provision", choices=choice2, location='headers', required=True)
        parser.add_argument("state", choices=choice, required=True)
        parser.add_argument("token", location='headers', required=True)
        args = parser.parse_args()
#### Check if the token provided matches the auth one
        if args['token'] == token:

#### Check if the ansible config file actually exists
            files = subprocess.check_output(['ls', '/home/ansible/dynamic-hostpath-with-nfs/hosts'])
            for file in files.split("\n"):
                if file == name:

#### If there is such file execute provisioning command
                    provision = args['provision'].encode('ascii', 'ignore')
                    name = name.encode('ascii','ignore')
                    state = args['state'].encode('ascii','ignore')
                    cmd = "/home/ansible/dynamic-hostpath-with-nfs/run.sh %s %s %s" % (provision,name,state)
                    subprocess.Popen([cmd], cwd='/home/ansible/dynamic-hostpath-with-nfs/',shell=True)
                    return "Executed successfully.. ", 200

#### Return 404 if the cofig file can not be found
            return "Config file {} can not be found".format(name), 404
        else:
            return "Auth token {} is not valid".format(args['token']), 401


#### Api endpoint to che the available files in the config directory
class Config(Resource):

    def get(self):
        reply = subprocess.check_output(['ls', '/home/ansible/dynamic-hostpath-with-nfs/hosts'])
        return reply, 200


#### Api endpoint to check the content of config file, create new config, modify existing one or delete
class Files(Resource):

#### Check the content of provided config file    
    def get(self, name):
        list = subprocess.check_output(['ls', '/home/ansible/dynamic-hostpath-with-nfs/hosts'])
        for file in list.split("\n"):
            if file == name:
                reply = subprocess.check_output(['cat', "/home/ansible/dynamic-hostpath-with-nfs/hosts/%s" % file])
                return reply, 200
        return "File {} not found..".format(name), 404

#### Create new config
    def post(self,name):
        parser = reqparse.RequestParser()
        parser.add_argument("options",required=True)
        parser.add_argument("token", location='headers',required=True)
        args = parser.parse_args()
        if args['token'] == token:
            files = subprocess.check_output(['ls', '/home/ansible/dynamic-hostpath-with-nfs/hosts'])
### Check if it exists first
            for file in files:
                if name == file:
                    return "File {} already exists".format(name), 400

#### List of needed options for new config file
            if name == 'help':
                return "Needed options for post: 'vg_name','devices','lv_name','lv_size','fs_type','mount_name','worker_host','nfs_server','work_dir'", 200

#### Get all json formated options and parse  
            path = "/home/ansible/dynamic-hostpath-with-nfs/hosts/%s" % name
            with open('template.jinja', 'r') as t:
                temp = t.read()
            template = Template(temp)
            data = json.loads(args['options'])

#### Render the jinja template and write the config file
            ready = template.render(nfs_server=data['nfs_server'],worker_host=data['worker_host'],devices=data['devices'],vg_name=data['vg_name'],lv_name=data['lv_name'],lv_size=data['lv_size'],fs_type=data['fs_type'],mount_name=data['mount_name'],work_dir=data['work_dir'])

            with open(path, 'w') as f:
                f.write(ready)
            return "File {} created successfully".format(path), 201
        else:
            return "Auth token {} is not valid..".format(args['token']),401

#### Change option for existing file , full option must be specified 
#### example:  option=lv_name=api-test , replace=lv_name=just-test
    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("option",required=True)
        parser.add_argument("replace",required=True)
        parser.add_argument("token", location='headers',required=True)
        args = parser.parse_args()
        if args['token'] == token:
            path = "/home/ansible/dynamic-hostpath-with-nfs/hosts/%s" % name
            try:
                with open(path, 'r') as f:
                    data = f.read()
                data = data.replace(args['option'],args['replace'])
                with open(path, 'w') as f:
                    f.write(data)
                return "Modified: {}".format(path), 200
            except:
                return "File {} not found".format(path)
        else:
            return "Auth token {} is not valid..".format(args['token']),401

#### Delete specified config file 
    def delete(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("token", location='headers',required=True)
        args = parser.parse_args()
        if args['token'] == token:
            path = "/home/ansible/dynamic-hostpath-with-nfs/hosts/%s" % name
            try:
                subprocess.check_output(['rm', path, '-rf'])
                return "{} is now deleted".format(name), 200
            except:
                return "File {} could not be deleted".format(name), 404
        else:
            return "Auth token {} is not valid..".format(args['token']), 401


#### Add resource and path mappings for the API
api.add_resource(Exec, "/exec/<string:name>")
api.add_resource(Config, "/configs")
api.add_resource(Files, "/configs/<string:name>")


#### Run the api with devel server in debug mode
app.run(host='0.0.0.0', port=5000,debug=True)
