package functions

import (
	"github.com/gorilla/mux"
	"log"
	"net/http"
)


func Router(db, cert, key string) {
	router := mux.NewRouter()
	//Token management
	router.HandleFunc("/tokens/list", func(w http.ResponseWriter, r *http.Request) { ListToken(w, r, db) }).Methods("GET")
	router.HandleFunc("/tokens/create/{user}", func(w http.ResponseWriter, r *http.Request) { CreateToken(w, r, db) }).Methods("POST")
	router.HandleFunc("/tokens/delete/{user}", func(w http.ResponseWriter, r *http.Request) { DeleteToken(w, r, db) }).Methods("DELETE")
	//Functionality
	router.HandleFunc("/exec/{name}", func(w http.ResponseWriter, r *http.Request) { Exec(w, r, db) }).Methods("POST")

	//Nfs
	router.HandleFunc("/nfs/connections/{action}", func(w http.ResponseWriter, r *http.Request) { Nfs_connection_mysql(w, r, db) }).Methods("POST")
	router.HandleFunc("/nfs/volume/{action}", func(w http.ResponseWriter, r *http.Request) { Nfs_provision(w, r, db) }).Methods("POST")

	//Help
	router.HandleFunc("/help", func(w http.ResponseWriter, r *http.Request) { Help(w, r, db) }).Methods("GET")

	log.Fatal(http.ListenAndServeTLS(":8000", cert, key ,router))
}
