package functions

import (
        "database/sql"
        _ "github.com/go-sql-driver/mysql"
        "fmt"
)


//Database initialization
func Db_install(host, pass string) {

        con_string := fmt.Sprintf("root:%s@tcp(%s:3306)/", pass, host)
        db, err := sql.Open("mysql", con_string)
        if err != nil {
                fmt.Println(err)
        }
        defer db.Close()

        query1 := "CREATE DATABASE api"
        query2 := `GRANT ALL PRIVILEGES ON api.* to "api"@"%" identified by password "*2DBEA98FA33583163DC5C7E3AF2BCEA356749BBF"` //lhG379pVnTZk18LN
        query3 := `CREATE TABLE api.tokens (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, user VARCHAR(10), token VARCHAR(50))`
        query4 := `CREATE TABLE api.connections (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, nfs_host VARCHAR(23), key_path VARCHAR(50), kube_api VARCHAR(23), kube_token VARCHAR(1000))`

        q := []string{query1, query2, query3, query4}

        for _, q := range q {
                insert, err := db.Query(q)
                if err != nil {
                        fmt.Println(err)
                }
                defer insert.Close()
        }
}



func Db_connection(query, host string) *sql.Rows {
	con_string := fmt.Sprintf("api:lhG379pVnTZk18LN@tcp(%s:3306)/api", host)
        db, err := sql.Open("mysql", con_string)
        if err != nil {
                fmt.Println(err)
        }
        defer db.Close()
	results, err := db.Query(query)
        if err != nil {
                fmt.Println(err)
        }
	return results
}


func Delete_token(host, user string) {
	query := fmt.Sprintf(`DELETE FROM api.tokens WHERE user="%s"`, user)
	_ = Db_connection(query, host)
}

func Create_token(host, user string) (response string) {
	token := String(40)
	query := fmt.Sprintf(`INSERT INTO api.tokens (user, token) values ("%s", "%s")`, user, token)
	_ = Db_connection(query, host)
        msg := fmt.Sprintf("Record created:\nuser: %s\ntoken: %s\n", user, token)
        fmt.Println(msg)
        return msg
}


type DB_entry struct {
        Id string `json:"id"`
        User string `json:"user"`
        Token string `json:token`
}

func List_token(host string) (entries []DB_entry) {
	query := "select * from api.tokens;"
	results := Db_connection(query, host)
	for results.Next() {
                var entry DB_entry
                err := results.Scan(&entry.Id, &entry.User, &entry.Token)
                if err != nil {
                        fmt.Println(err)
                }
                entries = append(entries, entry)
        }
        return entries
}

func Get_token(host, user string) (token string) {
	query := fmt.Sprintf(`SELECT token FROM api.tokens WHERE user="%s"`, user)
	tkn := Db_connection(query, host)
	for tkn.Next() {
		err := tkn.Scan(&token)
		if err != nil {
			fmt.Println(err)
		}
	}
	return token
}


type Connections struct {
	Id  int	`json:"id",omitempty`
        Nfs_host string `json:"nfs_host",omitempty`
        Key_path string `json:"key_path",omitempty`
        Kube_api string `json:"kube_api",omitempty`
        Kube_token string `json:"kube_token",omitempty`
}

func Create_nfs_connection(host, nfs_host, key_path, kube_api, kube_token string) string {
	query := fmt.Sprintf(`INSERT INTO api.connections (nfs_host, key_path, kube_api, kube_token) values ("%s", "%s", "%s", "%s")`, nfs_host, key_path, kube_api, kube_token)
	_ = Db_connection(query, host)
	msg := fmt.Sprintf("Record created:\nnfs_host: %s\nkey_path: %s\n,kube_api: %s\n,kube_tokebn: %s\n", nfs_host, key_path, kube_api, kube_token)
        fmt.Println(msg)
        return msg
}


func Get_connections(nfs_host, host string) (conns []Connections, conn Connections) {
	query := "select * from api.connections;"
	var entries []Connections
	var entry Connections
	results := Db_connection(query, host)
        for results.Next() {
                err := results.Scan(&entry.Id, &entry.Nfs_host, &entry.Key_path, &entry.Kube_api, &entry.Kube_token)
                if err != nil {
                        fmt.Println(err)
                }
		entries = append(entries, entry)
        }

	query2 := fmt.Sprintf(`select * from api.connections where nfs_host="%s"`, nfs_host)
	result := Db_connection(query2, host)
	for result.Next() {
		err := result.Scan(&entry.Id, &entry.Nfs_host, &entry.Key_path, &entry.Kube_api, &entry.Kube_token)
		if err != nil {
			fmt.Println(err)
		}
	}
	return entries, entry

}
