package main

import (
	"elk/functions"
	"flag"
)

func main() {

	var search string
	var del string
	var host string

	flag.StringVar(&del, "d", "", "Index to be deleted")
	flag.StringVar(&search, "s", "", "What to check: health, indices, threads")
	flag.StringVar(&host, "host", "", "Elastic search host")
	flag.Parse()

	if search != "" && host != "" {
		switch search {
		case "health":
			functions.Health(host)
		case "indices":
			functions.Indices(host)
		case "threads":
			functions.Thread_pool(host)
		default:
			flag.Usage()
		}
	} else if del != "" && host != "" {
		functions.Delete("10.0.8.62", del)
	} else {
		flag.Usage()
	}
}
