package main

import (
	"storage-check/functions"
	"flag"
	"fmt"
)

func main() {
	var host string

	flag.StringVar(&host, "host", "", "Heketi server address")
	flag.Parse()

	if host == "" {
		fmt.Println("Provide heketi host and port in format host:port")
		flag.Usage()
	} else {
		data := functions.Heketi(host)
		functions.Parse(data)
	}
}
