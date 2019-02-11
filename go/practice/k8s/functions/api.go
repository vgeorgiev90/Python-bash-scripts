package functions

import (
	"fmt"
	"net/http"
	"io/ioutil"
	"crypto/tls"
	"encoding/json"
)

func Get(server, token string) {

	auth := fmt.Sprintf("Bearer %s", token)
	//nodes_url := fmt.Sprintf("https://%s/api/v1/nodes", server)
	pods_url := fmt.Sprintf("https://%s/api/v1/pods", server)


	//Disable checking on apiserver certificate authority
	transp := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true} }
        //Create http client
        client := &http.Client{Transport: transp}

	//New request to nodes endpoint
	request, _ := http.NewRequest("GET", pods_url, nil)
	request.Header.Add("Authorization", auth)

	response, err := client.Do(request)
	if err != nil {
		fmt.Println(err)
	}

	defer response.Body.Close()

	text ,r_err := ioutil.ReadAll(response.Body)
	if r_err != nil {
		fmt.Println(r_err)
	}

	/*
	//Pretty print json
	var prettyJson bytes.Buffer

	json_error := json.Indent(&prettyJson, text, "", "  ")
	if json_error != nil {
		fmt.Println(json_error)
	}
	fmt.Println(string(prettyJson.Bytes()))
	*/

	type Itm struct {
		Metadata map[string]string
                Spec map[string]string
		Status map[string]string
	}

	type Repl struct {
		//Kind string `json:"kind"`
		//Apiversion string `json:"apiVersion"`
		//Metadata struct {
		//	Selflink string `json:"selfLink"`
		//	ResourceVersion string `json:"resourceVersion"`
		//}
		//Items []map[string]map[string]string `json:"items"`
		Items []Itm  `json:"items"`
	}

	var rep Repl
	d_err := json.Unmarshal(text ,&rep)
	if d_err != nil {
		fmt.Println(d_err)
	}


	//fmt.Println(rep.Items[0].Spec)
	//fmt.Println("")
	//fmt.Println(rep.Items[0].Metadata["name"])

	for c, _ := range rep.Items {
		fmt.Println(rep.Items[c].Metadata["name"])
	}
}
