package functions

import (
	"encoding/json"
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"fmt"
	"os/exec"
	"io"
	"io/ioutil"
)

func Router() {
	//New Router
	router := mux.NewRouter()
	//Endpoints Declaration
	router.HandleFunc("/people", GetPeople).Methods("GET")
	router.HandleFunc("/people/{id}", GetPerson).Methods("GET")
	router.HandleFunc("/people/{id}", CreatePerson).Methods("POST")
	router.HandleFunc("/people/{id}", DeletePerson).Methods("DELETE")

	router.HandleFunc("/write_file/{var}", Exec).Methods("POST")

	log.Fatal(http.ListenAndServe(":8000", router))
}


var people []Person

type Person struct {
	ID        string   `json:"id,omitempty"`
	Firstname string   `json:"firstname,omitempty"`
	Lastname  string   `json:"lastname,omitempty"`
	Address   *Address `json:"address,omitempty"`
}
type Address struct {
	City  string `json:"city,omitempty"`
	State string `json:"state,omitempty"`
}

func GetPeople(w http.ResponseWriter, r *http.Request) {
	w.Header().Add("Content-type", "application/json")
	json.NewEncoder(w).Encode(people)
}

func GetPerson(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	fmt.Println(r)
	for _, item := range people {
		if item.ID == params["id"] {
			json.NewEncoder(w).Encode(item)
			return
		}
	}
	json.NewEncoder(w).Encode(&Person{})
}

func CreatePerson(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	var person Person
	_ = json.NewDecoder(r.Body).Decode(&person)
	person.ID = params["id"]
	people = append(people, person)
	json.NewEncoder(w).Encode(people)
}

func DeletePerson(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	for index, item := range people {
		if item.ID == params["id"] {
			people = append(people[:index], people[index+1:]...)
			break
		}
		json.NewEncoder(w).Encode(people)
	}

}


/// Write file with params and body

type Command struct {
	Content string `json:"content",omitempty`
}

func Exec(w http.ResponseWriter, r *http.Request) {
	//Get params from the url path
	params := mux.Vars(r)

	//Set headers
	w.Header().Set("Content-type", "application/json")
	w.WriteHeader(http.StatusOK)

	auth := r.Header.Get("auth")
	if auth == "viktor" {
	//Cast the body to json like defined struct
	var c Command
	b, _ := ioutil.ReadAll(r.Body)
	defer r.Body.Close()
	_ = json.Unmarshal(b, &c)

	cmd := fmt.Sprintf("echo %s > %s", c.Content, params["var"])

	out, err := exec.Command("bash", "-c", cmd).Output()
	if err != nil {
		fmt.Println(err)
	}
	//Command Output
	w.Write(out)

	//Write a response
        fmt.Fprintf(w, `File Created: %v
Content: %v`, params["var"], c.Content )
	} else {
		io.WriteString(w, "Auth header does not match")
	}
}
