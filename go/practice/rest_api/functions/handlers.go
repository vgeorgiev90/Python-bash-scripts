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



func DeleteToken(w http.ResponseWriter, r *http.Request) {
        params := mux.Vars(r)
        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token("10.0.11.165", user)
        if provided_token == token {
                Delete_token("10.0.11.165", params["user"])
                io.WriteString(w, "User deleted")
        } else {
                io.WriteString(w, "Provided token is invalid for this user")
        }
}


func CreateToken(w http.ResponseWriter, r *http.Request) {
        params := mux.Vars(r)
        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token("10.0.11.165", user)
        if provided_token == token {
                msg := Create_token("10.0.11.165", params["user"])
                io.WriteString(w, msg)
        } else {
                io.WriteString(w, "Provided token is invalid for this user")
        }
}


func ListToken(w http.ResponseWriter, r *http.Request) {
        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token("10.0.11.165", user)

        if provided_token == token {
                tokens := List_token("10.0.11.165")
                for _, t := range tokens {
                        out, err := json.Marshal(t)
                        if err != nil {
                                fmt.Println(err)
                        }
                        io.WriteString(w, string(out))
                }
        } else {
                io.WriteString(w, "Provided token is invalid for this user")
        }
}

type Content struct {
        Cont string `json:"content",omitempty`
}

func Exec(w http.ResponseWriter, r *http.Request) {
        params := mux.Vars(r)

        w.Header().Set("Content-type", "application/json")
        w.WriteHeader(http.StatusOK)

        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token("10.0.11.165", user)

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
                io.WriteString(w, "Provided token is invalid for this user")
        }
}

