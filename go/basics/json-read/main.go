package main

import (
	"fmt"
	"encoding/json"
	"os"
)

type Config struct {
    Host string
    User string
}

func main() {
	config_file := "config.json"
	cfg := LoadConfig(config_file)

	fmt.Println(cfg.Host)
	fmt.Println(cfg.User)
}


func LoadConfig(file string) Config {
    var conf Config

    conf_file, err := os.Open(file)
    if err != nil {
       panic(err)
    }
   
    jsonParse := json.NewDecoder(conf_file)
    jsonParse.Decode(&conf)
    return conf

}
