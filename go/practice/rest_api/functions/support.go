package functions

import (
	"bufio"
	"fmt"
	"strings"
	"os"
	"math/rand"
	"time"
)

func GetRootPass() (pass string) {
	reader := bufio.NewReader(os.Stdin)
	fmt.Println("MySQL root password: ")
	pass, _ = reader.ReadString('\n')
	pass = strings.TrimSpace(pass)

	return pass
}

func Usage() {
	fmt.Println(`
----------------------------------------------------------
Before first run Database needs to be initialized
-cmd db-init -db DB_HOST
After this is done 
-cmd run -db DB_HOST -cert /path/to/cert -key /path/to-key
----------------------------------------------------------
`)
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

