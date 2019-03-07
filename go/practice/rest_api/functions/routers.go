package functions

import (
	"github.com/gorilla/mux"
	"log"
	"net/http"
)


func Router() {
	router := mux.NewRouter()
	//Token management
	router.HandleFunc("/tokens/list", ListToken).Methods("GET")
	router.HandleFunc("/tokens/create/{user}", CreateToken).Methods("POST")
	router.HandleFunc("/tokens/delete/{user}", DeleteToken).Methods("DELETE")
	//Functionality
	router.HandleFunc("/exec/{name}", Exec).Methods("POST")

	log.Fatal(http.ListenAndServe(":8000", router))
}
