#!/usr/bin/python

from flask import Flask, request, jsonify
import json
import base64
import jsonpatch
import yaml


app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
         
     
     api_request = json.loads(request.get_data())
 
     labels = api_request['request']['object']['metadata']['labels']
     for label in labels:
         if labels[label] == 'viktor-secret' and label == 'password':

             ## Get the object from the admission request
             api_object = api_request['request']['object']

             ## Check the image used in the first container
             image = api_object['spec']['template']['spec']['containers'][0]['image']

	     ## Check sidecar definition and add it to the patch
             with open('../sidecars/container.yaml', 'r') as f:
                 data = f.read()
             yaml_data = yaml.safe_load(data)
             sidecar = json.dumps(yaml_data)

             ## append the sidecar after last container in the pod
             count_last = (len(api_object['spec']['template']['spec']['containers']) - 1) + 1

             patch_string = '[{"op": "replace", "path": "/spec/template/spec/containers/0/image", "value": "viktor90/nginx:unpriv"}, {"op": "add", "path": "/spec/template/metadata/labels/webhook", "value": "passed"}, {"op": "add", "path": "/spec/template/spec/containers/%s", "value": %s }]' % (count_last, sidecar)


             ### Change container image and add label
             patch = jsonpatch.JsonPatch.from_string(patch_string)  


             response_patch = {
                "apiVersion": "admission.k8s.io/v1beta1",
                "kind": "AdmissionReview",
                "response": {
                        "allowed": True,
                        "uid": api_request['request']['uid'],
			"patch": base64.b64encode(str(patch)),
			"patchtype": "JSONPatch"
                	    }
		      }		

             return jsonify(response_patch)
         else:
             response_deny = {
                "apiVersion": "admission.k8s.io/v1beta1",
                "kind": "AdmissionReview",
                "response": {
                        "allowed": False,
                        "uid": api_request['request']['uid'],
                        "status": {
                                "code": 403,
                                "message": "NO PODS FOR YOU WITHOUT PASSWORD XAXAXAXA!!!!!"
                                }
                            }
                     }
             return jsonify(response_deny) 


app.run(host='0.0.0.0', port=10000, ssl_context=('../ssl/webhook.admission-test.svc.pem', '../ssl/webhook.admission-test.svc-key.pem'))
