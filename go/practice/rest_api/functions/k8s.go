package functions


import (
	"fmt"
	"net/http"
	"text/template"
	"bytes"
	"crypto/tls"
	"io/ioutil"
)


type Pv struct {
	Kube_api string
	Kube_token string
	Size string
	Name string
	Namespace string
	Path string
	Nfs_host string
}

func Pv_provision(name, path, nfs_host, kube_api, kube_token, size string) (pv_data Pv, reply string) {
	pv_data.Kube_api = kube_api
	pv_data.Kube_token = kube_token
	pv_data.Size = size
	pv_data.Name = name
	pv_data.Path = path
	pv_data.Nfs_host = nfs_host

	api_address := fmt.Sprintf("https://%s/api/v1/persistentvolumes", pv_data.Kube_api)

	t, _ := template.New("pv").Parse(`
{
  "kind": "PersistentVolume",
  "apiVersion": "v1",
  "metadata": {
    "name": "{{ .Name }}",
    "labels" : {
      "name": "{{ .Name }}"
    }
  },
  "spec": {
    "capacity": {
      "storage": "{{ .Size }}"
    },
    "nfs": {
      "path": "{{ .Path }}",
      "server": "{{ .Nfs_host }}",
      "readOnly": false
    },
    "accessModes": [
      "ReadWriteMany"
    ],
    "persistentVolumeReclaimPolicy": "Delete",
    "volumeMode": "Filesystem"
  }
}
`)
	tem := new(bytes.Buffer)
	err := t.Execute(tem, pv_data)
	if err != nil {
		fmt.Println(err)
	}

	auth := fmt.Sprintf("Bearer %s", pv_data.Kube_token)

	transp := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true} }
	client := &http.Client{Transport: transp}
	request, _ := http.NewRequest("POST", api_address, bytes.NewBuffer(tem.Bytes()))
	request.Header.Add("Authorization", auth)
	response, err := client.Do(request)
	if err != nil {
		fmt.Println(err)
	}
	defer response.Body.Close()
	text, _ := ioutil.ReadAll(response.Body)

	return pv_data, string(text)
}


func Pvc_provision(namespace string, pv_data Pv) (reply string) {
	auth := fmt.Sprintf("Bearer %s", pv_data.Kube_token)
	api_address := fmt.Sprintf("https://%s/api/v1/namespaces/%s/persistentvolumeclaims",pv_data.Kube_api ,namespace)
	pv_data.Namespace = namespace

	t, _ := template.New("pvc").Parse(`
{
  "kind": "PersistentVolumeClaim",
  "apiVersion": "v1",
  "metadata": {
     "name": "{{ .Name }}",
     "namespace": "{{ .Namespace }}"
  },
  "spec": {
    "accessModes": [ "ReadWriteMany" ],
    "resources": {
      "requests": { "storage": "{{ .Size }}" }
    },
    "selector": {
      "matchLabels": { "name": "{{ .Name }}" }
    },
    "storageClassName": ""
  }
}
`)
	tem := new(bytes.Buffer)
	err := t.Execute(tem, pv_data)
        if err != nil {
                fmt.Println(err)
        }

        transp := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true} }
        client := &http.Client{Transport: transp}
        request, _ := http.NewRequest("POST", api_address, bytes.NewBuffer(tem.Bytes()))
        request.Header.Add("Authorization", auth)
	response, err := client.Do(request)
        if err != nil {
                fmt.Println(err)
        }
        defer response.Body.Close()
	text , _ := ioutil.ReadAll(response.Body)
	return string(text)
}


func Pv_delete(name, path, nfs_host, kube_api, kube_token, size string) (pv_data Pv, reply string) {
        pv_data.Kube_api = kube_api
        pv_data.Kube_token = kube_token
        pv_data.Size = size
        pv_data.Name = name
        pv_data.Path = path
        pv_data.Nfs_host = nfs_host

        api_address := fmt.Sprintf("https://%s/api/v1/persistentvolumes/%s", pv_data.Kube_api, pv_data.Name)

        auth := fmt.Sprintf("Bearer %s", pv_data.Kube_token)

        transp := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true} }
        client := &http.Client{Transport: transp}
        request, _ := http.NewRequest("DELETE", api_address, nil)
        request.Header.Add("Authorization", auth)
        response, err := client.Do(request)
        if err != nil {
                fmt.Println(err)
        }
        defer response.Body.Close()
        text, _ := ioutil.ReadAll(response.Body)

        return pv_data, string(text)
}

func Pvc_delete(namespace string, pv_data Pv) (reply string) {
        auth := fmt.Sprintf("Bearer %s", pv_data.Kube_token)
        api_address := fmt.Sprintf("https://%s/api/v1/namespaces/%s/persistentvolumeclaims/%s",pv_data.Kube_api ,namespace, pv_data.Name)
        pv_data.Namespace = namespace

        transp := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true} }
        client := &http.Client{Transport: transp}
        request, _ := http.NewRequest("DELETE", api_address, nil)
        request.Header.Add("Authorization", auth)
        response, err := client.Do(request)
        if err != nil {
                fmt.Println(err)
        }
        defer response.Body.Close()
        text , _ := ioutil.ReadAll(response.Body)
        return string(text)
}
