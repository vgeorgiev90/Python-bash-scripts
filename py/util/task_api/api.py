#!/usr/bin/python3

from flask import Flask, request
from flask_restful import Api, Resource
from webargs import fields, validate
from webargs.flaskparser import use_kwargs, parser, abort
import requests
import json

app = Flask(__name__)
api = Api(app)

class Registry(Resource):

    arguments = {
        'name': fields.Str(required=True),
        'tag': fields.Str(required=True)
    }
    @use_kwargs(arguments)
    def get(self, name ,tag):
        #url = "http://%s/v2/%s/manifests/%s" % (host, name, tag)
        url = "http://registry:5000/v2/%s/manifests/%s" % (name, tag)

        response = requests.get(url)
        body = json.loads(response.text)
        layers = body['history']
        
        answer = []

        for layer in layers:
            stats = json.loads(layer['v1Compatibility'].strip())

            layer = [{"layer_id": stats['id']}, {"cmd": stats['container_config']['Cmd'] }]

            answer.append(layer)

        return answer



@parser.error_handler
def handle_request_parsing_error(err, req, schema, error_status_code, error_headers):
    abort(422, errors=err.messages)


api.add_resource(Registry, "/history")


#### Run the api with devel server in debug mode
app.run(host='0.0.0.0', port=6000,debug=True)
                                                   
