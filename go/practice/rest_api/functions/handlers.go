package functions

import (
        "encoding/json"
        "fmt"
        "os/exec"
        "io"
        "io/ioutil"
        "strings"
	"net/http"
	"github.com/gorilla/mux"
)

//Token manipulation functions

func DeleteToken(w http.ResponseWriter, r *http.Request, db_host string) {
        params := mux.Vars(r)
        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token(db_host, user)
        if provided_token == token {
                Delete_token(db_host, params["user"])
                io.WriteString(w, "User deleted")
        } else {
                io.WriteString(w, "Provided token is invalid for this user\n")
        }
}


func CreateToken(w http.ResponseWriter, r *http.Request, db_host string) {
        params := mux.Vars(r)
        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token(db_host, user)
        if provided_token == token {
                msg := Create_token(db_host, params["user"])
                io.WriteString(w, msg)
        } else {
                io.WriteString(w, "Provided token is invalid for this user\n")
        }
}


func ListToken(w http.ResponseWriter, r *http.Request, db_host string) {
        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token(db_host, user)

        if provided_token == token {
                tokens := List_token(db_host)
                for _, t := range tokens {
                        out, err := json.Marshal(t)
                        if err != nil {
                                fmt.Println(err)
                        }
                        io.WriteString(w, string(out))
                }
        } else {
                io.WriteString(w, "Provided token is invalid for this user\n")
        }
}

///Print help and API endpoints

func Help(w http.ResponseWriter, r *http.Request, db_host string) {
        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token(db_host, user)

	msg := `
GET /tokens/list		--- 	List all avaialble user tokens
POST /tokens/create/{user}	---	Create new user and token
DELETE /tokens/delete/{user}	---	Delete existing user
POST /exec/{name}		--- 	Endpoint for future functionalities( expects body with content {"content": "some info"})
GET /help			---	Print this help message
`

        if provided_token == token {
		io.WriteString(w, msg)
	} else {
                io.WriteString(w, "Provided token is invalid for this user\n")
        }
}


///Functionality to be added

type Content struct {
        Cont string `json:"content",omitempty`
}

func Exec(w http.ResponseWriter, r *http.Request, db_host string) {
        params := mux.Vars(r)

        w.Header().Set("Content-type", "application/json")
        w.WriteHeader(http.StatusOK)

        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token(db_host, user)

        if provided_token == token {
                var c Content
                b, _ := ioutil.ReadAll(r.Body)
                defer r.Body.Close()
                _ = json.Unmarshal(b, &c)

                cmd := fmt.Sprintf("echo %s > %s", c.Cont, params["name"])

                _, err := exec.Command("bash", "-c", cmd).Output()
                if err != nil {
                        fmt.Println(err)
                }
                fmt.Fprintf(w, `File Created: %v`, params["name"])
        } else {
                io.WriteString(w, "Provided token is invalid for this user\n")
        }
}

