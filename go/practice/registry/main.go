package main

import (
	"registry/functions"
	"flag"
	"fmt"
)

func main() {

	var repo string
	var tag string
	var cmd string
	flag.StringVar(&repo, "repo", "", "Repository name")
	flag.StringVar(&tag, "tag", "", "Tag name")
	flag.StringVar(&cmd, "cmd", "", "repo-list, tag-list or delete")
	flag.Parse()

	config := functions.Config()
	pass := functions.GetPassword(config.Pass)

	if cmd == "repo-list" {
		functions.Catalog(config.Url, config.User, pass)
	} else if cmd == "tag-list" {
		if repo != "" {
			functions.GetTags(config.Url, config.User, pass, repo)
		} else {
			fmt.Println("Provide repository name with -repo NAME")
		}
	} else if cmd == "delete" {
		if repo != "" && tag != "" {
			functions.DeleteTag(config.Url, config.User, pass, repo, tag)
		} else {
			fmt.Println("Provide repository name and tag name with -repo NAME -tag NAME")
		}
	} else {
		flag.Usage()
	}

}
