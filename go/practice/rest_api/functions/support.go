package functions

import (
	"bufio"
	"fmt"
	"strings"
	"os"
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
