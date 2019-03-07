package main

import (
	"rest_api/functions"
	"flag"
)


func main() {

	var db_host string
	var cmd string
	var cert string
	var key string
	flag.StringVar(&db_host, "db", "", "Database host")
	flag.StringVar(&cmd, "cmd", "", ` 
db-init -- Initialize the database and create default user and token
run     -- Run the API with already initilized database`)
	flag.StringVar(&cert, "cert", "", "Path to SSL certificate")
	flag.StringVar(&key, "key", "", "Path to SSL key")
	flag.Parse()

	if cmd == "db-init" && db_host != "" {
		pass := functions.GetRootPass()
		functions.Db_install(db_host, pass)
		functions.Create_token(db_host , "admin")
	} else if cmd == "run" && db_host != "" && cert != "" && key != "" {
		functions.Router(db_host, cert, key)
	} else {
		functions.Usage()
		flag.Usage()
	}
}
