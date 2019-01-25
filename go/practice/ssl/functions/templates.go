package functions

import (
	"fmt"
	"io/ioutil"
	"os"
	"text/template"
	"strings"
)


// Define struct to hold template variables
type configs struct {
	Common_name string
	Alt_names   string
}

func Template(c_name , a_names string) {
	//Create directory to hold our certificates
	if _, err := os.Stat("/root/certificates"); os.IsNotExist(err) {
	   os.Mkdir("/root/certificates", 0750)
	}


	//ca config template
	ca_config := `{
   "signing": {
    "default": {
      "expiry": "8760h"
    },
    "profiles": {
      "kubernetes": {
        "usages": ["signing", "key encipherment", "server auth", "client auth"],
        "expiry": "8760h"
      }
     }
    }
   }`

	//Check if ca-config exists exists if not create it
	if _, err := os.Stat("/root/certificates/config.json"); os.IsNotExist(err) {
		ioutil.WriteFile("/root/certificates/config.json", []byte(ca_config), 0644)
	}

	//Generate variables for template substitution with our defined struct
	c := configs{c_name, a_names}

	//Create new template
	t, err := template.New("csr").Parse(`
       {
         "CN": "{{ .Common_name }}",
         "key": {
         "algo": "rsa",
         "size": 2048
         },
        "names": [
          {
          "C": "BG",
          "L": "Sofia",
          "O": "{{ .Alt_names }}",
          "OU": "CA",
          "ST": "Sofia"
        }
        ]
       }
       `)
	if err != nil {
		fmt.Println(err)
	}

	// Use os.Create to open the output file name is derived from common_name struct var
	path := []string{"/root/certificates", c.Common_name}
	f, err := os.Create(strings.Join(path, "/"))
	//Execute template and write it to the open file
	t_err := t.Execute(f, c)
	if t_err != nil {
		fmt.Println(t_err)
	}
}
