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
POST /nfs/connections/{action}  ---     create, delete or get nfs connection string(json body containing {"nfs_host": "1.1.1.1", "key_path": "/path/to/private/key", "kube_api": "2.2.2.2:6443", "kube_token": "some-token-here"}) , for get only nfs host can be provided - {"nfs_host": "127.0.0.1"}
POST /nfs/volume/{action}	---     Provision NFS volune(json body {"directory": "/export/dir", "nfs_host": "2.2.2.2", "pvc_size": "1Gi", "pvc_name": "Something", "pvc_namespace": "default"}) action - either create or delete
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



func Nfs_connection_mysql(w http.ResponseWriter, r *http.Request, db_host string) {
        params := mux.Vars(r)

        w.Header().Set("Content-type", "application/json")
        w.WriteHeader(http.StatusOK)

        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token(db_host, user)

        if provided_token == token {
                var body Connections
                b, _ := ioutil.ReadAll(r.Body)
                defer r.Body.Close()
                _ = json.Unmarshal(b, &body)

		action := params["action"]
		if action == "create" {
			msg := Create_nfs_connection(db_host, body.Nfs_host, body.Key_path, body.Kube_api, body.Kube_token)
			io.WriteString(w, msg)
		} else if action == "get" {
			entries, _ := Get_connections(body.Nfs_host,db_host)
			for _, entry := range entries {
			msg := fmt.Sprintf("%s\n%s\n%s\n%s\n", entry.Nfs_host, entry.Key_path, entry.Kube_api, entry.Kube_token)
			io.WriteString(w, msg)
			}
                }
	} else {
                io.WriteString(w, "Provided token is invalid for this user\n")
        }
}


type Nfs struct {
	Dir string `json:"directory"`
	Host string `json:"nfs_host"`
	Size string `json:"pvc_size"`
	Name string `json:"pvc_name"`
	Namespace string `json:"pvc_namespace"`

}

func Nfs_provision(w http.ResponseWriter, r *http.Request, db_host string) {
        params := mux.Vars(r)

        w.Header().Set("Content-type", "application/json")
        w.WriteHeader(http.StatusOK)

        auth := r.Header.Get("Authorization")
        info := strings.Split(auth, " ")
        user := info[0]
        provided_token := info[1]

        token := Get_token(db_host, user)

        var body Nfs
        b, _ := ioutil.ReadAll(r.Body)
        defer r.Body.Close()
        _ = json.Unmarshal(b, &body)
        _, entry := Get_connections(body.Host, db_host)

        if provided_token == token {
		if params["action"] == "create" {
			sess := Ssh_session(entry.Nfs_host, entry.Key_path)
			Provision(sess, body.Dir)
			data, resp := Pv_provision(body.Name, body.Dir, entry.Nfs_host, entry.Kube_api, entry.Kube_token, body.Size)
			resp2 := Pvc_provision(body.Namespace, data)
			io.WriteString(w, resp)
			io.WriteString(w, resp2)
		} else if params["action"] == "delete" {
			sess := Ssh_session(entry.Nfs_host, entry.Key_path)
			Delete(sess, body.Dir)
		}
	} else {
                io.WriteString(w, "Provided token is invalid for this user\n")
        }
}
