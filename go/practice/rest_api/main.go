package main

import (
	"rest_api/functions"
)

func main() {
	//functions.Db_install("10.0.11.165", "viktor123")
	//token := functions.Get_token("10.0.11.165", "ioana")
	//functions.Create_token("10.0.11.165", "ioana")
	functions.Router()
	//tokens := functions.List_token("10.0.11.165")
	//fmt.Println(tokens)
}
