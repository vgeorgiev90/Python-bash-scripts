package functions

import (
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
	"fmt"
	"math/rand"
	"time"
)

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

	q := []string{query1, query2, query3}

	for _, q := range q {
		insert, err := db.Query(q)
		if err != nil {
			fmt.Println(err)
		}
		defer insert.Close()
	}
}


func Delete_token(host, user string) {
        con_string := fmt.Sprintf("api:lhG379pVnTZk18LN@tcp(%s:3306)/api", host)
        db, err := sql.Open("mysql", con_string)
        if err != nil {
                fmt.Println(err)
        }
        defer db.Close()
	query := fmt.Sprintf(`DELETE FROM api.tokens WHERE user="%s"`, user)
	_, err = db.Query(query)
        if err != nil {
                fmt.Println(err)
        }
}

type DB_entry struct {
	Id string `json:"id"`
	User string `json:"user"`
	Token string `json:token`
}


func List_token(host string) (entries []DB_entry) {
	con_string := fmt.Sprintf("api:lhG379pVnTZk18LN@tcp(%s:3306)/api", host)
        db, err := sql.Open("mysql", con_string)
        if err != nil {
                fmt.Println(err)
        }
        defer db.Close()
	query := "select * from api.tokens;"
	results, err := db.Query(query)
	if err != nil {
		fmt.Println(err)
	}

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

	var tkn string
	con_string := fmt.Sprintf("api:lhG379pVnTZk18LN@tcp(%s:3306)/api", host)
	db, err := sql.Open("mysql", con_string)
	if err != nil {
                fmt.Println(err)
        }
        defer db.Close()

	query := fmt.Sprintf(`SELECT token FROM api.tokens WHERE user="%s"`, user)
	err = db.QueryRow(query).Scan(&tkn)
	if err != nil {
		fmt.Println(err)
	}

	return tkn
}

func Create_token(host, user string) (response string) {
	con_string := fmt.Sprintf("api:lhG379pVnTZk18LN@tcp(%s:3306)/api", host)
        db, err := sql.Open("mysql", con_string)
        if err != nil {
                fmt.Println(err)
        }
        defer db.Close()

	token := String(40)
	query := fmt.Sprintf(`INSERT INTO api.tokens (user, token) values ("%s", "%s")`, user, token)
	_, err = db.Query(query)
        if err != nil {
                fmt.Println(err)
        }
	msg := fmt.Sprintf("Record created:\nuser: %s\ntoken: %s\n", user, token)
	fmt.Println(msg)
	return msg
}

///Random token generator
const charset = "abcdefghijklmnopqrstuvwxyz" +
  "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

var seededRand *rand.Rand = rand.New(
  rand.NewSource(time.Now().UnixNano()))

func StringWithCharset(length int, charset string) string {
  b := make([]byte, length)
  for i := range b {
    b[i] = charset[seededRand.Intn(len(charset))]
  }
  return string(b)
}

func String(length int) string {
  return StringWithCharset(length, charset)
}

