package functions

import (
	"fmt"
	"os"
	"encoding/json"
	"io/ioutil"
)

type Config struct {
    Resource_name string
    Device string
    Disk string
    Fs_type string
    Directory string
    Hostnames []string
    Ips []string
}


func LoadConfig(file string) Config {
    var conf Config

    conf_file, err := os.Open(file)
    if err != nil {
       fmt.Println(err)
    }

    jsonParse := json.NewDecoder(conf_file)
    jsonParse.Decode(&conf)
    return conf
}

func GenConfig() {
	config_data := `
{
  "resource_name": "res0",
  "device": "/dev/drbd0",
  "disk": "/dev/sdb",
  "fs_type": "ext4",
  "hostnames": ["node1", "node2"],
  "ips": ["10.0.1.10", "10.0.1.11"],
  "directory": "/mnt/drbd"
}
`

	_ = ioutil.WriteFile("/root/nfs-ha.json", []byte(config_data), 0644)

}
