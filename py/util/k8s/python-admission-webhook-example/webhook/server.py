#!/usr/bin/python

from flask import Flask, request, jsonify
import json
import base64
import jsonpatch
import yaml


app = Flask(__name__)

def check_for_pass_label(api_request, patch):

    ## Check for special label on the deployment for authorization in this case "password=viktor-secret"
    labels = api_request['request']['object']['metadata']['labels']
    for label in labels:
        if label == 'password' and labels[label] == 'viktor-secret':
            ## If correct label is there send valid response and patch
            response = {
                "apiVersion": "admission.k8s.io/v1beta1",
                "kind": "AdmissionReview",
                "response": {
                        "allowed": True,
                        "uid": api_request['request']['uid'],
                        "patch": base64.b64encode(str(patch)),
                        "patchtype": "JSONPatch"
                            }
                      }
        else:
            ## If there is no correct label Deny the request
            response = {
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
    return response



def get_patch(api_request):
    
    ## Get api object that will be created from the admission request
    api_object = api_request['request']['object']

    ## Get sidecar definition and parse it from yaml to json
    with open('/app/sidecars/container.yaml', 'r') as f:
        data = f.read()
    yaml_data = yaml.safe_load(data)
    sidecar = json.dumps(yaml_data)

    ## append the sidecar after last container in the pod
    count_last = (len(api_object['spec']['template']['spec']['containers']) - 1) + 1
    ## Replace image for first container, add label webhook=passed  and append sidecar container
    patch_string = '[{"op": "replace", "path": "/spec/template/spec/containers/0/image", "value": "viktor90/nginx:unpriv"}, {"op": "add", "path": "/spec/template/metadata/labels/webhook", "value": "passed"}, {"op": "add", "path": "/spec/template/spec/containers/%s", "value": %s }]' % (count_last, sidecar)

    patch = jsonpatch.JsonPatch.from_string(patch_string)
    return patch


## Main endpoint
@app.route('/', methods=['POST'])
def webhook():
     api_request = json.loads(request.get_data())
     patch = get_patch(api_request)
     response = check_for_pass_label(api_request, patch)
     return jsonify(response)


## Start the admission webhook app
app.run(host='0.0.0.0', port=443, ssl_context=('/app/ssl/tls.crt', '/app/ssl/tls.key'))
