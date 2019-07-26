#!/usr/bin/python

from ansible.module_utils.basic import *
import requests
import json
import yaml


DOCUMENTATION = """
---
Module: kubernetes
Short_description: Manage kubernetes resources with ansible and token based authentication
Supported resources for the moment:

deployment,
configmap,
secret,
service,
persistentvolumeclaim,
statefulset,
namespace


Notes:
There are two ways to provide object data for the moment: kubernetes yaml definition file, or json formatted data
"""

EXAMPLES = """
#Create deployment from yaml file

- name: My test module
  kubernetes:
    api_address: https://api_address:PORT
    token: YOUR_TOKEN_HERE
    type: deployment
    state: present
    file: files/nginx.yml

#Create configmap from yaml file

- name: My test module
  kubernetes:
    api_address: https://api_address:PORT
    token: YOUR_TOKEN_HERE
    type: configmap
    state: present
    file: files/config.yml

# Delete resources

- name: My test module
  kubernetes:
    api_address: https://api_address:PORT
    token: YOUR_TOKEN_HERE
    type: deployment                                 ## Type may be deployment, configmap
    state: absent
    name: ansible-test                               ## Name is mandatory to be able to find the resource as well as type


"""

### Namespace resource ######################

def namespace_present(data):
    config = data
    api_address = config['api_address']
    token = config['token']
    headers = {
        "Authorization": "",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    headers['Authorization'] = "Bearer " + token

    url = api_address + "/api/v1/namespaces"
    if config.get('data'):
        obj_data = json.loads(config['data'])
    elif config.get('file'):
        file_path = config['file']
        with open(file_path, 'r') as f:
            obj = f.read()
        obj_data = json.loads(json.dumps(yaml.safe_load(obj)))
    else:
        has_changed = False
        is_error = True
        meta = "Please provide eith data field with json formated kubernetes data or file with path to the yaml file"
        return (has_changed, meta, is_error)
    requests.packages.urllib3.disable_warnings()
    response = requests.post(url, headers=headers, data=json.dumps(obj_data), verify=False)
    if response.status_code == 201:
        has_changed = True
        meta = response.json()
        is_error = False
        return (has_changed, meta, is_error)
    else:
        has_changed = False
        meta = response.json()
        is_error = True
        return (has_changed, meta, is_error)

def namespace_absent(data):
    config = data
    api_address = config['api_address']
    token = config['token']
    headers = {
        "Authorization": "",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    headers['Authorization'] = "Bearer " + token
    if config.get('name'):
        obj_name = config['name']
    else:
        has_changed = False
        meta = "Please provide object name for absent state"
        is_error = True
        return (has_changed, meta, is_error)

    url = api_address + "/api/v1/namespaces/" + obj_name
    requests.packages.urllib3.disable_warnings()
    response = requests.delete(url, headers=headers, verify=False)
    if response.status_code == 201 or response.status_code == 200:
        has_changed = True
        meta = response.json()
        is_error = False
        return (has_changed, meta, is_error)
    else:
        has_changed = False
        meta = response.json()
        is_error = True
        return (has_changed, meta, is_error)


#### Deployment resource functions ############
def present(data):
    config = data
    api_address = config['api_address']
    token = config['token']
    kind = data['type']

    headers = {
        "Authorization": "",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    headers['Authorization'] = "Bearer " + token

    ## Check if inline deployment data is provided or yaml file is referenced and extract the namespace as it will be needed for url construction
    if config.get('data'):
        obj_data = json.loads(config['data'])
        if obj_data('namespace'):
            namespace = obj_data['namespace']
        else:
            namespace = "default"
    elif config.get('file'):
        file_path = config['file']
        with open(file_path, 'r') as f:
            obj = f.read()
        obj_data = json.loads(json.dumps(yaml.safe_load(obj)))
        if obj_data.get('namespace'):
            namespace = obj_data['namespace']
        else:
            namespace = "default"
    else:
        has_changed = False
        is_error = True
        meta = "Please provide eith data field with json formated kubernetes data or file with path to the yaml file"
        return (has_changed, meta, is_error)

    endpoints = {
         "deployment": "/apis/apps/v1/namespaces/",
         "configmap": "/api/v1/namespaces/",
         "secret": "/api/v1/namespaces/",
         "service": "/api/v1/namespaces/",
         "persistentvolumeclaim": "/api/v1/namespaces/",
         "statefulset": "/apis/apps/v1/namespaces/"
    }


    ## Construct the url and submit
    if kind == "deployment":
        url = api_address + endpoints[kind] + namespace + "/deployments"
    elif kind == "configmap":
        url = api_address + endpoints[kind] + namespace + "/configmaps"
    elif kind == "secret":
        url = api_address + endpoints[kind] + namespace + "/secrets"
    elif kind == "service":
        url = api_address + endpoints[kind] + namespace + "/services"
    elif kind == "persistentvolumeclaim":
        url = api_address + endpoints[kind] + namespace + "/persistentvolumeclaims"
    elif kind == "statefulset":
        url = api_address + endpoints[kind] + namespace + "/statefulsets"

    requests.packages.urllib3.disable_warnings()
    response = requests.post(url, headers=headers, data=json.dumps(obj_data), verify=False)

    ## Check the status code to determine success or failure
    if response.status_code == 201 or response.status_code == 200:
        has_changed = True
        meta = response.json()
        is_error = False
        return (has_changed, meta, is_error)
    else:
        has_changed = False
        meta = response.json()
        is_error = True
        return (has_changed, meta, is_error)


def absent(data):
    config = data
    api_address = config['api_address']
    token = config['token']
    kind = config['type']

    headers = {
        "Authorization": "",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    headers['Authorization'] = "Bearer " + token

    ##  Check if deployment name is provided or not to construct all deployments check url
    if config.get('name'):
        obj_name = config['name']
    else:
        has_changed = False
        meta = "Please provide object name for absent state"
        is_error = True
        return (has_changed, meta, is_error)

    ## Api endpoints based on object type
    endpoints = {
        "deployment": "/apis/extensions/v1beta1/deployments",
        "configmap": "/api/v1/configmaps/",
        "secret": "/api/v1/secrets/",
        "service": "/api/v1/services/",
        "persistentvolumeclaim": "/api/v1/persistentvolumeclaims/",
        "statefulset": "/apis/apps/v1/statefulsets",
    }

    ## Check all objects of this type in the cluster the match the correct one and extract the selfLink which will be used to construct delete url
    check_url = api_address + endpoints[kind]
    requests.packages.urllib3.disable_warnings()
    data = requests.get(check_url, headers=headers ,verify=False)

    all_objects = data.json()
    ## Extract the delete url for the specified deployment
    for item in all_objects['items']:
        name = item['metadata']['name']
        url = api_address + item['metadata']['selfLink']
        if name == obj_name:
            if kind == 'deployment' or kind == 'statefulset':
                delete = requests.delete(url + "?propagationPolicy=Foreground", headers=headers, verify=False)
            else:
                delete = requests.delete(url, headers=headers, verify=False)
            has_changed = True
            meta = delete.json()
            is_error = False
            return (has_changed, meta, is_error)
        else:
            has_changed = False
            meta = "Object with such name not found.."
            is_error = True
            return (has_changed, meta, is_error)
############################################################################




def main():
    ### Arguments for our kubernetes module
    arguments = {
        "api_address": {"required": True, "type": "str"},
        "token": {"required": True, "type": "str"},
        "type": {
             "required": True,
             "type": "str",
             "choices": ["deployment", "configmap", "secret", "service", "persistentvolumeclaim", "statefulset", "namespace"]
        },
        "state": {
             "default": "present",
             "type": "str",
             "choices": ["present", "absent"]
        },
        "data": {"required": False, "type": "dict"},
        "file": {"required": False, "type": "str"},
        "name": {"required": False, "type": "str"},
    }

    ### Choose function based on type and state declared
    choice_map = {
        "deployment": {
                "present": present,
                "absent": absent,
         },
        "configmap": {
                "present": present,
                "absent": absent,
         },
        "secret" : {
                "present": present,
                "absent": absent,
        },
        "service" : {
                "present": present,
                "absent": absent,
        },
        "persistentvolumeclaim" : {
                "present": present,
                "absent": absent,
        },
        "statefulset" : {
                "present": present,
                "absent": absent,
        },
        "namespace" : {
                "present": namespace_present,
                "absent": namespace_absent,
        },

    }

    module = AnsibleModule(argument_spec=arguments)
    has_changed, result, is_error = choice_map.get(module.params['type'])[module.params['state']](module.params)
    ### Check the execution status
    if is_error == False:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error received: ", meta=result)



if __name__ == '__main__':
    main()
