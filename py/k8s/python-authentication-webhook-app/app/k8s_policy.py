
import requests
import json
import yaml



class cluster():

    def __init__(self, ca_cert, api_address, token):
	self.token = token
	self.api_address = api_address
	self.ca_cert = ca_cert
        self.headers =  {}
        self.headers['Authorization'] = "Bearer " + token
	self.headers['Accept'] = "application/json"

    def role_create(self, role_yaml):
	url = "https://" + self.api_address + "/apis/rbac.authorization.k8s.io/v1/clusterroles/"
	role = json.dumps(yaml.load(role_yaml))
	response = requests.post(url, headers=self.headers, data=role, verify=self.ca_cert)

    def role_binding_create(self, rolebinding_yaml):
        url = "https://" + self.api_address + "/apis/rbac.authorization.k8s.io/v1/clusterrolebindings"
        role = json.dumps(yaml.load(role_yaml))
        response = requests.post(url, headers=self.headers, data=role, verify=self.ca_cert)


    def role_delete(self, role_name):
	url = "https://" + self.api_address + "/apis/rbac.authorization.k8s.io/v1/clusterroles/" + role_name
	res = requests.delete(url, headers=self.headers, verify=self.ca_cert)

    def rolebind_delete(self, bind_name):
	url = "https://" + self.api_address + "/apis/rbac.authorization.k8s.io/v1/clusterrolebindings/" + bind_name
	res = requests.delete(url, headers=self.headers, verify=self.ca_cert)


    def get_clusterroles(self):

        url = "https://" + self.api_address + "/apis/rbac.authorization.k8s.io/v1/clusterroles"
     
        response = requests.get(url, headers=self.headers, verify=self.ca_cert)
        all_roles = json.loads(response.text)
        not_system_roles = []
        for role in all_roles['items']:
            if 'system' not in role['metadata']['name']:
	        not_system_roles.append(role)
	return not_system_roles
	    
    def get_crbindings(self):
	url = "https://" + self.api_address + "/apis/rbac.authorization.k8s.io/v1/clusterrolebindings"

        response = requests.get(url, headers=self.headers, verify=self.ca_cert)
        all_binds = json.loads(response.text)
        not_system_binds = []
        for bind in all_binds['items']:
            if 'system' not in bind['metadata']['name']:
                not_system_binds.append(bind)
        return not_system_binds

